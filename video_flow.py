#!/usr/bin/env python3
"""
AI Video Director (`video_flow.py`) — Industrial Low-Cost Quality-Gated Video Pipeline

Architecture (inspired by OpenMontage, HKUDS/ViMax, VBench-2.0 / VideoScore2, and AV Script):
  - Strict Schema Validation (`validate`): blocks vague prompts lacking second-by-second
    `beat_timeline`, `camera`, `physics_and_fidelity_constraints`, `tier`, or `max_budget_usd`.
  - Budget Circuit Breaker: halts paid video generation if projected spend exceeds `max_budget_usd`.
  - Radio Play First (`audio`): unified TTS + optional BGM locks exact segment timing.
  - Visual Bible & Keyframes (`assets`, `keyframes`): locks character/product identity.
  - 5-Dimension CoT VLM Quality Gates (`qc_keys`, `qc_video`): scores physics/domain,
    subject/product fidelity, beat alignment, visual cleanliness, and composition safe zone.
    Hard veto if any dimension < 7 or average < min_pass_score (default 8.5).
  - Draft-First, Hero-Upgrade (`video --res 360p` -> `upgrade_hero --res 720p`).
  - Zero-Cost Local Assembly (`assemble`) + Exact Token Cost Report (`cost`).
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Official Gemini Developer API Paid Tier pricing (USD per 1M tokens)
PRICE = {
    "omni_in": 1.50,
    "omni_thought": 9.00,
    "omni_video": 12.00,
    "img_in": 1.50,
    "img_thought": 7.50,
    "img_out": 30.00,
    "tts_audio_per_sec": 25 * 9.00 / 1e6,
}

VTOK_PER_SEC = {
    "360p": 1931,
    "720p": 5792,
    "1080p": 12000,
    "4k": 28000,
}

QC_DIMENSIONS = [
    "physics_and_domain",
    "subject_and_product_fidelity",
    "beat_alignment",
    "visual_cleanliness",
    "composition_safe_zone",
]

FONT_CANDIDATES_BOLD = [
    os.environ.get("VIDEO_FLOW_FONT_BOLD", ""),
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

FONT_CANDIDATES_REG = [
    os.environ.get("VIDEO_FLOW_FONT_REG", ""),
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REG
    for path in candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def load_cfg(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_dirs(cfg: dict, cfg_path: Path) -> dict:
    work_root = cfg.get("work_dir")
    if work_root:
        root = Path(work_root)
        if not root.is_absolute():
            root = (cfg_path.parent / root).resolve()
    else:
        root = Path.cwd() / "work" / cfg["project"]
    dirs = {
        "root": root,
        "assets": root / "assets",
        "audio": root / "audio",
        "keyframes": root / "keyframes",
        "clips": root / "clips",
        "qc": root / "qc",
        "overlays": root / "overlays",
        "rendered": root / "rendered",
        "out": root / "out",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def canvas_size(cfg: dict) -> tuple[int, int]:
    if "width" in cfg and "height" in cfg:
        return int(cfg["width"]), int(cfg["height"])
    return (720, 1280) if cfg.get("aspect_ratio", "9:16") == "9:16" else (1280, 720)


def ffprobe_dur(path: Path) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            text=True,
        ).strip()
    )


def resolve_ref_path(ref: str, dirs: dict) -> Path:
    p = Path(ref)
    if p.exists():
        return p
    for key in ("assets", "keyframes", "root"):
        cand = dirs[key] / ref
        if cand.exists():
            return cand
    raise FileNotFoundError(f"Reference file not found: {ref}")


def fetch_usage(response_id: str | None) -> dict | None:
    if not response_id:
        return None
    p = subprocess.run(["gemini-api", "agent", "status", response_id, "-o", "json"], capture_output=True, text=True)
    if p.returncode == 0:
        try:
            return json.loads(p.stdout).get("usage")
        except json.JSONDecodeError:
            return None
    return None


def compile_video_prompt(shot: dict, cfg: dict) -> str:
    """Compile structured second-by-second shot metadata into a crisp pure-motion prompt."""
    if shot.get("video_prompt"):
        return shot["video_prompt"]
    cam = shot["camera"]
    beats = " ".join(f"[{b['t']}] {b['action']}." for b in shot["beat_timeline"])
    constraints = " ".join(shot["physics_and_fidelity_constraints"])
    amb = (shot.get("audio_sync") or {}).get("ambient_sfx", "subtle realistic natural environment ambience only")
    return (
        "Use this image as the starting frame. In a SINGLE continuous unbroken shot — strictly NO scene cuts, "
        "NO abrupt framing jumps, NO teleporting furniture or props. Pure visual motion only: NO dialogue, "
        "NO voiceover, NO speech, NO on-screen text, NO labels, NO floating hologram CGI, NO watermark. "
        f"Aspect ratio {cfg.get('aspect_ratio', '9:16')}. "
        f"Camera: {cam.get('framing', '')}, {cam.get('angle', '')}, {cam.get('movement', '')}. "
        f"Action timeline: {beats} "
        f"Hard constraints: {constraints} "
        f"Audio: {amb}."
    )


def compile_qc_checklist(shot: dict) -> str:
    beats = "; ".join(f"{b['t']}: {b['action']}" for b in shot.get("beat_timeline", []))
    cons = "; ".join(shot.get("physics_and_fidelity_constraints", []))
    extra = shot.get("qc_checklist", "")
    return f"Expected beats: {beats} | Hard constraints: {cons} | {extra}".strip()


# ---------- Stage 0: Strict Schema Validation ----------

def stage_validate(cfg: dict) -> list[str]:
    print(f"\n=== STAGE: validate ({cfg.get('project', '<unnamed>')}) ===")
    errors = []
    for req in ("project", "aspect_ratio", "max_budget_usd", "shots"):
        if req not in cfg:
            errors.append(f"Missing top-level field: '{req}'")
    if cfg.get("aspect_ratio") not in ("9:16", "16:9"):
        errors.append(f"Invalid aspect_ratio: {cfg.get('aspect_ratio')} (must be '9:16' or '16:9')")
    if not isinstance(cfg.get("max_budget_usd"), (int, float)) or cfg.get("max_budget_usd", 0) <= 0:
        errors.append("'max_budget_usd' must be a positive number")

    seen_ids = set()
    hero_count = 0
    for i, s in enumerate(cfg.get("shots", [])):
        sid = s.get("id") or f"shot#{i}"
        if sid in seen_ids:
            errors.append(f"[{sid}] duplicate shot id")
        seen_ids.add(sid)

        if s.get("tier") not in ("standard", "hero"):
            errors.append(f"[{sid}] missing or invalid 'tier' (must be 'standard' or 'hero')")
        elif s["tier"] == "hero":
            hero_count += 1

        cam = s.get("camera")
        if not isinstance(cam, dict) or not cam.get("framing") or not cam.get("movement"):
            errors.append(f"[{sid}] missing 'camera' with 'framing' and 'movement'")

        beats = s.get("beat_timeline")
        if not isinstance(beats, list) or len(beats) < 2:
            errors.append(f"[{sid}] 'beat_timeline' must have at least 2 second-level beats (no vague one-liners)")
        else:
            for bi, b in enumerate(beats):
                if not isinstance(b, dict) or not b.get("t") or not b.get("action"):
                    errors.append(f"[{sid}] beat_timeline[{bi}] requires 't' and 'action'")

        cons = s.get("physics_and_fidelity_constraints")
        if not isinstance(cons, list) or len(cons) < 1:
            errors.append(f"[{sid}] missing 'physics_and_fidelity_constraints' (must define physics/product/no-text rules)")

        if not s.get("keyframe_path") and not s.get("keyframe_prompt"):
            errors.append(f"[{sid}] requires either 'keyframe_path' or 'keyframe_prompt'")

    if errors:
        print(f"[FAIL] Schema validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(2)

    print(f"[PASS] Schema valid | shots={len(cfg['shots'])} (hero={hero_count}) | max_budget=${cfg['max_budget_usd']:.2f}")
    return errors


# ---------- Budget Calculator & Circuit Breaker ----------

def compute_current_cost(cfg: dict, dirs: dict) -> tuple[float, float, float, list[str]]:
    vid_cost = img_cost = tts_cost = 0.0
    vid_rows = []
    for shot in cfg["shots"]:
        sid = shot["id"]
        mp = dirs["clips"] / f"{sid}.json"
        if mp.exists():
            d = json.loads(mp.read_text(encoding="utf-8"))
            u = d.get("usage") or {}
            res = d.get("resolution", "?")
            dur = d.get("requested_duration", shot.get("video_duration", 5))
            vtok = u.get("total_output_tokens", 0)
            note = ""
            if vtok == 0:
                vtok = int(dur * VTOK_PER_SEC.get(res, 5792))
                note = " (est)"
            c = u.get("total_input_tokens", 1200) * PRICE["omni_in"] / 1e6 + u.get("total_thought_tokens", 700) * PRICE["omni_thought"] / 1e6 + vtok * PRICE["omni_video"] / 1e6
            vid_cost += c
            vid_rows.append(f"  - {sid:16s} [{shot.get('tier','?'):8s}] {dur}s @ {res:5s} | {vtok:6d} vtok -> ${c:.4f}{note}")
        elif (dirs["clips"] / f"{sid}.mp4").exists():
            dur = round(ffprobe_dur(dirs["clips"] / f"{sid}.mp4"))
            wh = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(dirs["clips"] / f"{sid}.mp4")], text=True).strip()
            min_dim = min(int(x) for x in wh.split(","))
            res = "360p" if min_dim <= 400 else "720p" if min_dim <= 760 else "1080p"
            vtok = int(dur * VTOK_PER_SEC[res])
            c = vtok * PRICE["omni_video"] / 1e6 + 0.01
            vid_cost += c
            vid_rows.append(f"  - {sid:16s} [{shot.get('tier','?'):8s}] {dur}s @ {res:5s} | {vtok:6d} vtok -> ${c:.4f} (est)")

    for folder in (dirs["assets"], dirs["keyframes"]):
        for jf in folder.glob("*.json"):
            d = json.loads(jf.read_text(encoding="utf-8"))
            u = d.get("usage") or {}
            ot = sum(m.get("tokens", 0) for m in u.get("output_tokens_by_modality", []) if m.get("modality") == "image")
            img_cost += u.get("total_input_tokens", 200) * PRICE["img_in"] / 1e6 + u.get("total_thought_tokens", 500) * PRICE["img_thought"] / 1e6 + (ot or 1120) * PRICE["img_out"] / 1e6

    tts_sec = sum(ffprobe_dur(wf) for wf in dirs["audio"].glob("*.wav"))
    tts_cost = tts_sec * PRICE["tts_audio_per_sec"]
    return vid_cost, img_cost, tts_cost, vid_rows


def check_budget_guard(cfg: dict, dirs: dict, pending_shots: list[dict], resolution: str, force: bool, ignore_budget: bool):
    to_gen = [s for s in pending_shots if force or not (dirs["clips"] / f"{s['id']}.mp4").exists()]
    if not to_gen:
        return
    vid_c, img_c, tts_c, _ = compute_current_cost(cfg, dirs)
    spent = vid_c + img_c + tts_c
    est_add = sum((int(s.get("video_duration", 5)) * VTOK_PER_SEC[resolution] * PRICE["omni_video"] / 1e6 + 0.01) for s in to_gen)
    projected = spent + est_add
    limit = float(cfg["max_budget_usd"])
    print(f"[BUDGET] Spent=${spent:.3f} + Projected({len(to_gen)} shots @ {resolution})=${est_add:.3f} => ${projected:.3f} / Limit=${limit:.2f}")
    if projected > limit and not ignore_budget:
        print(f"[BUDGET HALT] Projected total ${projected:.3f} exceeds max_budget_usd=${limit:.2f}.")
        print("Raise 'max_budget_usd' in config, lower --res, target fewer --shots, or pass --ignore-budget.")
        raise SystemExit(3)


# ---------- Stage 1 & 2: Assets, Audio, Keyframes ----------

def gen_image_item(out_path: Path, prompt: str, refs: list[Path], aspect: str, img_size: str, force: bool) -> tuple[str, bool, str]:
    meta_path = out_path.with_suffix(".json")
    if out_path.exists() and not force:
        return (out_path.name, True, "cached")
    cmd = ["gemini-api", "image", prompt, "--aspect-ratio", aspect, "--image-size", img_size, "--out", str(out_path), "-o", "json"]
    for r in refs:
        cmd += ["-i", str(r)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return (out_path.name, False, p.stderr or p.stdout)
    info = json.loads(p.stdout)
    info["usage"] = fetch_usage(info.get("response_id"))
    meta_path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return (out_path.name, True, "ok")


def stage_assets(cfg: dict, dirs: dict, force: bool):
    items = cfg.get("assets") or []
    if not items:
        print("\n=== STAGE: assets (none declared, skipping) ===")
        return
    print(f"\n=== STAGE: assets ({len(items)} anchor image(s)) ===")
    aspect, img_size = cfg.get("aspect_ratio", "9:16"), cfg.get("image_size", "1K")
    for item in items:
        out_path = dirs["assets"] / item["filename"]
        refs = [resolve_ref_path(r, dirs) for r in item.get("refs", [])]
        name, ok, msg = gen_image_item(out_path, item["prompt"], refs, item.get("aspect_ratio", aspect), item.get("image_size", img_size), force)
        print(f"[{'OK' if ok else 'FAIL'}] {name}: {msg}")
        if not ok:
            raise RuntimeError(f"Asset failed: {name}: {msg}")


def stage_audio(cfg: dict, dirs: dict, force: bool):
    print("\n=== STAGE: audio (Radio Play First: Unified TTS + Optional BGM) ===")
    tts_cfg = cfg.get("tts") or {}
    tracks: dict[str, str] = {}
    if cfg.get("narration_tracks"):
        tracks.update(cfg["narration_tracks"])
    else:
        for s in cfg["shots"]:
            if s.get("narration"):
                tracks[s.get("tts_id", s["id"])] = s["narration"]

    timings = {}
    for tid, text in tracks.items():
        wav = dirs["audio"] / f"{tid}.wav"
        if wav.exists() and not force:
            dur = ffprobe_dur(wav)
            print(f"[SKIP] {wav.name} ({dur:.2f}s)")
            timings[tid] = dur
            continue
        cmd = [
            "gemini-api", "tts", "--stdin",
            "-m", tts_cfg.get("model", "gemini-3.8-flash-tts"),
            "-v", tts_cfg.get("voice", "Kore"),
            "--language", tts_cfg.get("language", "zh-CN"),
            "--style", tts_cfg.get("style", "Warm, calm, clear Mandarin Chinese narrator."),
            "--out", str(wav), "-o", "json",
        ]
        p = subprocess.run(cmd, input=text, capture_output=True, text=True, encoding="utf-8")
        if p.returncode != 0:
            raise RuntimeError(f"TTS failed for {tid}: {p.stderr or p.stdout}")
        dur = ffprobe_dur(wav)
        print(f"[OK]   {wav.name} ({dur:.2f}s)")
        timings[tid] = dur
    (dirs["audio"] / "timings.json").write_text(json.dumps(timings, indent=2), encoding="utf-8")

    bgm_cfg = cfg.get("bgm") or {}
    if bgm_cfg.get("enabled") and bgm_cfg.get("prompt"):
        bgm_path = dirs["audio"] / bgm_cfg.get("filename", "bgm.mp3")
        if bgm_path.exists() and not force:
            print(f"[SKIP] {bgm_path.name} ({ffprobe_dur(bgm_path):.2f}s)")
        else:
            p = subprocess.run(["gemini-api", "music", bgm_cfg["prompt"], "-m", bgm_cfg.get("model", "lyria-3.5"), "--out", str(bgm_path), "-o", "json"], capture_output=True, text=True, encoding="utf-8")
            if p.returncode != 0:
                raise RuntimeError(f"BGM failed: {p.stderr or p.stdout}")
            print(f"[OK]   {bgm_path.name} ({ffprobe_dur(bgm_path):.2f}s)")


def get_shot_keyframe(shot: dict, dirs: dict) -> Path:
    if shot.get("keyframe_path"):
        return resolve_ref_path(shot["keyframe_path"], dirs)
    return dirs["keyframes"] / shot.get("keyframe_filename", f"{shot['id']}_key.jpg")


def stage_keyframes(cfg: dict, dirs: dict, target_shots: set[str] | None, force: bool):
    shots = [s for s in cfg["shots"] if not target_shots or s["id"] in target_shots]
    print(f"\n=== STAGE: keyframes ({len(shots)} shot(s)) ===")
    aspect, img_size = cfg.get("aspect_ratio", "9:16"), cfg.get("image_size", "1K")

    def run_one(shot):
        if shot.get("keyframe_path"):
            return (shot["id"], True, f"external:{resolve_ref_path(shot['keyframe_path'], dirs).name}")
        out_path = dirs["keyframes"] / shot.get("keyframe_filename", f"{shot['id']}_key.jpg")
        refs = [resolve_ref_path(r, dirs) for r in shot.get("keyframe_refs", [])]
        return gen_image_item(out_path, shot["keyframe_prompt"], refs, aspect, img_size, force)

    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(run_one, s) for s in shots]):
            name, ok, msg = f.result()
            print(f"[{'OK' if ok else 'FAIL'}] {name}: {msg}")
            if not ok:
                raise RuntimeError(f"Keyframe failed: {name}: {msg}")


# ---------- 5-Dimension CoT VLM Quality Gate (VBench-2.0 / VideoScore2) ----------

def vlm_5d_audit(model: str, image_path: Path, checklist: str, min_avg: float = 8.5, min_dim: int = 7, mode: str = "video_strip") -> dict:
    if mode == "keyframe":
        mode_note = (
            "IMPORTANT: This is a SINGLE STATIC STARTING KEYFRAME (t=0s) before video motion generation. "
            "For 'beat_alignment', evaluate ONLY whether this starting frame accurately sets up the initial "
            "pose, subject, setting, and camera framing of the first beat — do NOT penalize it for being a still image."
        )
    else:
        mode_note = (
            "This is a sequential 3-frame contact strip (early / mid / late frames) extracted from a generated video clip. "
            "Evaluate temporal continuity, motion progression across beats, physics realism, and visual stability."
        )
    prompt = (
        "You are a strict commercial film QC critic inspired by VBench-2.0 and VideoScore2. "
        f"{mode_note} "
        "Score each of the 5 dimensions from 1 to 10 (integers) with concise Chain-of-Thought rationale. "
        "Return ONLY valid JSON with exact schema:\n"
        '{"rationale": "...", "scores": {"physics_and_domain": 1-10, "subject_and_product_fidelity": 1-10, '
        '"beat_alignment": 1-10, "visual_cleanliness": 1-10, "composition_safe_zone": 1-10}, "issues": ["..."]}\n'
        f"Specification: {checklist}"
    )
    p = subprocess.run(["gemini-api", "analyze", prompt, "-m", model, "-i", str(image_path)], capture_output=True, text=True, encoding="utf-8")
    raw = (p.stdout or "").strip()
    if p.returncode != 0:
        return {"pass": False, "avg_score": 0.0, "scores": {}, "issues": [p.stderr or raw], "rationale": "CLI analyze error"}
    a, b = raw.find("{"), raw.rfind("}")
    data = None
    if a != -1 and b != -1:
        try:
            data = json.loads(raw[a:b + 1])
        except json.JSONDecodeError:
            pass
    if not data or not isinstance(data.get("scores"), dict):
        return {"pass": False, "avg_score": 0.0, "scores": {}, "issues": ["Unparseable VLM JSON"], "rationale": raw[:240]}

    scores = {k: int(data["scores"].get(k, 0)) for k in QC_DIMENSIONS}
    avg = round(sum(scores.values()) / len(QC_DIMENSIONS), 2)
    min_val = min(scores.values())
    passed = (avg >= min_avg) and (min_val >= min_dim)
    return {
        "pass": passed,
        "avg_score": avg,
        "min_dim_score": min_val,
        "scores": scores,
        "issues": data.get("issues", []),
        "rationale": data.get("rationale", ""),
    }


def stage_qc_keys(cfg: dict, dirs: dict, target_shots: set[str] | None, strict_gate: bool = True):
    shots = [s for s in cfg["shots"] if not target_shots or s["id"] in target_shots]
    model = cfg.get("vlm_qc_model", "gemini-3.5-flash-lite")
    min_avg = float((cfg.get("qc") or {}).get("min_pass_score", 8.5))
    min_dim = int((cfg.get("qc") or {}).get("min_dim_score", 7))
    print(f"\n=== GATE 1: 5D VLM Keyframe QC (model={model}, pass>=avg {min_avg} & min {min_dim}) ===")
    report, failed = {}, []
    for shot in shots:
        sid = shot["id"]
        kf = get_shot_keyframe(shot, dirs)
        res = vlm_5d_audit(model, kf, compile_qc_checklist(shot), min_avg, min_dim, mode="keyframe")
        report[sid] = res
        tag = "PASS" if res["pass"] else "VETO"
        print(f"[{tag}] {sid:14s} avg={res['avg_score']:4.2f} min={res.get('min_dim_score',0)} | {res['rationale'][:120]}")
        if not res["pass"]:
            failed.append(sid)
    (dirs["qc"] / "keyframes_qc.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if failed and strict_gate:
        print(f"[GATE 1 BLOCKED] Regenerate vetoed keyframe(s): {', '.join(failed)}")
        raise SystemExit(4)


def stage_video(cfg: dict, dirs: dict, resolution: str, target_shots: set[str] | None, force: bool, ignore_budget: bool):
    shots = [s for s in cfg["shots"] if not target_shots or s["id"] in target_shots]
    check_budget_guard(cfg, dirs, shots, resolution, force, ignore_budget)
    aspect, model = cfg.get("aspect_ratio", "9:16"), cfg.get("video_model", "gemini-omni-1.2-flash")
    print(f"\n=== STAGE: video ({len(shots)} shot(s) @ {resolution}, {aspect}) ===")

    def gen_one(shot):
        sid = shot["id"]
        out_mp4 = dirs["clips"] / f"{sid}.mp4"
        meta_json = dirs["clips"] / f"{sid}.json"
        if out_mp4.exists() and not force:
            return (sid, True, "cached")
        kf = get_shot_keyframe(shot, dirs)
        up = None
        for attempt in range(3):
            up = subprocess.run(["gemini-api", "files", "upload", str(kf), "--wait"], capture_output=True, text=True)
            if up.returncode == 0:
                break
        if not up or up.returncode != 0:
            return (sid, False, f"upload failed: {up.stderr if up else 'unknown'}")
        uri = up.stdout.strip().splitlines()[-1].strip()
        dur_s = int(shot.get("video_duration", cfg.get("default_video_duration", 5)))
        prompt = compile_video_prompt(shot, cfg)
        cmd = [
            "gemini-api", "video", "--stdin",
            "-m", model, "-i", uri,
            "--aspect-ratio", aspect,
            "--resolution", resolution,
            "--body", json.dumps({"response_format": {"duration": f"{dur_s}s"}}),
            "--poll-timeout", "10m",
            "--out", str(out_mp4), "-o", "json",
        ]
        print(f"[GEN]  {sid} ({dur_s}s @ {resolution})...")
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8")
        if p.returncode != 0:
            return (sid, False, p.stderr or p.stdout)
        info = json.loads(p.stdout)
        info["resolution"] = resolution
        info["requested_duration"] = dur_s
        info["usage"] = fetch_usage(info.get("response_id"))
        meta_json.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        return (sid, True, f"{resolution} | vtok={(info.get('usage') or {}).get('total_output_tokens', 0)}")

    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(gen_one, s) for s in shots]):
            sid, ok, msg = f.result()
            print(f"[{'DONE' if ok else 'FAIL'}] {sid}: {msg}")
            if not ok:
                raise RuntimeError(f"Video failed for {sid}: {msg}")


def stage_qc_video(cfg: dict, dirs: dict, target_shots: set[str] | None, strict_gate: bool = True):
    shots = [s for s in cfg["shots"] if not target_shots or s["id"] in target_shots]
    model = cfg.get("vlm_qc_model", "gemini-3.5-flash-lite")
    min_avg = float((cfg.get("qc") or {}).get("min_pass_score", 8.5))
    min_dim = int((cfg.get("qc") or {}).get("min_dim_score", 7))
    print(f"\n=== GATE 2: 5D VLM Video QC ({len(shots)} shot(s), pass>=avg {min_avg} & min {min_dim}) ===")
    report, failed = {}, []
    for shot in shots:
        sid = shot["id"]
        clip = dirs["clips"] / f"{sid}.mp4"
        dur = ffprobe_dur(clip)
        strips = []
        for idx, frac in enumerate((0.18, 0.50, 0.82)):
            fp = dirs["qc"] / f"{sid}_f{idx}.jpg"
            subprocess.run(["ffmpeg", "-y", "-ss", f"{dur * frac:.2f}", "-i", str(clip), "-frames:v", "1", "-vf", "scale=400:-1", str(fp)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            strips.append(fp)
        strip_jpg = dirs["qc"] / f"{sid}_strip.jpg"
        subprocess.run(["ffmpeg", "-y", "-i", str(strips[0]), "-i", str(strips[1]), "-i", str(strips[2]), "-filter_complex", "[0:v][1:v][2:v]hstack=inputs=3[v]", "-map", "[v]", str(strip_jpg)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        res = vlm_5d_audit(model, strip_jpg, compile_qc_checklist(shot), min_avg, min_dim)
        report[sid] = {"duration": round(dur, 2), **res}
        tag = "PASS" if res["pass"] else "VETO"
        print(f"[{tag}] {sid:14s} ({dur:.2f}s) avg={res['avg_score']:4.2f} min={res.get('min_dim_score',0)} | {res['rationale'][:120]}")
        if not res["pass"]:
            failed.append(sid)
    (dirs["qc"] / "video_qc.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if failed and strict_gate:
        print(f"[GATE 2 BLOCKED] Retake vetoed shot(s): {', '.join(failed)}")
        raise SystemExit(4)


# ---------- Zero-Cost Pillow Overlays & FFmpeg Assembly ----------

def draw_chapter_bar(chapters: list[str], active_idx: int, w: int, h: int, out_path: Path):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f = load_font(18 if w >= 1000 else 16, bold=True)
    pad, gap = 28, 10
    tab_w = (w - pad * 2 - gap * (len(chapters) - 1)) // len(chapters)
    tab_h = 36
    for i, lbl in enumerate(chapters):
        x0, y0 = pad + i * (tab_w + gap), 20
        if i == active_idx:
            draw.rounded_rectangle([x0, y0, x0 + tab_w, y0 + tab_h], 10, fill=(14, 165, 233, 225), outline=(255, 255, 255, 210), width=2)
            col = (255, 255, 255, 255)
        else:
            draw.rounded_rectangle([x0, y0, x0 + tab_w, y0 + tab_h], 10, fill=(15, 23, 42, 150), outline=(255, 255, 255, 70), width=1)
            col = (203, 213, 225, 220)
        bb = draw.textbbox((0, 0), lbl, font=f)
        draw.text((x0 + (tab_w - (bb[2] - bb[0])) / 2, y0 + (tab_h - (bb[3] - bb[1])) / 2 - 2), lbl, font=f, fill=col)
    img.save(out_path)


def draw_callout_card(item: dict, w: int, h: int, theme: str, out_path: Path):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    is_vert = h > w
    accent = (249, 115, 22, 240) if theme == "warm" else (56, 189, 248, 240)
    bg_fill = (255, 255, 255, 225) if theme == "warm" else (10, 18, 34, 212)
    title_col = (15, 23, 42, 255) if theme == "warm" else (255, 255, 255, 255)
    body_col = (51, 65, 85, 255) if theme == "warm" else (226, 232, 240, 250)

    if item.get("bullets"):
        f_title = load_font(24 if not is_vert else 26, bold=True)
        f_body = load_font(19 if not is_vert else 22, bold=False)
        card_w = (w - 64) if is_vert else 460
        card_h = 68 + 38 * len(item["bullets"])
        x0 = 32 if is_vert else (w - card_w - 32)
        y0 = int(item.get("y", 82))
        draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + card_h], 14, fill=bg_fill, outline=accent, width=2)
        draw.rounded_rectangle([x0 + 14, y0 + 16, x0 + 20, y0 + card_h - 16], 3, fill=accent)
        draw.text((x0 + 34, y0 + 16), item.get("title", ""), font=f_title, fill=title_col)
        yc = y0 + 58
        for b in item["bullets"]:
            draw.ellipse([x0 + 34, yc + 9, x0 + 42, yc + 17], fill=accent)
            draw.text((x0 + 52, yc), b, font=f_body, fill=body_col)
            yc += 38
    else:
        font = load_font(28 if is_vert else 24, bold=True)
        lines = item["text"].split("\n")
        bbs = [draw.textbbox((0, 0), ln, font=font) for ln in lines]
        max_tw = max(b[2] - b[0] for b in bbs)
        lh = max(b[3] - b[1] for b in bbs) + 12
        pad_x, pad_y = 30, 16
        bw, bh = max_tw + pad_x * 2, lh * len(lines) + pad_y * 2 - 8
        x0, y0 = (w - bw) / 2, int(item.get("y", 72 if is_vert else 84))
        draw.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 16, fill=bg_fill, outline=accent, width=2)
        draw.rounded_rectangle([x0 + 14, y0 + 14, x0 + 20, y0 + bh - 14], 3, fill=accent)
        yc = y0 + pad_y - 2
        for ln, b in zip(lines, bbs):
            draw.text((x0 + (bw - (b[2] - b[0])) / 2 + 6, yc), ln, font=font, fill=title_col)
            yc += lh

    for m in item.get("markers", []):
        mtype = m["type"]
        mcol = (251, 191, 36, 240) if m.get("color") == "amber" else accent
        if mtype == "hline":
            for x in range(60, w - 60, 28):
                draw.line([(x, m["y"]), (min(x + 16, w - 60), m["y"])], fill=mcol, width=3)
        elif mtype == "circle":
            cx, cy, r = m["x"], m["y"], m.get("r", 30)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=mcol, width=4)
        elif mtype == "line":
            draw.line([(m["x1"], m["y1"]), (m["x2"], m["y2"])], fill=mcol, width=4)
        if m.get("label"):
            ft = load_font(17, bold=True)
            lx, ly = m["lx"], m["ly"]
            bb = draw.textbbox((0, 0), m["label"], font=ft)
            draw.rounded_rectangle([lx - 10, ly - 5, lx + (bb[2] - bb[0]) + 10, ly + (bb[3] - bb[1]) + 8], 8, fill=(10, 18, 34, 210), outline=mcol, width=1)
            draw.text((lx, ly), m["label"], font=ft, fill=(255, 255, 255, 255))
    img.save(out_path)


def draw_subtitle(text: str, w: int, h: int, out_path: Path):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    is_vert = h > w
    font = load_font(30 if is_vert else 28, bold=True)
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad_x, pad_y = 24, 12
    x0, x1 = (w - tw) / 2 - pad_x, (w + tw) / 2 + pad_x
    y1 = h - (130 if is_vert else 28)
    y0 = y1 - th - pad_y * 2
    draw.rounded_rectangle([x0, y0, x1, y1], 12, fill=(15, 23, 42, 190))
    draw.text(((w - tw) / 2, y0 + pad_y - 4), text, font=font, fill=(255, 255, 255, 255))
    img.save(out_path)


def build_endcard(end_cfg: dict, dirs: dict, w: int, h: int, fps: int, out_path: Path):
    bg = Image.open(resolve_ref_path(end_cfg["image"], dirs)).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(bg)
    is_vert = h > w
    panel_h, margin = (300, 40) if is_vert else (190, 140)
    draw.rounded_rectangle([margin, h - panel_h - 56, w - margin, h - 56], 24, fill=(255, 255, 255, 232), outline=(249, 115, 22, 175), width=2)
    f_big = load_font(38 if is_vert else 34, bold=True)
    f_sub = load_font(24 if is_vert else 22, bold=False)
    f_pill = load_font(22 if is_vert else 20, bold=True)
    for txt, fnt, dy, col in [(end_cfg["title"], f_big, 30, (15, 23, 42, 255)), (end_cfg.get("subtitle", ""), f_sub, 92 if is_vert else 78, (71, 85, 105, 255))]:
        if txt:
            bb = draw.textbbox((0, 0), txt, font=fnt)
            draw.text(((w - (bb[2] - bb[0])) / 2, h - panel_h - 56 + dy), txt, font=fnt, fill=col)
    if end_cfg.get("badge"):
        bb = draw.textbbox((0, 0), end_cfg["badge"], font=f_pill)
        pw, ph = bb[2] - bb[0], bb[3] - bb[1]
        px0, py0 = (w - pw) / 2 - 26, h - (142 if is_vert else 118)
        draw.rounded_rectangle([px0, py0, px0 + pw + 52, py0 + ph + 22], 20, fill=(249, 115, 22, 240))
        draw.text(((w - pw) / 2, py0 + 9), end_cfg["badge"], font=f_pill, fill=(255, 255, 255, 255))
    png = dirs["overlays"] / "endcard.png"
    bg.convert("RGB").save(png, quality=95)
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", f"{float(end_cfg.get('duration', 2.5)):.3f}", "-vf", f"scale={w}:{h},fps={fps},format=yuv420p",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def stage_assemble(cfg: dict, dirs: dict, tag: str):
    w, h = canvas_size(cfg)
    fps = int(cfg.get("fps", 24))
    tts_tempo = float((cfg.get("tts") or {}).get("tempo", 1.12))
    theme = cfg.get("theme", "warm" if h > w else "tech")
    keep_ambient = float(cfg.get("keep_clip_ambient_volume", 0.0))
    show_bar = bool(cfg.get("show_chapter_bar", False))
    chapters = [s.get("chapter_short", s["id"]) for s in cfg["shots"]]

    print(f"\n=== STAGE: assemble ({w}x{h} @ {fps}fps, tag={tag}) ===")
    rendered_paths, durs = [], []
    for idx, shot in enumerate(cfg["shots"]):
        sid = shot["id"]
        clip = dirs["clips"] / f"{sid}.mp4"
        wav = dirs["audio"] / f"{shot.get('tts_id', sid)}.wav"
        raw_v, raw_a = ffprobe_dur(clip), ffprobe_dur(wav)

        ratio = shot.get("split_audio_ratio")
        a0, a1 = (raw_a * ratio[0], raw_a * ratio[1]) if ratio else (0.0, raw_a)
        eff_tts = (a1 - a0) / tts_tempo
        lead_in, tail_pad = float(shot.get("lead_in", 0.30)), float(shot.get("tail_pad", 0.45))
        target_dur = max(raw_v, eff_tts + lead_in + tail_pad)

        inputs, fc, in_idx = ["-i", str(clip), "-i", str(wav)], [], 2
        freeze_at = shot.get("freeze_at_sec")
        if freeze_at is not None:
            slow = float(shot.get("slow_factor", 2.0))
            motion_dur = raw_v * slow
            freeze_dur = max(2.8, target_dur - motion_dur)
            if motion_dur + 2.8 > target_dur:
                freeze_dur = 2.8
                motion_dur = max(raw_v, target_dur - freeze_dur)
                slow = motion_dur / raw_v
            total_dur = motion_dur + freeze_dur
            f_raw = min(float(freeze_at), raw_v - 0.5)
            f_st, f_en = f_raw * slow, f_raw * slow + freeze_dur
            fc += [
                f"[0:v]fps={fps},scale={w}:{h}:flags=lanczos,format=yuv420p,split=3[va0][vf0][vb0]",
                f"[va0]trim=0:{f_raw:.3f},setpts=(PTS-STARTPTS)*{slow:.4f}[va]",
                f"[vf0]trim={f_raw:.3f}:{f_raw + 0.08:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},trim=0:{freeze_dur:.3f},setpts=PTS-STARTPTS,eq=brightness=-0.04:contrast=1.03[vf]",
                f"[vb0]trim={f_raw:.3f}:{raw_v:.3f},setpts=(PTS-STARTPTS)*{slow:.4f}[vb]",
                f"[va][vf][vb]concat=n=3:v=1:a=0,fps={fps},format=rgba[vbase]",
            ]
        else:
            slow = min(float(shot.get("max_slow_factor", 1.95)), target_dur / raw_v)
            hold_pad = max(0.0, target_dur - raw_v * slow)
            total_dur, f_st, f_en = target_dur, 0.0, target_dur
            fc.append(
                f"[0:v]scale={w}:{h}:flags=lanczos,fps={fps},setpts=(PTS-STARTPTS)*{slow:.4f}"
                + (f",tpad=stop_mode=clone:stop_duration={hold_pad:.3f}" if hold_pad > 0.01 else "")
                + f",trim=0:{total_dur:.3f},setpts=PTS-STARTPTS,format=rgba[vbase]"
            )

        prev = "[vbase]"
        if show_bar:
            bp = dirs["overlays"] / f"{sid}_bar.png"
            draw_chapter_bar(chapters, idx, w, h, bp)
            inputs += ["-i", str(bp)]
            fc.append(f"{prev}[{in_idx}:v]overlay=0:0:format=auto[vbar]")
            prev, in_idx = "[vbar]", in_idx + 1

        for c_i, c_item in enumerate(shot.get("callouts", [])):
            cp = dirs["overlays"] / f"{sid}_call_{c_i}.png"
            draw_callout_card(c_item, w, h, theme, cp)
            inputs += ["-i", str(cp)]
            if c_item.get("during_freeze") and freeze_at is not None:
                t0, t1 = f_st, f_en
            else:
                r0, r1 = c_item.get("window", [0.15, 0.92])
                t0, t1 = total_dur * r0, total_dur * r1
            nxt = f"[vc{in_idx}]"
            fc.append(f"{prev}[{in_idx}:v]overlay=0:0:enable='between(t,{t0:.3f},{t1:.3f})':format=auto{nxt}")
            prev, in_idx = nxt, in_idx + 1

        subs = shot.get("subtitles", [])
        if subs:
            tot_ch, t_cur = sum(len(x) for x in subs), lead_in
            for s_i, stxt in enumerate(subs):
                sp = dirs["overlays"] / f"{sid}_sub_{s_i}.png"
                draw_subtitle(stxt, w, h, sp)
                inputs += ["-i", str(sp)]
                dt = eff_tts * (len(stxt) / tot_ch)
                nxt = f"[vs{in_idx}]"
                fc.append(f"{prev}[{in_idx}:v]overlay=0:0:enable='between(t,{t_cur:.3f},{t_cur + dt:.3f})':format=auto{nxt}")
                prev, in_idx, t_cur = nxt, in_idx + 1, t_cur + dt

        fc.append(f"{prev}trim=0:{total_dur:.3f},setpts=PTS-STARTPTS,format=yuv420p[vout]")
        lead_ms = int(lead_in * 1000)
        vox = (
            f"[1:a]atrim=start={a0:.3f}:end={a1:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
            f"aformat=sample_fmts=fltp:channel_layouts=stereo,atempo={tts_tempo:.3f},loudnorm=I=-16:TP=-1.5:LRA=11,"
            f"adelay={lead_ms}|{lead_ms},apad=whole_dur={total_dur:.3f},atrim=0:{total_dur:.3f},asetpts=PTS-STARTPTS[vox]"
        )
        if keep_ambient > 0.0:
            fc += [
                f"[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,aloop=loop=4:size=240000,atrim=0:{total_dur:.3f},asetpts=PTS-STARTPTS,volume={keep_ambient:.2f}[amb]",
                vox,
                "[amb][vox]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]",
            ]
        else:
            fc.append(vox.replace("[vox]", "[aout]"))

        rp = dirs["rendered"] / f"{sid}.mp4"
        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(rp)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"FFmpeg render failed for {sid}:\n{p.stderr[-2000:]}")
        d_act = ffprobe_dur(rp)
        print(f"[RENDER] {sid:14s}: raw={raw_v:.2f}s -> {d_act:.2f}s")
        rendered_paths.append(rp)
        durs.append(d_act)

    if (cfg.get("endcard") or {}).get("enabled"):
        ec = dirs["rendered"] / "endcard.mp4"
        build_endcard(cfg["endcard"], dirs, w, h, fps, ec)
        rendered_paths.append(ec)
        durs.append(ffprobe_dur(ec))

    F = float(cfg.get("crossfade_sec", 0.35))
    inputs = [arg for rp in rendered_paths for arg in ("-i", str(rp))]
    bgm_cfg = cfg.get("bgm") or {}
    bgm_file = dirs["audio"] / bgm_cfg.get("filename", "bgm.mp3")
    use_bgm = bool(bgm_cfg.get("enabled")) and bgm_file.exists()
    if use_bgm:
        bgm_idx = len(rendered_paths)
        inputs += ["-stream_loop", "-1", "-i", str(bgm_file)]

    fc = []
    for i, d in enumerate(durs):
        fc.append(f"[{i}:v]fps={fps},format=yuv420p,settb=AVTB,trim=0:{d:.3f},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:{d:.3f},asetpts=PTS-STARTPTS[a{i}]")

    cv, ca, acc = "[v0]", "[a0]", durs[0]
    for i in range(1, len(durs)):
        off = acc - F
        nv, na = f"[vx{i}]", f"[ax{i}]"
        fc.append(f"{cv}[v{i}]xfade=transition=fade:duration={F}:offset={off:.3f}{nv}")
        fc.append(f"{ca}[a{i}]acrossfade=d={F}:c1=tri:c2=tri{na}")
        cv, ca, acc = nv, na, off + durs[i]

    fo = max(0.0, acc - 0.85)
    fc.append(f"{cv}fade=t=in:st=0:d=0.35,fade=t=out:st={fo:.3f}:d=0.85[vfinal]")
    if use_bgm:
        vol = float(bgm_cfg.get("volume", 0.14))
        fc.append(f"[{bgm_idx}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:{acc:.3f},asetpts=PTS-STARTPTS,volume={vol:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={max(0.0, acc - 1.5):.3f}:d=1.5[bgm]")
        fc.append(f"{ca}[bgm]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[afinal]")
    else:
        fc.append(f"{ca}afade=t=in:st=0:d=0.25,afade=t=out:st={fo:.3f}:d=0.85[afinal]")

    final_mp4 = dirs["out"] / f"{cfg['project']}_{tag}.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vfinal]", "-map", "[afinal]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final_mp4)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Final merge failed:\n{p.stderr[-2000:]}")
    print(f"[FINAL] {final_mp4} | duration={ffprobe_dur(final_mp4):.2f}s | size={final_mp4.stat().st_size / 1048576:.2f} MB")


def stage_cost(cfg: dict, dirs: dict):
    print(f"\n=== COST REPORT: {cfg['project']} (budget cap=${cfg.get('max_budget_usd', 0):.2f}) ===")
    vid_c, img_c, tts_c, rows = compute_current_cost(cfg, dirs)
    for r in rows:
        print(r)
    print(f"Video subtotal : ${vid_c:.4f}")
    print(f"Images         : ${img_c:.4f}")
    print(f"TTS            : ${tts_c:.4f}")
    print(f"Local FFmpeg   : $0.0000")
    print(f"TOTAL SPENT    : ${vid_c + img_c + tts_c:.4f}")


def main():
    ap = argparse.ArgumentParser(description="AI Video Director — Quality-gated low-cost AI video production engine")
    ap.add_argument("--config", required=True, help="Path to strict project JSON storyboard")
    ap.add_argument("--stage", choices=["validate", "assets", "audio", "keyframes", "qc_keys", "video", "qc_video", "assemble", "upgrade_hero", "cost", "all"], default="all")
    ap.add_argument("--res", choices=["360p", "720p", "1080p"], default="360p", help="Video resolution (default 360p draft; upgrade_hero defaults to 720p)")
    ap.add_argument("--shots", default="", help="Comma-separated shot IDs to target")
    ap.add_argument("--tag", default="final", help="Output filename tag")
    ap.add_argument("--force", action="store_true", help="Overwrite cached files for targeted stage/shots")
    ap.add_argument("--ignore-budget", action="store_true", help="Override max_budget_usd circuit breaker")
    ap.add_argument("--no-strict-qc", action="store_true", help="Log QC failures without halting")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = load_cfg(cfg_path)
    dirs = resolve_dirs(cfg, cfg_path)
    target = {x.strip() for x in args.shots.split(",") if x.strip()} if args.shots else None
    strict_qc = not args.no_strict_qc

    if args.stage != "cost":
        stage_validate(cfg)
    if args.stage == "validate":
        return

    if args.stage == "upgrade_hero":
        hero_ids = {s["id"] for s in cfg["shots"] if s.get("tier") == "hero"}
        if not hero_ids:
            print("No shots marked tier='hero' in config.")
            return
        up_res = "720p" if args.res == "360p" else args.res
        stage_video(cfg, dirs, up_res, hero_ids, force=True, ignore_budget=args.ignore_budget)
        stage_qc_video(cfg, dirs, hero_ids, strict_gate=strict_qc)
        stage_assemble(cfg, dirs, args.tag)
        stage_cost(cfg, dirs)
        return

    order = ["audio", "assets", "keyframes", "qc_keys", "video", "qc_video", "assemble", "cost"]
    stages = order if args.stage == "all" else [args.stage]
    for st in stages:
        if st == "assets":
            stage_assets(cfg, dirs, args.force)
        elif st == "audio":
            stage_audio(cfg, dirs, args.force)
        elif st == "keyframes":
            stage_keyframes(cfg, dirs, target, args.force)
        elif st == "qc_keys":
            stage_qc_keys(cfg, dirs, target, strict_gate=strict_qc)
        elif st == "video":
            stage_video(cfg, dirs, args.res, target, args.force, args.ignore_budget)
        elif st == "qc_video":
            stage_qc_video(cfg, dirs, target, strict_gate=strict_qc)
        elif st == "assemble":
            stage_assemble(cfg, dirs, args.tag)
        elif st == "cost":
            stage_cost(cfg, dirs)


if __name__ == "__main__":
    main()

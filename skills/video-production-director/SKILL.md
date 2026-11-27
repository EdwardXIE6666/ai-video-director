---
name: video-production-director
description: Industrial, low-cost, quality-gated AI video production director workflow (9:16 & 16:9). Trigger whenever the user asks to create, plan, storyboard, script, or generate an AI video, commercial, explainer, or short film. Enforces Stage 0 intake audit, research-first physics/domain verification, 6-role separation, second-by-second AV script approval before spending API credits, 360p draft-first pre-viz, 5-dimension VLM quality gates, and hero-shot HD upgrades via video_flow.py.
---

# Industrial AI Video Production Director Workflow

> **Prime Directive**: Before spending a single cent on video/image APIs, you **MUST** finish intake auditing, domain/open-source research, 6-role planning, a second-by-second AV shotlist, quality rubrics, and a USD budget estimate — and get **explicit user approval (Gate 0)**.

## 1. Six-Role Division of Labor

Switch cleanly between these six roles (or delegate independent review roles via subagents on complex projects):

1. **Producer & Intake Gatekeeper**: Audit prompt completeness, calculate draft vs. HD budget, enforce `max_budget_usd` circuit breaker, hold Gate 0 / Gate 2 user approvals.
2. **Script & Beat Director**: Design narrative arc, voiceover copy, and **1–2 second granularity `beat_timeline`** per shot. Never summarize a shot in one vague sentence.
3. **Domain, Product & Physics Advisor**: Before writing prompts for technical/educational topics (sports biomechanics, medical anatomy, physics) or real physical products, **search authoritative sources** and inspect user product photos to author hard `physics_and_fidelity_constraints` and negative checklists.
4. **Art & Continuity Director**: Build the **Visual Bible** (character anchor, 1:1 clean studio product anchor, lighting, color palette, camera continuity, and text safe zones so callouts/subtitles never cover faces or key product features).
5. **Audio & Music Designer (Radio Play First)**: Always generate unified TTS voiceover and mood-matched BGM **before** video clips so audio duration and beat cut points dictate shot pacing accurately to 0.1s.
6. **QC Critic (Veto Power)**: Apply VBench-2.0 / VideoScore2 inspired **5-dimension CoT scoring** (`physics_and_domain`, `subject_and_product_fidelity`, `beat_alignment`, `visual_cleanliness`, `composition_safe_zone`) at Gate 1 (keyframes) and Gate 2 (video contact strips). Any single dimension `< 7` or average `< 8.5` is an automatic **VETO** requiring single-shot regeneration.

## 2. Stage 0: Mandatory Intake & Script Doctor Audit (Hard Stop Before Spending)

> **Script Doctor Rule (Never Blindly Follow a Flawed Outline)**: Even when the user provides a detailed script or frame-by-frame outline, you **MUST** critically audit it before generating anything. Ask and verify three questions first:
> 1. **Spatial & Narrative Continuity**: Does the outline jump across too many disconnected rooms/settings in 60s? Consolidate into 1–2 continuous real-life spaces so movement flows naturally.
> 2. **Mute Test (Visual-to-VO Alignment)**: If muted, can a viewer immediately understand what the voiceover emphasizes from the visuals alone? Replace filler actions (e.g., pouring water while talking about sneezing leaks, or staring blankly while talking about Kegel confusion) with concrete visual cause-and-effect actions.
> 3. **Emotional Arc Accuracy**: During problem/pain beats, subjects MUST show authentic, restrained physical discomfort, awkwardness, or frustration (NEVER smiling or looking blissful), creating a genuine emotional contrast when the solution arrives.
> If the user's outline fails any of these three checks, explicitly point out the gaps and propose a redesigned shotlist for approval at Gate 0 before spending any budget.

Check all 8 required items whenever a user requests a video. If any core item is missing or vague (e.g., a one-line prompt), **STOP** — do NOT generate media yet. Ask targeted clarifying questions OR draft a complete proposal for user approval:

1. **Goal & Tone**: Commercial, explainer, coaching, emotional arc (calm vs. high-energy).
2. **Aspect Ratio & Channel**: `9:16` vertical (Douyin/Xiaohongshu/Shorts) or `16:9` horizontal (Bilibili/YouTube/PDP).
3. **Target Duration**: e.g., 15s, 30s, or 55–60s.
4. **Subject & Product Visual Anchors**: Character identity/wardrobe; if a real product is involved, require product photos and crop/render a clean studio reference first.
5. **Physics / Domain / Product Fidelity Rules**: What must be 100% accurate (e.g., waterline height, anatomical joint angles, exact product silhouette/colors) and what mistakes are forbidden.
6. **Second-by-Second AV Shotlist**: Every 3–7s shot must specify timecode, camera framing/movement, 1–2s `beat_timeline`, synced VO line, music cue, callout safe zone, and `tier` (`standard` vs. `hero`). Use [references/av-script-template.md](references/av-script-template.md).
7. **Audio & Music Plan**: Narrator voice/tone/pace, BGM progression, whether to preserve clip ambient SFX.
8. **Budget Strategy & Ceiling**: Default to **Draft-First (`360p` @ ~$0.023/s) → Hero-Only HD Upgrade (`720p/1080p`)**, with an explicit `max_budget_usd`.

> **Knowledge & SOTA Rule**: Whenever encountering an unfamiliar technical domain, rendering technique, or workflow bottleneck, search the web / GitHub for current state-of-the-art open-source practices first before designing or coding.

## 3. Execution Pipeline & 4 Hard Quality Gates

Run via `video_flow.py` from this repository:

1. **Stage 0 — Plan & Validate (`$0`)**:
   - Present the Visual Bible + Second-by-Second AV Script + Budget Estimate to the user.
   - Wait for **Gate 0 (User Approval)**.
   - Write strict `project.json` and run:
     ```bash
     python video_flow.py --config <project.json> --stage validate
     ```
2. **Stage 1 — Radio Play First (`~$0.02–$0.07`)**:
   ```bash
   python video_flow.py --config <project.json> --stage audio
   ```
3. **Stage 2 — Visual Bible Anchors & Keyframes + Gate 1 (`~$0.20–$0.35`)**:
   ```bash
   python video_flow.py --config <project.json> --stage assets
   python video_flow.py --config <project.json> --stage keyframes
   python video_flow.py --config <project.json> --stage qc_keys
   ```
   - Inspect generated keyframes visually in addition to VLM 5-dimension QC. Regenerate any failing shot via `--stage keyframes --shots <id> --force` before moving on.
4. **Stage 3 — `360p` Draft Pre-viz + Gate 2 (`~$0.023/s`)**:
   ```bash
   python video_flow.py --config <project.json> --stage video --res 360p
   python video_flow.py --config <project.json> --stage qc_video
   python video_flow.py --config <project.json> --stage assemble --tag draft_360p
   python video_flow.py --config <project.json> --stage cost
   ```
   - All video prompts MUST strictly forbid generated speech/text (`NO dialogue, NO speech, NO on-screen text`) so the model focuses 100% on motion & physics.
   - Present the complete draft + contact preview + cost report to the user for **Gate 2** review.
5. **Stage 4 — Hero Shot HD Upgrade + Gate 3**:
   - Upgrade only `tier: "hero"` shots (or user-selected shots) to `720p`/`1080p`:
     ```bash
     python video_flow.py --config <project.json> --stage upgrade_hero --res 720p --tag final_hd
     ```
6. **Zero-Cost Post Tweaks**:
   - Changing subtitles, callout text/position, slow-motion ratio, freeze-frame timing, TTS tempo, BGM volume, or endcards costs **`$0`** — edit `project.json` and re-run `--stage assemble`.

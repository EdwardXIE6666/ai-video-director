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

## 2. Stage 0: Discovery Interview, Script Doctor & Planning Gate (Hard Stop Before Spending)

> **Stage 0.1 · Mandatory Discovery Interview (摸清需求再开工 — Never Guess Silently)**:
> Treat Stage 0 like a structured planning interview. Whenever the user's request is brief, incomplete, or exploratory (e.g. *"帮我做条产品视频"* / *"Make a video about X"*), **STOP immediately** — do NOT invent specs, jump straight into scripting, or spend a cent.
> 1. **Ask in 1–2 Focused Rounds** (prefer the `ask_question` multiple-choice UI with a smart `(Recommended)` option first so users who don't know can click in seconds; never drag into 10 tedious turns):
>    - **Goal & Audience**: Product commercial / 3D explainer / tutorial / brand story / short drama — who is watching and what core message or real pain point matters?
>    - **Aspect Ratio & Duration**: `9:16 vertical 45–60s (Recommended for Douyin/Xiaohongshu/Shorts)` / `9:16 fast 15–30s` / `16:9 horizontal 60–90s (Bilibili/YouTube/PDP)`.
>    - **Visual Direction & Budget Tier**: `Cost-first hybrid ($0.8–$1.5: Veo Lite + Ken Burns + Remotion 1080p) (Recommended)` / `Pure-code $0 art & 3D teardown (lemo-opuscar)` / `Commercial Pro ($3–$5: Veo Fast + Remotion 1080p)`.
>    - **Voiceover Engine**: `Edge TTS ($0 free)` / `ElevenLabs (top commercial tone)` / `Gemini TTS` / `User-provided recording`.
> 2. **Probe Real Facts & Visual Anchors**: If a real physical product is involved and the user hasn't supplied photos or real specs, explicitly ask for **2–3 multi-angle product photos + 2–3 real selling points/constraints** (never fabricate fake product specs or fake personal reviews).
> 3. **When the User Says "I Don't Know / You Decide"**: Do NOT stall — proactively propose **2 concrete creative directions (Option A vs. Option B)** with clear trade-offs and cost estimates so the user can simply pick A or B.
> 4. **Lock Requirements → Draft Gate 0 Plan**: Only AFTER the discovery answers are confirmed, run Domain Research → Script Doctor → Engine Routing → Prompt Crafting → present the complete Gate 0 AV Script & Budget Plan for final sign-off.

> **Script Doctor & De-AI Copywriting Rule (Never Blindly Follow a Flawed Outline)**: Even when the user provides a detailed script or frame-by-frame outline, you **MUST** critically audit it using [references/script-and-copy-playbook.md](references/script-and-copy-playbook.md) before generating anything. Verify four gates first:
> 1. **Spatial & Narrative Continuity**: Does the outline jump across too many disconnected rooms/settings in 60s? Consolidate into 1–2 continuous real-life spaces so movement flows naturally (and lock cross-episode state in `series_bible.json` for multi-episode series).
> 2. **Mute Test & Show-Don't-Tell**: If muted, can a viewer immediately understand what the voiceover emphasizes from concrete actions and objects alone? Anchor emotion on filmable gestures/props instead of internal monologue or filler actions.
> 3. **0–3s Hook & Authentic Emotional Arc**: Shot 1 must hook within 3 seconds; during problem/pain beats, subjects MUST show authentic, restrained physical discomfort, awkwardness, or frustration (NEVER smiling or looking blissful).
> 4. **De-AI Living Voiceover Copy**: Strip all AI clichés (`不是A，而是B` flip-premise tropes, `赋能/抓手/闭环`, `在当今…时代`, `让我们…吧`, neat 3-part parallelisms, explaining emotions already shown on screen). Keep spoken lines breath-length (~3.5–4 Mandarin chars/s) and protect strong hooks during edits.
> If the user's outline fails any check, explicitly point out the gaps and propose a redesigned shotlist for approval at Gate 0 before spending any budget.

Check all 8 required items whenever a user requests a video. If any core item is missing or vague (e.g., a one-line prompt), **STOP** — do NOT generate media yet. Ask targeted clarifying questions OR draft a complete proposal for user approval:

1. **Goal & Tone**: Commercial, explainer, coaching, emotional arc (calm vs. high-energy).
2. **Aspect Ratio & Channel**: `9:16` vertical (Douyin/Xiaohongshu/Shorts) or `16:9` horizontal (Bilibili/YouTube/PDP).
3. **Target Duration**: e.g., 15s, 30s, or 55–60s.
4. **Subject & Product Visual Anchors**: Character identity/wardrobe; if a real product is involved, require product photos and crop/render a clean studio reference first.
5. **Physics / Domain / Product Fidelity Rules**: What must be 100% accurate (e.g., waterline height, anatomical joint angles, exact product silhouette/colors) and what mistakes are forbidden.
6. **Second-by-Second AV Shotlist**: Every 3–7s shot must specify timecode, camera framing/movement, 1–2s `beat_timeline`, synced VO line, music cue, callout safe zone, and `tier` (`standard` vs. `hero`). Use [references/av-script-template.md](references/av-script-template.md).
7. **Audio & Music Plan (Multi-TTS Choice Menu)**: Always let the user pick their preferred voiceover provider in Stage 0 before running `--stage audio`:
   - `edge` (**Microsoft Edge TTS**, `$0` free, zero API key, natural Chinese/English neural voices like `zh-CN-XiaoxiaoNeural` / `zh-CN-YunxiNeural`)
   - `elevenlabs` (**ElevenLabs** `eleven_multilingual_v2` / voice cloning, top commercial emotion & breathiness, uses `ELEVENLABS_API_KEY`)
   - `gemini` (**Gemini TTS**, `~$0.0002/s`, natural language `--style` emotion direction)
   - `openai` (**OpenAI TTS** `gpt-4o-mini-tts`, strong English/bilingual control, uses `OPENAI_API_KEY`)
   - `local` (**User-supplied audio**: drop recordings or exports from MiniMax / Doubao / Fish Audio / CosyVoice / human voice actors into `audio/<shot_id>.wav|.mp3`)
   Also confirm BGM progression and whether to preserve clip ambient SFX.
8. **Budget Strategy & Ceiling**: Default to **Cost-First Production** with an explicit `max_budget_usd`:
   - On AI Studio: **Draft-First (`360p` @ ~$0.023/s) → Hero-Only HD Upgrade (`720p/1080p`)**.
   - On Vertex AI (`--backend vertex`): default to **`veo-3.1-lite-generate-001` ($0.05/s @ 720p)** with **4s clips + local FFmpeg tempo stretch**; reserve `veo-3.1-fast-generate-001` ($0.10/s) only for complex human interaction hero shots via per-shot `"vertex_video_model"`.
   - For static product hero shots, title cards, or calm outros, use `"motion": "static_ken_burns"` (or `"static_zoom_out"`) for **`$0` local FFmpeg HD smooth push-in/pull-out** from a crisp keyframe.

> **Knowledge & SOTA Rule**: Whenever encountering an unfamiliar technical domain, rendering technique, or workflow bottleneck, search the web / GitHub for current state-of-the-art open-source practices first before designing or coding.

> **Stage 0 Engine Routing Rule (Decide *Which Tool Makes Each Shot* Before Prompting)**:
> Never default blindly to paid AI video generation for every shot. Before writing prompts or quoting budget, classify the project — and **every individual shot** — using this decision matrix so paid tokens are ONLY spent where generative video is genuinely irreplaceable:
>
> | Shot / Film Type | Assigned Engine | Est. Cost | Why This Engine Wins |
> | :--- | :--- | :--- | :--- |
> | **3D product teardown, technical/data/map explainer, stylized art film (watercolor/oil/neon/ukiyo-e), motion concept** | **`lemo-opuscar`** (99 pure-code styles via Three.js / Canvas / Playwright) | **\$0** | Exact geometry, zero AI text/mesh hallucinations, 99 curated film styles |
> | **Static product macro hero, studio showcase, clean title/ending hold** | **`static_ken_burns`** (crisp keyframe + local FFmpeg 2× supersampled pan/zoom) | **~\$0.036** (image only) | 1:1 locked product texture, zero morphing, saves 90%+ |
> | **Simple live-action lifestyle, gentle ambient motion, calm transitions** | **`veo-lite`** (`veo-3.1-lite-generate-001`, 4s @ 720p + local tempo) | **\$0.20/shot** | Natural photorealism at half the cost of Fast |
> | **Complex human acting, nuanced micro-expressions, tricky human-product physics** | **`veo-fast`** (`veo-3.1-fast-generate-001`, 4–6s @ 720p) or AI Studio `360p→720p` | **\$0.40–\$0.60/shot** | Highest physics & facial adherence where live-action realism matters most |
> | **Final packaging: spring callouts, `ChecklistPop`, `LiquidGlass`, live HUD charts, kinetic captions, SFX, endcards** | **`remotion-best-practices` + `video-effects`** (1080p local render) | **\$0** | Vector-sharp typography, physics-driven motion graphics & sound design |
>
> **Hybrid Assembly Rule**: A single commercial SHOULD mix engines freely (e.g., Veo for human shots + `lemo-opuscar` for 3D teardown/explainer + `static_ken_burns` for macro product + Remotion for 1080p packaging) to hit agency quality under **\$1.00–\$1.40 total**.

> **Stage 0 Prompt Crafting Rule (Mandatory Before Gate 0)**: Never pass raw user prose or vague buzzwords (`cinematic`, `stunning`, `4K`, `masterpiece`) into `project.json`. Read and apply [references/prompt-crafting-playbook.md](references/prompt-crafting-playbook.md) to engineer every shot using:
> 1. **5-Layer Cinematography Formula**: `[Shot Type & Aesthetic] + [Subject, Materials & ≥2 Real-World Imperfections] + [Camera/Lens/Light Direction] + [Single-Take & Breath-Like Camera Float] + [Second-by-Second Beats + Restrained Ending]`.
> 2. **Strict Keyframe vs. I2V Split**: `keyframe_prompt` locks static `t=0s` identity/lighting/product fidelity; `beat_timeline` / `video_prompt` specifies **delta motion & physics only** (never re-describing static pixels).
> 3. **Positive-Noun Negative Prompt**: Populate Veo `negative_prompt` with comma-separated defect nouns (no `"no/don't"` prefixes) to block plastic skin, garbled text, holograms, and hard cuts.

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

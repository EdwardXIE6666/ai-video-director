# Stage 0 Script, Voiceover & De-AI Copywriting Playbook

> Distilled from empirically blind-tested open-source champions (`KKKKhazix/human-writing` ★4.7k & `zenstory-ai/drama-skills` ★4.7k, MIT).
>
> **Usage in Stage 0**: Apply this playbook when drafting or auditing **voiceover copy (口播旁白)**, **commercial hooks**, or **short-drama dialogue (短剧对白)** BEFORE generating audio (Stage 1) or keyframes (Stage 2).

---

## 1. De-AI Voiceover & Copywriting Gate (活人感去 AI 味铁律)

AI-generated Chinese/English scripts sound "smooth" yet instantly synthetic. Strip every single AI tell below before locking narration:

### A. Hard Bans (Zero Tolerance in Voiceover & Subtitles)
1. **No "Flip-the-Premise" Clichés (严禁翻案腔)**:
   - Banned patterns: `不是A，而是B` / `不在于A，而在于B` / `你以为A，其实B` / `表面上A，实际上B` / `与其说A，不如说B` / `A不重要，重要的是B`.
   - *Fix*: State your actual point directly upfront, and place concrete evidence right beside it.
2. **No Empty Openings, Grand Endings, or Buzzwords**:
   - Banned openings/closings: `在当今……时代`、`让我们一起……吧`、升华到时代/文明/所有人。
   - Banned AI filler & jargon: `说白了`、`值得注意的是`、`先说结论`、`赋能`、`抓手`、`闭环`、`底层逻辑`、`沉浸式体验`、`焕新升级`.
   - No neat 3-item symmetrical parallelisms (`三项以上整齐排比`) and no giving abstract nouns physical verbs (`焦虑显出形状`, `时间保管细节`).
   - Avoid em-dashes (`——`) in spoken scripts; colons (`:`) only for introducing literal speech.
3. **Never Explain What the Camera Already Showed**:
   - If the action or object already conveys the emotion, **STOP talking**. Never append a redundant sentence explaining *"she felt deeply relieved and understood her body better."*

### B. Write for the Ear (口播听觉法则)
1. **Backbone First**: Put *who did what* first, then add time/reason/condition. Rewrite any sentence stacking 3+ `的` (`进行了优化` → `改顺了`; `实现了提升` → `直接省了一半`).
2. **Breath-Length Sentences & Rhythm Contrast**: If a line cannot be spoken comfortably in one breath, split it. Alternate short punchy lines (6–12 chars) with slightly fuller lines (18–26 chars) for natural cadence.
3. **Read-Aloud Pace Estimation (Pre-TTS Timing Check)**:
   - Fast commercial/short-drama Mandarin VO: **~4 Chinese characters / second** (calm warm narration: **~3.5 chars / sec**).
   - English VO: **~2.5–3 words / second**.
   - Check every shot's narration character count against its planned shot duration BEFORE Stage 1 TTS so pacing never feels rushed or bloated.
4. **Honesty Beats Hype (商业稿可信度)**: Stating a clear real-world boundary or use-case limit builds 3× more viewer trust than piling exaggerated praise. Never fabricate fake personal anecdotes for official specs.

---

## 2. Show-Don't-Tell Screenwriting Rules (能演的不说)

Distilled from blind A/B winners (`zenstory-ai/drama-skills`, `jtydhr88/screenwriting-skills`):

1. **Anchor Emotion on Concrete Objects & Physical Actions (情绪落物件与动作)**:
   - Write ONLY what a camera can see or a microphone can hear: gestures, pauses, choices, and props.
   - *Bad (AI internal monologue)*: *"She felt overwhelmed and tired of guessing."*
   - *Good (filmable object + action)*: *"She pauses with her hand flat on her lower abdomen, glances down at the looping workout video on her propped phone, knits her brow, and drops her hand onto her knee with a quiet exhale."*
2. **First-Beat Hook Rule (0–3s 抓人第一拍)**:
   - Shot 1 standing completely alone must hook attention within 3 seconds via an unmistakable physical pain-point moment, visual anomaly, sharp contrast, or immediate conflict — NEVER start with slow generic establishing fluff.
3. **Short Dialogue & Distinct Voices (短台词 + 人物口气 + 潜台词)**:
   - In multi-character dramas/skits, give each character a clear goal for the scene and distinct speech rhythm. Dialogue serves immediate intent — never make characters recite backstory or product manuals to each other.
4. **Earned Turns & Props Continuity (有迹可循的反转与物件连戏)**:
   - Key turns must rely on visible evidence, physical demonstrations, or planted props — never random off-screen miracles.
   - Every recurring prop (chair, mug, cushion, phone) must hold consistent physical purpose and placement across shots (no conjuring a prop solely for forced bookending).

---

## 3. Chain-of-Truth Review & Surgical Patching (顺链条对账 + 亮点保护)

When auditing or revising a script/storyboard (Stage 0 or Gate 2):

1. **Audit Down the Chain**: Verify alignment step-by-step:
   `Script Facts & VO` → `Visual Bible & Props` → `Shot Start/End State` → `Keyframe Prompt` → `Video Motion Prompt` → `Next-Shot Match Cut`.
2. **Surgical Patches Only (不因局部毛病推倒重写)**: Fix only the specific broken beat or line; never wipe out approved shots or flatten the user's natural tone.
3. **Hook & Punchline Protection (亮点保护)**: When tightening script length to hit 30s/60s, trim repetitive filler and over-explanation FIRST — explicitly preserve strong opening hooks, crisp punchlines, and emotional peak beats.

---

## 4. Multi-Episode / Series Continuity Lock (系列片与短剧连戏档案)

For multi-video brand series or multi-episode vertical dramas, maintain a lightweight shared `series_bible.json` (or `SERIES_BIBLE.md`) in the project root locking:
- **Immutable Asset Anchors**: Lead character ref, wardrobe variants, primary room/lighting refs, 1:1 product/key-prop refs.
- **Knowledge & State Ledger**: What happened in prior episodes, current prop ownership/condition, and open hooks to pay off next.
- **Voice & Music Identity**: Locked TTS provider + `voice_id` + BGM motif so all episodes sound like one cohesive channel.

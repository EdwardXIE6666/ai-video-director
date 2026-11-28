# Production Proposal & Second-by-Second AV Script Template (Gate 0)

Present this complete structure and obtain explicit user approval before invoking any paid media APIs.

## 1. Project Overview & Budget Ceiling
- **Topic & Positioning**:
- **Aspect Ratio & Resolution Strategy**: `9:16` or `16:9` | Draft at `360p` (~$0.023/s) → Upgrade `hero` shots to `720p/1080p`
- **Target Duration**: `XX` seconds
- **Budget Ceiling (`max_budget_usd`)**: Draft est. `$X.XX` | Hero upgrade est. `$X.XX`

## 2. Visual Bible & Immutable Constraints
- **Lead Subject**: Age, appearance, hairstyle, makeup, wardrobe, demeanor
- **Product / Key Prop Anchor**: Reference image(s), immutable features (silhouette, colors, textures, proportions)
- **Setting & Lighting**: Primary environment, color temperature, natural vs. studio lighting
- **Physics / Domain Hard Constraints & Negative Checklist**:
  - Must be accurate:
  - Strictly forbidden (always include: NO AI-generated text, subtitles, or watermarks):

## 3. Audio & Music Plan (Radio Play First)
- **Voiceover**: Model, voice ID, delivery style, target tempo
- **Music Progression**: Emotional arc across `0–20s` / `20–40s` / `40–60s`
- **Ambient SFX**: Whether to preserve original clip ambience and ducking volume

## 4. Second-by-Second AV Shotlist & Engine Routing (No Vague One-Liners)

| Shot ID | Engine (`lemo-opuscar` / `ken-burns` / `veo-lite` / `veo-fast`) | Tier | Timecode | Framing & Movement | Second-by-Second Beats (1–2s) | Physics / Fidelity Rules | Synced VO & Subtitles | Remotion FX / Safe Zone | Music / SFX Cue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `shot1` | `veo-lite` | `standard` | `00:00–00:06` | MS → slow push-in | `[0-2s] ...`<br>`[2-4s] ...`<br>`[4-6s] ...` | Rule 1; Rule 2 | VO: "..."<br>Sub: 1 / 2 | Top `y=108`: glass pill | Soft piano enters |
| `shot2` | `lemo-opuscar` (\$0) | `hero` | `00:06–00:13` | 3D Exploded / Medical | `[0-3.5s] ...`<br>`[3.5-7s] ...` | Exact geometry, zero text | VO: "..." | Top `y=104`: live status bar | Subtle `click` SFX |
| `shot3` | `ken-burns` (\$0) | `hero` | `00:13–00:17` | Macro 100mm push-in | `[0-4s] Smooth 1.0→1.08 push-in` | 1:1 product fidelity | VO: "..." | `LiquidGlass` lens + badge | Soft `whoosh` SFX |

## 5. Quality Gate Criteria
- **Gate 1 (Keyframes) & Gate 2 (Video Strips)**: 5-dimension VLM CoT score average `>= 8.5` with no single dimension `< 7`, plus human visual verification.

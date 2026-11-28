# Stage 0 Prompt Crafting Playbook (Distilled from Open-Source SOTA Libraries)

> Synthesized from:
> - **Google Cloud Vertex AI Official Veo 3.1 Prompting Guide** (5-layer cinematography syntax, I2V motion focus, native negative prompts)
> - **`jnMetaCode/ai-shortfilm-prompts`** (5-stage skeleton, realism-via-imperfection, camera+lens lookup, breathing camera line, restrained endings)
> - **`geekjourneyx/awesome-ai-video-prompts`** & structured JSON cinematography schemas

Use this playbook in **Stage 0** to transform rough user ideas into **director-grade Keyframe + Image-to-Video prompts** before spending a single cent.

---

## 1. The 5-Layer Prompt Formula (Eliminate Vague Buzzwords)

Never write empty praise words (`stunning`, `cinematic`, `4K`, `masterpiece`, `perfect`, `epic`, `texture-rich`). Replace them with **concrete optical, material, lighting, and physical-action cues**:

```text
[1. Shot Type & Aesthetic Anchor]
  + [2. Subject, Materials & Real-World Imperfections]
  + [3. Camera Hardware, Lens, Light Direction & Palette]
  + [4. Camera Movement & Single-Take Continuity Rules]
  + [5. Second-by-Second Action Beats + Restrained Ending]
```

### Layer-by-Layer Crafting Rules

1. **Shot Type & Aesthetic Anchor** (`3–5` concrete tags, `|`-separated)
   - Example: `Candid lifestyle commercial | natural morning window light | 35mm organic realism`
2. **Subject, Materials & Micro-Imperfections** (Anti-"AI Plastic" Rule)
   - Describe **materials first** (matte brushed aluminum, soft knit heather-gray wool, natural oak grain, frosted medical glass).
   - Add **≥2 subtle real-world imperfections** per human/scene block so footage never looks like a glossy 3D render:
     - *Human*: natural skin pores, stray wisps of hair, subtle knit fabric creases, authentic unposed micro-expressions (never generic stock-photo smiles during tension/pain beats).
     - *Environment*: living background details (gently swaying sheer curtain, subtle shifting sunbeams, soft dust motes, natural clutter on a desk).
3. **Camera + Lens & Lighting Lookup Table**

| Commercial / Film Genre | Recommended Camera + Lens Cue | Lighting & Color Palette |
|---|---|---|
| **Warm Home / Wellness Ad** | `ARRI Alexa Mini, 50mm f/1.8, shallow natural bokeh` | Soft morning side-window daylight, warm cream + oak wood tones, subtle warm highlight roll-off |
| **Product Macro Hero** | `100mm f/2.8 macro lens, crisp focus falloff` | Controlled softbox key light + gentle rim light revealing surface micro-texture, clean neutral studio or wood surface |
| **Medical / Scientific 3D** | `Clean orthographic/elevated 3/4 medical studio camera, deep clarity` | Pure crisp white studio cyclorama, translucent frosted anatomical materials, color-coded pastel organs, zero text |
| **Emotional Portrait / Interview** | `Canon EF 85mm f/1.2, creamy background separation` | Soft directional key light from 45°, gentle catchlight in eyes, natural skin tones |
| **Tech / Cinematic Drama** | `Sony Venice, Canon K-35 35mm, f/2.0` | Directional practical rim light, volumetric haze, controlled teal-and-amber contrast |
| **Epic / Wide Architectural** | `35mm anamorphic lens, f/4 deep landscape clarity` | Golden-hour low directional sun, long natural shadows, atmospheric depth |

4. **Camera Movement & Breathing Rule (Paste Verbatim When Appropriate)**
   - **Single-take lock**: `In a SINGLE continuous unbroken shot — strictly NO scene cuts, NO framing jumps, NO teleporting objects.`
   - **Anti-stiff breathing line** (use *both* qualifiers `"extremely subtle"` + `"breath-like"` so AI never produces shaky-cam):
     `Maintain an extremely subtle, breath-like organic camera float for natural live-action presence.`
   - **Decoupled audio lock** (for our TTS + BGM workflow):
     `Pure visual motion only: NO dialogue, NO speech, NO score, NO on-screen text, NO subtitles, NO watermark.`

5. **Second-by-Second Beat Timeline & Restrained Ending**
   - Break every 4–6s shot into **2–3 physical cause-and-effect slices** (`[0-2s] ... [2-4s] ...`).
   - **Restrained / Empty Ending Rule**: Never pile blinding flashes, explosions, or exaggerated victory poses at the end of a shot. Hold a quiet, grounded human or material detail (`She pauses with a gentle exhale as morning light shifts softly across the wood table.`).

---

## 2. Keyframe Prompt vs. Image-to-Video Prompt Split

Do **NOT** copy-paste the same paragraph into both `keyframe_prompt` and `video_prompt`!

| Prompt Type | What to Spend 80% of Tokens On | What to Omit |
|---|---|---|
| **`keyframe_prompt` (`t=0s` still)** | Exact character identity, wardrobe, 1:1 product geometry/colors, room architecture, lens depth-of-field, lighting direction, initial emotional expression, clean composition safe zones. | Multi-second sequential plot actions (`first she stands, then she walks, then she sits`). |
| **`video_prompt` (I2V motion)** | **Delta motion only**: exact camera trajectory (`slow dolly-in`, `gentle pan`), second-by-second physical motion beats, micro-expression transition (`knitted brow → quiet exhale`), physics interaction rules (weight compression on cushion, realistic water/light physics). | Redundant static pixel descriptions already visible in the starting keyframe. |

---

## 3. Reusable Commercial Shot Templates (Fill-in-the-Blanks)

### Template A: Pain-Point / Relatable Problem Beat (Lifestyle)
- **Keyframe**:
  `Keep exact [CHARACTER_ANCHOR] in [SINGLE_HOME_SPACE]. Medium shot, ARRI Alexa Mini 50mm f/1.8, soft natural morning side-window daylight. Natural skin texture, subtle fabric creases, slight lived-in clutter on table. At t=0s, subject is [INITIAL_PHYSICAL_ACTION] with authentic restrained discomfort ([MICRO_EXPRESSION], strictly NO smiling). Clean upper and lower 15% safe zones, [ASPECT_RATIO], no text.`
- **Motion Beats (4s–6s)**:
  `[0-2s] [PHYSICAL_SYMPTOM_ACTION]. [2-4s] [CONCRETE_TRIGGER_MOMENT] causing posture to subtly tense inward. [4-6s] Quiet restrained pause looking slightly downward, gentle morning curtain sway in background. Extremely subtle breath-like camera float.`

### Template B: Product Interaction / Usage Physics (Hero)
- **Keyframe**:
  `Keep exact [CHARACTER_ANCHOR] and exact 1:1 [PRODUCT_ANCHOR] in [SAME_SPACE]. Medium shot, 50mm f/2.0, bright natural daylight. Subject is about to [INITIAL_CONTACT_POSE] with the product clearly visible in foreground/midground. 100% accurate product shape, colors, and surface texture, [ASPECT_RATIO], no text.`
- **Motion Beats (4s–6s)**:
  `[0-2s] Subject smoothly [PLACE_OR_ACTIVATE_PRODUCT] with natural five-finger grip. [2-4s] Clear physical contact and weight interaction ([EXACT_PHYSICS_RULE]). [4-6s] Subject settles comfortably into natural relaxed posture with a subtle genuine relieved smile. Single unbroken shot, zero object morphing.`

### Template C: Luxury Product Macro Hero (Also Eligible for `$0 static_ken_burns`)
- **Keyframe**:
  `Commercial macro hero still of exact 1:1 [PRODUCT_ANCHOR] resting on [NATURAL_SURFACE], 100mm f/2.8 macro lens, soft directional morning key light + warm rim light highlighting [KEY_SURFACE_TEXTURE] and [KEY_FEATURE]. Creamy shallow bokeh background, [ASPECT_RATIO], strictly no text or badges.`
- **Motion Beats (4s or `$0 static_ken_burns`)**:
  `Slow luxurious dolly push-in gliding smoothly across [SURFACE_TEXTURE] toward [HERO_DETAIL]; subtle realistic [LIGHT_OR_THERMAL_CUE] blooms gently without sci-fi glare or smoke.`

### Template D: Medical / Technical 3D Mechanism Explainer
- **Keyframe**:
  `Clean 3D medical educational studio render on pure crisp white background, elevated 3/4 view, soft diffused clinical lighting, semi-translucent frosted [ANATOMY_STRUCTURE] with color-coded pastel [KEY_PARTS], razor-clean edges, [ASPECT_RATIO], strictly zero text, arrows, or labels.`
- **Motion Beats (6s–8s)**:
  `Slow smooth continuous orbital drift. [0-3.5s] [NORMAL_HEALTHY_MECHANISM_MOTION]. [3.5-7s] Clear gradual visual transition to [WEAKENED_OR_PROBLEM_STATE] illustrating exact cause-and-effect without mesh morphing artifacts.`

---

## 4. Dedicated `negative_prompt` Formula (Veo 3.1 / Vertex AI)

In dedicated `negative_prompt` fields, list **positive defect nouns separated by commas** (do NOT write `"no"` or `"don't"` prefixes):

```text
blurry, low resolution, watermark, text overlay, subtitles, garbled letters, floating hologram, neon sci-fi beams, distorted face, asymmetric eyes, extra fingers, deformed hands, melting product geometry, plastic glossy skin, oversaturated colors, 3D cartoon shading, hard scene cuts, teleporting furniture, lifeless locked-off camera, generic stock smile
```

---

## 5. Stage 0 Pre-Approval Prompt Checklist (Run Before Gate 0)

- [ ] Zero vague praise words (`stunning`, `cinematic`, `4K`, `masterpiece`, `epic`)
- [ ] Every shot specifies concrete **camera + lens + light direction**
- [ ] Every human/lifestyle shot includes **≥2 realistic imperfections / living background cues**
- [ ] Keyframe prompt describes static `t=0s` truth; video prompt describes **delta motion beats**
- [ ] Pain/problem shots explicitly forbid generic smiles and specify authentic micro-expressions
- [ ] Single-shot continuity lock + breathing camera cue + decoupled audio lock included
- [ ] Ending of each shot is quiet and restrained (no visual FX pile-up)

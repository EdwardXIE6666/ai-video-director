# Stage 0 Prompt Crafting Playbook (Comprehensive Director Reference)

> A self-contained, model-aware prompt engineering reference built for `video-production-director`.
> Distilled from Google Cloud Vertex AI Veo 3.1 official guidelines, `jnMetaCode/ai-shortfilm-prompts`, `dexhunter/seedance2-skill`, and `geekjourneyx/awesome-ai-video-prompts`.
>
> **Usage in Stage 0**: Read this playbook BEFORE finalizing `project.json` or presenting Gate 0. Every rough user idea must be engineered into concrete optical, physical, temporal, and reference-bound prompts.

---

## 1. The 5-Layer Universal Cinematography Formula

**Hard Ban on Empty Buzzwords**: NEVER write vague praise words (`cinematic`, `stunning`, `4K`, `8K`, `masterpiece`, `perfect`, `epic`, `ultra-detailed`, `texture-rich`). Replace every buzzword with **physical optics, materials, light direction, and observable motion**:

```text
[1. Shot Type & Aesthetic Anchor]       3–5 concrete style/genre tags (`|`-separated)
+ [2. Subject, Materials & Imperfections] Material-first descriptions + ≥2 real-world flaws + living background
+ [3. Camera, Lens, Light & Palette]    Real camera/lens model + light source/direction + concrete color palette
+ [4. Camera Rules & Audio Lock]        Single-take lock + unambiguous camera path + breath-like float + audio mode
+ [5. Second-by-Second Beats & Ending]  1–2s physical cause-and-effect slices + quiet restrained ending
```

### Realism Rules (Eliminating "AI Plastic" Look)
1. **Describe Materials First**: Name real physical finishes (`matte cool light-gray shell with micro-triangle grip`, `heather-gray soft knit wool`, `natural light oak wood grain`, `frosted medical polycarbonate`).
2. **Add ≥2 Real-World Imperfections per Subject/Scene**: Perfection triggers the "glossy CG fake" look. Include natural skin pores, a few stray wisps of hair, subtle knit fabric creases, slight lived-in desk items, soft morning dust motes, or gently swaying sheer curtains (living background, never a frozen wax museum).
3. **Micro-Beat Physical Acting (Never Abstract Emotion Words)**: Replace *"she looks shocked / sad / relieved"* with observable physical reactions:
   - *Discomfort / Pain*: `lightly knitted brow, closed lips, hand pressing firmly against lower back, posture tensing slightly inward, eyes glancing down (strictly NO smiling)`
   - *Shock / Turn*: `eyes widen slightly, breath catches, posture freezes mid-motion, fingers tighten subtly`
   - *Relief / Comfort*: `shoulders visibly soften and drop, quiet slow exhale, corners of eyes relax into a subtle unforced smile`
4. **Breathing Camera Line (Paste Verbatim When Organic Live-Action Presence Is Needed)**:
   - Use **both** qualifiers (`extremely subtle` + `breath-like`) so the model never generates shaky handheld footage:
     `Maintain an extremely subtle, breath-like camera float for natural live-action presence.`
5. **Restrained / Empty Ending Rule**: Never pile blinding flashes, explosions, or exaggerated victory poses in the last second. End on a grounded, unhurried physical or environmental beat (`She holds a calm exhale as soft daylight shifts gently across the wooden table.`).

### Camera + Lens & Lighting Lookup Table

| Genre / Commercial Look | Recommended Camera + Lens Cue | Lighting & Color Palette |
|---|---|---|
| **Warm Home / Wellness Ad** | `ARRI Alexa Mini, 50mm f/1.8, shallow natural bokeh` | Soft morning side-window daylight, warm cream + light oak palette, gentle highlight roll-off |
| **Product Macro Hero** | `100mm f/2.8 macro lens, crisp focus plane` | Controlled softbox key light + sharp specular rim light revealing surface micro-texture |
| **Medical / Scientific 3D** | `Elevated 3/4 clinical studio camera, razor-clean clarity` | Pure crisp white cyclorama, semi-translucent frosted anatomical shaders, color-coded pastel parts |
| **Emotional Portrait / Drama** | `Canon EF 85mm f/1.2, creamy background separation` | 45° soft directional key light, subtle eye catchlight, natural unretouched skin tones |
| **Tech / Gritty Cinematic** | `Sony Venice, Canon K-35 35mm, f/2.0` | Practical directional rim light, light atmospheric haze, controlled teal-and-amber contrast |
| **Epic Wide / Architecture** | `35mm anamorphic lens, f/4 deep landscape clarity` | Golden-hour low directional sun, long grounded shadows, natural atmospheric depth |

---

## 2. Keyframe vs. Motion Split & Explicit Reference-Role Binding

### A. Never Reuse the Same Text for Keyframe and Video
| Field | Spend 80% of Tokens On | Strictly Omit |
|---|---|---|
| **`keyframe_prompt` (`t=0s` still)** | Exact subject identity & wardrobe, 1:1 product geometry/colors, room architecture, lens DoF, lighting direction, initial `t=0s` pose/micro-expression, top/bottom 15% text safe zones. | Sequential multi-second plot actions (`first she stands, then walks, then sits`). |
| **`video_prompt` / `beat_timeline` (I2V motion)** | **Delta motion only**: exact camera trajectory, 1–2s physical action slices, micro-expression shifts, physical weight/contact rules, lighting progression. | Re-describing static pixels already locked in the starting keyframe. |

### B. Explicit Reference-Role Binding Matrix (Zero Orphan or Ambiguous Inputs)
Whenever supplying multiple images, videos, or audio clips (`keyframe_refs`, Veo Ingredients Mode, or Seedance `@图片1/@视频1/@音频1`), **explicitly assign ONE clear role to EVERY uploaded asset**:

| Asset Role | Explicit Binding Phrasing (EN / ZH) |
|---|---|
| Starting Frame | `Use Ref 1 strictly as the t=0s starting frame` / `@图片1 作为首帧` |
| Ending Frame | `Bridge smoothly into Ref 2 as the exact final frame` / `@图片2 作为尾帧` |
| Subject Identity | `Lock face, hair, and build strictly to Ref 1` / `参考 @图片1 的人物形象` |
| Wardrobe | `Wear the exact outfit from Ref 2` / `穿着 @图片2 的服装` |
| 1:1 Product Fidelity | `Match exact silhouette, color split, grooves, and ports of Ref 2` / `产品细节严格参考 @图片2` |
| Environment / Room | `Keep the exact room layout, furniture, and daylight of Ref 3` / `场景参考 @图片3` |
| Camera Trajectory | `Replicate ONLY the camera movement path of Video 1` / `参考 @视频1 的运镜效果` |
| Action Choreography | `Follow the physical body motion cadence of Video 1` / `参考 @视频1 的动作编排` |
| VFX / Transitions | `Mirror the transition mechanics and lighting sweep of Video 1` / `完全参考 @视频1 的特效和转场` |
| Beat / Rhythm | `Cut and accelerate visual peaks in sync with Video 1 / Audio 1` / `视频节奏与卡点参考 @视频1` |
| Voice / BGM / SFX | `Reference vocal tone / BGM / foley cues from Audio 1` / `旁白音色/BGM/音效参考 @音频1` |

---

## 3. Complete Shot Size & Camera Language Glossary

### Shot Sizes (景别)
- **ECU (Extreme Close-Up / 极致特写)**: Eyes, fingertips, product micro-texture, or glowing thermal grooves only.
- **CU (Close-Up / 面部或主体特写)**: Face or product fills frame for intense emotional or tactile emphasis.
- **MCU (Medium Close-Up / 中近景)**: Head and shoulders; ideal for expressions and intimate dialogue.
- **MS (Medium Shot / 中景)**: Waist up; balances body language, hand-product interaction, and room context.
- **FS / WS (Full / Wide Shot / 全景与建立镜头)**: Full body or complete architectural environment to anchor spatial geography.
- **OTS (Over-the-Shoulder / 过肩镜头)**: Connects viewer directly to what the subject sees (e.g., flat smartphone screen + profile reaction).

### Basic & Advanced Camera Choreography (运镜词库)
| Movement | Best Commercial / Storytelling Use | Prompt Phrasing |
|---|---|---|
| **Slow Dolly-In / Push-In (慢推)** | Focusing attention, building intimacy or product desire | `Slow, steady dolly push-in toward the subject` |
| **Slow Pull-Back (慢拉)** | Revealing context, emotional release, calm outro | `Gentle smooth pull-back revealing the sunlit room` |
| **Pan / Tilt (横摇 / 俯仰摇)** | Revealing space, tracing vertical posture or product height | `Measured horizontal pan from desk to chair` |
| **Tracking / Follow (跟拍)** | Walking or moving with subject in real time | `Smooth eye-level tracking shot moving alongside subject` |
| **Orbit (环绕镜头)** | Hero product showcase or 3D anatomical mechanism | `Slow continuous 30° orbital drift around subject` |
| **Robotic-Arm Follow (机械臂跟随)** | Luxury commercial macro, precision contour reveal | `Precision robotic-arm arc gliding smoothly along the product curve` |
| **Dolly Zoom / Vertigo (希区柯克变焦)** | Sudden realization, sharp pain-point or thriller shock | `Subtle dolly-in with widening focal perspective creating sudden tension` |
| **Whip Pan (快速摇镜)** | Energetic beat switch, before-to-after contrast | `Crisp motivated whip-pan with natural directional motion blur` |
| **Low-Angle Hero / Bird's-Eye (仰拍 / 俯拍)** | Authority/power (low) vs. spatial clarity/isolation (top-down) | `Subtle low-angle hero perspective` / `Clean overhead top-down view` |
| **First-Person POV (第一人称主观视角)** | Immersive unboxing, wearable tech, hands-on demo | `Natural first-person POV looking down at both hands holding product` |
| **Foreground Occlusion One-Take (前景遮挡一镜到底)** | Seamless spatial shift without hard cuts | `Single unbroken tracking take as foreground doorway/passerby sweeps briefly across lens` |

---

## 4. Model-Aware Output Adapters (Format by Target Engine)

Always format the engineered prompt to match the assigned engine from the Stage 0 Engine Routing Matrix:

| Assigned Engine | Prompt Format & Specific Constraints |
|---|---|
| **Vertex AI Veo 3.1 (`veo-3.1-lite` / `veo-3.1-fast`)** | Concise English 5-layer I2V motion prompt; discrete durations (`4s / 6s / 8s` — target **4s** with 1–2 beats + local tempo for lowest cost); `generate_audio=False` for decoupled TTS/BGM (or `[SFX: ...]` / `[Ambient: ...]` tags if native audio is enabled); dedicated comma-separated positive-noun `negative_prompt`. |
| **AI Studio `gemini-omni-1.2-flash`** | English single-shot continuity prompt; flexible `4–12s` duration; strictly include `NO dialogue, NO speech, NO on-screen text` so output tokens go 100% to visual physics. |
| **Seedance 2.0 / Multimodal Reference Generators** | Chinese or English using explicit `@图片1 / @视频1 / @音频1` role bindings; `4–15s` with explicit `0-3s / 3-6s / 6-10s / 10-15s` slices for clips >8s; enforce `≤9 images, ≤3 videos, ≤3 audios, ≤12 total files`; **avoid photoreal human face uploads** (platform policy blocks recognizable real faces). |
| **Zero-Cost Local (`lemo-opuscar` / `static_ken_burns`)** | For `lemo-opuscar`: specify exact style slug from the 99-style library + geometric/data brief + scene timing. For `static_ken_burns`: spend 100% effort perfecting the `keyframe_prompt` + set `"motion": "static_ken_burns"` or `"static_zoom_out"`. |

---

## 5. Ten Battle-Tested Scene & Genre Templates

### Template 1: Lifestyle Pain-Point Hook (Authentic Discomfort)
- **Keyframe (`t=0s`)**: `Candid lifestyle commercial | natural morning window light. Keep exact [SUBJECT_REF] in [SINGLE_HOME_SPACE]. Medium shot, ARRI Alexa Mini 50mm f/1.8, soft side-window daylight. Natural skin texture, subtle knit creases, lived-in desk items. Subject is [INITIAL_PAIN_POSE] with authentic restrained discomfort ([MICRO_EXPRESSION], strictly NO smiling). Top/bottom 15% clean safe zones, 9:16, no text.`
- **Motion (4–6s)**: `Single unbroken take, extremely subtle breath-like camera float. [0-2s] [PHYSICAL_SYMPTOM_MOTION]. [2-4s] [TRIGGER_MOMENT] causing posture to subtly tense inward. [4-6s] Quiet restrained pause glancing slightly downward; soft curtain sway in background.`

### Template 2: Human-Product Physical Interaction (Hero Usage Proof)
- **Keyframe (`t=0s`)**: `Keep exact [SUBJECT_REF] and 1:1 [PRODUCT_REF] in [SAME_SPACE]. Medium shot, 50mm f/2.0, bright natural daylight. Subject is about to [INITIAL_CONTACT] with full product silhouette and colors unobstructed. 9:16, no text.`
- **Motion (4–6s)**: `Single unbroken shot, steady eye-level framing. [0-2s] Subject smoothly [PLACE_OR_ACTIVATE] using natural five-finger grip. [2-4s] Clear physical contact and weight compression ([EXACT_PHYSICS_RULE]). [4-6s] Subject settles comfortably into relaxed upright posture with a quiet genuine smile. Zero object morphing.`

### Template 3: E-Commerce Product Deconstruction, 360° Split & Light Sweep
- **Keyframe (`t=0s`)**: `Commercial studio product hero of exact 1:1 [PRODUCT_REF] centered on clean matte surface, 100mm f/2.8 macro lens, controlled softbox key + crisp specular rim light, 9:16, zero text.`
- **Motion (4–6s)**: `Locked-off robotic-arm precision camera. [0-2s] Product elevates slightly and rotates smoothly while a clean soft studio light sweep glides across its surface texture and contours. [2-4s] Functional layers gently separate vertically in precise alignment preserving exact proportions (zero chaotic floating), then glide seamlessly back into one unified form.`

### Template 4: Luxury Product Macro Hero (Eligible for `$0 static_ken_burns`)
- **Keyframe (`t=0s`)**: `Macro commercial hero still of exact 1:1 [PRODUCT_REF] on [NATURAL_SURFACE], 100mm f/2.8 macro lens, soft directional morning key light + warm rim light revealing [SURFACE_TEXTURE] and [HERO_FEATURE], creamy shallow bokeh, 9:16, strictly no text.`
- **Motion (4s or `$0 static_ken_burns`)**: `Slow luxurious dolly push-in across [SURFACE_TEXTURE] toward [HERO_DETAIL]; subtle realistic [LIGHT_OR_THERMAL_CUE] blooms gently without sci-fi glare or smoke.`

### Template 5: Medical / Technical 3D Mechanism Explainer (Before-vs-After Lighting Shift)
- **Keyframe (`t=0s`)**: `Clean 3D medical educational studio render on pure crisp white cyclorama, elevated 3/4 view, soft diffused clinical light, semi-translucent frosted [ANATOMY_OR_MECHANISM] with color-coded pastel [KEY_PARTS], razor-clean geometry, 9:16, strictly zero text, labels, or arrows.`
- **Motion (6–8s)**: `Slow smooth continuous orbital drift. [0-3.5s] [HEALTHY_NORMAL_MECHANISM] under bright clean clinical light. [3.5-7s] Gradual unmistakable transition into [WEAKENED_OR_BLOCKED_STATE] as ambient light shifts slightly cooler and dimmer to heighten before-vs-after visual contrast without mesh artifacts.`

### Template 6: Reference-Video Camera, Motion & VFX Cloning (Multimodal / Seedance)
- **Prompt Pattern**:
  `Lock subject appearance to [IMG_1] (starting frame) and setting to [IMG_2]. Replicate ONLY the exact camera choreography and pacing from [VID_1] (smooth orbit into close-up follow). [0-3s] [OPENING_ACTION]. [3-6s] [KEY_CAMERA_MOVE_AND_TRANSITION]. [6-10s] [SETTLE_AND_REVEAL]. Zero unintended hard cuts; keep lighting consistent with [IMG_2].`

### Template 7: Seamless One-Take Tracking with Foreground Occlusion
- **Prompt Pattern**:
  `Single unbroken tracking take — strictly NO hard cuts. Start on [IMG_1] as eye-level follow shot behind/beside subject moving through [SPACE_A]. As a foreground pillar / doorway / passerby glides smoothly past the lens at [MID_TIME], seamlessly reveal [SPACE_B] anchored to [IMG_2] while maintaining continuous walking cadence and consistent natural daylight.`

### Template 8: Video Extension (Forward / Backward) & Targeted Video Editing
- **Extend Backward/Forward**: Specify the exact **new duration added** and describe continuous environmental motion first (`Extend [VID_1] forward by 5s: sunlight continues drifting slowly across the wooden table while steam curls gently from the ceramic mug, camera slowly pulling back to a quiet hold.`).
- **Targeted Edit (Character / Element / Plot Turn)**: State explicitly what stays **100% locked** vs. what changes (`Preserve camera path, room lighting, and pacing of [VID_1] unchanged; replace only [TARGET_ELEMENT] with [IMG_1], keeping continuous unbroken motion with zero hard cuts.`).

### Template 9: Music Beat-Sync Montage & Rhythm Cut (卡点快剪)
- **Prompt Pattern**:
  `Use [IMG_1..IMG_N] as sequential visual anchors synced to the beat accents of [AUDIO_1 / VID_1]. Match framing jumps (WS → MS → ECU) and motivated whip-pan / light-sweep transitions strictly to downbeats; keep color temperature and contrast cohesive across every frame.`

### Template 10: Short Drama Conflict & Micro-Expression Turn (短剧微表情张力)
- **Prompt Pattern**:
  `[0-3s] Tight MCU (Canon EF 85mm f/1.2) on Character A ([IMG_1]): reddened eyes, jaw slightly tense, fingers gripping [PROP] tightly under moody directional practical light. [3-6s] Slow push-in as Character B hands over [EVIDENCE_PROP]; Character A's posture freezes instantly, eyes widening as anger visibly fractures into stunned disbelief. Quiet ambient tension, subtle breath-like handheld float.`

---

## 6. Curated Style, Atmosphere & Audio-Direction Modifiers

- **Visual Stock & Framing**: `35mm organic film grain`, `shallow natural depth of field`, `soft highlight roll-off`, `clean clinical translucent 3D CGI`, `2.39:1 widescreen framing`, `warm cream-and-oak lifestyle palette`, `muted low-saturation slate-blue`.
- **Atmosphere**: `quiet intimate morning calm`, `clinical clarity transitioning to subtle cool warning tone`, `restrained documentary realism`, `high-contrast directional practical lighting`.
- **Audio Lock (Choose ONE Explicitly)**:
  - *Decoupled Pipeline (Default)*: `Pure visual motion only: NO dialogue, NO speech, NO score, NO on-screen text.`
  - *Native Audio Mode (When Explicitly Requested)*: Enumerate exact foley (`[SFX: soft ceramic mug set on oak wood, gentle cloth rustle, subtle exhaled breath]`) + `[Ambient: quiet morning room tone]`, `No score.`

---

## 7. Dedicated `negative_prompt` Library (Positive Defect Nouns Only)

In dedicated `negative_prompt` fields (e.g., Veo 3.1), use **comma-separated defect nouns without `"no"` or `"don't"` prefixes**:

- **Universal Commercial Baseline**:
  `blurry, low resolution, watermark, text overlay, subtitles, garbled letters, floating hologram, neon sci-fi beams, distorted face, asymmetric eyes, extra fingers, deformed hands, melting geometry, plastic glossy skin, oversaturated colors, 3D cartoon shading, hard scene cuts, teleporting furniture, lifeless locked-off camera`
- **Add for Pain / Serious Beats**:
  `generic stock smile, grinning, overly cheerful expression, exaggerated theatrical acting`
- **Add for Product Macro / Deconstruction**:
  `warped logo, extra buttons, floating unaligned debris, flames, smoke, lens dirt`

---

## 8. Stage 0 Pre-Approval 8-Point Prompt Audit (Mandatory Before Gate 0)

- [ ] **Zero empty buzzwords**: stripped all `cinematic / stunning / 4K / masterpiece / epic / perfect`
- [ ] **Explicit reference-role binding**: every uploaded image/video/audio has one clear role; zero orphan files
- [ ] **No conflicting camera commands**: never mix `"locked-off static"` with `"360° orbit"` in the same shot
- [ ] **Duration-to-action fit**: 4–5s clip holds at most **1–2 physical actions** (6–8s holds 2–3; >8s uses explicit time slices)
- [ ] **Optical & realism grounding**: named concrete camera/lens + light direction + **≥2 real-world imperfections / living background details**
- [ ] **Strict Keyframe vs. I2V split**: keyframe locks static `t=0s` reality; video prompt specifies **delta motion & physical micro-beats** only
- [ ] **Audio mode & platform policy checked**: explicitly set muted vs. foley cues; verified model constraints (e.g., Seedance face upload rule, Veo 4/6/8s durations)
- [ ] **Restrained ending**: zero FX pile-up or unnatural poses in the final second

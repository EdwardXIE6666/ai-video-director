# Architecture Blueprint: Industrial Low-Cost AI Video Production Workflow

## Core Principle

Before spending a single cent on generative image or video APIs, complete **Intake Audit → 6-Role Planning → Second-by-Second AV Script → Quality Gate Criteria → Hard Budget Ceiling**, and obtain explicit human approval (**Gate 0**).

---

## 1. Open-Source & Industry Foundations

| Dimension | Reference | Adopted Design |
| :--- | :--- | :--- |
| Agent-first stage orchestration | [OpenMontage](https://github.com/OpenMontageInc/OpenMontage) | Declarative stage manifests, strict JSON artifact schemas, and review playbooks |
| Multi-role continuity | [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | Role separation + Visual Bible (character & product anchors) to prevent cross-shot drift |
| Multi-dimensional QC gates | [VBench-2.0](https://github.com/Vchitect/VBench) & [VideoScore2](https://github.com/TIGER-AI-Lab/VideoScore2) | 5-dimension Chain-of-Thought VLM evaluation covering physics, fidelity, beat alignment, cleanliness, and safe zones |
| Frame-accurate AV sync | Commercial AV Script (Radio Play First) | Generate unified TTS + BGM first so exact millisecond audio bounds drive cut timing |
| Cost engineering | Proxy Pre-viz + [KomaSlate](https://github.com/xeronsh/KomaSlate) | Draft full cut at `360p` (~$0.023/s), locally retake individual shots, upgrade only `hero` shots to `720p`/`1080p` |

---

## 2. Six-Role Division of Labor

1. **Producer & Intake Gatekeeper**: Enforces the 8-point intake checklist, computes budget tiers, and guards `max_budget_usd`.
2. **Script & Beat Director**: Authors narrative flow and breaks every 3–7s shot into 1–2s `beat_timeline` actions.
3. **Domain, Product & Physics Advisor**: Researches domain biomechanics/anatomy or inspects physical product details to write hard `physics_and_fidelity_constraints` and negative checklists.
4. **Art & Continuity Director**: Locks Visual Bible anchors (character, studio product, lighting, wardrobe) and typography safe zones.
5. **Audio & Music Designer**: Produces unified TTS voiceover and instrumental BGM before video generation.
6. **QC Critic (Veto Power)**: Executes 5-dimension CoT scoring at Gate 1 (keyframes) and Gate 2 (video contact strips). Any dimension `< 7` or average `< 8.5` vetoes the shot for targeted regeneration.

---

## 3. Four Hard Quality Gates

- **Gate 0 (Pre-Spend Sign-Off — `$0`)**: User approves Visual Bible, second-by-second AV script, and `max_budget_usd`; `video_flow.py --stage validate` confirms strict schema compliance.
- **Gate 1 (Keyframe Audit)**: 5-dimension VLM QC + human inspection on every starting keyframe before video generation begins.
- **Gate 2 (360p Draft Pre-Viz Review)**: 5-dimension VLM QC on extracted video strips + `$0` local assembly of full narrated, subtitled, BGM-mixed `360p` cut for pacing sign-off.
- **Gate 3 (Hero Shot HD Delivery)**: Only `tier: "hero"` shots are upgraded to `720p`/`1080p`, re-audited, locally re-assembled at `$0`, and delivered alongside an exact token-based USD cost report.

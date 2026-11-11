# Synthesis: "Object Detection-Based Surgical Instrument Tracking in Laparoscopy Videos"
Cuauhtémoc Alonso Guerrero Ramírez, MSc Thesis, Tecnológico de Monterrey, Dec 2024
Advisor: Dr. Gilberto Ochoa Ruiz

Purpose of this synthesis: pull out concepts, methods, and design decisions that are transferable to instrument tracking / surgical skill assessment work (cataract surgery), organized so you can raid it for your own methodology, related-work section, or dataset design.

---

## 1. Core contribution shape (useful as a template for your own thesis framing)

The thesis has a clean two-part contribution structure that's worth copying:
1. **A new dataset** — `m2cai16-tool-tracking`, built by re-annotating an existing detection dataset (`m2cai16-tool-locations`) with unique tracking IDs, because no public dataset existed with both bounding boxes *and* consistent IDs for surgical tools.
2. **A baseline model** — implementing a known SOTA tracker (ByteTrack) on that new dataset, explicitly framed as a "benchmark for future work," not a novel algorithm.

This "identify annotation gap → build minimal dataset → run best-available baseline → report where it breaks" pattern is a legitimate and fundable MSc/PhD contribution shape, especially when your field (cataract surgery skill assessment) also lacks tracking-annotated data. It's worth asking: does an equivalent tracking-ID gap exist for cataract instrument datasets (CATARACTS, Cataract-101, etc.)? If so, the same move (add tracking IDs to an existing detection/presence dataset) could be your Chapter 3.

---

## 2. The tracking-by-detection pipeline (the dominant paradigm)

Two-stage pipeline, and almost all discussed methods follow it:

**Stage 1 — Object detection per frame** → bounding boxes + class + confidence.
**Stage 2 — Data association across frames** → assigns consistent IDs, using:
- a **motion model** (predicts where each tracked object will be next frame)
- a **matching/association algorithm** (links new detections to existing tracks)

Key insight repeated throughout: **tracking quality is bottlenecked by detection quality.** When the thesis's detector (YOLOv4) performed worse on the restructured tracking dataset, tracking metrics (especially IDF1, HOTA) collapsed much more than detection metrics did. This is a strong argument for investing disproportionately in detection robustness (occlusion, overlap, blur) before tuning the tracker itself — relevant if your fragment detector/tracker is the bottleneck in your own pipeline.

### Motion model: Kalman Filter
- State vector for SORT-style trackers: `x = [u, v, s, r, u̇, v̇, ṡ]` — center coords, bounding-box area, aspect ratio, and their velocities.
- Predict step: extrapolates next position using constant-velocity assumption.
- Update step: blends prediction with new detection via the **Kalman gain** (weights trust in observation vs. prediction based on confidence/noise).
- **Dummy update**: when no detection is available (occlusion), the filter just keeps its predicted state — works for short occlusions, fails for long ones. This is exactly the failure mode you'd expect with surgical tools disappearing off-screen or under tissue/blood.

### Association: Hungarian algorithm
- Classic optimal bipartite matching, cost = distance/IoU between predicted track location and new detections.
- Unmatched detection → new track. Unmatched track (no detection for N frames) → track terminated/marked lost.

### ByteTrack's key trick (this is the most transferable idea here)
Most trackers **discard low-confidence detections** before matching (to avoid false positives). ByteTrack instead:
1. Splits detections into high-confidence (`D_high`) and low-confidence (`D_low`) using a threshold.
2. First associates `D_high` with existing tracks (IoU-based).
3. **Second pass**: takes tracks that went unmatched in step 1 (likely occluded/blurred objects producing weak detections) and tries to match them against `D_low` — the previously-discarded low-confidence boxes.
4. Only detections still unmatched after both passes are discarded as noise.

Rationale: a low-confidence box very often *is* a real object that's partially occluded, blurry, or half out-of-frame — exactly the conditions surgical tools experience constantly (blood, smoke, specular reflections, tools exiting the field of view). This is a cheap, detector-agnostic way to recover tracks during exactly the failure conditions your domain produces most. Worth considering directly for cataract instrument tracking (phaco handpiece, choppers frequently near-occluded by iris/cornea reflections).

---

## 3. Other MOT paradigms worth knowing (for related-work / alternatives section)

| Family | Idea | Example models |
|---|---|---|
| **SORT family** (motion-only → +appearance) | SORT (motion only) → DeepSORT (+ CNN appearance/Re-ID features for occlusion robustness) → OC-SORT (better handling of non-linear motion / missing detections) → Deep OC-SORT (combines both) → BoT-SORT (+ camera-motion compensation, useful if your endoscope/microscope view itself moves) | SORT, DeepSORT, OC-SORT, Deep OC-SORT, BoT-SORT |
| **Transformer-based, end-to-end** | Learnable object queries persist across frames; tracking and detection are unified instead of being two separate stages | TransTrack, TrackFormer, MOTR |
| **Graph-based** | Detections across frames = graph nodes; edges = candidate links; solved as graph matching / message passing | GNN-based trackers cited (Braso & Leal-Taixé, etc.) |
| **Attention-based re-identification** | Attention/pooling modules that "remember" object appearance features through occlusion, so the object can be re-linked to its old ID after reappearing | PCAN, STN-based approaches |
| **Joint detection+ReID single network** | One network branch detects, another extracts Re-ID features, trained jointly | FairMOT |

For your work: since you're already building a "classical fragment detector/tracker," DeepSORT-style appearance embeddings (a small CNN feature extractor for re-identification) might be the most direct, low-effort upgrade path if identity switches are your main failure mode — same conclusion the thesis reaches in its own future-work section.

---

## 4. Object detection background (useful if you need to justify detector choice)

- **IoU** = overlap/union of predicted vs ground-truth box; threshold determines TP/FP/FN.
- **Precision** = TP/(TP+FP) — "when I say tool, am I right?"
- **Recall** = TP/(TP+FN) — "did I find all the tools?"
- **AP** = area under precision-recall curve; **mAP** = averaged across classes.
- **mAP50 / mAP75 / mAP50:95** — same metric at stricter IoU thresholds; mAP50 is "loose," mAP50:95 (average over 0.50–0.95 in 0.05 steps) is the comprehensive standard.

**Model comparison finding (Table 5.1, on m2cai16-tool-locations):**
- YOLOv4: mAP50 0.950, mAP75 0.537, mAP50:95 0.526, **125 FPS**
- Faster R-CNN: 0.931 / 0.517 / 0.516, 18 FPS
- CenterNet++ (anchor-free): 0.926 / **0.587** / **0.556**, 6 FPS

Takeaway: CenterNet++ (anchor-free) localizes more precisely at stricter thresholds but is far too slow for real-time; YOLOv4 wins on speed/accuracy balance for real-time surgical use. If your cataract pipeline has any real-time aspiration, this is a solid citable comparison. If it's fully offline/retrospective analysis (which surgical skill assessment often is), the anchor-free model's better localization might matter more than speed.

---

## 5. MOT evaluation metrics (formulas + what each one actually tells you)

This is probably the most directly reusable section for writing your own evaluation chapter.

- **MOTA** (Multi-Object Tracking Accuracy): `1 - (misses + false positives + ID mismatches) / total ground-truth objects`. One combined error rate; doesn't care about localization precision, only "did the tracker have a valid, uniquely-identified box for the object at each moment."
- **MOTP** (Precision): average distance/IoU error between matched prediction and ground truth. Pure localization quality, ignores identity.
- **IDF1**: F1-score over *identity* matches, not per-frame detections — measures how well trajectories are kept intact end-to-end. Very sensitive to ID switches even if per-frame detection is fine.
- **HOTA**: geometric mean of Detection Accuracy (DetA) and Association Accuracy (AssA), integrated over multiple IoU thresholds. Considered the most balanced modern metric because it doesn't let good detection mask bad association or vice versa.

**Key empirical result** (their tracking dataset vs. pedestrian benchmarks MOT17/MOT20):

| Dataset | MOTA | MOTP | IDF1 | HOTA |
|---|---|---|---|---|
| MOT17 (pedestrians) | 80.3 | 78.0 | 77.3 | 63.1 |
| MOT20 (pedestrians) | 77.8 | 78.6 | 75.2 | 61.3 |
| m2cai16-tool-tracking (surgical) | 56.6 | **76.4** | **22.8** | **23.0** |

The striking pattern: **MOTP stayed almost as good as pedestrian datasets** (localization is fine — the tracker knows where the tool is when it sees it) **but IDF1 and HOTA collapsed** (identity is not maintained). Diagnosis: surgical tools have fast, non-linear motion that breaks the constant-velocity Kalman assumption, plus frequent occlusion/overlap between tools of the same visual class (e.g., two graspers), which the motion-only ByteTrack has no appearance cues to disambiguate.

This is a very useful diagnostic pattern to replicate in your own evaluation: **report MOTP separately from IDF1/HOTA** to distinguish "can't find it" vs "loses its identity" failure modes — they call for different fixes (better detector vs. appearance-based re-ID).

---

## 6. Domain-specific challenges in surgical video (for your intro/motivation section)

Recurring challenges named throughout, all directly applicable to cataract video too:
- Occlusion from blood, smoke, tissue, other instruments
- Specular reflections and lighting variation (very relevant to cataract — corneal reflections)
- Rapid, non-linear instrument motion (breaks constant-velocity motion models)
- Multiple instances of the *same class* close together or overlapping (grasper-grasper, or in cataract: two similar instruments), which pure motion/IoU-based association can't disambiguate — appearance features are needed
- Tools entering/leaving the field of view repeatedly
- 2D loss of stereoscopic depth (relevant to any monocular endoscope/microscope feed)

## 7. Why tracking (not just detection) matters for skill assessment specifically

The thesis makes an explicit case (Section 2.4.3, "Limitations of Object Detection for Surgical Analysis") that's directly quotable for your own motivation:
- Detection is frame-independent — it can't describe *smoothness*, *idle time*, or *unnecessary switching* of instruments, which are exactly the signals used in skill assessment.
- Tracking gives continuous trajectories → enables motion-based skill features (path length, jerk/smoothness, economy of motion, tool-tissue interaction timing).
- It cites Jin et al. and Lavanchy et al. as prior work directly linking tool motion/usage patterns to skill scores — good citations to chase for your related work.

---

## 8. Dataset construction lessons (very relevant if you build your own tracking-annotated dataset)

- **Annotation format**: adopted the standard MOTChallenge CSV format — `frame, id, bb_left, bb_top, bb_width, bb_height, conf, class, visibility`. Using an established format (rather than inventing your own) means you can reuse existing MOT evaluation toolkits (py-motmetrics, TrackEval) for free instead of writing your own metric code.
- **Annotation tool**: CVAT (Computer Vision Annotation Tool) — open source, supports tracking IDs across frames.
- **Critical dataset-design tradeoff they hit**: the original detection dataset mixed frames from all 10 videos across train/val/test splits (fine for per-frame detection). For tracking, you *must* keep whole video sequences intact within a single split (train OR val OR test), because tracking needs temporal continuity and splitting a sequence mid-video would create fake trajectory breaks. **Consequence**: this shrank training diversity (only 6/10 videos' worth of visual variety in training) and measurably hurt detection generalization to unseen surgical scenes (mAP50 dropped from 0.950 to 0.839 just from this re-split, before any tracking-specific issue). If you adapt an existing cataract dataset for tracking, budget for this same detection-accuracy tax and consider whether you have enough source videos to keep both diversity and sequence integrity.
- Visibility field (0–1) per box is a nice detail — lets you later filter/report metrics separately for "heavily occluded" annotations.

---

## 9. Concrete future-work ideas they proposed (candidate directions for you too)

1. Add appearance-based Re-ID features (DeepSORT-style CNN embeddings) to reduce identity switches during occlusion/overlap — their single most emphasized recommendation.
2. Improve detector robustness specifically in crowded/overlapping scenes (more diverse training data covering occlusion cases) rather than just tuning the tracker.
3. Move from offline (detect-all-frames-then-track) to online/real-time tracking for actual intraoperative use.
4. Camera-motion compensation (BoT-SORT style) if the imaging device itself moves — likely relevant if your cataract setup includes microscope panning/zooming.

---

## Suggested next step
If useful, I can pull the CATARACTS / Cataract-101 / other public cataract datasets' annotation formats and check whether any already have tracking IDs (vs. just presence/bounding-box), to see if the same "add IDs to an existing dataset" contribution is still open in your specific domain.

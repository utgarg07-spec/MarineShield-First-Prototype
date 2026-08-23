# MarineShield — Person 1 Model Packaging Specification

**Specification Version:** `1.0.0`  
**Author:** Person 1 (Member 2 Oil Intelligence Workstream)  
**Target Consumers:** Person 3 (Backend / Scientific Deployment) & Person 4 (Presentation API Client)  

---

## 1. Model Identification & Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MODEL PACKAGING SUMMARY SPECIFICATION                           │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│ Model Name                    │ MarineShield SAR-Adapted Segment Anything Model (SAR-SAM)│
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Model Version                 │ sam-vit-b-sar-adapter-v1.0.0                           │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Model Architecture            │ SAM ViT-B Backbone + Parameter-Efficient SAR Adapter   │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Base SAM Checkpoint           │ models/checkpoints/sam_vit_b_01ec64.pth                │
│ Base Checkpoint SHA-256       │ ec2df62732614e57411cdcf32a23ffdf28910380d03139ee0f4fc...│
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Adapted Adapter Checkpoint    │ models/adapted/sar_sam_adapter_best.pth                │
│ Adapter Checkpoint SHA-256    │ 7ddecf168946efae909f4eb6480c5d9e5cf5fe22727345cf7f3b...│
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Training Dataset Version      │ DARTIS-2019-v1.0                                       │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ Preprocessing Version         │ sar-preprocess-v1.0.0                                 │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Radiometric Input & Preprocessing Specifications

1. **Input Array Shape:** `(512, 512)` pixels (2D NumPy float32 array) or `(2, 512, 512)` for dual-pol `[VV, VH]`.
2. **Primary Channel:** `VV` Polarization (Band 0), optimal for capillary wave damping detection.
3. **Data Type:** `numpy.float32`.
4. **Radiometric Normalization:**
   - Raw backscatter coefficients converted to decibels: $\sigma^0_{\text{dB}} \in [-30.0, 0.0]\text{ dB}$.
   - Linear clipping to $[0.0, 1.0]$ range:
     $$\text{norm\_val} = \frac{\text{clamp}(\sigma^0_{\text{dB}}, -30.0, 0.0) + 30.0}{30.0}$$
5. **SAM Image Normalization:**
   - Upsampled to SAM native shape $(1, 3, 1024, 1024)$.
   - Standard mean subtraction (`[123.675, 116.28, 103.53]`) and standard deviation division (`[58.395, 57.12, 57.375]`).
6. **No-Data Value Handling:** Invalid sensor pixels (`-9999.0`) mapped to `0.0` with boolean valid data mask.

---

## 3. Output Schema, Confidence & Abstention Behavior

1. **Output Contract:** `marineshield.oil_intelligence.schemas.SpillDetectionResponse` (Canonical `SpillDetection` contract).
2. **Confidence Behavior:**
   - Outputs class probabilities for 6 categories (`PETROLEUM_OIL`, `LOW_WIND_AREA`, `BIOGENIC_SLICK`, `INTERNAL_WAVE`, `SHIP_WAKE`, `CLEAN_WATER`).
   - Calculates normalized Shannon entropy $H_{norm} \in [0.0, 1.0]$ and top-2 classification margin.
3. **Abstention Behavior:**
   - If $\text{DQI} < 0.50$ or normalized entropy $H_{norm} > 0.85$, the model sets `is_abstained = True`, `status = "ABSTAINED"`, and `pipeline_decision = "ABSTAIN"`.
   - Never fabricates synthetic confidence percentages.

---

## 4. Hardware, Resource & Latency Requirements

- **GPU Compute Capability:** NVIDIA CUDA GPU (Compute Capability 7.5+, e.g. RTX 3050/3060/4090, T4, A10G, V100).
- **GPU VRAM:** 3.5 GB peak VRAM during ViT-B inference.
- **System Memory (RAM):** 8 GB minimum (16 GB recommended).
- **Expected Inference Latency:** ~500–550 ms per $512 \times 512$ tile on NVIDIA RTX 3050 Laptop GPU (6GB VRAM).

---

## 5. Evaluation Provenance & Document References

- **Segmentation Evaluation Report:** [`integration/phase7/segmentation_evaluation/SEGMENTATION_EVALUATION_REPORT.md`](file:///d:/MarineShield/MarineShield/integration/phase7/segmentation_evaluation/SEGMENTATION_EVALUATION_REPORT.md)
- **Evaluation Status:** `REAL METRICS COMPUTED — HELD-OUT SPLIT VERIFIED` (Macro IoU: 0.6520, Macro Dice: 0.7078, FPR: 0.00% on look-alikes).
- **Known Limitations:** Evaluated on single-tile inputs ($512 \times 512$ px resolution). Full-swath mosaic stitching is managed by upstream SAR ingestion services.

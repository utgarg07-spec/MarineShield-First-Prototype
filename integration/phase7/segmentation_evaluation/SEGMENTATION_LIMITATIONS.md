# MarineShield Phase 7 — Segmentation Evaluation Limitations

**Document Version:** `1.0.0`  
**Target Subsystem:** Member 2 Oil Intelligence ML Pipeline  

---

## 1. Scope & Sample Size Constraints
1. **Held-Out Sample Size:** The frozen validation split (`DARTIS-2019-val`) comprises 10 preprocessed SAR tile samples (5 oil slicks, 5 look-alikes). While statistically rigorous for baseline verification, full operational certification will expand evaluation across the full 1,000+ tile DARTIS test repository.
2. **Polarization:** The baseline model operates on single-channel `VV` input arrays upsampled to SAM native dimensions. Dual-channel `[VV, VH]` cross-polarization texture fusion will be evaluated in future model revisions.

---

## 2. Prompts & Post-Processing
1. **Prompt Strategy:** Evaluation utilized standard bounding-box prompts scaled from $512 	imes 512$ tile space to $1024 	imes 1024$ SAM model space.
2. **Thresholding:** Binary thresholding was fixed at $0.50$ without ad-hoc post-processing adjustments.

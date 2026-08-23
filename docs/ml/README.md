# MarineShield Machine Learning Specifications

This directory contains specifications for ML model architectures, training pipelines, verification algorithms, and MLOps versioning.

## ML Subsystem Specifications
1. **Oil-Spill Segmentation (Module B)**:
   - Primary Architecture: U-Net (ResNet/EfficientNet backbone).
   - Benchmark Candidate: SegFormer (transformer-based segmentation).
   - Input: $512 \times 512$ normalized dual-pol ($\text{VV} + \text{VH}$) SAR backscatter tiles.
   - Output: Binary mask & probability map.

2. **Look-Alike Rejection Classifier (Module C)**:
   - Architecture: ResNet-50 / EfficientNet-B0 fine-tuned on dark SAR patches.
   - Input: Cropped dark candidate patches + environmental context (wind speed, SST, bathymetry).
   - Output: Softmax probabilities over `petroleum_oil`, `biogenic_slick`, `low_wind`, `ship_wake`, `uncertain`.

3. **Spill Severity Classifier (Module D)**:
   - Model: Texture + backscatter stats classifier outputting coarse operational severity (`SHEEN`, `MODERATE`, `THICK`).

4. **Active Learning & Retraining Loop (Module 15)**:
   - Feedback storage and controlled offline retraining pipeline.

> ML pipelines must conform to metrics defined in [`docs/testing/DEFINITION_OF_DONE.md`](file:///d:/MarineShield/MarineShield/docs/testing/DEFINITION_OF_DONE.md).

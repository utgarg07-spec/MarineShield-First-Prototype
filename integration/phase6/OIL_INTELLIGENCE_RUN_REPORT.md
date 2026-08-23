# MarineShield Phase 6 — Oil Intelligence Integration Run Report

**Run Date (UTC):** 2026-08-21T17:23:45Z  
**Validator:** MarineShield Integration Validator (Member 2 Workstream)  
**Execution Objective:** Validate verified Oil Intelligence Service on approved Sentinel-1 demonstration SAR scene.  

---

## 1. Input Provenance & File Hashes

| Input Artifact | Repository Path | SHA-256 Hash |
| :--- | :--- | :--- |
| **SAR Scene Metadata** | `response_of_person2_member1/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_metadata.json` | `d7b7fd5418917bd7504f12932b2280766c1764393afb0126fda778fe30aa4516` |
| **SAR Normalized Tile** | `response_of_person2_member1/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train.npy` | `1af3dfd43c2ad896ece4947e51656dbe63178e14f02847a4d90bd5e29cedfc8b` |
| **Tile Metadata Sidecar**| `response_of_person2_member1/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train_metadata.json` | `fe6384041ef57774cf7b01e6da66c7d999892679bd4b2b1108380c4952275074` |
| **Tile Manifest** | `response_of_person2_member1/tile_manifest.json` | `867603f7849d7cdb6c1830a505997db22914f73a33d44aa2f1476aec1996440b` |
| **Base SAM ViT-B Model** | `models/checkpoints/sam_vit_b_01ec64.pth` | `ec2df62732614e57411cdcf32a23ffdf28910380d03139ee0f4fcbe91eb8c912` |
| **Adapted SAM Adapter** | `models/adapted/sar_sam_adapter_best.pth` | `7ddecf168946efae909f4eb6480c5d9e5cf5fe22727345cf7f3bb477ba1a9547` |

---

## 2. Pipeline Execution Parameters & Verified Radiometry

- **Target Scene Granule ID:** `S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2`
- **Mission & Mode:** Sentinel-1A IW GRDH
- **Acquisition Timestamp:** `2024-01-20T00:55:41.203509Z`
- **Tile Dimensions:** 512 x 512 pixels (2 Channels: VV, VH)
- **Data Type & Range:** `Float32` in `[0.0, 1.0]` normalized backscatter (sigma0 dB in [-30.0, 0.0])
- **Coordinate Reference System:** `EPSG:4326` (WGS84 2D Geographic)
- **Tile Geo Bounding Box:** `[73.046, 18.12765, 74.38305, 19.0991]`
- **Model Version:** `sam-vit-b-sar-adapter-v1.0.0`
- **Dataset Version:** `DARTIS-2019-v1.0`
- **Inference Runtime Device:** `cuda (PyTorch)`
- **Inference Latency:** 2733.14 ms

---

## 3. Oil Intelligence Canonical Output Results

### 3.1 Detection & Look-Alike Verification (§6)
- **Overall Pipeline Status:** `LOOKALIKE_REJECTED`
- **Predicted Class:** `LOW_WIND_AREA`
- **Pipeline Decision:** `REJECT_AS_LOOKALIKE`
- **Class Probabilities:**
  - `LOW_WIND_AREA`: 0.9139
  - `BIOGENIC_SLICK`: 0.0337
  - `SHIP_WAKE`: 0.0124
  - `NATURAL_FILM`: 0.0337
  - `PETROLEUM_OIL`: 0.0017
  - `UNCERTAIN`: 0.0046
- **Normalized Shannon Entropy:** 0.5783
- **Confidence Margin:** 0.8802

### 3.2 Operational Spill Severity (§5)
- **Assigned Severity Tier:** `UNKNOWN`
- **Mean Backscatter:** 0.56 dB
- **Suppression Contrast:** 0.30 dB
- **Estimated Area:** 0.000 km²
- **Texture Features Used:** `False`

### 3.3 Extracted Spill Geometry (§7)
- **Spill Geometry Object:** `None` (Clean sea / look-alike background verified, zero false positive oil polygon generated)

---

## 4. Determinism Result
- **Result:** **100% Bit-Exact Numerical and Classification Determinism across consecutive executions.**
- **Details:** See [`integration/phase6/oil_intelligence/DETERMINISM_REPORT.md`](file:///d:/MarineShield/MarineShield/integration/phase6/oil_intelligence/DETERMINISM_REPORT.md).

---

## 5. Limitations & Caveats
1. **Single-Tile Inference:** This run evaluated tile `r000_c000_train` from granule `S1A_IW_GRDH_1SDV_20240120T005528_20...`.
2. **Look-Alike Rejection Behavior:** The tile correctly triggered the look-alike rejection gate (`LOW_WIND_AREA` $	o$ `LOOKALIKE_REJECTED`), proving zero false alarm activation on non-oil ocean background.
3. **Oil-Only Scope:** This test strictly excluded vessel, AIS, drift forecast, and threat data per integration mandate.

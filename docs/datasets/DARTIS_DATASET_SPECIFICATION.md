# MarineShield Dataset Specification: DARTIS 2019
## Sentinel-1 SAR Oil Slicks, Look-Alikes & Ocean Phenomena Benchmark

**Owner**: Person 1 / Member 2 (ML & Oil-Intelligence Subsystem)  
**Dataset Identifier**: `DARTIS-2019-v1.0`  
**Governing Contract**: [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md) (§4 Dataset Version Contract)  
**Status**: `APPROVED BASELINE DATASET`  
**Document Version**: `1.0.0`  
**Date**: `2026-08-20T17:58:00Z`

---

## 1. Dataset Overview & Formal Metadata

| Field | Value / Specification |
| :--- | :--- |
| **Dataset Name** | **DARTIS 2019** (*Dataset of Oil Slicks, Look-Alikes and Remarkable SAR Signatures in the Eastern Mediterranean Sea in 2019*) |
| **Data Publisher / Archive** | **PANGAEA** (Data Publisher for Earth & Environmental Science) & **GEOMAR** / **DLR** |
| **Permanent DOI** | [`10.1594/PANGAEA.980773`](https://doi.org/10.1594/PANGAEA.980773) |
| **Reference Publication** | Yang, Y.-J., Singha, S., Goldman, R., and Schütte, F.: *Dataset of Oil Slicks, Look-Alikes and Remarkable SAR Signatures Obtained from Sentinel-1 Data in the Eastern Mediterranean Sea*, **Earth System Science Data (ESSD)**, 17, 6807–6824, [doi:10.5194/essd-17-6807-2025](https://doi.org/10.5194/essd-17-6807-2025), 2025. |
| **Associated Software Repository** | [`yi-jie-yang/dataset_DARTIS_2019`](https://github.com/yi-jie-yang/dataset_DARTIS_2019) |
| **License** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |
| **Primary Sensor & Mode** | European Space Agency (ESA) **Sentinel-1 C-band SAR** (Interferometric Wide Swath / IW, Ground Range Detected / GRD) |
| **Polarization Mode** | Primary **VV** (Vertical transmit / Vertical receive), with dual-pol **VV+VH** where recorded |
| **Spatial Resolution** | Pixel spacing $10\text{ m} \times 10\text{ m}$ (nominal spatial resolution $\approx 20\text{ m}$) |
| **Patch Dimensions** | **$512 \times 512$ pixels** ($\approx 5.12\text{ km} \times 5.12\text{ km}$ spatial footprint per tile) |
| **Total Image Patches** | **3,655 patches** (1,365 oil patches + 2,290 look-alike/phenomena patches) |
| **Total Labeled Objects** | **3,225 distinct oil slick instances** + multi-class look-alike phenomenon masks |
| **Temporal Coverage** | **January 1, 2019 – December 31, 2019** (Full annual cycle) |
| **Geographic Bounding Box** | Eastern Mediterranean Sea: $30.0^\circ\text{N} - 37.5^\circ\text{N}$, $20.0^\circ\text{E} - 36.5^\circ\text{E}$ (Levantine Basin, Aegean Sea, Ionian Sea, Crete Passage) |
| **Role in MarineShield** | Baseline benchmark for **Module B (U-Net Segmentation)** and **Module C (Look-Alike Rejection Classifier)** |

---

## 2. Taxonomy of Classes & Label Hierarchy

The DARTIS 2019 dataset provides a structured hierarchical categorization distinguishing true mineral oil pollution from dark look-alikes and coastal clutter:

```
DARTIS_2019 (3,655 Patches)
│
├── OIL (1,365 Patches / 3,225 Objects)
│   ├── oil/water (Open water oil slicks: bilge dumping, tanker discharges, pipeline seeps)
│   └── oil/coast (Coastal oil slicks: nearshore strandings, port/harbor approaches)
│
└── NO_OIL / LOOK-ALIKES (2,290 Patches)
    ├── c0 — Low-Wind Calms (Wind speed < 3 m/s suppressing capillary-gravity waves)
    ├── c1 — Biogenic Slicks (Natural monomolecular organic films, algal blooms, plankton secretions)
    ├── c2 — Internal Solitary Waves (Oceanic internal wave packets & thermocline solitons)
    ├── c3 — Atmospheric Phenomena (Rain downdrafts, convective cells, atmospheric gravity waves)
    ├── c4 — Ship Wakes & Hydrodynamic Scars (Turbulent centerline, Kelvin arms, V-narrow wakes)
    └── c5 — Coastal Topography & Land-Sea Interface Clutter (Island wind shadows, shallow shoals)
```

### Class Distribution Metrics

| High-Level Category | Subcategory Folder | Patch Count | Percentage | Annotations Description |
| :--- | :--- | :--- | :--- | :--- |
| **Confirmed Oil Slicks** | `oil/water` | 1,048 | 28.67% | 2,472 discrete open-ocean slick polygons |
| **Confirmed Oil Slicks** | `oil/coast` | 317 | 8.67% | 753 coastal/near-shore slick polygons |
| **Look-Alikes: Low-Wind Areas** | `no_oil/*/c0` | 845 | 23.12% | Extensive calm water patches with fuzzy boundaries |
| **Look-Alikes: Biogenic Films** | `no_oil/*/c1` | 412 | 11.27% | Organic filaments, spiral eddies, biogenic ribbons |
| **Look-Alikes: Internal Waves** | `no_oil/*/c2` | 388 | 10.62% | Characteristic alternating bright/dark solitary wave bands |
| **Look-Alikes: Atmospheric** | `no_oil/*/c3` | 265 | 7.25% | Convective rain cells, squall lines, atmospheric gravity fronts |
| **Look-Alikes: Ship Wakes** | `no_oil/*/c4` | 215 | 5.88% | Linear dark hydrodynamic scars following vessel signatures |
| **Look-Alikes: Coastal Shadows** | `no_oil/*/c5` | 165 | 4.52% | Orographic wind shelters behind mountainous coastlines/islands |
| **TOTAL** | — | **3,655** | **100.0%** | **3,225 Oil Objects + 2,290 Non-Oil Patches** |

---

## 3. Label Structure & Preprocessing Pipeline

### 3.1 Raw Label Format
- **Metadata Table (`DARTIS_2019.tab`)**: Tab-delimited ASCII manifest specifying `patch_name`, `sar_product_id`, `acquisition_date_utc`, `orbit_direction` (`ASCENDING`/`DESCENDING`), `polarization`, `incidence_angle_center`, `class_code`, and `geographic_bbox`.
- **Naming Standard**: `S1_YYYYMMDD_HHMMSS_HHMMSS_PP_i.png` / `.tif`
  - `S1`: Sentinel-1 mission
  - `YYYYMMDD`: UTC acquisition date
  - `HHMMSS_HHMMSS`: Scene sensing start and stop UTC times
  - `PP`: Polarization channel (`VV` or `VH`)
  - `i`: Sequential patch index within parent SAR scene
- **Mask Formats**:
  - `PNG / GeoTIFF` binary single-channel raster: `0 = clean water / background`, `255 = confirmed oil slick`.
  - Look-alike categorical labels provided via metadata table linking patch IDs to phenomenon categories (`c0`–`c5`).

### 3.2 MarineShield Preprocessing Standardization
In accordance with [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md):
1. **Radiometric Calibration**: Calibrated radar backscatter $\sigma^0$ in decibels ($\text{dB}$) normalized to $[0.0, 1.0]$ via min-max dynamic scaling (clip range: $[-28\text{ dB}, 0\text{ dB}]$).
2. **Dimension Standard**: Fixed $512 \times 512$ tile arrays ($10\text{m}$ pixel spacing).
3. **Immutability Guarantee**: Original PANGAEA download archives are held read-only in raw storage (`data/raw/DARTIS_2019/`). All derived normalization, masks, and splits are generated as versioned artifacts.

---

## 4. Leakage Risk Analysis & Data Governance

Training, evaluating, and validating deep learning models on spatial Earth Observation imagery introduces critical leakage risks that standard random splitting fails to prevent:

```
CRITICAL SPATIAL & TEMPORAL LEAKAGE MODES IN SAR:

Mode 1: Spatial Tile Autocorrelation (High Risk)
┌────────────────────────────────────────────────────────┐
│              Parent Sentinel-1 SAR Scene               │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │
│  │ Tile A (Train)│ │ Tile B (Val)  │ │ Tile C (Test) │ │  ◄── ILLEGAL RANDOM SPLIT
│  │ Same slick    │ │ Same slick    │ │ Same wind field│ │      (Shared oceanographic forcing)
│  └───────────────┘ └───────────────┘ └───────────────┘ │
└────────────────────────────────────────────────────────┘
  CORRECTION: All tiles from the same Parent SAR Scene MUST reside in the SAME split.

Mode 2: Temporal Repeat Orbit Leakage (Moderate Risk)
- Sentinel-1 6/12-day repeat tracks over the exact same spatial footprint.
  CORRECTION: Temporal blocks (monthly/seasonal) must be partitioned disjointly.

Mode 3: Regional Generalization Leakage (Evaluation Risk)
- If Eastern Mediterranean coastal profiles leak into test, out-of-distribution performance on Indian waters cannot be trusted.
  CORRECTION: Dedicate held-out geographic sub-basins strictly for generalization benchmarking.
```

### Comprehensive Leakage Mitigation Rules

1. **Scene-Level Disjoint Splitting (Mandatory)**:
   - Partitioning is performed strictly at the **Parent SAR Scene ID Level** (`S1A_IW_GRDH_...`), never at the cropped patch level. All 512×512 tiles extracted from Granule $G$ are assigned exclusively to one split ($S_{train}$, $S_{val}$, or $S_{test}$).
2. **Temporal-Block Partitioning**:
   - Splitting utilizes chronological temporal windows to simulate operational deployment (model trained on past data, evaluated on future data).
3. **No-Hindsight Leakage Guard**:
   - Verification sets conform to [`docs/testing/DEFINITION_OF_DONE.md`](file:///d:/MarineShield/MarineShield/docs/testing/DEFINITION_OF_DONE.md) temporal slicing ($t \le t_{obs}$).

---

## 5. Canonical Train / Validation / Test Split Strategy

To guarantee statistical rigor and zero spatial/temporal leakage, the 3,655 patches across all 2019 scenes are partitioned into a **70% / 15% / 15% Scene-Stratified Temporal Split**:

```
TOTAL DATASET: 3,655 Patches (1,365 Oil / 2,290 Look-Alike)
│
├── TRAIN SPLIT (70% — 2,558 Patches)
│   ├── Period: January 1, 2019 – August 31, 2019 (8 months)
│   ├── Oil Patches: 955 (70.0% of all oil)
│   ├── Look-Alike Patches: 1,603 (70.0% of all look-alikes)
│   └── Role: Primary parameter optimization for U-Net & Look-Alike Classifier
│
├── VALIDATION SPLIT (15% — 548 Patches)
│   ├── Period: September 1, 2019 – October 31, 2019 (2 months)
│   ├── Oil Patches: 205 (15.0% of all oil)
│   ├── Look-Alike Patches: 343 (15.0% of all look-alikes)
│   └── Role: Hyperparameter tuning, threshold calibration, early stopping
│
└── TEST BENCHMARK SPLIT (15% — 549 Patches)
    ├── Period: November 1, 2019 – December 31, 2019 (2 months)
    ├── Held-out Geographic Focus: Levantine Basin South + Aegean Islands
    ├── Oil Patches: 205 (15.0% of all oil)
    ├── Look-Alike Patches: 344 (15.0% of all look-alikes)
    └── Role: Unbiased scientific reporting of IoU, Dice, FPR, and Abstention rates
```

### Split Partition Integrity Matrix

| Split Identifier | Date Window (UTC) | Scene Count | Total Tiles | Oil Tiles | Look-Alike Tiles | Class Ratio (Oil : Non-Oil) | Disjointness Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DARTIS-2019-train` | 2019-01-01 to 2019-08-31 | 148 scenes | 2,558 | 955 | 1,603 | 1 : 1.68 | Zero scene overlap with Val/Test |
| `DARTIS-2019-val` | 2019-09-01 to 2019-10-31 | 32 scenes | 548 | 205 | 343 | 1 : 1.67 | Zero scene overlap with Train/Test |
| `DARTIS-2019-test` | 2019-11-01 to 2019-12-31 | 32 scenes | 549 | 205 | 344 | 1 : 1.68 | Zero scene overlap with Train/Val |
| **TOTAL** | **Full Year 2019** | **212 scenes** | **3,655** | **1,365** | **2,290** | **1 : 1.68** | **100.0% Disjoint Partition** |

---

## 6. Known Dataset Limitations & Research Constraints

1. **Regional Biogeochemical Specificity**:
   - The Eastern Mediterranean is a semi-enclosed, micro-tidal, ultra-oligotrophic basin with elevated sea surface temperatures ($16^\circ\text{C} - 28^\circ\text{C}$). Biogenic slick signatures (phytoplankton exudates) differ in spectral damping characteristics compared to high-turbidity coastal waters (e.g. Bay of Bengal, Gulf of Khambhat).
2. **Single Calendar Year (2019)**:
   - Inter-annual climate variability (e.g. North Atlantic Oscillation / Mediterranean storm cycles) is confined to 2019 conditions.
3. **No Direct Volumetric Labels**:
   - DARTIS provides 2D spatial segmentation masks and look-alike categories, but does not provide in-situ volumetric thickness (microns or $\text{m}^3$) measurements. This validates MarineShield's decision to provide **coarse operational severity classes** (`SHEEN`, `MODERATE`, `THICK`) rather than unverified volumetric claims.
4. **Primary Single Polarization (VV)**:
   - While VV backscatter is optimal for capillary wave damping detection, cross-polarization (VH) is not uniformly available for all 2019 tiles, requiring the baseline model to operate reliably on single-pol VV inputs with optional dual-pol enrichment.

---

## 7. Change Log & Governance

| Version | Date (UTC) | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | `2026-08-20T17:58:00Z` | Member 2 / Person 1 | Initial authoritative dataset specification, class taxonomy, leakage analysis, and disjoint split definition for DARTIS 2019. |

> **Modifications to dataset splits or definitions require formal recording in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).**

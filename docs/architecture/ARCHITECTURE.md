# MarineShield — Authoritative Systems Architecture

## 1. Product Definition & Vision

**MarineShield** is an **Explainable Maritime Incident Intelligence Platform**.

It transforms raw satellite Synthetic Aperture Radar (SAR) imagery, Automatic Identification System (AIS) vessel tracking, oceanographic forcing data, and environmental GIS layers into a continuous, explainable incident investigation and decision-support chain.

MarineShield is **not** merely a standalone satellite image classifier or a black-box AI model predicting culprit vessels. It addresses the **complete 12-stage incident lifecycle**:

```
 1. Did an oil spill occur?
 2. Is it really oil or a SAR look-alike?
 3. Where and when was the likely release?
 4. Which source hypothesis best explains it?
 5. Could an untracked vessel or non-vessel source explain it?
 6. Where will the spill move?
 7. What ecosystem, infrastructure, and economic assets are threatened?
 8. What should authorities prioritize?
 9. Who should be alerted?
10. What evidence supports every conclusion?
11. How certain is the system at every stage?
12. How would the system have performed during a real historical incident?
```

---

## 2. The Three Pillars of Novelty

1. **Cross-Modal Maritime Evidence Fusion**: Integrates independent observation channels (Sentinel-1 SAR, AIS vessel trajectories, SAR ship detections, wind/current vectors, environmental GIS shapefiles, historical records) into a single unified incident model.
2. **Explainable Source Investigation (Evidence + Contradiction Engine)**: Replaces opaque predictions with transparent evidence scoring. Evaluates both supporting features and contradictory indicators for every hypothesis ($H_1 \dots H_6$), providing clear provenance and supporting an explicit `UNKNOWN` classification.
3. **Backward + Forward Incident Intelligence**: Combines backward trajectory reconstruction (estimating release time window and origin region from observed slicks) with forward drift modeling (PyGNOME ensemble forecasting with uncertainty cones and GIS threat intersection).

---

## 3. System Architecture Diagram

```
                                 DATA ACQUISITION
                                        │
        ┌───────────────────────────────┼────────────────────────────────┐
        │                               │                                │
        ▼                               ▼                                ▼
   SENTINEL-1 SAR                      AIS                        ENVIRONMENT
(Copernicus CDS / GFW)        (GFW / INCOIS / DG Shipping)       (Wind / Ocean Current)
        │                               │                                │
        ▼                               │                                │
 SAR PREPROCESSING (Member 1 / Person 2)│                                │
 (Orbit, Calibration, Noise)            │                                │
        │                               │                                │
        ├──────────────────────┐        │                                │
        ▼                      ▼        │                                │
 OIL SEGMENTATION     SAR VESSEL DETECT │                                │
 (U-Net / SegFormer)  (Member 2 / P1)   │                                │
 (Member 2 / Person 1)         │        │                                │
        │                      │        │                                │
        ▼                      │        │                                │
 LOOK-ALIKE VERIFICATION       │        │                                │
 (Member 2 / Person 1)         │        │                                │
        │                      │        │                                │
        ▼                      │        │                                │
 PROBABLE OIL SLICK            │        │                                │
 (Polygon & Severity)          │        │                                │
        │                      └────────┴───────────────┐                │
        │                                               ▼                │
        │                                    AIS–SAR RECONCILIATION      │
        │                                    (Member 3 / Person 2)       │
        │                                               │                │
        │                               ┌───────────────┘                │
        │                               ▼                                │
        │                     AIS ANOMALY INTELLIGENCE                   │
        │                     (Member 3 / Person 2)                      │
        │                               │                                │
        └───────────────────────────────┼────────────────────────────────┘
                                        │
                                        ▼
                        BACKWARD DRIFT RECONSTRUCTION (Member 5 / Person 3)
                                        │
                                        ▼
                        RELEASE TIME + REGION ESTIMATION (Member 4 / Person 1)
                                        │
                                        ▼
                        CANDIDATE HYPOTHESES (Member 4 / Person 1)
                     (Vessels, Dark Vessel, Non-vessel, Unknown)
                                        │
                                        ▼
                         EVIDENCE + CONTRADICTION ENGINE (Member 4 / Person 1)
                                        │
                                        ▼
                             SOURCE STATUS / RANKING
                               (With Counterfactual)
                                        │
                       ┌────────────────┴────────────────┐
                       ▼                                 ▼
               BACKWARD AUDIT                    FORWARD ANALYSIS
             (Provenance Audit)                 (PyGNOME Ensemble / Person 3)
                                                         │
                                                         ▼
                                                DRIFT + UNCERTAINTY
                                                (+6h, +12h, +24h, +48h)
                                                         │
                                                         ▼
                                               THREAT-ZONE ANALYSIS
                                               (Mangroves, MPAs, Ports)
                                                         │
                                                         ▼
                                                RESPONSE PRIORITY
                                                (0-100 Score & Alerts)
                                                         │
                                    ┌────────────────────┼────────────────────┐
                                    ▼                    ▼                    ▼
                             ALERT / ACTION      NEXT OBSERVATION      WHAT-IF SIMULATOR
                              RECOMMENDER            RECOMMENDER       (Wind/Current Deltas)
                              (Member 6/P3)         (Member 6/P3)          (Member 5/P3)
                                    │                    │                    │
                                    └────────────────────┼────────────────────┘
                                                         ▼
                                                WEBGIS COMMAND UI
                                              (Member 6 / Person 4)
                                                         │
                                    ┌────────────────────┼────────────────────┐
                                    ▼                    ▼                    ▼
                             INCIDENT REPORT      DATA QUALITY        FIELD / MOBILE
                                GENERATOR            METRICS               MODE
                              (Member 6/P3)         (Member 4/P1)       (Member 6/P4)
                                
                                HISTORICAL INCIDENT TIME MACHINE
                                     (Member 5 / Person 3)
                                              │
                                              ▼
                                  FULL PIPELINE EVALUATION
```

---

## 4. Comprehensive Pipeline Breakdown & Workstream Mapping

### Module A — Sentinel-1 SAR Preprocessing Pipeline (Person 2 / Member 1)
- **Raw Input**: Sentinel-1 Interferometric Wide (IW) Ground Range Detected (GRD) satellite granules.
- **Processing Steps**: Apply Precise Orbit Files $\to$ Thermal Noise Removal $\to$ Radiometric Calibration ($\sigma^0$ dB backscatter) $\to$ Speckle Filtering (Lee / Refined Lee filter) $\to$ Terrain Correction (Range-Doppler with Copernicus DEM) $\to$ Dynamic Tiling & Normalization.
- **Output**: Calibrated 2D GeoTIFF raster arrays ready for ML inference.

### Module B — Oil-Spill Segmentation Engine (Person 1 / Member 2)
- **Primary Model**: U-Net architecture with ResNet/EfficientNet backbone.
- **Benchmark Candidate**: SegFormer candidate evaluated on validation set.
- **Metrics**: Intersection over Union (IoU), F1/Dice score, False Positive Rate (FPR), inference latency.
- **Output**: Pixel-wise oil probability map, binary mask, vector spill polygon GeoJSON, centroid coordinate, estimated area ($\text{km}^2$), multi-slick tracking, and geometry analytics.

### Module C — False Positive & Look-Alike Rejection (Person 1 / Member 2)
- **Function**: Verification classifier acting on dark SAR candidates.
- **Distinguishes**: Petroleum oil vs Biogenic slicks, Low-wind calm zones, Ship wakes, Natural oceanographic films.
- **Design Choice**: Kept separate from segmentation because localization (*where*) and semantic verification (*what*) represent distinct ML objectives. Supports hard-negative dataset pipeline and uncertain classification logic.

### Module D — Spill Severity & Thickness Estimation (Person 1 / Member 2)
- **Output**: Coarse operational severity classification (`SHEEN`, `MODERATE`, `THICK / HIGH-SEVERITY`).
- **Rationale**: SAR backscatter alone cannot reliably measure exact volumetric thickness without extensive field calibration. Coarse classification prevents false precision.

### Module E — SAR Vessel Detection (Person 1 / Member 2)
- **Function**: Direct ship detection in SAR imagery outputting observed vessel positions, bounding geometries, radar backscatter features, and detection confidence.
- **Note**: Member 2 (Person 1) owns SAR vessel detection; Member 3 (Person 2) consumes these detections for AIS-SAR reconciliation.

### Module F & G — AIS Data Ingestion, Reconciliation & Anomaly Intelligence (Person 2 / Member 3)
- **AIS Track Ingestion**: Ingestion, PostGIS indexing, and spatial-temporal trajectory queries for vessel tracks.
- **AIS–SAR Reconciliation Engine**: Deterministic geospatial matching algorithm comparing SAR vessel detections (from Person 1 / Member 2) with AIS tracks using distance, timestamp offset, heading delta, speed delta, and vessel dimensions.
- **Dark Vessel & Anomaly Intelligence**: Flagging SAR-observed vessels lacking AIS matches (`Unmatched Vessel`), detecting AIS transmission gaps, loitering, route deviations, and abnormal speed drops during release windows.

### Release Reconstruction Layer (Person 1 / Member 4 & Person 3 / Member 5)
- **Mechanism**: Member 5 (Person 3) performs backward drift modeling using PyGNOME with historical wind and ocean current data. Member 4 (Person 1) combines backward drift outputs with wind/current history to compute estimated release region polygon ($\text{km}^2$ uncertainty area) and estimated release time window $[t_{start}, t_{end}]$.

### Source Attribution Layer (Person 1 / Member 4)
- **Candidate Hypotheses**: $H_1 \dots H_n$ (Vessels), $H_{untracked}$ (SAR-detected dark vessel), $H_{non-vessel}$ (Offshore/natural source), $H_{unknown}$ (`UNKNOWN`).
- **Evidence Formula**:
  $$E(H) = w_s S_{spatial} + w_t S_{temporal} + w_r S_{trajectory} + w_d S_{drift} + w_v S_{vessel} + w_b S_{behavior} - w_c C_{contradiction}$$
- **Counterfactual Attribution**: Evaluates ranking stability by testing hypothesis distribution deltas when the top-ranked vessel is temporarily removed.
- **Unknown Engine**: Automatically outputs `UNKNOWN` status if no hypothesis crosses the validated evidence threshold.

### Forward Drift Intelligence (Person 3 / Member 5)
- **Framework**: Integrates NOAA's PyGNOME particle tracking engine.
- **Ensemble Simulation**: Runs multi-particle stochastic forcing to output forecast paths at $+6\text{h}, +12\text{h}, +24\text{h}, +48\text{h}$ with probability density uncertainty cones.

### Environmental Threat & Response Priority Engine (Person 3 / Member 5 & Member 6 Backend)
- **Spatial GIS Intersection**: Intersects forecast drift geometry with sensitive layers (mangroves, MPAs, fisheries, ports, coastlines).
- **Response Priority Score ($0-100$)**:
  $$\text{Priority} = \text{Severity} \times \text{Sensitivity} \times \text{Impact Probability} \times \text{Time Urgency} \times \text{Evidence Quality}$$
- **Alert Levels**: `LOW` (Monitor), `MEDIUM` (Increase Observation), `HIGH` (Prepare Response), `CRITICAL` (Immediate Escalation & Containment).

### Decision Support Features
- **Next-Best Observation Recommender (Person 3 / Member 6)**: Calculates geographic bounding box where subsequent satellite pass provides maximum info value.
- **What-If Simulator (Person 3 / Member 5)**: Allows planners to alter wind speed/direction or current vectors to assess impact sensitivity.
- **Historical Incident Time Machine (Person 3 / Member 5)**: Replays historical incidents using strict temporal slicing ($t \le t_{obs}$) to benchmark end-to-end pipeline accuracy against documented outcomes.
- **Active Learning Loop (Person 1 / Member 2 & Person 3 / Member 6)**: Analyst-confirmed tags (oil, look-alike, false alarm) enter a controlled training repository for offline retraining.
- **Incident Report Generator (Person 3 / Member 6)**: One-click deterministic PDF/JSON report generation.
- **WebGIS Command Center UI & Low-Bandwidth Field Mode (Person 4 / Member 6 Frontend)**: Responsive MapLibre GL command interface, temporal playback, split view, analyst review controls, and low-bandwidth coastal field mode.

---

## 5. Technology Stack & Rationale

| Component | Selected Technology | Engineering Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Primary ecosystem for scientific computing, geospatial processing, and deep learning. |
| **Deep Learning** | PyTorch / Torchvision | Flexible framework for oil segmentation (U-Net) and look-alike classification. |
| **SAR Processing** | ESA SNAP / GDAL / Rasterio | Standard geospatial raster tools for orbit correction, radiometric calibration, and GeoTIFF processing. |
| **Vector GIS** | GeoPandas / Shapely / PyProj | High-performance vector spatial operations, polygon geometry intersections, and CRS conversions. |
| **Database** | PostgreSQL 15+ + PostGIS 3+ | Industrial spatial database for indexing vessel tracks, spill geometries, and environmental layers (`EPSG:4326`). |
| **Backend API** | FastAPI | High-performance async REST framework with automatic OpenAPI documentation and Pydantic validation. |
| **Drift Modeling** | PyGNOME | Established, scientifically validated NOAA oil trajectory particle modeling engine. |
| **Frontend UI** | React + MapLibre GL / Leaflet | Responsive WebGIS interactive command center rendering vector tiles, rasters, and vessel tracks. |
| **Task Queue** | Redis + Celery | Asynchronous background processing for heavy SAR processing and PyGNOME ensemble jobs. |
| **Data Ingestion** | Copernicus CDS / Global Fishing Watch | Satellite granule acquisition and AIS vessel track ingestion APIs. |

---

## 6. Explicit Non-Claims & Responsible-AI Constraints

To maintain scientific credibility and prevent automation bias, MarineShield explicitly enforces:

1. **No Real-Time Streaming Claims**: The system processes newly available satellite passes as granules arrive; it does NOT claim continuous real-time global streaming.
2. **No Legal Guilt Declarations**: Output scores represent evidence compatibility rankings ($0.0 - 1.0$), NOT legal proof of criminal liability or MARPOL violations.
3. **No Volumetric Petroleum Claims**: Output provides coarse severity classes (`SHEEN`, `MODERATE`, `THICK`), NOT exact volumetric oil quantities.
4. **No Deterministic Trajectories**: Forecasts present ensemble probability cones, NOT single deterministic paths.
5. **No Synthetic Percentages**: Confidence metrics derive strictly from empirical model probabilities or calibrated evidence weights; arbitrary numbers are prohibited.
6. **No LLM Chatbots for Evidence**: LLMs MUST NOT serve as evidence authorities or score calculators; transparent deterministic algorithms are mandatory.

---
trigger: always_on
---

# MarineShield Architecture Rules

## 1. Modular Subsystem Design
MarineShield is structured into modular Python subsystems and a web-based decision support system:
- **Data Ingestion & Preprocessing (Person 2 / Member 1)**: Manages Sentinel-1 SAR acquisition, orbit correction, calibration, speckle filtering, dB conversion, and dataset preparation.
- **Detection & Verification (Person 1 / Member 2)**: Dual-stage ML pipeline comprising Spill Segmentation (U-Net / SegFormer baseline), Look-Alike Rejection (biogenic slicks, low wind, wakes), Spill Severity classification, and SAR Vessel Detection.
- **Maritime & Vessel Intelligence (Person 2 / Member 3)**: AIS track ingestion and deterministic AIS–SAR Reconciliation matching, dark-vessel flagging, and AIS anomaly analysis.
- **Release Reconstruction (Person 1 / Member 4 & Person 3 / Member 5)**: Combines backward drift simulations (Person 3 / Member 5) with wind/current history to compute estimated release region polygon and release time window $[t_{start}, t_{end}]$ (Person 1 / Member 4).
- **Source Attribution Engine (Person 1 / Member 4)**: Evidence + Contradiction Engine ranking candidate hypotheses ($H_1 \dots H_n$, $H_{untracked}$, $H_{non-vessel}$, $H_{unknown}$) with counterfactual robustness checks and explicit `UNKNOWN` classification.
- **Drift & Forecasting (Person 3 / Member 5)**: PyGNOME integration for forward trajectory ensemble simulations with uncertainty probability cones ($+6\text{h}, +12\text{h}, +24\text{h}, +48\text{h}$).
- **Threat & Response Intelligence (Person 3 / Member 5 & Member 6 Backend)**: Spatial intersection with sensitive GIS layers (mangroves, MPAs, fisheries, ports) computing MarineShield Response Priority ($0-100$) and automated alert escalation.
- **Decision Support & Replay (Person 3 & Person 4 / Member 6)**: WebGIS Command Center UI, Incident Report Generator, Historical Incident Time Machine, and Low-bandwidth Field Mode.

## 2. Strict Architectural Boundaries
- **No Direct Frontend-to-ML Coupling**: WebGIS frontend must exclusively communicate with backend services via versioned FastAPI REST endpoints.
- **Stateless Intelligence Services**: ML inference, drift simulations, and evidence calculation services must be stateless and consume explicit input parameters and database records.
- **Asynchronous Processing**: Heavy computations (SAR scene processing, PyGNOME drift ensembles) must run asynchronously via background job queues (Redis Queue / Celery) and communicate state updates via API status endpoints or WebSockets.
- **Data Provenance Enforcement**: Every output polygon, score, and forecast must carry metadata identifying source satellite granule ID, model version, execution timestamp, and data quality metrics.

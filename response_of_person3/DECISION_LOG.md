# MarineShield Decision Log, ADR Register & Source Audit

## 1. Architectural Decision Records (ADRs)

### ADR-001: Adoption of Multi-Stage Incident Pipeline over Single Classification Model
- **Status**: Accepted
- **Context**: Standard approaches build a single image classification model ("oil vs no oil"). This fails operational needs (source investigation, trajectory forecasting, threat priority).
- **Decision**: Adopt the 12-stage incident lifecycle pipeline integrating SAR preprocessing, U-Net segmentation, look-alike classification, AIS-SAR reconciliation, release reconstruction, evidence scoring, PyGNOME drift modeling, and threat intersection.
- **Consequences**: System provides full operational decision support and explainability, but requires modular engineering across 4 workstreams.

### ADR-002: Deterministic Geospatial Matching for AIS–SAR Reconciliation
- **Status**: Accepted
- **Context**: Reconciling SAR-detected vessels with AIS tracks could use complex ML matching or deterministic spatial-temporal heuristics.
- **Decision**: Implement a deterministic spatio-temporal matching algorithm using distance, time offset, heading delta, speed delta, and vessel dimensions.
- **Consequences**: Highly explainable, transparent, fast, and scientifically defensible without black-box matching risks.

### ADR-003: PyGNOME Integration for Drift Modeling
- **Status**: Accepted
- **Context**: Re-implementing ocean physics equations from scratch during development is prone to error and lacks scientific validation.
- **Decision**: Integrate NOAA's PyGNOME particle tracking engine for forward and backward drift simulations.
- **Consequences**: Leverages mature NOAA oceanographic modeling; requires C++ compiler dependencies and Python bindings during deployment setup.

### ADR-004: Evidence + Contradiction Engine with Explicit `UNKNOWN` Output
- **Status**: Accepted
- **Context**: Forced vessel attribution leads to false accusations when AIS coverage is incomplete or multiple candidates exist.
- **Decision**: Score candidate hypotheses ($H_1 \dots H_n$) using supporting evidence minus contradictory indicators, supporting counterfactual robustness checks and an explicit `UNKNOWN` source status.
- **Consequences**: Eliminates false attribution bias; ensures system abstains when evidence quality is insufficient.

---

## 2. Contradictions Identified Across Source Documents

### Contradiction 1: Team Division Mapping (6 Functional Members vs 4 Engineering Persons)
- **Source Documents**: `master-plan.md` Section 20 defines a 6-member team structure (M1-M6), whereas the project engineering structure is assigned to 4 Persons (Person 1 to Person 4).
- **Recorded Impact**: Potential confusion regarding module ownership and API contracts.
- **Resolution**: Map the 6 functional roles directly into 4 engineering workstreams as documented in [`WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md):
  - **Person 1**: Member 2 (ML / Segmentation / Look-alike / SAR Vessel Detection) + Member 4 (Release Region Estimation / Evidence Engine / Attribution).
  - **Person 2**: Member 1 (Sentinel-1 SAR Prep) + Member 3 (AIS Tracking / PostGIS / AIS-SAR Reconciliation / AIS Anomalies).
  - **Person 3**: Member 5 (GNOME Drift / Threat Analysis / Replay) + Backend half of Member 6 (FastAPI / Response Priority Engine / Reports).
  - **Person 4**: Frontend half of Member 6 (React / WebGIS Command Center UI / Analyst Review / Field Mode).

### Contradiction 2: Segmentation Architecture Selection (Single Baseline vs Multiple Models)
- **Source Documents**: `master-plan.md` Section 3 recommends freezing one primary architecture (U-Net) and one benchmark alternative (SegFormer), while `feature-inventory.md` Section 6 lists U-Net, DeepLabV3+, and SegFormer.
- **Recorded Impact**: Risk of over-engineering multiple ML pipelines simultaneously.
- **Resolution**: Freeze U-Net as the default primary baseline for initial integration, and maintain SegFormer as the single benchmark candidate evaluated during model validation.

### Contradiction 3: AIS Data Provider Strategy & Indian Coastal Coverage
- **Source Documents**: `master-plan.md` Section 18 notes Global Fishing Watch AIS coverage may be incomplete in Indian coastal scenarios, whereas `marine-shield-theory.md` Section 8 treats GFW as primary.
- **Recorded Impact**: Potential data blackout or incomplete vessel trajectory tracking in regional waters.
- **Resolution**: Architect a pluggable AIS provider ingestion interface (`AISProviderAdapter`) supporting Global Fishing Watch, INCOIS oceanographic products, and DG Shipping AIS feeds.

### Contradiction 4: Economic Damage Assessment Scope (Monetary vs Qualitative Exposure)
- **Source Documents**: `master-plan.md` Section 8 explicitly warns against inventing precise monetary damage figures, while `feature-inventory.md` Section 41 lists environmental sensitivity scoring.
- **Recorded Impact**: Risk of producing unverified monetary financial claims.
- **Resolution**: Limit impact metrics to qualitative threat levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), affected geographic area ($\text{km}^2$), and time-to-impact (ETA hours), strictly avoiding synthetic monetary figures.

### Contradiction 5: Real-Time vs Event-Driven Granule Processing
- **Source Documents**: `master-plan.md` Section 22 explicitly non-claims continuous global real-time monitoring and specifies processing newly available satellite passes as scenes arrive.
- **Recorded Impact**: Potential misinterpretation of backend processing speed requirements.
- **Resolution**: Architecture uses event-driven job queues (Celery/Redis) triggered upon satellite granule availability, not polling or claiming instant real-time global streaming.

---

## 3. Correction of Person 1 / Member 2 / Member 4 Ownership Misalignment

During initial documentation drafting, an incorrect assumption misallocated **SAR Vessel Detection (Module E)** to Person 2 / Member 3. 

### Audit & Correction Summary:
- **Member 2 Ownership (Person 1)**: Corrected to include:
  1. Oil-Spill Segmentation (Module B)
  2. Look-Alike Rejection Classifier (Module C)
  3. Spill Severity & Thickness Classifier (Module D)
  4. **SAR Vessel Detection (Module E)** — Direct ship detection from SAR imagery.
  5. Multi-slick tracking and spill geometry analytics.
- **Member 3 Ownership (Person 2)**: Corrected to include:
  1. AIS Track Ingestion & PostGIS Trajectory Processing
  2. **AIS–SAR Reconciliation Engine (Module F)** — Consumes SAR vessel detections from Member 2 and matches with AIS tracks.
  3. Dark Vessel Flagging & AIS Anomaly Intelligence (Module G).
- **Member 4 Ownership (Person 1)**: Re-confirmed to include:
  1. Release Time & Location Estimation (Layer 5) — Uses backward drift inputs from Member 5 (Person 3) to compute release region polygon and time window $[t_{start}, t_{end}]$.
  2. Candidate Hypothesis Generation ($H_1 \dots H_n$, $H_{untracked}$, $H_{non-vessel}$, $H_{unknown}$).
  3. Evidence + Contradiction Engine (Module F).
  4. Counterfactual Attribution & Unknown Engine.

---

## 4. Invented Architecture Decisions Audit & Resolutions

The following architectural items were identified as **invented rather than supported by the source material**, and have been audited and corrected:

1. **Invented Arbitrary Numerical Thresholds in Definition of Done**:
   - *Audit*: Previous documentation drafts introduced arbitrary percentage numbers (e.g., IoU $\ge 0.70$, F1 $\ge 0.75$, FPR $\le 0.05$, trajectory error $\le 5.0\text{ km}$, API response $< 300\text{ms}$).
   - *Source Alignment*: `master-plan.md` Section 14 and `feature-inventory.md` Sections 50-53 define the *evaluation metrics* (IoU, F1, Precision, Recall, mAP, Top-1, Top-3, MRR, trajectory error), but do *not* specify fixed numeric targets.
   - *Correction*: `DEFINITION_OF_DONE.md` was updated to frame quality gates around empirical validation against historical incident ground truth datasets, removing invented arbitrary numbers.
2. **Legacy Template Rules in `coding_guidelines.md`**:
   - *Audit*: Pre-existing `.agents/rules/coding_guidelines.md` template referenced `supabase`, `shadcn/ui`, `Tailwind CSS v4`, `pnpm`, and `testsprite`.
   - *Source Alignment*: Source docs (`master-plan.md` Section 19) mandate standard PostgreSQL + PostGIS, FastAPI, React, and MapLibre GL.
   - *Correction*: Preserved `coding_guidelines.md` per strict directive, but explicitly added MarineShield architecture overrides in Section 5 and `.agents/rules/agent_core.md`.

---

## 5. Decisions Requiring Explicit Human Review & Approval

| # | Decision Item | Context & Trade-off | Recommended Option | Human Status |
| :-: | :--- | :--- | :--- | :-: |
| **D-1** | **Primary Segmentation Baseline** | U-Net (fast inference, low resource requirement) vs SegFormer (transformer-based, higher GPU memory). | **U-Net** as primary baseline; **SegFormer** as benchmark candidate. | **PENDING REVIEW** |
| **D-2** | **PyGNOME Deployment Environment** | PyGNOME requires C++ compilation and NetCDF bindings. Can be deployed via Docker container or standard conda env. | Containerized **Docker service** isolated from FastAPI backend. | **PENDING REVIEW** |
| **D-3** | **Evidence Weight Calibration** | Weight vector $(w_s, w_t, w_r, w_d, w_v, w_b, w_c)$ can be fixed heuristically or calibrated on historical incident benchmarks. | Initial **heuristic weights** calibrated via Historical Incident Time Machine. | **PENDING REVIEW** |
| **D-4** | **Pluggable AIS Provider Order** | Default fallback priority for AIS ingestion feeds. | **1. Global Fishing Watch API**, **2. INCOIS data**, **3. Synthetic / Local AIS**. | **PENDING REVIEW** |

# MarineShield Definition of Done & Quality Gate Specification

## 1. General Repository Definition of Done (DoD)

Before any feature, code module, or pull request is considered **DONE** and ready for merge into `main`, it MUST satisfy:

1. **No Code Implementation in Architectural Tasks**: Verification that architectural rules were respected and no product code was written.
2. **Rule & Guideline Adherence**: Code complies with `.agents/rules/agent_core.md`, `.agents/rules/architecture.md`, and `.agents/rules/coding_guidelines.md`.
3. **Workstream Scope Compliance**: Code modifications fall strictly within the assigned workstream ownership in [`WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md).
4. **Clean Code & Linting**: Zero diagnostic errors, lint warnings, or type errors (Pyright/Mypy for Python, ESLint/TypeScript for React).
5. **Unit & Integration Test Coverage**: Automated test suites pass 100% with no suppressed failures or masked errors.
6. **Documentation & API Contracts**: Any new API endpoint or data model update is documented in `docs/api/` and `docs/architecture/ARCHITECTURE.md`.
7. **Database Migrations**: Schema mutations include versioned migration scripts and PostGIS spatial index definitions (`EPSG:4326`).
8. **No Secrets / Credentials**: Clean audit confirming zero hardcoded credentials or API keys.

---

## 2. Subsystem Evaluation Criteria (Source Material Metrics)

As specified in `master-plan.md` Section 14 and `feature-inventory.md` Sections 50-53, subsystems MUST be evaluated against ground-truth datasets using the following mandatory scientific metrics:

### A. SAR Oil-Spill Segmentation (Person 1 / Member 2)
- **Intersection over Union (IoU)**
- **Dice / F1 Score**
- **Precision & Recall**
- **False Positive Rate (FPR)** on hard-negative look-alike test scenes (biogenic slicks, low wind, ship wakes)
- **Inference Latency**

### B. SAR Vessel Detection & AIS–SAR Reconciliation (Person 2 / Member 1 & Member 3)
- **SAR Vessel Detection Precision & Recall** (Person 1 / Member 2)
- **Mean Average Precision (mAP)** (Person 1 / Member 2)
- **AIS–SAR Match Precision & Recall** (Person 2 / Member 3) on benchmark vessel pairs within spatial-temporal buffer

### C. Source Attribution & Evidence Engine (Person 1 / Member 4)
- **Top-1 Attribution Accuracy** on verified historical incident ground-truth dataset
- **Top-3 Attribution Accuracy**
- **Mean Reciprocal Rank (MRR)**
- **Abstention / Unknown Reliability**: Verification that ambiguous scenarios properly return `UNKNOWN` status without forced false attribution

### D. PyGNOME Forward Drift & Threat Forecasting (Person 3 / Member 5)
- **Spatial Trajectory Displacement Error** compared to observed historical slick trajectories
- **Ensemble Coverage**: Percentage of observed slick centroids falling within computed forecast uncertainty probability cones
- **Threat Impact ETA Error**: Arrival time estimation error at sensitive coastal GIS zones

### E. System Performance & Latency (Person 3 & Person 4 / Member 6)
- **Full SAR Scene Pipeline Latency**: Measured processing duration from satellite granule ingestion to spill polygon output
- **API Response Latency**: Measured response duration for GIS query endpoints
- **WebGIS Interface Responsiveness**: Smooth rendering rate during map pan/zoom operations on command center UI

---

## 3. Historical Incident Time Machine Validation (No-Hindsight Check)

Evaluation suites for historical incident replay MUST verify:
- **Strict Temporal Slicing**: Pipeline execution at timestamp $T$ receives ONLY data records with $t \le T$.
- **Zero Information Leakage**: Neither future AIS points ($t > T$) nor future weather forecasts are accessed during incident reconstruction.
- **Documented Outcome Alignment**: Performance metrics (segmentation IoU, vessel detection mAP, attribution rank, forecast spatial error) are benchmarked against verified post-incident reports.

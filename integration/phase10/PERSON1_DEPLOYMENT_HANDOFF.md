# MarineShield Phase 10 — Person 1 Deployment Handoff Document

**Handoff Date (UTC):** 2026-08-22T01:34:00Z  
**From:** Person 1 (Member 2 Oil Intelligence & Member 4 Source Investigation)  
**To:** Person 3 (Backend / Scientific Deployment) & Person 4 (Frontend / WebGIS Command Center UI)  
**Handoff Status:** **`PERSON 1 MODEL/PACKAGING HANDOFF READY`**  

---

## 1. Section A: Handoff to Person 3 (Backend & Scientific Deployment)

### 1.1 Service Entry Points & Module Paths
- **Oil Intelligence Service Entry Point:** `marineshield.oil_intelligence.service.OilIntelligenceService`
  - Method: `process_tile(input_source: Any, metadata: Optional[Dict[str, Any]]) -> SpillDetectionResponse`
- **Release Reconstruction & Investigation Engine:** `marineshield.investigation.engine.SourceInvestigationEngine`
  - Method: `run_investigation(spill_centroid: Tuple[float, float], t_observation_utc: str, environmental_history: Any, vessel_observations: List[VesselObservation]) -> InvestigationResult`
- **Counterfactual Attribution Engine:** `marineshield.investigation.counterfactual.CounterfactualAttributionEngine`
  - Method: `evaluate_counterfactual(...) -> CounterfactualResult`

### 1.2 Required Non-Secret Environment Variables
| Environment Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `DEVICE_TYPE` | `cuda` (if available, else `cpu`) | PyTorch inference device target |
| `MIN_DQI_THRESHOLD` | `0.35` | Minimum Data Quality Index required for execution |
| `MODEL_VERSION_ID` | `sam-vit-b-sar-adapter-v1.0.0` | Official model version string |
| `DATASET_VERSION_ID` | `DARTIS-2019-v1.0` | Training dataset reference string |
| `BASE_SAM_CHECKPOINT_PATH` | `models/checkpoints/sam_vit_b_01ec64.pth` | Path to base SAM ViT-B weights |
| `SAR_ADAPTER_CHECKPOINT_PATH` | `models/adapted/sar_sam_adapter_best.pth` | Path to adapted SAR SAM weights |

### 1.3 Resource, Health-Check & Error Requirements
- **Resource Requirements:** NVIDIA GPU (Compute 7.5+), 3.5 GB peak VRAM, 8 GB System RAM.
- **Health-Check Procedure:** Verify existence of `models/checkpoints/sam_vit_b_01ec64.pth` and `models/adapted/sar_sam_adapter_best.pth`.
- **Error & Abstention Behavior:** Low DQI ($<0.35$) returns status `ABSTAINED` with explicit `AbstentionDetails` object.

---

## 2. Section B: Handoff to Person 4 (Frontend / WebGIS Command Center UI)

### 2.1 Available API Response Fields for WebGIS Display
1. **Oil Detection Layers:** `incident_id`, `tile_id`, `sar_granule_id`, `status` (`OIL_DETECTED | LOOKALIKE_REJECTED`), `lookalike_verification` class probabilities (`LOW_WIND_AREA`, `BIOGENIC_SLICK`, `PETROLEUM_OIL`), Shannon entropy, margin, `spill_geometry` GeoJSON in `EPSG:4326` `[lon, lat]`, `severity` tier (`MINOR`, `MODERATE`, etc.), `data_quality_index`, and `provenance` block.
2. **Attribution & Evidence Drawer:** `incident_id`, `mode`, `attribution_status` (`ATTRIBUTED_CANDIDATES_EVALUATED`, `SOURCE_UNKNOWN`), `evaluated_candidates` with component scores ($0-100$), `supporting_evidence`, `contradictory_evidence`, and mandatory non-guilt clause.
3. **Counterfactual Sensitivity Panel:** `status` (`SUCCESS`, `NOT_APPLICABLE`), `removed_candidate_id`, `is_top_hypothesis_dominant`, before/after position shift table (`rank_changes`).

### 2.2 Fields That MUST NOT Be Exposed to Frontend
- Raw PyTorch model weight tensors, internal CUDA memory pointers, or uncalibrated float matrices.

### 2.3 Frontend Integration Boundaries
- Person 4's frontend operates as a visual decision-support interface. All geometry calculations, drift modeling, and scoring remain strictly on Person 1/Person 3 backend services.

---

## 3. Final Handoff Status

**PERSON 1 MODEL/PACKAGING HANDOFF READY**

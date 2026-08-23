# Person 1 Backend Service Integration Handoff

**Target Subsystem:** Person 1 Core Intelligence Modules  
**Receiving Workstream:** Person 3 FastAPI Backend Integration  
**Handoff Date:** 2026-08-23 (UTC)  
**Status:** READY FOR PERSON 3 TO WIRE FASTAPI HANDLERS

---

## 1. Executive Summary

This handoff document provides Person 3 with the exact Python module paths, class constructors, method signatures, deterministic test commands, and input-to-output mappings required to replace the HTTP 501 placeholders in the FastAPI gateway:

- `POST /api/v1/oil-intelligence/detect`
- `POST /api/v1/investigation/reconstruct`
- `POST /api/v1/investigation/counterfactual`

---

## 2. Route A Integration: `POST /api/v1/oil-intelligence/detect`

### Service Entry Point Summary:
- **Module Path:** [`marineshield/oil_intelligence/service.py`](file:///D:/MarineShield/MarineShield/marineshield/oil_intelligence/service.py#L24)
- **Class Name:** `OilIntelligenceService`
- **Method Name:** `process_tile`
- **Complete Method Signature:**
  ```python
  def process_tile(
      self,
      input_source: Union[str, Path, np.ndarray, torch.Tensor],
      metadata: Optional[Dict[str, Any]] = None
  ) -> SpillDetectionResponse:
  ```
- **Execution Mode:** Synchronous (PyTorch CPU / CUDA inference)
- **Returned Object:** `SpillDetectionResponse` (conforms to `docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`)
- **Exceptions Raised:** `FileNotFoundError` (missing checkpoint), `ValueError` (disallowed checkpoint path)

### Input-to-Output Mapping:
```
HTTP Request Body (JSON)
  ├── sar_granule_id ----> metadata["sar_granule_id"]
  ├── tile_id -----------> metadata["tile_id"]
  ├── incident_id -------> metadata["incident_id"]
  ├── tile_bounds -------> metadata["tile_bounds"]
  ├── data_quality ------> metadata["data_quality"]
  └── prompts -----------> metadata["prompts"]
                               │
                               ▼
                OilIntelligenceService.process_tile()
                               │
                               ▼
                 SpillDetectionResponse (JSON)
```

### Deterministic Test Command & Fixtures:
- **Command:** `python scripts/run_phase6_oil_demonstration.py`
- **Fixture File:** `data/fixtures/phase6/` or `response_of_person2_member1/` SAR tiles
- **Output Artifact:** `integration/phase6/oil_intelligence/spill_detection_run1.json`

---

## 3. Route B Integration: `POST /api/v1/investigation/reconstruct`

### Service Entry Point Summary:
- **Module Path:** [`marineshield/investigation/engine.py`](file:///D:/MarineShield/MarineShield/marineshield/investigation/engine.py#L17)
- **Class Name:** `SourceInvestigationEngine`
- **Method Name:** `run_investigation`
- **Complete Method Signature:**
  ```python
  def run_investigation(
      self,
      spill_centroid: Tuple[float, float],
      t_observation_utc: str,
      environmental_history: Union[EnvironmentalHistory, Dict[str, Any]],
      vessel_observations: Optional[List[Union[VesselObservation, Dict[str, Any]]]] = None,
      ais_coverage_percentage: float = 100.0,
      data_quality_index: float = 0.90,
      incident_id: Optional[str] = None,
      spill_geometry_id: Optional[str] = None,
      scenario_id: str = "SCENARIO-LIVE"
  ) -> InvestigationResult:
  ```
- **Execution Mode:** Synchronous (Deterministic Lagrangian backward drift + evidence matrix calculation)
- **Returned Object:** `InvestigationResult` (conforms to `docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`)

### Input-to-Output Mapping:
```
HTTP Request Body (JSON)
  ├── spill_centroid -----------> spill_centroid
  ├── t_observation_utc --------> t_observation_utc
  ├── environmental_history ----> environmental_history
  ├── vessel_observations ------> vessel_observations
  ├── ais_coverage_percentage -> ais_coverage_percentage
  └── data_quality_index -------> data_quality_index
                                       │
                                       ▼
                    SourceInvestigationEngine.run_investigation()
                                       │
                                       ▼
                          InvestigationResult (JSON)
```

### Deterministic Test Command & Fixtures:
- **Command:** `python scripts/run_phase6_controlled_investigation.py`
- **Fixture File:** `tests/fixtures/investigation/01_single_dominant_candidate.json`
- **Output Artifact:** `integration/phase6/member4/controlled_investigation/CONTROLLED_INVESTIGATION_RESULT.json`

---

## 4. Route C Integration: `POST /api/v1/investigation/counterfactual`

### Service Entry Point Summary:
- **Module Path:** [`marineshield/investigation/counterfactual.py`](file:///D:/MarineShield/MarineShield/marineshield/investigation/counterfactual.py#L70)
- **Class Name:** `CounterfactualAttributionEngine`
- **Method Name:** `evaluate_counterfactual`
- **Complete Method Signature:**
  ```python
  def evaluate_counterfactual(
      self,
      incident_id: str,
      spill_geometry_geojson: Dict[str, Any],
      spill_timestamp_utc: str,
      vessel_observations: List[VesselObservation],
      env_history: Optional[Union[EnvironmentalHistory, Dict[str, Any]]] = None,
      replay_timestamp_utc: Optional[str] = None,
      frozen_view: Optional[FrozenReplayView] = None
  ) -> CounterfactualResult:
  ```
- **Execution Mode:** Synchronous (Deterministic top-candidate removal & sensitivity analysis)
- **Returned Object:** `CounterfactualResult` (conforms to `docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`)

### Input-to-Output Mapping:
```
HTTP Request Body (JSON)
  ├── incident_id -------------> incident_id
  ├── spill_geometry_geojson --> spill_geometry_geojson
  ├── spill_timestamp_utc -----> spill_timestamp_utc
  ├── vessel_observations ------> vessel_observations
  └── env_history --------------> env_history
                                       │
                                       ▼
              CounterfactualAttributionEngine.evaluate_counterfactual()
                                       │
                                       ▼
                         CounterfactualResult (JSON)
```

### Deterministic Test Command & Fixtures:
- **Command:** `python scripts/run_phase8_counterfactual_tests.py`
- **Output Artifact:** `integration/phase8/counterfactual_attribution/COUNTERFACTUAL_RESULTS.json`

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from marineshield.investigation.engine import SourceInvestigationEngine
from marineshield.investigation.counterfactual import CounterfactualAttributionEngine
from marineshield.investigation.schemas import VesselObservation, EnvironmentalHistory

router = APIRouter()

# --- Pydantic Request Schemas ---

class OilDetectRequest(BaseModel):
    sar_granule_id: str
    tile_id: Optional[str] = None
    incident_id: Optional[str] = None
    tile_bounds: Optional[Tuple[float, float, float, float]] = None
    data_quality: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None

class InvestigationReconstructRequest(BaseModel):
    spill_centroid: Tuple[float, float]
    t_observation_utc: str
    environmental_history: Dict[str, Any]
    vessel_observations: Optional[List[Dict[str, Any]]] = []
    ais_coverage_percentage: float = 100.0
    data_quality_index: float = 0.90
    incident_id: Optional[str] = None
    spill_geometry_id: Optional[str] = None
    scenario_id: str = "SCENARIO-LIVE"

class CounterfactualRequest(BaseModel):
    incident_id: str
    spill_geometry_geojson: Dict[str, Any]
    spill_timestamp_utc: str
    vessel_observations: List[Dict[str, Any]]
    env_history: Optional[Dict[str, Any]] = None
    replay_timestamp_utc: Optional[str] = None


# --- Prototype Endpoint Implementation ---

@router.post("/v1/oil-intelligence/detect")
def detect_oil_intelligence(request: OilDetectRequest):
    """Temporary prototype endpoint for Oil Intelligence detection.
    
    Uses deterministic Phase 6 synthetic development fixture for full contract fidelity
    when live PyTorch/SAM model weight checkpoints are absent in lightweight environment.
    """
    fixture_path = Path("integration/phase6/oil_intelligence/spill_detection_run1.json")
    if not fixture_path.exists():
        raise HTTPException(status_code=500, detail=f"Phase 6 oil intelligence fixture missing at {fixture_path}")
    
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Update request-specific metadata if provided
    if request.incident_id:
        data["incident_id"] = request.incident_id
    if request.sar_granule_id:
        data["sar_granule_id"] = request.sar_granule_id
    if request.tile_id:
        data["tile_id"] = request.tile_id
        
    return data


@router.post("/v1/investigation/reconstruct")
def reconstruct_investigation(request: InvestigationReconstructRequest):
    """Temporary prototype endpoint for Investigation Reconstruction.
    
    Executes Person 1's SourceInvestigationEngine callable in deterministic mode.
    """
    try:
        engine = SourceInvestigationEngine()
        
        # Convert vessel telemetry dicts to VesselObservation instances
        vessel_objs = [VesselObservation(**v) for v in (request.vessel_observations or [])]
        
        result = engine.run_investigation(
            spill_centroid=request.spill_centroid,
            t_observation_utc=request.t_observation_utc,
            environmental_history=request.environmental_history,
            vessel_observations=vessel_objs,
            ais_coverage_percentage=request.ais_coverage_percentage,
            data_quality_index=request.data_quality_index,
            incident_id=request.incident_id,
            spill_geometry_id=request.spill_geometry_id,
            scenario_id=request.scenario_id
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Investigation reconstruction error: {str(e)}")


@router.post("/v1/investigation/counterfactual")
def counterfactual_attribution(request: CounterfactualRequest):
    """Temporary prototype endpoint for Counterfactual Attribution.
    
    Executes Person 1's CounterfactualAttributionEngine callable in deterministic mode.
    """
    try:
        cf_engine = CounterfactualAttributionEngine()
        
        # Convert vessel telemetry dicts to VesselObservation instances
        vessel_objs = [VesselObservation(**v) for v in request.vessel_observations]
        
        result = cf_engine.evaluate_counterfactual(
            incident_id=request.incident_id,
            spill_geometry_geojson=request.spill_geometry_geojson,
            spill_timestamp_utc=request.spill_timestamp_utc,
            vessel_observations=vessel_objs,
            env_history=request.env_history,
            replay_timestamp_utc=request.replay_timestamp_utc
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Counterfactual evaluation error: {str(e)}")


# --- Preserved Person 3 Forecast Prototype Endpoint ---

from backend.api.forecast import ForecastCreateRequest, ForecastResponse
from backend.domain.forecast import Forecast, Provenance, UncertaintyRegion, GeoPolygon
from backend.api.mapper import map_investigation_result_to_release

class SyntheticForecastResponse(ForecastResponse):
    warnings: List[str] = []
    limitations: List[str] = []
    is_unknown_state: bool = False

@router.post("/forecast", response_model=SyntheticForecastResponse)
def create_synthetic_forecast(request: ForecastCreateRequest):
    release = map_investigation_result_to_release("integration/phase6/member4/controlled_investigation/CONTROLLED_INVESTIGATION_RESULT.json")

    prov = Provenance(
        model_version="synthetic-dev-1.0",
        configuration_version="bounded-contract",
        library_versions={"pygnome": "synthetic-mock"},
        dataset_versions={"data_mode": "SYNTHETIC_DEVELOPMENT_FIXTURE"}
    )

    if request.horizon_hours > 48:
        return SyntheticForecastResponse(
            forecast=Forecast(
                id="synth-fcst-000",
                status="failed",
                failure_reason="Unknown state triggered: Horizon exceeds synthetic maximum",
                horizon_hours=48,
                release=release,
                provenance=prov,
                created_at=datetime.now(timezone.utc)
            ),
            warnings=["Horizon too far for synthetic mock"],
            limitations=["Synthetic environment only allows up to 48 hours"],
            is_unknown_state=True
        )

    polygon = GeoPolygon(coordinates=[[
        [73.1, 18.4], [73.3, 18.4], [73.3, 18.6], [73.1, 18.6], [73.1, 18.4]
    ]])
    
    uncertainty = UncertaintyRegion(
        horizon_hours=request.horizon_hours,
        geometry=polygon,
        confidence_level=0.95,
        semantics="Synthetic 95% confidence bounds"
    )

    forecast = Forecast(
        id="synth-fcst-001",
        status="completed",
        horizon_hours=request.horizon_hours,
        release=release,
        scenario=request.scenario,
        provenance=prov,
        uncertainty_regions=[uncertainty],
        created_at=datetime.now(timezone.utc)
    )
    
    return SyntheticForecastResponse(
        forecast=forecast,
        warnings=["This is a synthetic mock response, not a real forecast"],
        limitations=["No real hydrodynamic processing occurred", "SYNTHETIC_DEVELOPMENT_FIXTURE"],
        is_unknown_state=False
    )

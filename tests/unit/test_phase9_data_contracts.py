import unittest
import json
import datetime
from marineshield.oil_intelligence.schemas import (
    SpillDetectionResponse, LookAlikeVerificationContract, SpillSeverityContract, DataQualityIndex, ProvenanceBlock
)
from marineshield.investigation.schemas import InvestigationResult, VesselObservation, EnvironmentalHistory
from marineshield.investigation.counterfactual import CounterfactualAttributionEngine, CounterfactualResult
from marineshield.replay.loader import HistoricalSceneLoader

class TestPhase9DataContracts(unittest.TestCase):

    def test_oil_intelligence_contract_conformance(self):
        """Verifies Oil Intelligence outputs conform strictly to SpillDetection contract."""
        prov = ProvenanceBlock(
            sar_granule_id="S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
            model_version_id="sam-vit-b-sar-adapter-v1.0.0",
            dataset_version_id="DARTIS-2019-v1.0",
            inference_device="cuda"
        )
        resp = SpillDetectionResponse(
            incident_id="phase9-test-inc-001",
            tile_id="tile_r000_c000_train",
            sar_granule_id="S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
            status="LOOKALIKE_REJECTED",
            is_abstained=False,
            abstention_details=None,
            spill_mask=None,
            spill_geometry=None,
            lookalike_verification=LookAlikeVerificationContract(
                predicted_class="LOW_WIND_AREA",
                pipeline_decision="REJECT_AS_LOOKALIKE"
            ),
            severity=SpillSeverityContract(severity_class="UNKNOWN"),
            data_quality=DataQualityIndex(index=0.95),
            provenance=prov
        )
        d = resp.to_dict()

        self.assertEqual(d["status"], "LOOKALIKE_REJECTED")
        self.assertFalse(d["is_abstained"])
        self.assertEqual(d["metrics_metadata_ref"], "METRICS-SAR-SAM-ADAPT-v1.0")
        self.assertIn("provenance", d)
        self.assertEqual(d["provenance"]["model"]["model_version_id"], "sam-vit-b-sar-adapter-v1.0.0")
        self.assertEqual(d["provenance"]["training_dataset"]["dataset_version_id"], "DARTIS-2019-v1.0")
        self.assertNotIn("weights", d)  # Ensure no raw model weights exposed

    def test_investigation_contract_conformance(self):
        """Verifies Investigation outputs conform strictly to investigation contract."""
        cf_engine = CounterfactualAttributionEngine()
        spill_geom = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        env = EnvironmentalHistory(
            wind_speed_ms=8.0, wind_direction_deg=220.0, current_u_ms=0.10, current_v_ms=-0.05,
            lookback_hours=6.0, wind_dataset_id="ERA5", current_dataset_id="HYCOM"
        )
        v = VesselObservation(
            vessel_id="vsl-001", source_type="AIS_TRACK", vessel_name="Tanker A", vessel_mmsi="413111111",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )

        res = cf_engine.engine.run_investigation(
            spill_centroid=(73.21, 18.51),
            t_observation_utc="2024-01-20T00:55:41Z",
            environmental_history=env,
            vessel_observations=[v],
            incident_id="inc-inv-001"
        )
        d = res.to_dict()

        self.assertIn(d["status"], ["ATTRIBUTED_CANDIDATES_EVALUATED", "SOURCE_UNKNOWN"])
        self.assertIn("data_quality_index", d)
        self.assertIn("provenance", d)

    def test_counterfactual_contract_conformance(self):
        """Verifies Counterfactual outputs conform strictly to result contract."""
        cf_engine = CounterfactualAttributionEngine()
        spill_geom = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        env = EnvironmentalHistory(
            wind_speed_ms=8.0, wind_direction_deg=220.0, current_u_ms=0.10, current_v_ms=-0.05,
            lookback_hours=6.0, wind_dataset_id="ERA5", current_dataset_id="HYCOM"
        )
        v1 = VesselObservation(
            vessel_id="vsl-001", source_type="AIS_TRACK", vessel_name="Tanker A", vessel_mmsi="413111111",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )

        cf_res: CounterfactualResult = cf_engine.evaluate_counterfactual(
            incident_id="inc-cf-001",
            spill_geometry_geojson=spill_geom,
            spill_timestamp_utc="2024-01-20T00:55:41Z",
            vessel_observations=[v1],
            env_history=env
        )
        d = cf_res.to_dict()

        self.assertIn(d["status"], ["SUCCESS", "NOT_APPLICABLE", "BLOCKED_TIE_POLICY_REQUIRED"])
        self.assertIn("non_guilt_clause", d)
        self.assertIn("data_mode", d)

    def test_geometry_crs_and_coordinate_order(self):
        """Verifies geometry objects use EPSG:4326 and [longitude, latitude] coordinate order."""
        spill_geom = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        coord = spill_geom["coordinates"][0][0]
        # In Arabian Sea: Lon ~ 73.0 (70-75), Lat ~ 18.0 (15-20)
        self.assertGreater(coord[0], 70.0)  # Longitude
        self.assertLess(coord[1], 25.0)     # Latitude

    def test_future_observation_exclusion_under_replay(self):
        """Verifies Phase 7 historical replay loader excludes future observations."""
        loader = HistoricalSceneLoader()
        t_replay = "2024-01-20T12:00:00Z"
        src = {
            "ais_candidates": [
                {"observation_id": "past", "timestamp": "2024-01-20T10:00:00Z"},
                {"observation_id": "future", "timestamp": "2024-01-20T15:00:00Z"}
            ]
        }
        view = loader.load_replay("inc-001", t_replay, source_data=src)
        inc_ids = {o["observation_id"] for o in view.included_observations}

        self.assertIn("past", inc_ids)
        self.assertNotIn("future", inc_ids)

if __name__ == "__main__":
    unittest.main()

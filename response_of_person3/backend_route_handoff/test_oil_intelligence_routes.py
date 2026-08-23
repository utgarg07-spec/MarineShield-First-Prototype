# backend/tests/test_oil_intelligence_routes.py

import unittest
from fastapi.testclient import TestClient
from response_of_person3.backend_route_handoff.main import app

class TestPerson1PrototypeRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_oil_intelligence_detect_route(self):
        """Verify POST /api/v1/oil-intelligence/detect returns canonical Person 1 detection response."""
        payload = {
            "sar_granule_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
            "tile_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train",
            "incident_id": "phase6-val-inc-20260821-001",
            "tile_bounds": [72.0, 18.0, 72.5, 18.5]
        }
        
        # Run 1
        res1 = self.client.post("/api/v1/oil-intelligence/detect", json=payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["incident_id"], "phase6-val-inc-20260821-001")
        self.assertIn(data1["status"], ["OIL_DETECTED", "LOOKALIKE_REJECTED", "UNCERTAIN_ANALYSIS", "ABSTAINED"])
        self.assertIn("lookalike_verification", data1)
        self.assertIn("severity", data1)

        # Run 2 (Repeatability Check)
        res2 = self.client.post("/api/v1/oil-intelligence/detect", json=payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data1, data2)

    def test_investigation_reconstruct_route(self):
        """Verify POST /api/v1/investigation/reconstruct executes Person 1 engine deterministically."""
        payload = {
            "spill_centroid": [73.2015, 18.5012],
            "t_observation_utc": "2024-01-20T00:55:41Z",
            "environmental_history": {
                "wind_speed_ms": 8.5,
                "wind_direction_deg": 225.0,
                "current_u_ms": 0.12,
                "current_v_ms": -0.08,
                "lookback_hours": 6.0,
                "wind_dataset_id": "ERA5-REANALYSIS-2024",
                "current_dataset_id": "HYCOM-GLOBAL-2024",
                "data_quality_index": 0.95
            },
            "vessel_observations": [
                {
                    "observation_id": "obs-001",
                    "vessel_mmsi": "413123456",
                    "vessel_name": "Cooperative Vessel MMSI-413123456",
                    "vessel_type": "CARGO",
                    "timestamp_utc": "2024-01-20T00:10:00Z",
                    "latitude": 18.4950,
                    "longitude": 73.1950,
                    "speed_knots": 12.5,
                    "heading_deg": 45.0
                }
            ],
            "incident_id": "MS-PHASE6-DEV-001"
        }

        # Run 1
        res1 = self.client.post("/api/v1/investigation/reconstruct", json=payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["incident_id"], "MS-PHASE6-DEV-001")
        self.assertIn(data1["status"], ["ATTRIBUTED_CANDIDATES_EVALUATED", "SOURCE_UNKNOWN", "ABSTAINED"])
        self.assertIn("release_hypothesis", data1)
        self.assertIn("non_guilt_clause", data1)

        # Run 2 (Repeatability Check)
        res2 = self.client.post("/api/v1/investigation/reconstruct", json=payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data1, data2)

    def test_counterfactual_attribution_route(self):
        """Verify POST /api/v1/investigation/counterfactual executes Person 1 sensitivity engine."""
        payload = {
            "incident_id": "inc-cf-test-01",
            "spill_geometry_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [73.18, 18.48],
                        [73.22, 18.48],
                        [73.22, 18.52],
                        [73.18, 18.52],
                        [73.18, 18.48]
                    ]
                ]
            },
            "spill_timestamp_utc": "2024-01-20T00:55:41Z",
            "vessel_observations": [
                {
                    "observation_id": "obs-001",
                    "vessel_mmsi": "413111111",
                    "vessel_name": "Primary Suspect MMSI-413111111",
                    "vessel_type": "TANKER",
                    "timestamp_utc": "2024-01-20T00:10:00Z",
                    "latitude": 18.4950,
                    "longitude": 73.1950
                },
                {
                    "observation_id": "obs-002",
                    "vessel_mmsi": "413222222",
                    "vessel_name": "Secondary Candidate MMSI-413222222",
                    "vessel_type": "CARGO",
                    "timestamp_utc": "2024-01-20T00:15:00Z",
                    "latitude": 18.5100,
                    "longitude": 73.2100
                }
            ]
        }

        # Run 1
        res1 = self.client.post("/api/v1/investigation/counterfactual", json=payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["incident_id"], "inc-cf-test-01")
        self.assertIn(data1["status"], ["SUCCESS", "NOT_APPLICABLE", "BLOCKED_TIE_POLICY_REQUIRED"])
        self.assertIn("rank_changes", data1)
        self.assertIn("non_guilt_clause", data1)

        # Run 2 (Repeatability Check)
        res2 = self.client.post("/api/v1/investigation/counterfactual", json=payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data1, data2)

    def test_invalid_missing_input_raises_422(self):
        """Verify that sending malformed or missing fields returns HTTP 422 Unprocessable Entity."""
        res = self.client.post("/api/v1/oil-intelligence/detect", json={})
        self.assertEqual(res.status_code, 422)

        res_inv = self.client.post("/api/v1/investigation/reconstruct", json={"incident_id": "bad-request"})
        self.assertEqual(res_inv.status_code, 422)

if __name__ == "__main__":
    unittest.main()

import json
import unittest
import numpy as np
from pathlib import Path
from marineshield.oil_intelligence import OilIntelligenceService

class TestOilIntelligenceIntegration(unittest.TestCase):
    """End-to-End Integration Test for OilIntelligenceService using known Sentinel-1 SAR scene tiles."""
    SAMPLE_IMAGE = Path("data/samples/oil/sample_oil_01_linear_slick.png")
    MANIFEST_PATH = Path("data/samples/samples_manifest.json")

    def test_full_pipeline_on_known_sar_tile(self):
        """Executes full pipeline and validates complete JSON serializability and schema conformance."""
        self.assertTrue(self.SAMPLE_IMAGE.exists(), f"Sample SAR image missing: {self.SAMPLE_IMAGE}")
        
        with open(self.MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        sample_meta = manifest["samples"][0]

        service = OilIntelligenceService()
        metadata = {
            "incident_id": "8f3b21c4-91a5-4e89-b762-d21f8a49c099",
            "sar_granule_id": sample_meta["parent_scene_id"],
            "tile_id": sample_meta["sample_id"],
            "tile_bounds": (73.120, 15.240, 73.620, 15.740),
            "prompts": sample_meta["prompts"],
            "data_quality": {
                "index": 0.94,
                "quality_flags": []
            }
        }

        response = service.process_tile(self.SAMPLE_IMAGE, metadata=metadata)
        
        # Validate output dict structure
        result_dict = response.to_dict()
        
        # Test JSON serializability
        serialized_json = json.dumps(result_dict, indent=2)
        self.assertIsInstance(serialized_json, str)
        self.assertGreater(len(serialized_json), 500)

        # Validate mandatory contract fields
        self.assertEqual(result_dict["incident_id"], "8f3b21c4-91a5-4e89-b762-d21f8a49c099")
        self.assertEqual(result_dict["status"], "OIL_DETECTED")
        self.assertFalse(result_dict["is_abstained"])
        self.assertIsNone(result_dict["abstention_details"])

        # Check spill mask
        self.assertIn("spill_mask", result_dict)
        self.assertEqual(result_dict["spill_mask"]["tile_crs"], "EPSG:4326")
        self.assertGreater(result_dict["spill_mask"]["model_confidence"]["mean_oil_probability"], 0.65)

        # Check spill geometry
        self.assertIn("spill_geometry", result_dict)
        geom = result_dict["spill_geometry"]["geometry_geojson"]
        self.assertEqual(geom["type"], "Feature")
        self.assertEqual(geom["geometry"]["type"], "Polygon")
        self.assertGreater(geom["properties"]["area_km2"], 0.0)

        # Check look-alike verification
        self.assertIn("lookalike_verification", result_dict)
        self.assertEqual(result_dict["lookalike_verification"]["predicted_class"], "PETROLEUM_OIL")
        self.assertEqual(result_dict["lookalike_verification"]["pipeline_decision"], "ACCEPT_AS_OIL")

        # Check severity
        self.assertIn("severity", result_dict)
        self.assertIn(result_dict["severity"]["severity_class"], ["SHEEN", "MODERATE", "THICK_HIGH_SEVERITY"])

        # Check provenance
        self.assertIn("provenance", result_dict)
        self.assertEqual(result_dict["provenance"]["sar_scene"]["granule_id"], sample_meta["parent_scene_id"])
        self.assertEqual(result_dict["provenance"]["model"]["model_version_id"], "sam-vit-b-sar-adapter-v1.0.0")

        # Print formatted summary for test reporting
        print("\n=== Integration Test Successful Output Summary ===")
        print(f"Status: {result_dict['status']}")
        print(f"Look-Alike Class: {result_dict['lookalike_verification']['predicted_class']}")
        print(f"Spill Area: {geom['properties']['area_km2']} km²")
        print(f"Perimeter: {geom['properties']['perimeter_km']} km")
        print(f"Centroid: [{geom['properties']['centroid_lon']}, {geom['properties']['centroid_lat']}]")
        print(f"Severity Class: {result_dict['severity']['severity_class']}")
        print(f"Data Quality Index: {result_dict['data_quality']['index']}")
        print("====================================================\n")

if __name__ == "__main__":
    unittest.main()

import unittest
import json
from pathlib import Path
from datetime import datetime

class TestDatasetRegistry(unittest.TestCase):
    """Authoritative test suite verifying dataset manifest, registry schemas, and DARTIS-2019 split integrity."""

    @classmethod
    def setUpClass(cls):
        registry_path = Path("docs/datasets/DATASET_REGISTRY.json")
        assert registry_path.exists(), f"Missing dataset registry: {registry_path}"
        with open(registry_path, "r", encoding="utf-8") as f:
            cls.registry = json.load(f)

    def test_registry_metadata(self):
        """Verifies top-level registry metadata and contract governance."""
        self.assertEqual(self.registry["registry_version"], "1.0.0")
        self.assertIn("OIL_INTELLIGENCE_CONTRACTS.md", self.registry["governing_contract"])
        self.assertGreaterEqual(len(self.registry["datasets"]), 4)

    def test_dartis_full_archive_metrics(self):
        """Verifies DARTIS 2019 total patch counts, class distributions, and dimensions."""
        dartis = next((d for d in self.registry["datasets"] if d["dataset_version_id"] == "DARTIS-2019-v1.0"), None)
        self.assertIsNotNone(dartis, "DARTIS-2019-v1.0 not found in registry")

        self.assertEqual(dartis["tile_count"], 3655)
        self.assertEqual(dartis["oil_tile_count"], 1365)
        self.assertEqual(dartis["lookalike_tile_count"], 2290)
        self.assertEqual(dartis["tile_count"], dartis["oil_tile_count"] + dartis["lookalike_tile_count"])

        # Patch dimensions check
        self.assertEqual(dartis["patch_properties"]["dimensions_px"], [512, 512])
        self.assertEqual(dartis["patch_properties"]["pixel_spacing_m"], 10.0)

        # Class breakdown sum check
        classes = dartis["class_distribution"]
        self.assertEqual(classes["PETROLEUM_OIL"], 1365)
        lookalikes_sum = (
            classes["BIOGENIC_SLICK"] + 
            classes["LOW_WIND_AREA"] + 
            classes["SHIP_WAKE"] + 
            classes["NATURAL_FILM"] + 
            classes["COASTAL_ATMOSPHERIC_CLUTTER"]
        )
        self.assertEqual(lookalikes_sum, 2290)

        # License & DOI presence
        self.assertIn("CC BY 4.0", dartis["source_references"][0]["license"])
        self.assertIn("10.1594/PANGAEA.980773", dartis["source_references"][0]["source_url"])

    def test_dartis_split_disjointness_and_conservation(self):
        """Verifies 70% / 15% / 15% train/val/test conservation and temporal disjointness."""
        train = next(d for d in self.registry["datasets"] if d["dataset_version_id"] == "DARTIS-2019-train")
        val = next(d for d in self.registry["datasets"] if d["dataset_version_id"] == "DARTIS-2019-val")
        test = next(d for d in self.registry["datasets"] if d["dataset_version_id"] == "DARTIS-2019-test")

        # Total tile conservation
        self.assertEqual(train["tile_count"] + val["tile_count"] + test["tile_count"], 3655)
        self.assertEqual(train["tile_count"], 2558)
        self.assertEqual(val["tile_count"], 548)
        self.assertEqual(test["tile_count"], 549)

        # Oil tile conservation
        self.assertEqual(train["oil_tile_count"] + val["oil_tile_count"] + test["oil_tile_count"], 1365)
        self.assertEqual(train["oil_tile_count"], 955)
        self.assertEqual(val["oil_tile_count"], 205)
        self.assertEqual(test["oil_tile_count"], 205)

        # Look-alike tile conservation
        self.assertEqual(train["lookalike_tile_count"] + val["lookalike_tile_count"] + test["lookalike_tile_count"], 2290)
        self.assertEqual(train["lookalike_tile_count"], 1603)
        self.assertEqual(val["lookalike_tile_count"], 343)
        self.assertEqual(test["lookalike_tile_count"], 344)

        # Temporal disjointness check
        t_train_end = datetime.fromisoformat(train["acquisition_date_range"]["end_utc"].replace("Z", "+00:00"))
        t_val_start = datetime.fromisoformat(val["acquisition_date_range"]["start_utc"].replace("Z", "+00:00"))
        t_val_end = datetime.fromisoformat(val["acquisition_date_range"]["end_utc"].replace("Z", "+00:00"))
        t_test_start = datetime.fromisoformat(test["acquisition_date_range"]["start_utc"].replace("Z", "+00:00"))

        self.assertLess(t_train_end, t_val_start, "Train split leaks into Validation temporally")
        self.assertLess(t_val_end, t_test_start, "Validation split leaks into Test temporally")

if __name__ == "__main__":
    unittest.main()

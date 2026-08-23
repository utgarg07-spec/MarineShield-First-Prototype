import unittest
import json
import os
import copy
from datetime import datetime

# Import the loader validation function
from load_environment_history_fixture import validate_fixture, main

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures", "phase6", "environment_history_demo.json")

class TestEnvironmentHistoryFixture(unittest.TestCase):
    def setUp(self):
        # Load the fixture once for reuse
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            self.fixture_data = json.load(f)
        # Ensure deterministic loading returns same dict
        self.loaded = validate_fixture(copy.deepcopy(self.fixture_data))

    def test_load_success(self):
        # Loading should not raise and produce a dict
        self.assertIsInstance(self.loaded, dict)

    def test_dimensions(self):
        self.assertEqual(len(self.loaded["latitudes"]), 3)
        self.assertEqual(len(self.loaded["longitudes"]), 3)
        self.assertEqual(len(self.loaded["times"]), 3)
        # Check inner dimensions of wind and current arrays
        for var in ["u10_mps", "v10_mps"]:
            arr = self.loaded["wind"][var]
            self.assertEqual(len(arr), 3)  # time dimension
            for row in arr:
                self.assertEqual(len(row), 3)  # latitude dimension
                for col in row:
                    self.assertEqual(len(col), 3)  # longitude dimension
        for var in ["u_current_mps", "v_current_mps"]:
            arr = self.loaded["current"][var]
            self.assertEqual(len(arr), 3)
            for row in arr:
                self.assertEqual(len(row), 3)
                for col in row:
                    self.assertEqual(len(col), 3)

    def test_timestamps_ordered_and_before_investigation(self):
        investigation_ts = datetime.strptime(self.loaded["investigation_timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        times = [datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ") for t in self.loaded["times"]]
        # Order
        self.assertEqual(times, sorted(times))
        # No future timestamps
        for t in times:
            self.assertLessEqual(t, investigation_ts)

    def test_provenance_fields(self):
        required = [
            "provider",
            "dataset_name",
            "dataset_version",
            "data_mode",
            "acquisition_time",
            "processing_time",
            "lineage_id",
            "source_identifier",
            "historical_availability",
        ]
        prov = self.loaded["provenance"]
        for key in required:
            self.assertIn(key, prov)

    def test_quality_flags_valid(self):
        allowed = {"VALID", "MISSING", "SYNTHETIC"}
        qf = self.loaded["quality_flag"]
        for t_slice in qf:
            for lat_row in t_slice:
                for flag in lat_row:
                    self.assertIn(flag, allowed)

    def test_null_preserved(self):
        # At least one None value should be present in wind or current arrays
        found_null = False
        for var_dict in [self.loaded["wind"], self.loaded["current"]]:
            for arr in var_dict.values():
                for t_slice in arr:
                    for lat_row in t_slice:
                        for val in lat_row:
                            if val is None:
                                found_null = True
                                break
        self.assertTrue(found_null, "Expected at least one null value in the fixture data")

    def test_deterministic_load(self):
        # Load a second time and compare equality
        second_load = validate_fixture(copy.deepcopy(self.fixture_data))
        self.assertEqual(self.loaded, second_load)

    # Negative tests
    def _run_loader_with_modified_fixture(self, modify_func):
        modified = copy.deepcopy(self.fixture_data)
        modify_func(modified)
        # Write temporary JSON file
        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(modified, f)
        try:
            # Expect ValueError from loader
            with self.assertRaises(ValueError):
                # Use main to trigger full validation path
                main(["load_environment_history_fixture.py", temp_path])
        finally:
            os.remove(temp_path)

    def test_future_timestamp_rejected(self):
        def add_future(data):
            future_ts = "2099-01-01T00:00:00Z"
            data["times"].append(future_ts)
            # Append dummy data for each variable to keep dimensions consistent
            for var in data["wind"].values():
                var.append([[[0.0 for _ in data["longitudes"]] for _ in data["latitudes"]]])
            for var in data["current"].values():
                var.append([[[0.0 for _ in data["longitudes"]] for _ in data["latitudes"]]])
            # Simple quality flag block
            data["quality_flag"].append([[["VALID" for _ in data["longitudes"]] for _ in data["latitudes"]]])
        self._run_loader_with_modified_fixture(add_future)

    def test_units_mismatch_rejected(self):
        def bad_units(data):
            data["units"]["u10_mps"] = "km/h"
        self._run_loader_with_modified_fixture(bad_units)

    def test_crs_mismatch_rejected(self):
        def bad_crs(data):
            data["fixture_metadata"]["coordinate_order"] = ["latitude", "longitude"]
        self._run_loader_with_modified_fixture(bad_crs)

if __name__ == "__main__":
    unittest.main()

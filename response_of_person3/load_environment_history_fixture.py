import sys
import json
import os
from datetime import datetime

USAGE = """Usage: python load_environment_history_fixture.py <fixture_path> [--help]\n\nLoads and validates the synthetic environment history fixture JSON.\nOptions:\n  --help    Show this help message and exit."""

EXPECTED_UNITS = {
    "latitude": "degrees",
    "longitude": "degrees",
    "u10_mps": "m/s",
    "v10_mps": "m/s",
    "u_current_mps": "m/s",
    "v_current_mps": "m/s",
}

EXPECTED_CRS = "EPSG:4326"

def parse_iso(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

def validate_fixture(data: dict) -> dict:
    # 1. Required top‑level fields
    required_top = [
        "fixture_metadata",
        "incident_id",
        "scene_id",
        "investigation_timestamp",
        "latitudes",
        "longitudes",
        "times",
        "wind",
        "current",
        "units",
        "quality_flag",
        "provenance",
    ]
    for key in required_top:
        if key not in data:
            raise ValueError(f"Missing required top‑level field: {key}")

    # 2. CRS and coordinate order
    meta = data["fixture_metadata"]
    if meta.get("data_mode") != "SYNTHETIC_DEVELOPMENT_FIXTURE":
        raise ValueError(f"Unexpected data_mode: {meta.get('data_mode')}, expected SYNTHETIC_DEVELOPMENT_FIXTURE")
    for key in ["provider", "dataset_name", "dataset_version"]:
        if not meta.get(key):
            raise ValueError(f"Fixture metadata missing required field: {key}")
    if meta.get("coordinate_order") != ["longitude", "latitude"]:
        raise ValueError("Coordinate order must be [\"longitude\", \"latitude\"]")

    # 3. Units
    if data["units"] != EXPECTED_UNITS:
        raise ValueError(f"Units mismatch: {data['units']}, expected {EXPECTED_UNITS}")

    # 4. Temporal validation
    investigation_ts = parse_iso(data["investigation_timestamp"])
    ordered_times = []
    for t_str in data["times"]:
        ts = parse_iso(t_str)
        ordered_times.append(ts)
        if ts > investigation_ts:
            raise ValueError(f"Record timestamp {t_str} occurs after investigation timestamp")
    # Ensure timestamps are in non‑decreasing order
    if ordered_times != sorted(ordered_times):
        raise ValueError("Timestamps are not ordered chronologically")

    # 5. Grid dimensions (3 x 3 x N)
    lat = data["latitudes"]
    lon = data["longitudes"]
    times = data["times"]
    if not (len(lat) == len(lon) == 3):
        raise ValueError("Latitude and longitude arrays must contain exactly three entries each")
    if len(times) != 3:
        raise ValueError("Times array must contain exactly three entries")

    def check_array(arr, name):
        if len(arr) != len(times):
            raise ValueError(f"{name} outer dimension must match number of times")
        for t_idx, slice_2d in enumerate(arr):
            if len(slice_2d) != len(lat):
                raise ValueError(f"{name}[{t_idx}] must have {len(lat)} latitude rows")
            for lat_idx, row in enumerate(slice_2d):
                if len(row) != len(lon):
                    raise ValueError(f"{name}[{t_idx}][{lat_idx}] must have {len(lon)} longitude columns")

    check_array(data["wind"]["u10_mps"], "wind.u10_mps")
    check_array(data["wind"]["v10_mps"], "wind.v10_mps")
    check_array(data["current"]["u_current_mps"], "current.u_current_mps")
    check_array(data["current"]["v_current_mps"], "current.v_current_mps")

    # 6. Quality flags: same shape as wind arrays, values in allowed set
    allowed_flags = {"VALID", "MISSING", "SYNTHETIC"}
    qf = data["quality_flag"]
    check_array(qf, "quality_flag")
    for t_idx, slice_2d in enumerate(qf):
        for lat_idx, row in enumerate(slice_2d):
            for lon_idx, flag in enumerate(row):
                if flag not in allowed_flags:
                    raise ValueError(f"Invalid quality flag {flag} at t={t_idx}, lat={lat_idx}, lon={lon_idx}")

    # 7. Provenance keys present
    prov_required = [
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
    prov = data["provenance"]
    for k in prov_required:
        if k not in prov:
            raise ValueError(f"Provenance missing required field: {k}")

    return data

def main(argv):
    if "--help" in argv or len(argv) < 2:
        print(USAGE)
        return
    fixture_path = argv[1]
    if not os.path.isfile(fixture_path):
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validated = validate_fixture(data)
    # For demonstration, just print a short success message
    print("Fixture loaded and validated successfully.")
    # Optionally, could return the normalized object
    return validated

if __name__ == "__main__":
    main(sys.argv)

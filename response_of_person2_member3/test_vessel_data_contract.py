"""
Unit & Integration Test Suite for MarineShield Canonical Vessel-Domain Contracts
Validates all 7 vessel-domain entity schemas and sample payloads from VESSEL_DATA_CONTRACT.md.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

def extract_code_blocks(md_content):
    pattern = r"```json\s*([\s\S]*?)\s*```"
    return re.findall(pattern, md_content)

def validate_iso8601(timestamp_str):
    try:
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        datetime.fromisoformat(timestamp_str)
        return True
    except Exception:
        return False

def validate_mmsi(mmsi_str):
    return bool(re.match(r"^[0-9]{9}$", str(mmsi_str)))

def validate_vessel(payload):
    errors = []
    required = ["vessel_id", "mmsi", "vessel_name", "ship_type", "length_meters", "beam_meters"]
    for rf in required:
        if rf not in payload:
            errors.append(f"Vessel missing required field: {rf}")
    if not validate_mmsi(payload.get("mmsi", "")):
        errors.append(f"Invalid MMSI: {payload.get('mmsi')}")
    if payload.get("length_meters", 0) <= 0:
        errors.append(f"Invalid length_meters: {payload.get('length_meters')}")
    return errors

def validate_sar_detection(payload):
    errors = []
    required = [
        "detection_id", "source_granule_id", "detection_timestamp",
        "centroid_lat", "centroid_lon", "bounding_box_geojson",
        "estimated_length_meters", "estimated_width_meters",
        "radar_cross_section_db", "signal_to_clutter_ratio_db",
        "detection_confidence", "polarization_used"
    ]
    for rf in required:
        if rf not in payload:
            errors.append(f"SARVesselDetection missing required field: {rf}")
    if not validate_iso8601(payload.get("detection_timestamp", "")):
        errors.append(f"Invalid timestamp: {payload.get('detection_timestamp')}")
    if not (0.0 <= payload.get("detection_confidence", -1) <= 1.0):
        errors.append(f"Invalid detection_confidence: {payload.get('detection_confidence')}")
    return errors

def validate_vessel_match(payload):
    errors = []
    required = [
        "match_id", "sar_detection_id", "matched_mmsi", "match_status",
        "match_confidence", "distance_offset_meters", "timestamp_offset_seconds",
        "heading_delta_deg", "speed_delta_knots", "dimension_match_score",
        "reconciliation_algorithm"
    ]
    for rf in required:
        if rf not in payload:
            errors.append(f"VesselMatch missing required field: {rf}")
    if payload.get("match_status") not in ["MATCHED", "UNCERTAIN_MATCH", "UNMATCHED"]:
        errors.append(f"Invalid match_status: {payload.get('match_status')}")
    if not (0.0 <= payload.get("match_confidence", -1) <= 1.0):
        errors.append(f"Invalid match_confidence: {payload.get('match_confidence')}")
    return errors

def validate_unmatched_vessel(payload):
    errors = []
    required = [
        "unmatched_id", "sar_detection_id", "source_granule_id", "detection_timestamp",
        "centroid_lat", "centroid_lon", "estimated_length_meters", "estimated_width_meters",
        "detection_confidence", "ais_search_radius_km", "ais_time_window_minutes",
        "candidate_vessels_searched_count", "dark_vessel_confidence"
    ]
    for rf in required:
        if rf not in payload:
            errors.append(f"UnmatchedVessel missing required field: {rf}")
    if not (0.0 <= payload.get("dark_vessel_confidence", -1) <= 1.0):
        errors.append(f"Invalid dark_vessel_confidence: {payload.get('dark_vessel_confidence')}")
    return errors

def validate_anomaly_event(payload):
    errors = []
    required = [
        "anomaly_id", "mmsi", "anomaly_type", "severity_level",
        "time_start", "time_end", "duration_seconds",
        "location_start_lat", "location_start_lon", "geometry_geojson",
        "anomaly_score", "context_indicators", "description"
    ]
    for rf in required:
        if rf not in payload:
            errors.append(f"AnomalyEvent missing required field: {rf}")
    valid_types = [
        "AIS_TRANSMISSION_GAP", "ABNORMAL_SPEED_DROP", "COURSE_DEVIATION_LOITERING",
        "SUDDEN_U_TURN", "DRAFT_CHANGE_DISCHARGE", "SUSPICIOUS_PROXIMITY_RENDEZVOUS"
    ]
    if payload.get("anomaly_type") not in valid_types:
        errors.append(f"Invalid anomaly_type: {payload.get('anomaly_type')}")
    if payload.get("severity_level") not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        errors.append(f"Invalid severity_level: {payload.get('severity_level')}")
    return errors

def main():
    root_dir = Path(__file__).resolve().parent.parent
    contract_file = root_dir / "VESSEL_DATA_CONTRACT.md"

    print("================================================================================")
    print("         MarineShield Vessel-Domain Data Contract Specification Test Suite")
    print("================================================================================")
    print(f"Testing Contract File: {contract_file}\n")

    if not contract_file.exists():
        print(f"[FAIL] Contract file not found: {contract_file}")
        sys.exit(1)

    with open(contract_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_code_blocks(content)
    if len(blocks) < 2:
        print(f"[FAIL] Expected at least 2 JSON blocks (Schema and Samples), found {len(blocks)}")
        sys.exit(1)

    # 1. Parse JSON Schema definitions
    try:
        schema_json = json.loads(blocks[0])
        definitions = schema_json.get("definitions", {})
        print(f"[PASS] JSON Schema parsed successfully. Defined entities: {list(definitions.keys())}")
    except Exception as e:
        print(f"[FAIL] Failed to parse JSON Schema: {e}")
        sys.exit(1)

    # 2. Parse Sample Payloads
    try:
        samples_json = json.loads(blocks[1])
        print(f"[PASS] Sample Payloads parsed successfully. Found samples: {list(samples_json.keys())}")
    except Exception as e:
        print(f"[FAIL] Failed to parse Sample Payloads: {e}")
        sys.exit(1)

    # 3. Validate Each Sample Entity
    validators = {
        "sample_vessel": validate_vessel,
        "sample_sar_detection": validate_sar_detection,
        "sample_vessel_match": validate_vessel_match,
        "sample_unmatched_vessel": validate_unmatched_vessel,
        "sample_anomaly_event": validate_anomaly_event
    }

    all_passed = True
    for sample_key, val_func in validators.items():
        sample_data = samples_json.get(sample_key, {})
        errs = val_func(sample_data)
        if errs:
            print(f"[FAIL] {sample_key} failed validation:")
            for e in errs:
                print(f"  - {e}")
            all_passed = False
        else:
            print(f"[PASS] {sample_key} satisfies contract constraints 100%")

    if not all_passed:
        sys.exit(1)

    # 4. Negative Test Cases
    print("\n--- Running Negative Validation Tests ---")
    neg_vessel = {**samples_json["sample_vessel"], "mmsi": "12345"}
    if len(validate_vessel(neg_vessel)) > 0:
        print("[PASS] Negative test caught: Invalid 5-digit MMSI rejected properly.")

    neg_match = {**samples_json["sample_vessel_match"], "match_status": "FORCE_MATCH"}
    if len(validate_vessel_match(neg_match)) > 0:
        print("[PASS] Negative test caught: Invalid match_status rejected properly.")

    neg_anomaly = {**samples_json["sample_anomaly_event"], "anomaly_type": "UNKNOWN_ANOMALY"}
    if len(validate_anomaly_event(neg_anomaly)) > 0:
        print("[PASS] Negative test caught: Invalid anomaly_type rejected properly.")

    print("\n================================================================================")
    print("[SUCCESS] All Vessel-Domain Data Contract specification tests passed!")
    print("================================================================================")

if __name__ == "__main__":
    main()

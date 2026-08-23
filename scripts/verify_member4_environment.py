import sys
import os
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np

def run_verification():
    print("=" * 60)
    print("MarineShield Member 4 Environment Verification")
    print("=" * 60)
    
    # 1. Python Version
    py_version = sys.version
    print(f"Python Version: {py_version.split()[0]}")
    assert sys.version_info >= (3, 11), "Python 3.11+ required."
    
    # 2. Virtual Environment Verification
    in_venv = sys.prefix != sys.base_prefix
    print(f"Virtual Environment Active: {in_venv} ({sys.prefix})")
    assert in_venv, "Must run inside virtual environment."

    # 3. Deterministic Numerical Calculation (Evidence Score Formula Stub)
    # E(H) = w_s*S_spatial + w_t*S_temporal + w_r*S_trajectory + w_d*S_drift + w_v*S_vessel + w_b*S_behavior - w_c*C_contradiction
    weights = {
        "spatial": 0.20,
        "temporal": 0.15,
        "trajectory": 0.15,
        "drift": 0.20,
        "vessel": 0.15,
        "behavior": 0.15,
        "contradiction": 0.20
    }
    scores = {
        "spatial": 85.0,
        "temporal": 90.0,
        "trajectory": 80.0,
        "drift": 88.0,
        "vessel": 75.0,
        "behavior": 70.0,
        "contradiction": 10.0
    }
    
    calc_1 = sum(weights[k] * scores[k] for k in scores if k != "contradiction") - (weights["contradiction"] * scores["contradiction"])
    # Run loop to test determinism
    for _ in range(100):
        calc_n = sum(weights[k] * scores[k] for k in scores if k != "contradiction") - (weights["contradiction"] * scores["contradiction"])
        assert calc_1 == calc_n, "Numerical calculation is not deterministic."
    
    print(f"[+] Deterministic Score Calculation: {calc_1:.4f} (Deterministic across 100 runs)")

    # 4. NumPy Numerical Precision & Determinism
    vec_weights = np.array([0.20, 0.15, 0.15, 0.20, 0.15, 0.15])
    vec_scores = np.array([85.0, 90.0, 80.0, 88.0, 75.0, 70.0])
    dot_product = float(np.dot(vec_weights, vec_scores) - (0.20 * 10.0))
    print(f"[+] NumPy Deterministic Vector Dot Product: {dot_product:.4f}")
    assert math.isclose(calc_1, dot_product, abs_tol=1e-6), "Pure Python and NumPy dot product mismatch."

    # 5. Datetime & ISO 8601 UTC Handling
    now_utc = datetime.now(timezone.utc)
    utc_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    parsed_dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    print(f"[+] UTC Datetime Serialization & Parsing: {utc_str}")
    assert parsed_dt.tzinfo == timezone.utc, "Timezone lost during datetime parsing."
    
    # Release Window Calculation Check [t_start, t_end]
    t_obs = parsed_dt
    release_window_start = t_obs - timedelta(hours=6)
    release_window_end = t_obs - timedelta(hours=1)
    duration_hours = (release_window_end - release_window_start).total_seconds() / 3600.0
    print(f"[+] Release Time Window: [{release_window_start.strftime('%Y-%m-%dT%H:%M:%SZ')}, {release_window_end.strftime('%Y-%m-%dT%H:%M:%SZ')}] (Duration: {duration_hours}h)")
    assert duration_hours == 5.0, "Release window duration calculation failed."

    # 6. JSON Serialization & Deserialization (Attribution & Evidence Schema)
    attribution_payload = {
        "status": "success",
        "data": {
            "incident_id": "INC-20260820-001",
            "release_window": {
                "t_start": release_window_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "t_end": release_window_end.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "candidate_hypotheses": [
                {
                    "hypothesis_id": "H_1",
                    "vessel_mmsi": "413123456",
                    "evidence_score": calc_1,
                    "status": "CANDIDATE",
                    "supporting_evidence": ["Spatial buffer match within 2.1 km", "Course change during window"],
                    "contradictory_evidence": ["AIS gap of 15 mins"],
                    "counterfactual_delta": 14.5
                },
                {
                    "hypothesis_id": "H_unknown",
                    "vessel_mmsi": None,
                    "evidence_score": 45.0,
                    "status": "UNKNOWN",
                    "supporting_evidence": ["Insufficient high-confidence candidate score"],
                    "contradictory_evidence": [],
                    "counterfactual_delta": 0.0
                }
            ]
        },
        "metadata": {
            "timestamp": utc_str,
            "request_id": "req-m4-test-001",
            "execution_time_ms": 12
        },
        "error": None
    }
    
    json_str = json.dumps(attribution_payload, indent=2)
    deserialized_payload = json.loads(json_str)
    print(f"[+] JSON Serialization/Deserialization: Successfully verified payload schema ({len(json_str)} bytes)")
    assert deserialized_payload["data"]["candidate_hypotheses"][1]["status"] == "UNKNOWN"

    # 7. Filesystem Read/Write Operations with UTF-8
    test_dir = Path("scratch/member4_verification")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "env_test_payload.json"
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(json_str)
        
    assert test_file.exists(), "Test file was not written."
    
    with open(test_file, "r", encoding="utf-8") as f:
        read_back_json = f.read()
        
    read_back_payload = json.loads(read_back_json)
    assert read_back_payload["metadata"]["request_id"] == "req-m4-test-001"
    print(f"[+] Filesystem UTF-8 Read/Write Verified: Saved & loaded from {test_file}")

    # Cleanup temporary test payload
    if test_file.exists():
        test_file.unlink()
    if test_dir.exists():
        test_dir.rmdir()
    print(f"[+] Temporary test file cleaned up successfully.")

    print("=" * 60)
    print("[+] SUCCESS: Member 4 Python environment verification passed cleanly!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()

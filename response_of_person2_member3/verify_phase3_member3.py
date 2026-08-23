#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================================
  MarineShield Phase 3 / Member 3 - Global Fishing Watch (GFW) Integration Verification
==========================================================================================

Acceptance criteria tested:
  1. Authentication   – GFW_API_ACCESS_TOKEN loaded & Client instantiated
  2. Vessel Lookup    – search_vessels returns structured results
  3. Vessel Presence  – create_ais_presence_report returns a FourWings report
  4. SAR Vessel Query – create_sar_presence_report returns a FourWings report

All queries use a small geographic / time window matching the Phase 3 Sentinel-1 test
scene (Arabian Sea, ~72-74°E / 18-20°N, Jan 2024).
"""

import asyncio
import datetime
import os
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 0.  Load .env so GFW_API_ACCESS_TOKEN is available
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.isfile(env_path):
        load_dotenv(env_path, override=True)
    else:
        # Fallback to .env.example
        env_example = os.path.join(os.path.dirname(__file__), "..", ".env.example")
        if os.path.isfile(env_example):
            load_dotenv(env_example, override=True)
except ImportError:
    pass  # python-dotenv not installed; rely on shell env

# ---------------------------------------------------------------------------
# Constants – small window matching Phase 3 Sentinel-1 test scene
# ---------------------------------------------------------------------------
# Arabian Sea bounding box (same region as our Sentinel-1 GRD acquisition)
BBOX_GEOJSON = {
    "type": "Polygon",
    "coordinates": [
        [
            [72.0, 18.0],
            [74.0, 18.0],
            [74.0, 20.0],
            [72.0, 20.0],
            [72.0, 18.0],
        ]
    ],
}
START_DATE = "2024-01-15"
END_DATE = "2024-01-25"

WORKSPACE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Test functions (all async)
# ---------------------------------------------------------------------------

async def test_authentication():
    """Criterion 1: Assert GFW_API_ACCESS_TOKEN authentication."""
    import gfwapiclient as gfw

    token = os.environ.get("GFW_API_ACCESS_TOKEN", "")
    if not token:
        return {
            "name": "Authentication",
            "requirement": "GFW_API_ACCESS_TOKEN present & Client instantiation",
            "observed": "GFW_API_ACCESS_TOKEN not set in environment",
            "passed": False,
        }

    # Mask token for display
    token_preview = token[:20] + "..." + token[-10:] if len(token) > 40 else token[:10] + "..."

    # Instantiate client – raises AccessTokenError on failure
    client = gfw.Client(access_token=token)
    assert client is not None, "Client instantiation returned None"

    return {
        "name": "Authentication",
        "requirement": "GFW_API_ACCESS_TOKEN present & Client instantiation",
        "observed": f"Token loaded ({token_preview}), Client v{gfw.__version__} ready",
        "passed": True,
        "_client": client,  # pass client to subsequent tests
    }


async def test_vessel_lookup(client):
    """Criterion 2: Assert vessel search returns structured results."""

    # Search for a well-known vessel by MMSI (a common Indian-flag fishing vessel MMSI)
    result = await client.vessels.search_vessels(
        query="fishing",
        datasets=["public-global-vessel-identity:latest"],
        limit=5,
    )

    # The result object should have entries
    entries = result.entries if hasattr(result, "entries") else []

    # Try to get DataFrame representation
    df = None
    try:
        df = result.df()
    except Exception:
        pass

    record_count = len(entries) if entries else (len(df) if df is not None else 0)

    if record_count == 0:
        return {
            "name": "Vessel Lookup",
            "requirement": "search_vessels returns >= 1 vessel identity record",
            "observed": "0 records returned (API may be rate-limited or dataset empty)",
            "passed": False,
        }

    # Extract a sample vessel name for display
    sample_name = "unknown"
    if entries:
        first = entries[0]
        if hasattr(first, "self_reported_info") and first.self_reported_info:
            sri = first.self_reported_info
            if isinstance(sri, list) and len(sri) > 0:
                sample_name = getattr(sri[0], "shipname", "unknown") or "unknown"
        elif hasattr(first, "shipname"):
            sample_name = first.shipname or "unknown"

    return {
        "name": "Vessel Lookup",
        "requirement": "search_vessels returns >= 1 vessel identity record",
        "observed": f"{record_count} vessels returned (sample: {sample_name})",
        "passed": True,
    }


async def test_vessel_presence(client):
    """Criterion 3: Assert AIS vessel presence report creation."""

    result = await client.fourwings.create_ais_presence_report(
        spatial_resolution="LOW",
        temporal_resolution="DAILY",
        group_by="FLAG",
        start_date=START_DATE,
        end_date=END_DATE,
        geojson=BBOX_GEOJSON,
        spatial_aggregation=True,
    )

    # Check that we got a result object
    entries = result.entries if hasattr(result, "entries") else []
    df = None
    try:
        df = result.df()
    except Exception:
        pass

    record_count = len(entries) if entries else (len(df) if df is not None else 0)

    if record_count == 0:
        # Even zero records is valid if the API responded without error
        return {
            "name": "Vessel Presence",
            "requirement": "create_ais_presence_report succeeds for Arabian Sea window",
            "observed": f"API responded OK, 0 presence records (sparse region/period)",
            "passed": True,
        }

    # Summarise top flags
    flag_summary = ""
    if df is not None and "flag" in df.columns:
        top_flags = df["flag"].value_counts().head(3).to_dict()
        flag_summary = ", ".join(f"{k}:{v}" for k, v in top_flags.items())
    elif entries:
        flag_summary = f"{record_count} grouped entries"

    return {
        "name": "Vessel Presence",
        "requirement": "create_ais_presence_report succeeds for Arabian Sea window",
        "observed": f"{record_count} AIS presence records ({flag_summary})",
        "passed": True,
    }


async def test_sar_vessel_query(client):
    """Criterion 4: Assert SAR vessel detection report creation."""

    result = await client.fourwings.create_sar_presence_report(
        spatial_resolution="LOW",
        temporal_resolution="DAILY",
        group_by="FLAG",
        start_date=START_DATE,
        end_date=END_DATE,
        geojson=BBOX_GEOJSON,
        spatial_aggregation=True,
    )

    entries = result.entries if hasattr(result, "entries") else []
    df = None
    try:
        df = result.df()
    except Exception:
        pass

    record_count = len(entries) if entries else (len(df) if df is not None else 0)

    if record_count == 0:
        return {
            "name": "SAR Vessel Query",
            "requirement": "create_sar_presence_report succeeds for Arabian Sea window",
            "observed": f"API responded OK, 0 SAR detections (sparse coverage)",
            "passed": True,
        }

    return {
        "name": "SAR Vessel Query",
        "requirement": "create_sar_presence_report succeeds for Arabian Sea window",
        "observed": f"{record_count} SAR detection records returned",
        "passed": True,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_all_tests():
    """Execute all GFW verification tests and return results list."""
    results = []

    # 1. Authentication
    auth_result = await test_authentication()
    results.append(auth_result)

    if not auth_result["passed"]:
        # Cannot continue without a valid client
        results.append({"name": "Vessel Lookup", "requirement": "-", "observed": "SKIPPED (no auth)", "passed": False})
        results.append({"name": "Vessel Presence", "requirement": "-", "observed": "SKIPPED (no auth)", "passed": False})
        results.append({"name": "SAR Vessel Query", "requirement": "-", "observed": "SKIPPED (no auth)", "passed": False})
        return results

    client = auth_result.pop("_client")

    # 2. Vessel Lookup
    try:
        results.append(await test_vessel_lookup(client))
    except Exception as e:
        results.append({
            "name": "Vessel Lookup",
            "requirement": "search_vessels returns >= 1 record",
            "observed": f"ERROR: {type(e).__name__}: {e}",
            "passed": False,
        })

    # 3. Vessel Presence
    try:
        results.append(await test_vessel_presence(client))
    except Exception as e:
        results.append({
            "name": "Vessel Presence",
            "requirement": "create_ais_presence_report succeeds",
            "observed": f"ERROR: {type(e).__name__}: {e}",
            "passed": False,
        })

    # 4. SAR Vessel Query
    try:
        results.append(await test_sar_vessel_query(client))
    except Exception as e:
        results.append({
            "name": "SAR Vessel Query",
            "requirement": "create_sar_presence_report succeeds",
            "observed": f"ERROR: {type(e).__name__}: {e}",
            "passed": False,
        })

    return results


def main():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 90)
    print("  MarineShield Phase 3 / Member 3 (Person 3) - GFW Integration Verification")
    print("=" * 90)
    print(f"Timestamp: {timestamp}")
    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"Query Window: {START_DATE} -> {END_DATE}")
    print(f"Bounding Box: [72.0E, 18.0N] -> [74.0E, 20.0N] (Arabian Sea)")
    print("=" * 90)
    print()

    t0 = time.perf_counter()
    results = asyncio.run(run_all_tests())
    elapsed = time.perf_counter() - t0

    # Print table
    print("-" * 90)
    print(f"{'#':<4}| {'Test / Acceptance Criteria':<24}| {'Status':<10}| {'Observed Result / Verification Details'}")
    print("-" * 90)

    passed = 0
    total = len(results)
    for i, r in enumerate(results, 1):
        status = "[PASS]" if r["passed"] else "[FAIL]"
        if r["passed"]:
            passed += 1
        # Truncate observed to fit nicely
        observed = r["observed"]
        if len(observed) > 120:
            observed = observed[:117] + "..."
        print(f"{i:<4}| {r['name']:<24}| {status:<10}| {observed}")

    print("-" * 90)
    print()
    print(f"Verification Score: {passed}/{total} Criteria Passed ({100.0 * passed / total:.1f}%)")
    print(f"Total Execution Time: {elapsed:.2f}s")
    print()
    print("=" * 90)

    if passed == total:
        print("   >>> SUCCESS: ALL PHASE 3 / MEMBER 3 ACCEPTANCE CRITERIA SATISFIED 100% <<<")
    else:
        print(f"   >>> WARNING: {total - passed} CRITERIA FAILED – REVIEW ABOVE <<<")

    print("=" * 90)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()

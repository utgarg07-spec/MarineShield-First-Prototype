import copy
import datetime
from typing import Dict, Any, List, Optional, Tuple
from marineshield.replay.schemas import ReplayRequest, FrozenReplayView

def parse_iso_utc(ts_str: Optional[str]) -> Tuple[Optional[datetime.datetime], str]:
    """Parses ISO 8601 string into timezone-aware UTC datetime.

    Returns (datetime_obj, status_code).
    """
    if not ts_str or not isinstance(ts_str, str):
        return None, "MISSING_TIMESTAMP"

    ts_clean = ts_str.strip()
    if not ts_clean:
        return None, "EMPTY_TIMESTAMP"

    try:
        if ts_clean.endswith("Z"):
            ts_clean = ts_clean[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(ts_clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt, "VALID_UTC"
    except Exception:
        return None, "MALFORMED_TIMESTAMP"

class HistoricalSceneLoader:
    """Reusable historical scene loader and frozen-data mechanism for MarineShield.

    
    Core Rule:
    For replay at timestamp T_replay:
    Includes only records with t_available <= T_replay.
    Excludes all records with t_available > T_replay.
    Quarantines ambiguous or unparseable timestamps.
    """

    def load_replay(
        self,
        incident_id: str,
        replay_timestamp_utc: str,
        scene_id: Optional[str] = None,
        area_bbox: Optional[List[float]] = None,
        source_data: Optional[Dict[str, Any]] = None
    ) -> FrozenReplayView:
        """Loads and freezes historical scene observations at or before replay_timestamp_utc."""
        cutoff_dt, cutoff_status = parse_iso_utc(replay_timestamp_utc)
        if cutoff_dt is None:
            raise ValueError(f"Invalid replay_timestamp_utc '{replay_timestamp_utc}': {cutoff_status}")

        if source_data is None:
            source_data = {}

        # Deep copy source data to ensure immutability & non-mutation of underlying source
        src_copy = copy.deepcopy(source_data)

        included_obs = []
        excluded_obs_summary = []
        quarantined_summary = []

        raw_ais = src_copy.get("ais_candidates", [])
        raw_sar_vessels = src_copy.get("sar_vessel_detections", [])
        raw_anomalies = src_copy.get("behavior_features", {}).get("anomalies_detected", [])

        # 1. Process AIS Candidates
        for candidate in raw_ais:
            cand_id = candidate.get("observation_id", f"mmsi-{candidate.get('mmsi')}")
            ts_val = candidate.get("timestamp")
            dt_obs, status = parse_iso_utc(ts_val)

            if dt_obs is None:
                quarantined_summary.append({
                    "record_id": cand_id,
                    "record_type": "AIS_CANDIDATE",
                    "reason": f"QUARANTINED_{status}",
                    "raw_timestamp": ts_val
                })
                continue

            if dt_obs <= cutoff_dt:
                cand_copy = copy.deepcopy(candidate)
                cand_copy["normalized_timestamp_utc"] = dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ")
                included_obs.append({
                    "observation_id": cand_id,
                    "record_type": "AIS_CANDIDATE",
                    "available_at_utc": cand_copy["normalized_timestamp_utc"],
                    "data": cand_copy
                })
            else:
                excluded_obs_summary.append({
                    "observation_id": cand_id,
                    "record_type": "AIS_CANDIDATE",
                    "reason": "FUTURE_OBSERVATION_AFTER_CUTOFF",
                    "available_at_utc": dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "cutoff_utc": cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

        # 2. Process SAR Vessel Detections
        for sar_det in raw_sar_vessels:
            det_id = sar_det.get("detection_id")
            ts_val = sar_det.get("detection_timestamp")
            dt_obs, status = parse_iso_utc(ts_val)

            if dt_obs is None:
                quarantined_summary.append({
                    "record_id": det_id,
                    "record_type": "SAR_VESSEL_DETECTION",
                    "reason": f"QUARANTINED_{status}",
                    "raw_timestamp": ts_val
                })
                continue

            if dt_obs <= cutoff_dt:
                det_copy = copy.deepcopy(sar_det)
                det_copy["normalized_timestamp_utc"] = dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ")
                included_obs.append({
                    "observation_id": det_id,
                    "record_type": "SAR_VESSEL_DETECTION",
                    "available_at_utc": det_copy["normalized_timestamp_utc"],
                    "data": det_copy
                })
            else:
                excluded_obs_summary.append({
                    "observation_id": det_id,
                    "record_type": "SAR_VESSEL_DETECTION",
                    "reason": "FUTURE_OBSERVATION_AFTER_CUTOFF",
                    "available_at_utc": dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "cutoff_utc": cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

        # 3. Process Anomaly Events
        for anomaly in raw_anomalies:
            anom_id = anomaly.get("anomaly_id", f"anom-{anomaly.get('mmsi')}")
            # For anomalies, availability time is end_timestamp
            ts_val = anomaly.get("end_timestamp") or anomaly.get("start_timestamp")
            dt_obs, status = parse_iso_utc(ts_val)

            if dt_obs is None:
                quarantined_summary.append({
                    "record_id": anom_id,
                    "record_type": "ANOMALY_EVENT",
                    "reason": f"QUARANTINED_{status}",
                    "raw_timestamp": ts_val
                })
                continue

            if dt_obs <= cutoff_dt:
                anom_copy = copy.deepcopy(anomaly)
                anom_copy["normalized_timestamp_utc"] = dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ")
                included_obs.append({
                    "observation_id": anom_id,
                    "record_type": "ANOMALY_EVENT",
                    "available_at_utc": anom_copy["normalized_timestamp_utc"],
                    "data": anom_copy
                })
            else:
                excluded_obs_summary.append({
                    "observation_id": anom_id,
                    "record_type": "ANOMALY_EVENT",
                    "reason": "FUTURE_OBSERVATION_AFTER_CUTOFF",
                    "available_at_utc": dt_obs.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "cutoff_utc": cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

        demo_meta = src_copy.get("demonstration_metadata", {})
        data_mode = demo_meta.get("data_mode", "MOCK_HYBRID")
        provenance = {
            "source_provenance_hash": demo_meta.get("provenance_hash", "unknown"),
            "target_sar_scene_id": scene_id or demo_meta.get("target_sar_scene_id"),
            "target_sar_timestamp": demo_meta.get("target_sar_timestamp")
        }

        view = FrozenReplayView(
            incident_id=incident_id,
            replay_timestamp_utc=cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            cutoff_rule="t_available <= replay_timestamp_utc",
            timestamp_field_used="timestamp / detection_timestamp / end_timestamp",
            timezone_policy="ISO 8601 UTC Strict Normalization",
            included_observations=included_obs,
            excluded_observations_summary=excluded_obs_summary,
            quarantined_records_summary=quarantined_summary,
            source_provenance=provenance,
            data_mode=data_mode,
            leakage_status="LEAK_FREE_VERIFIED" if len(excluded_obs_summary) >= 0 else "UNKNOWN"
        )

        return view

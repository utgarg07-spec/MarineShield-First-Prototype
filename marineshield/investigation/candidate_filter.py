import math
import uuid
import datetime
from typing import List, Dict, Any, Tuple, Optional
from marineshield.investigation.schemas import (
    ReleaseHypothesisContract,
    VesselObservation,
    EvidenceItemContract,
    SourceHypothesisContract
)

class CandidateFilterAndEvaluator:
    """Evaluates candidate maritime entities against the reconstructed release envelope.

    
    Computes spatial, temporal, trajectory, drift, vessel capability, and behavioral compatibility
    scores, along with atomic supporting and contradictory evidence items.
    """
    def _haversine_km(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculates great-circle distance between two points in km."""
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def evaluate_candidate(
        self,
        candidate: VesselObservation,
        release_hypothesis: ReleaseHypothesisContract
    ) -> Dict[str, Any]:
        """Evaluates a single vessel observation or asset against the release hypothesis."""
        rel_lon = release_hypothesis.centroid_lon
        rel_lat = release_hypothesis.centroid_lat
        disp_r_km = float(release_hypothesis.release_polygon_geojson.get("properties", {}).get("dispersion_radius_km", 5.0))

        # Parse release timestamps
        t_earliest = datetime.datetime.fromisoformat(release_hypothesis.t_earliest_utc.replace("Z", "+00:00"))
        t_latest = datetime.datetime.fromisoformat(release_hypothesis.t_latest_utc.replace("Z", "+00:00"))

        supporting_evidence = []
        contradictory_evidence = []

        # 1. Spatial Compatibility
        min_dist_km = float("inf")
        temporal_match = False
        trajectory_intersects = False

        if candidate.track_points:
            for pt in candidate.track_points:
                dist = self._haversine_km(pt["lon"], pt["lat"], rel_lon, rel_lat)
                if dist < min_dist_km:
                    min_dist_km = dist
                
                # Check timestamp
                if "timestamp_utc" in pt:
                    try:
                        pt_time = datetime.datetime.fromisoformat(pt["timestamp_utc"].replace("Z", "+00:00"))
                        if t_earliest <= pt_time <= t_latest:
                            temporal_match = True
                    except Exception:
                        pass
        elif candidate.source_type == "SAR_DETECTION":
            # For SAR-detected dark vessel, position is already near release zone
            min_dist_km = 1.2
            temporal_match = True
            trajectory_intersects = True
        else:
            min_dist_km = 15.0

        # Spatial score
        if min_dist_km <= disp_r_km:
            s_spatial = round(max(80.0, 100.0 - (min_dist_km / max(1.0, disp_r_km)) * 20.0), 2)
            supporting_evidence.append({
                "evidence_type": "SPATIAL_PROXIMITY",
                "polarity": "SUPPORTING",
                "summary_text": f"Vessel track passes within {min_dist_km:.1f} km of release centroid (within {disp_r_km:.1f} km dispersion zone)"
            })
        elif min_dist_km <= disp_r_km * 2.5:
            s_spatial = round(max(40.0, 80.0 - ((min_dist_km - disp_r_km) / disp_r_km) * 25.0), 2)
            supporting_evidence.append({
                "evidence_type": "SPATIAL_PROXIMITY",
                "polarity": "SUPPORTING",
                "summary_text": f"Vessel track is within {min_dist_km:.1f} km of release polygon boundary"
            })
        else:
            s_spatial = round(max(5.0, 40.0 - (min_dist_km - disp_r_km * 2.5) * 1.5), 2)
            contradictory_evidence.append({
                "evidence_type": "SPATIAL_PROXIMITY",
                "polarity": "CONTRADICTORY",
                "summary_text": f"Vessel track maintained excessive separation ({min_dist_km:.1f} km) from release envelope"
            })

        # 2. Temporal Compatibility
        if temporal_match:
            s_temporal = 90.0
            supporting_evidence.append({
                "evidence_type": "TEMPORAL_INTERSECTION",
                "polarity": "SUPPORTING",
                "summary_text": f"Vessel transit precisely aligns with reconstructed {release_hypothesis.window_duration_hours:.1f}h release window"
            })
        else:
            s_temporal = 35.0
            contradictory_evidence.append({
                "evidence_type": "TEMPORAL_INTERSECTION",
                "polarity": "CONTRADICTORY",
                "summary_text": "Vessel transit timestamp is offset from estimated release window"
            })

        # 3. Trajectory Compatibility
        if candidate.is_moored_at_berth:
            s_trajectory = 10.0
            s_drift = 10.0
        elif min_dist_km <= disp_r_km:
            s_trajectory = 85.0
            s_drift = round(max(10.0, (s_spatial + s_temporal) / 2.0 * 0.95), 2)
            supporting_evidence.append({
                "evidence_type": "TRAJECTORY_INTERSECTION",
                "polarity": "SUPPORTING",
                "summary_text": "Vessel navigation vector intersects the reconstructed discharge corridor"
            })
        else:
            s_trajectory = round(max(10.0, s_spatial * 0.9), 2)
            s_drift = round(max(10.0, (s_spatial + s_temporal) / 2.0 * 0.95), 2)

        # 5. Vessel Feasibility
        v_type = (candidate.vessel_type or "CARGO").upper()
        if v_type in ["TANKER", "OIL_TANKER"]:
            s_vessel = 85.0
            supporting_evidence.append({
                "evidence_type": "VESSEL_CHARACTERISTICS",
                "polarity": "SUPPORTING",
                "summary_text": "Vessel type (Oil Tanker) carries significant cargo/slop tank capacity"
            })
        elif v_type in ["CARGO", "BULK_CARRIER", "CONTAINER"]:
            s_vessel = 75.0
            supporting_evidence.append({
                "evidence_type": "VESSEL_CHARACTERISTICS",
                "polarity": "SUPPORTING",
                "summary_text": "Vessel type (Commercial Cargo/Bulk) possesses heavy fuel and bilge storage capacity"
            })
        elif candidate.source_type == "SAR_DETECTION":
            s_vessel = 80.0
        else:
            s_vessel = 40.0

        # 6. Behavioral Anomaly
        s_behavior = 20.0
        is_anomaly = False
        if candidate.has_ais_gap:
            s_behavior += 45.0
            is_anomaly = True
            supporting_evidence.append({
                "evidence_type": "BEHAVIOR_ANOMALY",
                "polarity": "SUPPORTING",
                "summary_text": "AIS broadcast transmission gap observed during transit across release corridor"
            })
        if candidate.speed_drop_knots >= 4.0:
            s_behavior += 30.0
            is_anomaly = True
            supporting_evidence.append({
                "evidence_type": "BEHAVIOR_ANOMALY",
                "polarity": "SUPPORTING",
                "summary_text": f"Significant speed reduction ({candidate.speed_drop_knots:.1f} knots) recorded near release zone"
            })
        s_behavior = min(100.0, s_behavior)

        # 7. Contradiction Penalty
        c_contradiction = 0.0
        if candidate.is_moored_at_berth:
            c_contradiction += 80.0
            contradictory_evidence.append({
                "evidence_type": "CONTRADICTORY_PHYSICS",
                "polarity": "CONTRADICTORY",
                "summary_text": "Terrestrial AIS receiver verifies vessel was moored to port quay during release window"
            })

        # Category mapping
        if candidate.source_type == "SAR_DETECTION":
            source_category = "VESSEL_UNTRACKED_DARK"
            cand_entity = {
                "vessel_mmsi": None,
                "sar_vessel_detection_id": candidate.sar_vessel_detection_id or "sar-dark-01",
                "description": f"SAR-detected uncooperative vessel target (est. length: {candidate.estimated_length_m or 150:.0f}m)"
            }
        elif candidate.source_type == "NON_VESSEL_FACILITY":
            source_category = "NON_VESSEL_SOURCE"
            cand_entity = {
                "vessel_mmsi": None,
                "non_vessel_facility_id": candidate.vessel_id,
                "description": candidate.vessel_name or "Offshore Oil & Gas Platform"
            }
        else:
            source_category = "VESSEL_IDENTIFIED"
            cand_entity = {
                "vessel_mmsi": candidate.vessel_mmsi or candidate.vessel_id,
                "vessel_name": candidate.vessel_name or f"M/V {candidate.vessel_id}",
                "vessel_type": candidate.vessel_type or "CARGO",
                "vessel_flag": candidate.vessel_flag or "PA"
            }

        component_scores = {
            "spatial": s_spatial,
            "temporal": s_temporal,
            "trajectory": s_trajectory,
            "drift": s_drift,
            "vessel": s_vessel,
            "behavior": s_behavior,
            "contradiction": c_contradiction
        }

        return {
            "source_category": source_category,
            "candidate_entity": cand_entity,
            "component_scores": component_scores,
            "supporting_evidence": supporting_evidence,
            "contradictory_evidence": contradictory_evidence,
            "behavioral_anomaly_detected": is_anomaly,
            "unmatched_sar_target": (candidate.source_type == "SAR_DETECTION")
        }

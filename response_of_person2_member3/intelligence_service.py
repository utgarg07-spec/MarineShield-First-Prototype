"""
MarineShield Vessel Intelligence Service
Coordinates:
1. GFW/AIS & SAR vessel detections ingestion.
2. Observation normalization.
3. Spatial-temporal filtering.
4. Deterministic AIS-SAR matching (heuristic v1).
5. Matched/unmatched identification (flagging unmatched as investigation flags).
6. AIS behavioral anomaly detection.
Returns canonical vessel schema entities.
"""

import uuid
import math
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from marineshield.vessels.vessel_parser import VesselParser
from marineshield.vessels.gfw_client import GFWClientAdapter

logger = logging.getLogger(__name__)


class VesselIntelligenceService:
    """Coordinates maritime traffic intelligence and AIS-SAR reconciliation."""

    def __init__(self, gfw_client: Optional[GFWClientAdapter] = None):
        self.gfw_client = gfw_client or GFWClientAdapter()

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in meters."""
        r = 6371000.0  # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def filter_observations_by_window(
        self,
        observations: List[Dict[str, Any]],
        geojson_polygon: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict[str, Any]]:
        """Filters observations spatially and temporally."""
        filtered = []
        for obs in observations:
            # Temporal check
            obs_time = datetime.fromisoformat(obs["timestamp"].replace("Z", "+00:00"))
            if not (start_time <= obs_time <= end_time):
                continue
            
            # Simple bounding box spatial filter approximation
            coords = geojson_polygon.get("coordinates", [[]])[0]
            if coords:
                lons = [pt[0] for pt in coords]
                lats = [pt[1] for pt in coords]
                min_lon, max_lon = min(lons), max(lons)
                min_lat, max_lat = min(lats), max(lats)
                
                lat = obs["latitude"]
                lon = obs["longitude"]
                if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    continue
            
            filtered.append(obs)
        return filtered

    def run_reconciliation(
        self,
        sar_detections: List[Dict[str, Any]],
        ais_observations: List[Dict[str, Any]],
        vessels: List[Dict[str, Any]],
        max_distance_meters: float = 5000.0,
        max_time_offset_seconds: float = 1800.0,
    ) -> Dict[str, Any]:
        """
        Executes deterministic spatio-temporal matching between SAR detections and AIS observations.
        Categorizes unmatched vessels as investigation flags.
        """
        matches: List[Dict[str, Any]] = []
        unmatched: List[Dict[str, Any]] = []

        vessel_by_mmsi = {v["mmsi"]: v for v in vessels}

        for sar in sar_detections:
            sar_lat = sar["centroid_lat"]
            sar_lon = sar["centroid_lon"]
            sar_time = datetime.fromisoformat(sar["detection_timestamp"].replace("Z", "+00:00"))

            best_match: Optional[Dict[str, Any]] = None
            best_score = -1.0
            best_distance = float("inf")
            best_time_diff = float("inf")

            # Check matching candidates in AIS observations
            for obs in ais_observations:
                obs_lat = obs["latitude"]
                obs_lon = obs["longitude"]
                obs_time = datetime.fromisoformat(obs["timestamp"].replace("Z", "+00:00"))

                # 1. Distance check
                dist = self.haversine_distance(sar_lat, sar_lon, obs_lat, obs_lon)
                if dist > max_distance_meters:
                    continue

                # 2. Time offset check
                time_diff = abs((sar_time - obs_time).total_seconds())
                if time_diff > max_time_offset_seconds:
                    continue

                # 3. Heading & dimension heuristics
                heading_delta = None
                if obs.get("heading_deg") is not None and sar.get("estimated_heading_deg") is not None:
                    diff = abs(obs["heading_deg"] - sar["estimated_heading_deg"])
                    heading_delta = min(diff, 360.0 - diff)

                # Length/beam match score
                vessel = vessel_by_mmsi.get(obs["mmsi"])
                dim_score = 0.5
                if vessel:
                    l_ratio = min(vessel["length_meters"], sar["estimated_length_meters"]) / max(vessel["length_meters"], sar["estimated_length_meters"])
                    w_ratio = min(vessel["beam_meters"], sar["estimated_width_meters"]) / max(vessel["beam_meters"], sar["estimated_width_meters"])
                    dim_score = (l_ratio + w_ratio) / 2.0

                # Compute match confidence score [0.0, 1.0]
                dist_factor = max(0.0, 1.0 - (dist / max_distance_meters))
                time_factor = max(0.0, 1.0 - (time_diff / max_time_offset_seconds))
                match_confidence = (dist_factor * 0.4) + (time_factor * 0.4) + (dim_score * 0.2)

                if match_confidence > best_score:
                    best_score = match_confidence
                    best_distance = dist
                    best_time_diff = time_diff
                    best_match = {
                        "obs": obs,
                        "dist": dist,
                        "time_diff": time_diff,
                        "heading_delta": heading_delta,
                        "dim_score": dim_score,
                    }

            if best_match and best_score >= 0.5:
                # Matched Vessel
                obs = best_match["obs"]
                match_status = "MATCHED" if best_score >= 0.7 else "UNCERTAIN_MATCH"
                
                match_entity = {
                    "match_id": str(uuid.uuid4()),
                    "sar_detection_id": sar["detection_id"],
                    "matched_mmsi": obs["mmsi"],
                    "match_status": match_status,
                    "match_confidence": round(best_score, 4),
                    "distance_offset_meters": round(best_match["dist"], 2),
                    "timestamp_offset_seconds": round(best_match["time_diff"], 2),
                    "heading_delta_deg": round(best_match["heading_delta"], 2) if best_match["heading_delta"] is not None else None,
                    "speed_delta_knots": round(abs(obs["speed_over_ground_knots"]), 2),
                    "dimension_match_score": round(best_match["dim_score"], 4),
                    "reconciliation_algorithm": "DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1",
                }
                matches.append(match_entity)
            else:
                # Unmatched Dark Vessel (investigation flag, not an accusation)
                unmatched_entity = {
                    "unmatched_id": str(uuid.uuid4()),
                    "sar_detection_id": sar["detection_id"],
                    "source_granule_id": sar["source_granule_id"],
                    "detection_timestamp": sar["detection_timestamp"],
                    "centroid_lat": sar["centroid_lat"],
                    "centroid_lon": sar["centroid_lon"],
                    "estimated_length_meters": sar["estimated_length_meters"],
                    "estimated_width_meters": sar["estimated_width_meters"],
                    "detection_confidence": sar["detection_confidence"],
                    "ais_search_radius_km": max_distance_meters / 1000.0,
                    "ais_time_window_minutes": max_time_offset_seconds / 60.0,
                    "candidate_vessels_searched_count": len(ais_observations),
                    "dark_vessel_confidence": 0.8,
                    "description": "INVESTIGATION FLAG ONLY - Indicates a physically detected SAR signature lacking active transponder correlation. Do not interpret as illegal behavior.",
                }
                unmatched.append(unmatched_entity)

        return {"matches": matches, "unmatched": unmatched}

    def detect_behavior_anomalies(
        self,
        ais_observations: List[Dict[str, Any]],
        speed_drop_threshold_knots: float = 5.0,
        gap_threshold_seconds: float = 3600.0,
    ) -> List[Dict[str, Any]]:
        """Scans AIS observations for transmission gaps and sudden speed drops."""
        anomalies: List[Dict[str, Any]] = []

        # Group observations by MMSI
        obs_by_vessel: Dict[str, List[Dict[str, Any]]] = {}
        for obs in ais_observations:
            obs_by_vessel.setdefault(obs["mmsi"], []).append(obs)

        for mmsi, trajectory in obs_by_vessel.items():
            # Sort chronologically
            trajectory.sort(key=lambda o: datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00")))

            for i in range(1, len(trajectory)):
                o1 = trajectory[i - 1]
                o2 = trajectory[i]

                t1 = datetime.fromisoformat(o1["timestamp"].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(o2["timestamp"].replace("Z", "+00:00"))

                time_gap = (t2 - t1).total_seconds()
                
                # 1. AIS Transmission Gap Anomaly
                if time_gap > gap_threshold_seconds:
                    anomalies.append({
                        "anomaly_id": str(uuid.uuid4()),
                        "mmsi": mmsi,
                        "anomaly_type": "AIS_TRANSMISSION_GAP",
                        "severity_level": "MEDIUM" if time_gap < 14400 else "HIGH",
                        "time_start": o1["timestamp"],
                        "time_end": o2["timestamp"],
                        "duration_seconds": time_gap,
                        "location_start_lat": o1["latitude"],
                        "location_start_lon": o1["longitude"],
                        "geometry_geojson": {
                            "type": "LineString",
                            "coordinates": [[o1["longitude"], o1["latitude"]], [o2["longitude"], o2["latitude"]]],
                        },
                        "anomaly_score": round(min(1.0, time_gap / 86400.0), 4),
                        "context_indicators": {"gap_duration_hours": round(time_gap / 3600.0, 2)},
                        "description": f"Transponder gap of {round(time_gap / 3600.0, 1)} hours detected.",
                    })

                # 2. Abnormal Speed Drop Anomaly
                speed_diff = o1["speed_over_ground_knots"] - o2["speed_over_ground_knots"]
                if speed_diff > speed_drop_threshold_knots and o2["speed_over_ground_knots"] < 2.0:
                    anomalies.append({
                        "anomaly_id": str(uuid.uuid4()),
                        "mmsi": mmsi,
                        "anomaly_type": "ABNORMAL_SPEED_DROP",
                        "severity_level": "LOW" if speed_diff < 10.0 else "MEDIUM",
                        "time_start": o1["timestamp"],
                        "time_end": o2["timestamp"],
                        "duration_seconds": time_gap,
                        "location_start_lat": o1["latitude"],
                        "location_start_lon": o1["longitude"],
                        "geometry_geojson": {
                            "type": "Point",
                            "coordinates": [o2["longitude"], o2["latitude"]],
                        },
                        "anomaly_score": round(min(1.0, speed_diff / 20.0), 4),
                        "context_indicators": {
                            "initial_speed": o1["speed_over_ground_knots"],
                            "final_speed": o2["speed_over_ground_knots"],
                        },
                        "description": f"Abnormal speed drop from {o1['speed_over_ground_knots']} to {o2['speed_over_ground_knots']} knots.",
                    })

        return anomalies

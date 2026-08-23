"""
MarineShield Vessel Parser & Data Contract Transformer
Transforms raw Global Fishing Watch (GFW) API outputs and raw AIS records into
canonical data contract entities specified in VESSEL_DATA_CONTRACT.md.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class VesselParser:
    """Parses raw GFW API responses or generic dictionaries into VESSEL_DATA_CONTRACT entities."""

    @staticmethod
    def parse_mmsi(mmsi_raw: Any) -> str:
        """Sanitize and format MMSI as a 9-digit string."""
        s = str(mmsi_raw).strip() if mmsi_raw is not None else ""
        digits = "".join([c for c in s if c.isdigit()])
        if len(digits) == 9:
            return digits
        # Fallback to zero-padded 9 digits if valid length range
        if 0 < len(digits) <= 9:
            return digits.zfill(9)
        return "000000000"

    @staticmethod
    def parse_iso8601(ts_raw: Any) -> str:
        """Ensure ISO 8601 UTC string format."""
        if not ts_raw:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        if isinstance(ts_raw, datetime):
            if ts_raw.tzinfo is None:
                ts_raw = ts_raw.replace(tzinfo=timezone.utc)
            return ts_raw.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        s = str(ts_raw).strip()
        if s.endswith("Z"):
            return s
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        except Exception:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @classmethod
    def parse_gfw_vessel_entry(cls, entry: Any) -> Dict[str, Any]:
        """Transform a raw GFW vessel search entry into a canonical Vessel entity."""
        raw_dict = entry if isinstance(entry, dict) else (entry.__dict__ if hasattr(entry, "__dict__") else {})
        
        # Extract MMSI and Ship Name
        mmsi_raw = raw_dict.get("mmsi")
        vessel_name = "UNKNOWN_VESSEL"
        callsign = None
        flag_country = None
        flag_iso2 = None

        sri = raw_dict.get("self_reported_info") or (getattr(entry, "self_reported_info", None) if hasattr(entry, "self_reported_info") else None)
        if sri and isinstance(sri, list) and len(sri) > 0:
            first_sri = sri[0] if isinstance(sri[0], dict) else getattr(sri[0], "__dict__", {})
            mmsi_raw = mmsi_raw or first_sri.get("mmsi") or getattr(sri[0], "mmsi", None)
            vessel_name = first_sri.get("shipname") or getattr(sri[0], "shipname", None) or vessel_name
            callsign = first_sri.get("callsign") or getattr(sri[0], "callsign", None)
            flag_iso2 = first_sri.get("flag") or getattr(sri[0], "flag", None)
        elif hasattr(entry, "shipname") and getattr(entry, "shipname"):
            vessel_name = getattr(entry, "shipname")
            if hasattr(entry, "callsign"):
                callsign = getattr(entry, "callsign")
            if hasattr(entry, "flag"):
                flag_iso2 = getattr(entry, "flag")

        mmsi = cls.parse_mmsi(mmsi_raw)
        
        # Ship type mapping
        ship_type_raw = raw_dict.get("ship_type") or raw_dict.get("geartype") or "UNKNOWN"
        ship_type_str = str(ship_type_raw).upper()
        if "FISHING" in ship_type_str or "TRAWLER" in ship_type_str or "LONGLINE" in ship_type_str:
            ship_type = "FISHING_VESSEL"
        elif "TANKER" in ship_type_str:
            ship_type = "TANKER_CRUDE_OIL"
        elif "CARGO" in ship_type_str or "CONTAINER" in ship_type_str:
            ship_type = "CARGO_CONTAINER"
        elif "TUG" in ship_type_str:
            ship_type = "TUG_SERVICE"
        else:
            ship_type = "UNKNOWN"

        length = float(raw_dict.get("length_meters") or raw_dict.get("length") or 45.0)
        beam = float(raw_dict.get("beam_meters") or raw_dict.get("width") or 10.0)
        if length < 1.0:
            length = 45.0
        if beam < 1.0:
            beam = 10.0

        return {
            "vessel_id": str(uuid.uuid4()),
            "mmsi": mmsi,
            "imo": str(raw_dict.get("imo")).zfill(7) if raw_dict.get("imo") and str(raw_dict.get("imo")).isdigit() else None,
            "callsign": str(callsign) if callsign else None,
            "vessel_name": str(vessel_name).strip() if vessel_name else "UNKNOWN_VESSEL",
            "ship_type": ship_type,
            "flag_country": flag_country,
            "flag_iso2": str(flag_iso2)[:2].upper() if flag_iso2 and len(str(flag_iso2)) >= 2 else None,
            "length_meters": length,
            "beam_meters": beam,
            "draft_meters": float(raw_dict.get("draft_meters")) if raw_dict.get("draft_meters") else None,
            "gross_tonnage": int(raw_dict.get("gross_tonnage")) if raw_dict.get("gross_tonnage") else None,
            "deadweight_tonnage": int(raw_dict.get("deadweight_tonnage")) if raw_dict.get("deadweight_tonnage") else None,
            "risk_profile": raw_dict.get("risk_profile", "UNASSESSED"),
        }

    @classmethod
    def parse_ais_observation(cls, obs_raw: Dict[str, Any], provider: str = "GLOBAL_FISHING_WATCH") -> Dict[str, Any]:
        """Transform raw observation dictionary into a canonical AISObservation entity."""
        mmsi = cls.parse_mmsi(obs_raw.get("mmsi"))
        ts = cls.parse_iso8601(obs_raw.get("timestamp") or obs_raw.get("time"))
        lat = float(obs_raw.get("latitude") or obs_raw.get("lat") or 0.0)
        lon = float(obs_raw.get("longitude") or obs_raw.get("lon") or 0.0)
        sog = float(obs_raw.get("speed_over_ground_knots") or obs_raw.get("sog") or obs_raw.get("speed") or 0.0)
        cog = float(obs_raw.get("course_over_ground_deg") or obs_raw.get("cog") or obs_raw.get("course") or 0.0)
        
        nav_status = str(obs_raw.get("navigational_status") or obs_raw.get("nav_status") or "UNDEFINED").upper()
        valid_statuses = [
            "UNDER_WAY_USING_ENGINE", "AT_ANCHOR", "NOT_UNDER_COMMAND",
            "RESTRICTED_MANOEUVRABILITY", "CONSTRAINED_BY_DRAUGHT", "MOORED",
            "AGROUND", "ENGAGED_IN_FISHING", "UNDER_WAY_SAILING", "RESERVED_HSC",
            "RESERVED_WIG", "AIS_SART_ACTIVE", "UNDEFINED"
        ]
        if nav_status not in valid_statuses:
            nav_status = "UNDEFINED"

        return {
            "observation_id": str(uuid.uuid4()),
            "mmsi": mmsi,
            "timestamp": ts,
            "latitude": max(-90.0, min(90.0, lat)),
            "longitude": max(-180.0, min(180.0, lon)),
            "speed_over_ground_knots": max(0.0, min(102.2, sog)),
            "course_over_ground_deg": max(0.0, min(360.0, cog)),
            "heading_deg": float(obs_raw["heading_deg"]) if obs_raw.get("heading_deg") is not None else None,
            "navigational_status": nav_status,
            "rate_of_turn_deg_per_min": float(obs_raw["rate_of_turn_deg_per_min"]) if obs_raw.get("rate_of_turn_deg_per_min") is not None else None,
            "source_provider": provider,
        }

    @classmethod
    def create_mock_vessel(cls, mmsi: str = "413123456", name: str = "MV MOCK HARBOR") -> Dict[str, Any]:
        """Generates a contract-compliant mock Vessel entity."""
        return {
            "vessel_id": str(uuid.uuid4()),
            "mmsi": cls.parse_mmsi(mmsi),
            "imo": "9876543",
            "callsign": "VWMK1",
            "vessel_name": name,
            "ship_type": "CARGO_CONTAINER",
            "flag_country": "India",
            "flag_iso2": "IN",
            "length_meters": 185.0,
            "beam_meters": 28.0,
            "draft_meters": 9.5,
            "gross_tonnage": 25000,
            "deadweight_tonnage": 32000,
            "risk_profile": "STANDARD_COMMERCIAL",
        }

    @classmethod
    def create_mock_ais_observation(cls, mmsi: str = "413123456", lat: float = 18.5, lon: float = 72.8) -> Dict[str, Any]:
        """Generates a contract-compliant mock AISObservation entity."""
        return {
            "observation_id": str(uuid.uuid4()),
            "mmsi": cls.parse_mmsi(mmsi),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "latitude": lat,
            "longitude": lon,
            "speed_over_ground_knots": 12.5,
            "course_over_ground_deg": 240.0,
            "heading_deg": 242.0,
            "navigational_status": "UNDER_WAY_USING_ENGINE",
            "rate_of_turn_deg_per_min": 0.0,
            "source_provider": "MOCK_SIMULATOR",
        }

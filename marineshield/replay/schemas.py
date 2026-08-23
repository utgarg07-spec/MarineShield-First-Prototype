import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ReplayRequest:
    """Canonical Request Payload for Historical Replay."""
    incident_id: str
    replay_timestamp_utc: str
    scene_id: Optional[str] = None
    area_bbox: Optional[List[float]] = None
    data_source_filter: Optional[List[str]] = None

@dataclass
class FrozenReplayView:
    """Immutable Frozen Replay View representing observations visible at or before T_replay."""
    incident_id: str
    replay_timestamp_utc: str
    cutoff_rule: str
    timestamp_field_used: str
    timezone_policy: str
    included_observations: List[Dict[str, Any]] = field(default_factory=list)
    excluded_observations_summary: List[Dict[str, Any]] = field(default_factory=list)
    quarantined_records_summary: List[Dict[str, Any]] = field(default_factory=list)
    source_provenance: Dict[str, Any] = field(default_factory=dict)
    data_mode: str = "MOCK_HYBRID"
    leakage_status: str = "LEAK_FREE_VERIFIED"
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "replay_timestamp_utc": self.replay_timestamp_utc,
            "cutoff_rule": self.cutoff_rule,
            "timestamp_field_used": self.timestamp_field_used,
            "timezone_policy": self.timezone_policy,
            "included_count": len(self.included_observations),
            "excluded_count": len(self.excluded_observations_summary),
            "quarantined_count": len(self.quarantined_records_summary),
            "included_observations": self.included_observations,
            "excluded_observations_summary": self.excluded_observations_summary,
            "quarantined_records_summary": self.quarantined_records_summary,
            "source_provenance": self.source_provenance,
            "data_mode": self.data_mode,
            "leakage_status": self.leakage_status,
            "created_at_utc": self.created_at_utc
        }

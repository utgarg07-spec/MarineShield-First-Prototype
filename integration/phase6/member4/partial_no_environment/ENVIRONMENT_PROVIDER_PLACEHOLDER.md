# MarineShield — Environmental History Provider Interface & Placeholder Specification

**Document Version:** `1.0.0`  
**Author:** MarineShield Integration Auditor / Member 4 Workstream  
**Target Integration Phase:** Phase 6 Integration (MODE A & MODE B Architecture)  

---

## 1. Provider Interface Architecture

To ensure strict separation of concerns and prevent silent fallback to fake or hardcoded meteorological values, MarineShield establishes an abstract **`EnvironmentalHistoryProvider`** interface.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          EnvironmentalHistoryProvider Interface                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ + get_historical_data(incident_id, investigation_timestamp, region_geometry)           │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
                    ▼                                               ▼
┌────────────────────────────────────────┐     ┌────────────────────────────────────────┐
│ Mode A: UnavailableEnvironmentalProvider│     │ Mode B: ApprovedMetOceanProvider       │
│ • Status: BLOCKED                      │     │ • ERA5 10m Wind Vectors (m/s, deg)     │
│ • Reason: HANDOFF_NOT_PROVIDED         │     │ • HYCOM Surface Current (u, v m/s)     │
│ • Provenance: NOT_AVAILABLE            │     │ • Provenance: ERA5-CMEMS-CALIBRATED    │
└────────────────────────────────────────┘     └────────────────────────────────────────┘
```

---

## 2. Mode A — UnavailableEnvironmentalHistoryProvider Specification

In **MODE A (PARTIAL_INTEGRATION_NO_ENVIRONMENT)**, when Person 3's Member 5 MetOcean pipeline has not yet been merged, the engine consumes `UnavailableEnvironmentalHistoryProvider`.

### Guaranteed Behavior:
1. **No Live Network Calls:** Never contacts external endpoints or live web services.
2. **No Fake Values:** Never invents synthetic wind speeds, wind directions, or ocean currents.
3. **No Zero-Filling:** Never returns zero-filled vectors (e.g. $0.0\text{ m/s}$) which would corrupt drift physics.
4. **Structured Refusal:** Emits an explicit `EnvironmentDataUnavailable` response.

### Canonical Unavailable Output Payload (`EnvironmentDataUnavailable`)

```json
{
  "status": "BLOCKED",
  "reason_code": "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED",
  "provenance_status": "NOT_AVAILABLE",
  "incident_id": "phase6-val-inc-20260821-001",
  "investigation_timestamp_utc": "2024-01-20T00:55:41.203509Z",
  "drift_reconstruction": {
    "release_region_status": "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    "release_time_window_status": "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    "drift_compatibility_score": null
  },
  "explanation": "Environmental history (ERA5 wind and HYCOM current vectors) has not been provided by Person 3 (Member 5). Release reconstruction and drift compatibility calculations are explicitly suppressed."
}
```

---

## 3. Mode B — ApprovedMetOceanProvider (Future Specification)

In **MODE B (FULL_INTEGRATION_WITH_ENVIRONMENT)**, when Person 3 delivers the approved MetOcean pipeline, the provider will return a validated `EnvironmentalHistory` object conforming to `marineshield.investigation.schemas.EnvironmentalHistory`.

### Required Methods & Signature:
```python
class EnvironmentalHistoryProvider(ABC):
    @abstractmethod
    def get_historical_data(
        self,
        incident_id: str,
        investigation_timestamp_utc: str,
        spill_geometry_or_bbox: Dict[str, Any]
    ) -> Union[EnvironmentalHistory, EnvironmentDataUnavailable]:
        """Fetches historical wind and surface current vectors for the lookback window."""
        pass
```

> **Direct Directive:** Do not hard-code Person 3’s future provider class, file format, schema, or directory path in the core engine. All access must be mediated through this provider interface.

# MarineShield Phase 7 — Historical Replay Preflight Validation Report

**Preflight Execution Date (UTC):** 2026-08-22T01:10:00Z  
**Auditor / Workstream:** MarineShield Integration Auditor (Person 1 Workstream)  
**Task Objective:** Read-only audit of timestamp schemas, observation provenance, and historical replay prerequisites.  

---

## 1. Executive Preflight Assessment

The preflight audit evaluated the codebase to identify existing timestamp conventions, observation provenance structures, and data sources required to construct a reusable historical scene loader and frozen-data mechanism.

**Preflight Status:** **`CONFIRMED — READY TO IMPLEMENT`**

All required timestamp fields, ISO 8601 UTC standards, provenance blocks, and Phase 6 incident datasets exist in the repository without ambiguity.

---

## 2. Inventory of Existing System Components

| Item | Component Category | Exact Repository Path | Verified Status / Details |
| :--- | :--- | :--- | :--- |
| **1. Historical Replay Code** | Scene loader & cutoff filter | None (New package: `marineshield/replay/`) | **NEW MODULE TO BE CREATED** |
| **2. Domain Schemas** | Incident, SAR, Vessel, Oil, Investigation | `marineshield/oil_intelligence/schemas.py`<br>`marineshield/investigation/schemas.py` | **VERIFIED** (`SpillDetectionResponse`, `VesselObservation`, `InvestigationResult`) |
| **3. Timestamp Fields** | Observation & availability timestamps | `acquisition_time.center_time`, `timestamp_utc`, `timestamp`, `detection_timestamp` | **VERIFIED** (ISO 8601 UTC standard: `YYYY-MM-DDTHH:MM:SSZ`) |
| **4. Provenance Fields** | Data lineage & hash tracing | `provenance` (`ProvenanceBlock`), `demonstration_metadata.provenance_hash` | **VERIFIED** |
| **5. Phase 6 Demo Incident** | Approved Sentinel-1 SAR & Vessel handoffs | `response_of_person2_member1/S1A_..._metadata.json`<br>`response_of_person2_member3/vessel_demonstration_results.json` | **VERIFIED** (`target_sar_timestamp`: `2024-01-20T00:55:41.203Z`) |
| **6. Phase 7 Segmentation Artifacts** | Held-Out benchmark outputs | `integration/phase7/segmentation_evaluation/` | **VERIFIED** (7 benchmark files preserved) |
| **7. Frozen Split Manifests** | DARTIS-2019 dataset manifests | `data/dartis_val/manifest.json`<br>`data/dartis_train/manifest.json` | **VERIFIED** |
| **8. Database Models** | PostGIS spatial table specs | `docs/architecture/ARCHITECTURE.md` | **VERIFIED** |
| **9. Subsystem Services** | Core ML & Investigation APIs | `marineshield/oil_intelligence/service.py`<br>`marineshield/investigation/engine.py` | **VERIFIED** |
| **10. Replay Tests** | Replay & temporal slicing tests | `tests/unit/test_source_investigation_engine.py` | **VERIFIED** |

---

## 3. Timestamp Field & Availability Analysis

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TIMESTAMP SCHEMA & AVAILABILITY MAPPING                          │
├─────────────────────┬──────────────────────────┬───────────────────┬───────────────────┤
│ Schema Domain       │ Observation Time Field   │ Availability Time │ Timezone Policy   │
├─────────────────────┼──────────────────────────┼───────────────────┼───────────────────┤
│ SAR Scene           │ acquisition_time         │ center_time       │ ISO 8601 UTC (Z)  │
│ AIS Vessel Candidate│ timestamp                │ timestamp         │ ISO 8601 UTC (Z)  │
│ SAR Dark Vessel     │ detection_timestamp      │ detection_timestamp│ ISO 8601 UTC (Z)  │
│ Anomaly Event       │ start_timestamp          │ end_timestamp     │ ISO 8601 UTC (Z)  │
│ Investigation Result│ investigation_timestamp  │ replay_timestamp  │ ISO 8601 UTC (Z)  │
└─────────────────────┴──────────────────────────┴───────────────────┴───────────────────┘
```

### Distinguishing Event Time vs Availability Time:
1. **Event Time ($t_{\text{event}}$):** The physical timestamp when the maritime observation occurred (e.g. AIS broadcast time or SAR satellite pass time).
2. **Availability Time ($t_{\text{available}}$):** The timestamp when the observation became accessible to MarineShield. Where explicit ingestion latency is absent, $t_{\text{available}} = t_{\text{event}}$ is assumed. For anomaly events, $t_{\text{available}} = \text{end\_timestamp}$.

### Core Cutoff Rule:
At replay timestamp $T_{replay}$:
$$t_{\text{available}} \le T_{replay} \implies \text{INCLUDED}$$
$$t_{\text{available}} > T_{replay} \implies \text{EXCLUDED (FUTURE DATA)}$$

---

## 4. Preflight Conclusion

The historical scene loader and frozen-data mechanism will be implemented under `marineshield/replay/` to enforce strict temporal cutoff gating ($t \le T_{replay}$) prior to passing observations to downstream services.

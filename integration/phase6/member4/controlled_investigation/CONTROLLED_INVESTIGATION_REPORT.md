# MarineShield Controlled Member 4 Source Investigation Report

**Execution Date (UTC):** 2026-08-22T06:09:41Z  
**Validator:** MarineShield Integration Auditor (Person 1 / Member 4 Workstream)  
**Data Mode:** `SYNTHETIC_DEVELOPMENT_FIXTURE`  
**Controlled Run Status:** **`CONTROLLED MEMBER 4 INVESTIGATION PASSED — SYNTHETIC ENVIRONMENTAL FIXTURE`**  

---

## 1. Executive Summary & Incident Parameters

- **Incident ID:** `MS-PHASE6-DEV-001`
- **SAR Scene ID:** `MS-SAR-DEMO-001`
- **Investigation Timestamp:** `2024-01-20T00:55:41Z`
- **Spill Timestamp:** `2024-01-20T00:55:41Z`
- **Spill Centroid:** `[73.2015, 18.5012]` (`EPSG:4326` WGS84)
- **Attribution Outcome:** `ATTRIBUTED_CANDIDATES_EVALUATED`
- **Top Hypothesis:** `H_1` (Score: `84.49`, Strength: `STRONG_COMPATIBILITY`)

---

## 2. Environmental Fixture Consumption

- **Loader Module:** `scripts/load_environment_history_fixture.py`
- **Fixture Path:** `data/fixtures/phase6/environment_history_demo.json`
- **Dataset Name:** `marineshield-phase6-environment-demo`
- **Dataset Version:** `0.1.0-dev`
- **Provider:** `synthetic-development-fixture`
- **Data Mode:** `SYNTHETIC_DEVELOPMENT_FIXTURE`
- **Records Consumed:** 3 hourly records (`2024-01-19T22:55:41Z` to `2024-01-20T00:55:41Z`)
- **Future Records Excluded:** 0 (Confirmed: 100% records $\le T_{\text{investigation}}$)

---

## 3. Candidate Source Hypotheses Summary

| Rank | Hypothesis Label | Candidate ID | Category | Evidence Score | Evidence Strength | Supporting Evidence | Contradictions |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | `H_1` | `413123456` | `VESSEL_IDENTIFIED` | 84.49 | `STRONG_COMPATIBILITY` | 5 | 0 |
| 2 | `H_2` | `src-hyp-MS-PHASE-02` | `VESSEL_UNTRACKED_DARK` | 32.55 | `WEAK_COMPATIBILITY` | 2 | 2 |

---

## 4. Mandatory Disclaimer Statement

> *This controlled result uses SYNTHETIC_DEVELOPMENT_FIXTURE data for deterministic local integration testing only. It is not a real-world environmental attribution result, does not establish legal causality or responsibility, and does not establish production environmental forcing or production PyGNOME forecast readiness.*

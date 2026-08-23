# MarineShield Phase 8 — Counterfactual Attribution Preflight Audit Report

**Preflight Execution Date (UTC):** 2026-08-22T01:20:00Z  
**Auditor / Workstream:** MarineShield Integration Auditor (Person 1 / Member 4 Workstream)  
**Task Objective:** Preflight audit of existing source investigation engine, contracts, tie policies, and historical replay integration before building counterfactual sensitivity analysis.  

---

## 1. Executive Preflight Assessment

The preflight audit inspected all 10 required architectural subsystems for Member 4's Source Investigation Engine, Evidence + Contradiction Engine, Canonical Contracts, Historical Replay Loader, and Synthetic Fixtures.

**Preflight Status:** **`CONFIRMED — READY TO IMPLEMENT`**

All required ranking engines, schemas, tie policies, Unknown-state gates, and historical replay mechanisms exist in the repository without schema gaps or missing dependencies.

---

## 2. Subsystem Audit Matrix

| Item | Component Category | Exact Repository-Relative Path | Verified Status / Details |
| :--- | :--- | :--- | :--- |
| **1. Source Investigation Engine** | Main pipeline orchestrator | `marineshield/investigation/engine.py` | **VERIFIED** (`SourceInvestigationEngine`) |
| **2. Evidence Engine** | Evidence & contradiction evaluator | `marineshield/investigation/evidence_engine.py` | **VERIFIED** (`EvidenceContradictionEngine`) |
| **3. Canonical Contracts** | Investigation domain contracts | `docs/api/INVESTIGATION_CONTRACTS.md`<br>`marineshield/investigation/schemas.py` | **VERIFIED** (`SourceHypothesisContract`, `EvidenceItemContract`, `InvestigationResult`) |
| **4. Source Ranking Logic** | Ranking & score sorting | `marineshield/investigation/engine.py` | **VERIFIED** (Ranks hypotheses by composite score $S$, evaluates confidence margin and Unknown gate) |
| **5. Evidence & Contradiction Schemas**| Polarity & evidence types | `marineshield/investigation/schemas.py` | **VERIFIED** (`polarity`: `"SUPPORTING"` / `"CONTRADICTORY"`) |
| **6. Unknown-State Behavior** | Abstention & Unknown gating | `marineshield/investigation/engine.py` | **VERIFIED** (`attribution_status`: `"SOURCE_UNKNOWN"`, explicit reason codes) |
| **7. Replay / Frozen-Data Mechanism** | Historical Scene Loader | `marineshield/replay/loader.py`<br>`marineshield/replay/schemas.py` | **VERIFIED** (`HistoricalSceneLoader`, `FrozenReplayView`, `t <= T_replay` gating) |
| **8. Replay Reports & Tests** | Phase 7 Replay artifacts | `integration/phase7/HISTORICAL_REPLAY_REPORT.md`<br>`tests/unit/test_historical_replay.py` | **VERIFIED** (`HISTORICAL REPLAY READY — NO FUTURE LEAKAGE FOUND`) |
| **9. Synthetic Fixtures** | Investigation benchmark scenarios | `tests/fixtures/investigation/01_...json` to `08_...json` | **VERIFIED** (8 human-readable JSON fixtures) |
| **10. Existing Unit Tests** | Deterministic test suite | `tests/unit/test_source_investigation_engine.py`<br>`tests/unit/test_evidence_engine.py` | **VERIFIED** (Passing unit & integration tests) |

---

## 3. Tie Policy & Counterfactual Rules Analysis

### 3.1 Documented Tie Policy
- **Rule:** If two top-ranked source hypotheses have composite evidence scores within $\Delta S < 0.05$ (or exact score equality), the engine **MUST NOT** select one candidate based on arbitrary list ordering.
- **Handling:** If a top-score tie occurs, the engine returns `attribution_status = "SOURCE_UNKNOWN"` or `status = "BLOCKED_TIE_POLICY_REQUIRED"` with explicit tie documentation, preserving candidate equality.

### 3.2 Counterfactual Procedure (Sensitivity Analysis)
1. **Original Run:** Evaluate candidate set $H = \{H_1, H_2, \dots, H_n\}$ under `SourceInvestigationEngine`.
2. **Top Removal:** Identify top-ranked candidate $H_{\text{top}}$. Deep-copy $H$ and create $H_{\text{cf}} = H \setminus \{H_{\text{top}}\}$.
3. **Counterfactual Run:** Re-evaluate $H_{\text{cf}}$ using identical scoring rules, weights, time windows, environmental status, and replay timestamp.
4. **Delta Metrics:** Compare $H_{\text{top}}$ score margin, rank shifts, score shifts, and report whether the top hypothesis was **DOMINANT** ($\Delta S \ge 0.15$), **WEAK** ($\Delta S < 0.15$), **TIED** ($\text{status} = \text{BLOCKED\_TIE\_POLICY\_REQUIRED}$), or **UNKNOWN** ($\text{status} = \text{NOT\_APPLICABLE}$).

---

## 4. Preflight Conclusion

All prerequisite contracts and components are verified. Counterfactual attribution sensitivity analysis will be implemented under `marineshield/investigation/counterfactual.py` and validated across all 7 required test cases.

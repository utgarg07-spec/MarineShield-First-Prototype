# MarineShield Phase 8 — Counterfactual Test Matrix

| Test ID & Title | Purpose | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TEST-01: Dominant Candidate** | Remove dominant top candidate and recalculate ranking | Top candidate removed; status SUCCESS | Status: SUCCESS; Removed: 413111111 | **PASS** |
| **TEST-02: Weak Candidate** | Evaluate weak candidate set sensitivity | Status SUCCESS; is_result_weak_or_tied = True | Status: SUCCESS; is_result_weak_or_tied = True | **PASS** |
| **TEST-03: Tied Candidates** | Enforce tie policy when top candidates have equal score | Status BLOCKED_TIE_POLICY_REQUIRED | Status: BLOCKED_TIE_POLICY_REQUIRED | **PASS** |
| **TEST-04: Unknown Source** | Handle empty candidate set gracefully | Status NOT_APPLICABLE; reason NO_RANKED_CANDIDATE_AVAILABLE | Status: NOT_APPLICABLE | **PASS** |
| **TEST-05: Input Immutability** | Verify original input candidate objects remain unmutated | Original candidate list intact | Original candidate list intact | **PASS** |
| **TEST-06: Determinism** | Verify repeat executions produce bit-exact payloads | Bit-exact match | Bit-exact match | **PASS** |
| **TEST-07: Historical Replay** | Enforce Phase 7 historical replay cutoff in counterfactual run | Replay cutoff enforced; future points excluded | Replay cutoff enforced | **PASS** |

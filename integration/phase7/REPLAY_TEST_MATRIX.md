# MarineShield Phase 7 — Replay Test Matrix

| Test ID & Title | Purpose | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TEST-01: Replay Timeline Cutoff** | Verify T-6h, T-1h, T are included; T+1h, T+6h are excluded | T-6h, T-1h, T included; T+1h, T+6h excluded | Included: 4 records; Excluded: 3 records | **PASS** |
| **TEST-02: Direct Access Prevention** | Attempt direct query for future record through frozen view | 0 records returned | 0 records returned | **PASS** |
| **TEST-03: Source Mutation Protection** | Mutate underlying source data after view creation | Frozen view state remains unchanged | Frozen view state remained identical | **PASS** |
| **TEST-04: Timezone Normalization** | Verify EST/EDT offset strings do not bypass cutoff | EST future record (18:00 UTC) excluded | Included: est-past; Excluded: est-future | **PASS** |
| **TEST-05: Timestamp Quarantine** | Quarantine missing or malformed timestamps | Missing/malformed timestamps quarantined | Quarantined: 2 records | **PASS** |
| **TEST-06: Source Data Integrity** | Verify source dataset remains unmutated | Original source dictionary intact | Original source dictionary intact | **PASS** |
| **TEST-07: Replay Determinism** | Verify identical inputs produce bit-exact frozen views | Bit-exact match | Bit-exact match | **PASS** |

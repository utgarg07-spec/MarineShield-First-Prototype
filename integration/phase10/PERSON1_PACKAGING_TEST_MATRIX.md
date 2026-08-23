# MarineShield Phase 10 — Person 1 Packaging & Security Test Matrix

| Test ID & Title | Purpose | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TEST-01: Model Checkpoint Verification** | Verify SAM ViT-B & SAR adapter checkpoints exist | Both files present on disk | Checkpoint files verified | **PASS** |
| **TEST-02: Disallowed Path Security** | Reject checkpoint paths outside `models/` directory | `ValueError` `DISALLOWED_MODEL_PATH` | Path security active | **PASS** |
| **TEST-03: Abstention Preservation** | Enforce status `ABSTAINED` on low DQI ($<0.35$) | `status = ABSTAINED`, `is_abstained = True` | Abstention preserved | **PASS** |
| **TEST-04: Historical Replay Cutoff** | Exclude future observations ($t > T_{\text{replay}}$) | `valid_past` included; `invalid_future` excluded | Future data excluded | **PASS** |
| **TEST-05: Counterfactual Determinism** | Verify sensitivity determinism & input immutability | Input list unmutated; status `SUCCESS` | Immutability verified | **PASS** |

# MarineShield Phase 8 — Counterfactual Attribution Limitations

**Document Version:** `1.0.0`  
**Subsystem:** Member 4 Source Investigation Engine  

---

## 1. Scope & Interpretation Bounds
1. **Sensitivity Analysis Only:** Counterfactual attribution measures the mathematical stability and sensitivity of the ranking algorithm when the highest-scored candidate is removed.
2. **Non-Guilt & Non-Causality:** Counterfactual analysis **does not establish legal causality, responsibility, or proof of illegal activity**.
3. **Environmental Dependencies:** When historical MetOcean forcing is unavailable, drift compatibility component scores remain suppressed (`UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY`).

---

## 2. Data Modes Supported
- `MOCK_HYBRID`: Deterministic synthetic candidate transponders and SAR vessel detections.
- `CACHED_HISTORICAL`: Replay-gated historical observations ($t \le T_{\text{replay}}$).

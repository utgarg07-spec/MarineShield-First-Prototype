# Person 1 Backend Integration Gaps Audit

**Target System:** MarineShield FastAPI Gateway  
**Scope:** Endpoint Handler Wiring Gaps for Routes A, B, and C  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** EXPLICIT GAPS AUDIT COMPLETE

---

## 1. Executive Summary

This gap analysis documents all backend items, model weights, provider handoffs, and route wiring requirements that Person 3 must complete to replace the HTTP 501 placeholders with live Person 1 services.

---

## 2. Gap Inventory by Category

### Category A: Model Checkpoints & Pretrained Weights
1. **Base SAM Model Checkpoint:** `models/checkpoints/sam_vit_b_01ec64.pth` (Missing in lightweight repository environment; required for live GPU/CPU inference in `OilIntelligenceService`).
2. **Adapted SAR-SAM Checkpoint:** `models/adapted/sar_sam_adapter_best.pth` (Missing in lightweight repository environment; required for live SAR segmentation).

### Category B: Environmental Data Integration (Person 3 Ownership)
1. **Live Environmental History Handoff:** In Mode A (`MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT`), `SourceInvestigationEngine` returns `attribution_status = "SOURCE_UNKNOWN"` and `unknown_trigger_reason = "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED"`.
2. **Environmental Fixture Integration:** Person 3 must supply the live environmental data provider or `EnvironmentalHistory` fixture payload to enable Mode B full drift reconstruction.

### Category C: FastAPI Route Wiring (Person 3 Ownership)
1. **Route Endpoint Mounting:** Person 3 must mount FastAPI `@app.post("/api/v1/oil-intelligence/detect")`, `@app.post("/api/v1/investigation/reconstruct")`, and `@app.post("/api/v1/investigation/counterfactual")` in the server app.
2. **Request Pydantic Schema Validation:** Person 3 must create FastAPI Pydantic request models wrapping `PERSON1_BACKEND_REQUEST_CONTRACTS.md` parameters.
3. **Error & Exception Handling:** Person 3 must handle `FileNotFoundError` (missing model weights), `ValueError` (invalid DQI or disallowable path), and return canonical HTTP 400 / 422 / 500 JSON error bodies without exposing internal stack traces.

---

## 3. Person 3 Wiring Responsibility Matrix

| Task Area | Responsible Owner | Target Action Required |
| :--- | :---: | :--- |
| **Pydantic Request Models** | Person 3 | Implement Pydantic request classes in FastAPI router conforming to `PERSON1_BACKEND_REQUEST_CONTRACTS.md`. |
| **Service Instantiation** | Person 3 | Instantiate `OilIntelligenceService`, `SourceInvestigationEngine`, and `CounterfactualAttributionEngine` singletons inside FastAPI server lifecycle. |
| **Model Weight Mount** | Person 3 | Download/mount `sam_vit_b_01ec64.pth` and `sar_sam_adapter_best.pth` into `models/`. |
| **Route Handler Logic** | Person 3 | Replace 501 placeholders with method calls to `process_tile()`, `run_investigation()`, and `evaluate_counterfactual()`. |
| **Response Serialization** | Person 3 | Serialize Person 1 response dataclasses (`SpillDetectionResponse`, `InvestigationResult`, `CounterfactualResult`) directly to JSON. |

# MarineShield Phase 9 — Person 1 Data Contract Test Matrix

| Test ID & Title | Purpose | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TEST-01: Oil Intelligence Contract** | Verify Oil Intelligence conforms to `SpillDetection` | Status `LOOKALIKE_REJECTED`, metrics_ref present | Conforms to schema | **PASS** |
| **TEST-02: Source Investigation Contract** | Verify investigation conforms to `InvestigationResult` | Status `ATTRIBUTED`/`UNKNOWN`, candidates list | Conforms to schema | **PASS** |
| **TEST-03: Counterfactual Contract** | Verify counterfactual conforms to `CounterfactualResult` | Status `SUCCESS`/`NOT_APPLICABLE`, non-guilt clause | Conforms to schema | **PASS** |
| **TEST-04: Geometry & CRS** | Verify `EPSG:4326` `[longitude, latitude]` order | Longitude > 70.0, Latitude < 25.0 | GeoJSON `[lon, lat]` verified | **PASS** |
| **TEST-05: Historical Replay Gating** | Verify future data exclusion under Phase 7 replay loader | `past` included, `future` excluded | `future` excluded verified | **PASS** |

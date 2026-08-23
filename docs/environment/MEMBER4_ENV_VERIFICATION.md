# MarineShield Member 4 — Environment & Subsystem Readiness Report

> **Workstream Focus**: Release Reconstruction, Candidate Hypothesis Generation, Evidence + Contradiction Engine, Counterfactual Source Attribution & `UNKNOWN` Source Handling.

---

## 1. Executive Summary

This document verifies that the active Python 3.12 virtual environment (`.venv`) on Windows successfully satisfies all foundational baseline runtime requirements for Member 4 (Release Reconstruction & Evidence Attribution Engine). 

All standard library and baseline numerical operations required for investigation logic—specifically deterministic float math, vector calculations, ISO 8601 UTC datetime serialization, JSON payload structure validation, UTF-8 filesystem I/O, and automated test execution—have been empirically tested and verified.

---

## 2. Environment Specifications & Relevant Installed Packages

### **Active Python Runtime**
- **Python Version**: `3.12.0` (`tags/v3.12.0:0fb18b0`)
- **Virtual Environment Path**: `D:\MarineShield\MarineShield\.venv`
- **Execution Mode**: Isolated Virtual Environment (`sys.prefix != sys.base_prefix`)

### **Relevant Currently Installed Packages**
| Package | Installed Version | Role in Member 4 Subsystem |
| :--- | :--- | :--- |
| **`numpy`** | `2.5.2` | Vectorized evidence matrix multiplication, weight calculations, dot products |
| **`torch`** | `2.11.0+cu128` | Deep learning backbone (shared environment with Member 2) |
| **`typing_extensions`** | `4.16.0` | Type hint annotations for complex investigation schemas |

---

## 3. Packages Required by Member 4 in Future Tasks

As development progresses to feature implementation, Member 4 will require the following additional libraries (to be installed strictly when features require them):

| Category | Package Name | Functional Purpose |
| :--- | :--- | :--- |
| **Data Validation & Schemas** | `pydantic` (v2+) | API request/response validation for evidence score payloads (`.agents/rules/api_contracts.md`) |
| **Vector Geospatial Analysis** | `shapely`, `geopandas`, `pyproj` | Spatial buffer checks, estimated release region polygon geometry operations, area calculations |
| **Database Operations** | `sqlalchemy`, `asyncpg` / `psycopg2-binary` | Querying PostGIS candidate vessel tracks, AIS anomaly tables, and storing evidence records |
| **Testing & Coverage** | `pytest`, `pytest-cov` | Automated test suite execution, parametric evidence testing, and code coverage measurement |
| **Scientific Computing** | `scipy` | Probability density calculations and score calibration statistics |

---

## 4. Windows-Native Dependency & Environment Risks

1. **Timezone Enforcement & System Clock Defaults**:
   - *Risk*: Windows default system clock operates in local time (e.g. `IST / UTC+5:30`). Naive `datetime.now()` calls without explicit `tzinfo` risk corrupting spatio-temporal queries or violating ISO 8601 UTC standards (`YYYY-MM-DDTHH:MM:SSZ`).
   - *Mitigation*: Strictly enforce `datetime.now(timezone.utc)` and string formatting `%Y-%m-%dT%H:%M:%SZ` across all temporal scoring functions.

2. **Geospatial Native C-Binaries (GEOS / GDAL / PROJ)**:
   - *Risk*: Installing vector GIS tools (`shapely`, `geopandas`, `fiona`) on Windows can encounter DLL missing errors or binary build failures if installed from raw source tarballs instead of pre-compiled wheels.
   - *Mitigation*: Ensure wheel installations (`pip install shapely geopandas`) utilize official PyPI pre-compiled binary wheels containing embedded GEOS DLLs.

3. **File Path Handling & Line Endings (`CRLF` vs `LF`)**:
   - *Risk*: Windows path separators (`\`) and default file encoding (`cp1252`) can cause cross-platform JSON parsing failures or malformed file URIs.
   - *Mitigation*: Enforce `pathlib.Path` for all path manipulations and mandate `encoding="utf-8"` on all file I/O operations.

4. **Floating-Point Determinism Across Platforms**:
   - *Risk*: Differences in underlying C math libraries between Windows MSVC and Linux GCC can introduce sub-microscopic floating-point deltas in score calculations.
   - *Mitigation*: Use standard rounding and tolerance thresholds (`math.isclose(a, b, abs_tol=1e-6)`) during score assertions.

---

## 5. Factors Affecting the Investigation Subsystem

1. **Strict Support for `UNKNOWN` Classification**:
   - The evidence engine MUST NOT force vessel attribution when evidence criteria are not met. The system status MUST safely default to `UNKNOWN` with zero artificial percentage inflation.
2. **Counterfactual Score Stability**:
   - Hypothesis ranking tests require deterministic delta computation when the top candidate vessel is temporarily removed from the hypothesis set.
3. **No-Hindsight Hindsight Bias Prevention**:
   - Verification suites for historical incident replays must enforce temporal slicing ($t \le t_{obs}$) to prevent future AIS data or weather parameters from leaking into evidence calculation logic.

---

## 6. Empirical Test Execution Results

Two verification suites were created and executed:
1. **Script Verification** ([`scripts/verify_member4_environment.py`](file:///d:/MarineShield/MarineShield/scripts/verify_member4_environment.py)):
   - Command: `python scripts/verify_member4_environment.py`
   - Outcome: **Passed (Code 0)** — Verified 100-run float determinism, NumPy dot product matching, ISO 8601 UTC parsing, JSON serialization/deserialization, and UTF-8 filesystem operations.
2. **Unit Test Suite Discovery** ([`tests/unit/test_member4_environment.py`](file:///d:/MarineShield/MarineShield/tests/unit/test_member4_environment.py)):
   - Command: `python -m unittest discover -s tests/unit -p "test_*.py"`
   - Outcome: **5/5 Tests Passed (0.022s)** — Zero diagnostic errors, zero failures.

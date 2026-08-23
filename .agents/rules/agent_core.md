---
trigger: always_on
---

# MarineShield Agent Core Rules

These rules govern all AI agents, subagents, and automated coding assistants working on the MarineShield codebase.

## 1. Architectural Integrity & System Pre-requisites
- **Read Architecture First**: Always read [`docs/architecture/ARCHITECTURE.md`](file:///d:/MarineShield/MarineShield/docs/architecture/ARCHITECTURE.md) and [`docs/architecture/WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md) before designing, modifying, or creating any code files.
- **Inspect Before Creation**: Always inspect existing module implementations, utility files, schemas, and tests before creating new files or writing duplicate functions.
- **Respect Workstream Ownership**: Check [`WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md) to ensure changes stay strictly within assigned workstream ownership boundaries (Person 1, Person 2, Person 3, or Person 4).
- **Never Silently Redesign**: Never modify, bypass, or redesign system architecture, pipeline stages, or API contracts without explicit recorded agreement and documentation in [`DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).

## 2. Scientific & Domain Constraints
- **Prefer Established Scientific Libraries**: Use established tools (e.g., PyGNOME for drift modeling, ESA SNAP / GDAL / Rasterio for SAR processing, PostGIS for geospatial indexing) instead of custom physics or geometry implementations.
- **Benchmark Before Replacing**: Any alternative ML architecture or processing model must be benchmarked against baseline validation metrics before adoption.
- **Record Sources & Licenses**: Record and track data provenance, dataset sources, external pre-trained model weights, and open-source licenses for all external components.
- **Timestamps Must Be UTC**: All timestamps throughout APIs, database tables, models, and UI payloads MUST be ISO 8601 UTC string standard (`YYYY-MM-DDTHH:MM:SSZ` or UTC UNIX timestamps).
- **Unknown is a Valid Output**: The system MUST explicitly support `Unknown` or `Insufficient Evidence` as valid outputs for source attribution and classification. Never force false certainty.
- **Evidence Compatibility != Legal Guilt**: Evidence scores represent spatial-temporal compatibility rankings. Never output legal guilt declarations, criminal terminology, or uncalibrated probabilities as legal proof.
- **Never Fabricate Confidence**: Confidence scores must originate from empirical model probabilities or calibrated evidence weights. Never generate synthetic or arbitrary random percentage metrics.
- **No Black-Box Chatbots for Evidence**: LLMs MUST NOT act as evidence calculation or operational decision authorities. Structured, deterministic evidence algorithms are mandatory for incident investigation.

## 3. Engineering & Code Guidelines
- **Frontend Scoping**: Frontend / WebGIS layers must function as visualization and decision-support command interfaces only. Frontend components MUST NOT contain business intelligence, ML inference, drift calculations, or evidence scoring logic.
- **Database Migrations Required**: All database schema changes MUST be implemented via explicit version-controlled migration scripts (e.g., Alembic / PostGIS migrations). Never alter production schemas manually.
- **API Contract Synchronization**: Any modification to API endpoints or data structures MUST be updated in the OpenAPI specification and documented in `docs/api/`.
- **ML Output Provenance**: All ML pipeline outputs (spill polygons, look-alike scores, SAR vessel matches) must include provenance metadata (model version, dataset ID, processing timestamp, pipeline parameters).
- **Never Commit Secrets**: API keys, database passwords, token secrets, and private credentials MUST be read from environment variables or secure secret managers. Never commit raw credentials.
- **Test Before Completing**: Never declare completion of any task without running unit tests, integration tests, and build checks, and verifying zero diagnostic or execution errors.
- **Report Blockers Honestly**: If a task cannot be completed due to missing dependencies, uncalibrated data, or structural blockers, report the exact failure and diagnostic log honestly to the team.

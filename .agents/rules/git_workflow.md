---
trigger: always_on
---

# MarineShield Git Workflow & Branching Guidelines

## 1. Branch Naming Conventions
- **Feature Branches**: `feat/workstream-<person_id>-<short_description>` (e.g. `feat/workstream-p1-lookalike-classifier`)
- **Bug Fix Branches**: `fix/workstream-<person_id>-<short_description>` (e.g. `fix/workstream-p2-ais-reconciliation-bug`)
- **Docs & Spec Branches**: `docs/<short_description>` (e.g. `docs/api-spec-update`)

## 2. Commit Message Standards
Use Conventional Commits format:
- `feat(ml): add look-alike rejection inference pipeline`
- `fix(ais): correct spatial buffer calculation for SAR-AIS matching`
- `docs(arch): update WORKSTREAMS.md module assignments`
- `test(drift): add PyGNOME ensemble trajectory unit test`

## 3. Pull Request & Merging Rules
- Every PR must target `main` and undergo automated syntax, linting, and unit test verification.
- PRs modifying core architecture, API contracts, or database schemas MUST be linked to an update in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).
- Never force push (`git push --force`) to `main`.
- Large model weight files or raw SAR granules (>50MB) MUST NOT be committed directly to Git. Use object storage references or Git LFS if strictly required.

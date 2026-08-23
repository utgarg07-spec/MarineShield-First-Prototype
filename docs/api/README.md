# MarineShield API Specifications

This directory contains the authoritative API contracts, domain schema specifications, and OpenAPI endpoint definitions for MarineShield.

## Domain Contract Documents
- [`INVESTIGATION_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/api/INVESTIGATION_CONTRACTS.md) — Canonical Investigation & Attribution Domain Contracts (Member 4 / Person 1).

## Core API Endpoints Overview
- `/api/v1/incidents` — Incident creation, retrieval, and lifecycle status management.
- `/api/v1/detection` — SAR scene upload, segmentation trigger, and spill polygon retrieval.
- `/api/v1/vessels` — AIS vessel tracking, SAR vessel detections, and AIS-SAR match records.
- `/api/v1/attribution` — Release region estimates, evidence scoring breakdown, counterfactual results, and hypothesis ranking.
- `/api/v1/forecast` — PyGNOME drift trajectory ensemble predictions and what-if scenario simulations.
- `/api/v1/threats` — Environmental threat intersection, asset ETA, and MarineShield Response Priority ($0-100$).
- `/api/v1/replay` — Historical Incident Time Machine execution and evaluation endpoints.

> All endpoints must conform to [`.agents/rules/api_contracts.md`](file:///d:/MarineShield/MarineShield/.agents/rules/api_contracts.md).


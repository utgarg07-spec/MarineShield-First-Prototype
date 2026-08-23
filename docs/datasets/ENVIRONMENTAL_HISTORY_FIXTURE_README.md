# Environmental History Fixture (Development)

**IMPORTANT: This is synthetic development data. It does NOT authorize production forecast implementation.**

This document describes the synthetic environmental history fixture used for Phase 6 Member 4 integration testing of the release-reconstruction and source-investigation engine.

## Dataset Details
- **Provider:** `synthetic-development-fixture`
- **Dataset Name:** `marineshield-phase6-environment-demo`
- **Dataset Version:** `0.1.0-dev`
- **Data Mode:** `SYNTHETIC_DEVELOPMENT_FIXTURE`

## Spatial & Temporal Grid
- **Grid Size:** Deterministic 3 x 3 regular latitude/longitude grid.
- **Location:** Centered around latitude `19.0` and longitude `73.0`.
- **Temporal Resolution:** 3 hourly records before the investigation timestamp (`2024-01-20T00:55:41Z`).
- **No Future Data:** This dataset guarantees that no future records exist beyond the investigation timestamp.

## Purpose
The exact synthetic values in this fixture are not scientific claims; they exist only to test:
- Loading mechanisms
- Timestamp filtering (rejecting future data)
- Provenance tracking
- Deterministic behavior of the investigation engine

This fixture guarantees deterministic, reproducible integration testing without relying on external live APIs or production data.

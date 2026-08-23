# MarineShield Database & PostGIS Schemas

This directory contains database schema specifications, PostGIS spatial table structures, and versioned migration rules.

## Core Spatial Tables Specification
- `incidents`: Central incident record, status, detection timestamp, severity class, overall response priority.
- `spill_polygons`: Geospatial polygons (`GEOMETRY(Polygon, 4326)`), confidence masks, area ($\text{km}^2$), perimeter, and centroid.
- `vessel_tracks`: Spatial vessel positions (`GEOMETRY(Point, 4326)` / LineString), MMSI, velocity over ground, course over ground, timestamp.
- `sar_vessels`: SAR-detected ship locations, bounding geometries, radar intensity features.
- `ais_sar_matches`: Reconciliation match scores, candidate distance, heading delta, match status.
- `sensitive_zones`: Environmental GIS layers (mangroves, MPAs, fishing zones, ports, coastline) with spatial `GIST` indexes.
- `drift_forecasts`: Forecast particle distributions and uncertainty polygons at $+6\text{h}, +12\text{h}, +24\text{h}, +48\text{h}$.

> All tables must conform to `.agents/rules/database_rules.md`.

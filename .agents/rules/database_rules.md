---
trigger: always_on
---

# MarineShield Database & PostGIS Rules

## 1. Engine & Extensions
- Primary database: **PostgreSQL 15+** with **PostGIS 3+** extensions enabled.
- Spatial coordinate reference system: **WGS 84 (`EPSG:4326`)** for all stored geometry objects.

## 2. Spatial Table Standards
- All spatial tables (`incidents`, `spill_polygons`, `vessel_tracks`, `sensitive_zones`, `sar_observations`) must use standard PostGIS `GEOMETRY` or `GEOGRAPHY` column types.
- **Spatial Indexing**: Mandatory `GIST` or `SP-GiST` spatial indexes on all geometry columns.
- **Temporal Indexing**: Mandatory B-Tree indexes on timestamp columns (`created_at`, `acquisition_time`, `timestamp_utc`) to accelerate spatio-temporal queries.

## 3. Migration & Security Rules
- Schema mutations must be authored as explicit versioned migration scripts.
- Enable Row-Level Security (RLS) policies for tenant/role access where multi-agency isolation is required.
- Never store raw binary satellite rasters directly inside PostgreSQL columns. Store raster file metadata, bounding boxes, and cloud storage URIs (S3/MinIO) in the database.

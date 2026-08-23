# WebGIS Handoff Regression Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Comprehensive comparison between `MARINESHIELD_WEBGIS_LAYERS_HANDOFF.md` specification and the current `MapContainer.tsx`, `MapWorkspace.tsx`, and `RightInspector.tsx` implementation.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE — READY FOR CODE RESTORATION

---

## 1. MapLibre Source & Layer Registry Audit Matrix

| WebGIS System | Handoff Source ID | Handoff Layer IDs | Current Code Status | Missing / Regressed Items |
| :--- | :--- | :--- | :--- | :--- |
| **SAR WebGIS** | `sar-footprint` | `sar-fill-layer`<br>`sar-outline-layer` | Partial | Source `sar-footprint` and layers `sar-fill-layer`, `sar-outline-layer` are missing. Current code only renders `person1-spill-detection`. |
| **Forecast WebGIS** | `forecast-trajectory-source`<br>`forecast-timesteps-source`<br>`forecast-uncertainty-source` | `forecast-trajectory-layer`<br>`forecast-timesteps-layer`<br>`forecast-timesteps-label-layer`<br>`forecast-uncertainty-fill`<br>`forecast-uncertainty-outline` | Missing | All 3 forecast sources and 5 forecast layers specified in the handoff are completely missing from `MapContainer.tsx`. |
| **Threat WebGIS** | `threat-assets-source`<br>`threat-intersections-source` | `threat-assets-fill`<br>`threat-assets-outline`<br>`threat-assets-label`<br>`threat-intersections-fill`<br>`threat-intersections-outline` | Missing | All 2 threat sources and 5 threat layers specified in the handoff are completely missing from `MapContainer.tsx`. |
| **Vessels WebGIS** | `vessels-source` | `vessels-circle-layer`<br>`vessels-label-layer` | Present | Source and layers exist. Click handlers are bound, but require seamless synchronization with shared selection state. |
| **Spill & Release** | `person1-spill-detection`<br>`person1-release-reconstruction` | `person1-spill-detection-fill`<br>`person1-spill-detection-line`<br>`person1-release-reconstruction-fill`<br>`person1-release-reconstruction-line` | Present | Present and working for Person 1 canonical outputs. Must coexist cleanly with SAR footprint layers. |

---

## 2. Identified Gap Analysis

1. **Missing SAR Footprint WebGIS Registry:**
   - Handoff requires source `sar-footprint` using `scene.spatial_reference.footprint_geojson` from `sarScenes[0]`.
   - Fill layer `sar-fill-layer` (`rgba(6, 182, 212, 0.25)`) and outline layer `sar-outline-layer` (`#06b6d4`, line-width 2.5) must be registered and respond to `sarVisible` state.
2. **Missing Forecast Trajectory, Timesteps, & Uncertainty Layers:**
   - `forecast-trajectory-source` & `forecast-trajectory-layer` (LineString, `#3b82f6`, width 3.5).
   - `forecast-timesteps-source`, `forecast-timesteps-layer` (circle, `#60a5fa`), and `forecast-timesteps-label-layer` (symbol `+6h`, `+12h`, etc.).
   - `forecast-uncertainty-source`, `forecast-uncertainty-fill` (`rgba(59, 130, 246, 0.18)`), and `forecast-uncertainty-outline` (`#3b82f6`, line-dasharray `[3, 2]`).
3. **Missing Threat Sensitive Assets & Intersections Layers:**
   - `threat-assets-source`, `threat-assets-fill` (dynamic color: very high `#ef4444`, high `#f97316`, moderate `#eab308`), `threat-assets-outline`, and `threat-assets-label`.
   - `threat-intersections-source`, `threat-intersections-fill` (`rgba(245, 158, 11, 0.35)`), and `threat-intersections-outline` (`#f59e0b`).
4. **Click Handlers & Selection State Wiring:**
   - Clicking `sar-fill-layer` calls `onSarSelectRef.current(scene)`.
   - Clicking `forecast-trajectory-layer` or `forecast-timesteps-layer` calls `onForecastSelectRef.current(forecast)`.
   - Clicking `threat-assets-fill` or `threat-intersections-fill` calls `onThreatSelectRef.current(threatAssessment)`.
5. **Fixture Availability:**
   - `mockSARScene` (`sar.ts`): Contains valid `spatial_reference.footprint_geojson` Polygon.
   - `mockForecastSucceeded` (`forecasts.ts`): Contains valid LineString trajectories, timesteps, and particle uncertainty regions.
   - `mockThreatSucceeded` (`threats.ts`): Contains valid sensitive asset polygons (`assets`) and threat intersection polygons (`threat_geometries`).
6. **Files Requiring Minimal Changes:**
   - [`frontend/src/map/MapContainer.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/map/MapContainer.tsx)
   - [`frontend/src/layouts/MapWorkspace.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/layouts/MapWorkspace.tsx)
   - [`frontend/src/pages/MapPage.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/pages/MapPage.tsx)
   - [`frontend/src/pages/IncidentDetailPage.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/pages/IncidentDetailPage.tsx)

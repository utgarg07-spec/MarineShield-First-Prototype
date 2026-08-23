# Forecast Reference Behavior Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Diagnose gaps in Forecast WebGIS trajectory rendering, timestep selection, translucent selection halo, and RightInspector details against Person 4 reference behavior.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE — READY FOR FORECAST WEBGIS REPAIR

---

## 1. Current Forecast Architecture Audit

| Audit Parameter | Current Implementation Status | Identified Gaps / Gaps vs Reference Behavior |
| :--- | :--- | :--- |
| **Fixture Path** | `frontend/src/mocks/fixtures/forecasts.ts` (`mockForecastSucceeded`) | Fixture contains full contract data: `trajectory` LineStrings, 4 `timesteps` (+6h, +12h, +24h, +48h), and `uncertainty.regions`. |
| **Trajectory Source & Layer** | `forecast-trajectory-source`<br>`forecast-trajectory-layer` | Source & layer are present (`#3b82f6`, width 3.5). MapLibre visibility toggles correctly. |
| **Timestep Dot Source & Layer** | `forecast-timesteps-source`<br>`forecast-timesteps-layer` | Source & circle layer (`#60a5fa`, radius 7) are present on map canvas. |
| **Timestep Label Layer** | `forecast-timesteps-label-layer` | Symbol layer renders `+6h`, `+12h`, `+24h`, and `+48h` labels correctly. |
| **Uncertainty Source & Layers** | `forecast-uncertainty-source`<br>`forecast-uncertainty-fill`<br>`forecast-uncertainty-outline` | Source & polygon layers (`rgba(59, 130, 246, 0.18)`) are present on map canvas. |
| **Selected Timestep Halo Layer** | **MISSING** | `forecast-selected-timestep-source` & `forecast-selected-timestep-halo` are missing from `MapContainer.tsx`. No blue translucent halo surrounds the clicked dot. |
| **Timestep Selection Callback** | Partial | Clicking a timestep dot calls `onForecastSelect(forecast)` but does NOT attach the clicked `activeTimestep` (+6h, +12h, +24h, +48h) to `selectedForecast`. |
| **RightInspector Mapping** | Incomplete | `RightInspector.tsx` only renders `selectedForecast.status` and `forecast_id`. It does NOT render selected horizon, valid time, coordinates, engine provenance, or data mode. |
| **Selected Intelligence Banner** | Generic | `MapWorkspace.tsx` displays `Forecast df22d41b...` instead of indicating the active timestep horizon (e.g. `Forecast (+6h)`). |
| **Incidents Detail Integration** | Partial | Clicking `View Forecast` or horizon badges (+6h, +12h, +24h, +48h) on `IncidentDetailPage.tsx` does NOT update the active selected timestep. |

---

## 2. Root Cause Analysis

1. **Missing Translucent Blue Halo Layer:**
   - MapLibre lacks `forecast-selected-timestep-source` and `forecast-selected-timestep-halo` (type `circle`, radius ~16-20, `fill-color: rgba(59, 130, 246, 0.3)`, `stroke-color: #3b82f6`).
2. **Missing Active Timestep State Payload:**
   - `onForecastSelect` only passed the raw `forecast` object without identifying which specific timestep (`+6h`, `+12h`, `+24h`, or `+48h`) was clicked.
3. **Incomplete RightInspector Card:**
   - `RightInspector.tsx` lacked structured rendering for `selectedForecast.activeTimestep` (horizon hours, valid time, coordinates, engine provenance, dataset versions, and data mode `MOCK_HYBRID`).

---

## 3. Minimal Repair Plan

1. **`frontend/src/api/types/forecast.ts`:**
   - Add optional `activeTimestep?: ForecastTimestep | null;` to `Forecast` interface.
2. **`frontend/src/map/MapContainer.tsx`:**
   - Register `forecast-selected-timestep-source` & `forecast-selected-timestep-halo` (radius 18, `rgba(59, 130, 246, 0.35)` fill, `#3b82f6` stroke, width 2).
   - In `m.on('click', 'forecast-timesteps-layer')`, extract feature `horizon_hours`, find matching `ForecastTimestep`, attach `activeTimestep` to `forecast`, update `onForecastSelect`, and set halo GeoJSON data.
   - When `forecastVisible` is toggled OFF, clear/hide `forecast-selected-timestep-halo`.
3. **`frontend/src/layouts/RightInspector.tsx`:**
   - Upgrade Forecast Card to render `activeTimestep.horizon_hours` (`+6h`, `+12h`, `+24h`, `+48h`), `valid_time`, `position.coordinates`, PyGNOME model engine, and data mode `MOCK_HYBRID`.
4. **`frontend/src/layouts/MapWorkspace.tsx`:**
   - Format Selected Intelligence Banner title for Forecast: e.g. `Forecast (+6h)` when `activeTimestep` exists.
5. **`frontend/src/pages/IncidentDetailPage.tsx`:**
   - Wire domain horizon buttons (`+6h`, `+12h`, `+24h`, `+48h`) to invoke `setSelectedForecast` with the corresponding `activeTimestep`.

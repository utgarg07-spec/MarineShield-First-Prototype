# Default-OFF Forecast Regression Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root-cause analysis of Forecast trajectory and timestep behavior when layers initialize OFF by default.  
**Audit Timestamp:** 2026-08-23 (UTC)  

---

## 1. Exact Cause of Forecast Regression

When layer visibility states (`sarVisible`, `vesselsVisible`, `forecastVisible`, `threatVisible`) were changed from `true` to `false` in `MapContainer.tsx`:
1. `forecastVisible` initialized to `false`.
2. On initial mount, `updateForecastLayers()` entered its `else` branch: setting `forecast-trajectory-layer`, `forecast-timesteps-layer`, `forecast-timesteps-label-layer`, and uncertainty layers to `visibility: 'none'`.
3. When `forecast` data finished loading asynchronously from `api.getForecast(...)`, `updateForecastLayers()` checked `if (forecastVisible && hasTrajectory && activeForecast?.trajectory)`. Because `forecastVisible` was `false`, it remained in the `else` branch, keeping the layers hidden.
4. When `selectedForecast` was selected or when a user clicked the Forecast toggle button, `forecastVisible` changed to `true`. However, if `updateForecastLayers()` ran before `forecast` state was synchronized with `selectedForecast` (or if `activeForecast` was `null`), the layer visibility property was not set correctly or required a second render.

---

## 2. Forecast State Variables & Initialization Points

- **`MapContainer.tsx`:**
  - `forecast` (`Forecast | null`): Loaded via `api.getForecast(incId, ...)`.
  - `forecastVisible` (`boolean`): Initialized to `false`.
  - `selectedForecast` (`Forecast | null`): Received as prop from `MapWorkspace` / `AppShell` context.
- **Sync Effect:**
  - `useEffect` monitors `selectedForecast`. When non-null, sets local `forecast = selectedForecast` AND `forecastVisible = true`.
- **Mount Locations:**
  - `MapPage.tsx` -> mounts `MapWorkspace` -> mounts `MapContainer`.
  - `IncidentDetailPage.tsx` -> mounts `MapWorkspace` -> mounts `MapContainer`.

---

## 3. Forecast Sources & Layers Registry

- **Sources:**
  - `forecast-trajectory-source` (LineString centerline)
  - `forecast-timesteps-source` (Point timesteps +6h, +12h, +24h, +48h)
  - `forecast-uncertainty-source` (Particle spread polygons)
  - `forecast-selected-timestep-source` (Active timestep halo Point)
- **Layers:**
  - `forecast-trajectory-layer` (`line`, `#3b82f6`, width 3.5)
  - `forecast-timesteps-layer` (`circle`, `#60a5fa`, radius 8, white stroke)
  - `forecast-timesteps-label-layer` (`symbol`, text `+6h`, `+12h`, `+24h`, `+48h`)
  - `forecast-uncertainty-fill` & `forecast-uncertainty-outline`
  - `forecast-selected-timestep-halo` (`circle`, radius 18, `rgba(59, 130, 246, 0.35)` fill, `#3b82f6` stroke)

---

## 4. Timestep Feature IDs & Click Handlers

- Every timestep feature receives a stable GeoJSON `id: ts.horizon_hours` (`6`, `12`, `24`, `48`).
- Click listeners are registered on:
  - `forecast-timesteps-layer`
  - `forecast-timesteps-label-layer`
  - `forecast-selected-timestep-halo`
- In click handlers, `horizon_hours` is parsed directly via `feat?.properties?.horizon_hours ?? feat?.id`, matching `ForecastTimestep` and enriching `selectedForecast.activeTimestep`.

---

## 5. Minimal Fix Plan

1. In `MapContainer.tsx`, keep initial defaults as `false`:
   - `sarVisible`: `false`
   - `vesselsVisible`: `false`
   - `forecastVisible`: `false`
   - `threatVisible`: `false`
2. Ensure `updateForecastLayers()`, `updateVesselLayers()`, `updateThreatLayers()`, and `updateSarFootprintLayers()` correctly construct and register sources/layers even when initially hidden (`visibility: 'none'`), so that when toggled `ON`, data is immediately available and rendered.
3. In layer control button `onClick` handlers, immediately calculate `next = !v`, set layout property visibility to `next ? 'visible' : 'none'`, and trigger source data updates cleanly without requiring a second toggle.

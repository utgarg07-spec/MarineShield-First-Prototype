# Forecast, Vessel, & Threat WebGIS Bug Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root-cause analysis of Incident tab forecast trajectory visibility, timestep clickability & halo rendering (+6h, +12h, +24h, +48h), and first-toggle visibility race conditions for Vessels and Threat layers.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE — READY FOR FIXES

---

## 1. Component Mounting & Prop Flow Matrix

| Parameter | MapPage.tsx | IncidentDetailPage.tsx |
| :--- | :--- | :--- |
| **Map Workspace Mount** | Mounts `MapWorkspace` | Mounts `MapWorkspace` |
| **Incident Context** | `incident` is `undefined` | `incident` fetched via `api.getIncident(incidentId)` |
| **Selected State Props Passed** | Passes `selectedSar`, `selectedVessel`, `selectedForecast`, `selectedThreat` to `MapWorkspace` | Passes `selectedSar`, `selectedVessel`, `selectedForecast`, `selectedThreat` to `MapWorkspace` |
| **MapContainer Props** | `MapWorkspace` previously omitted `selectedForecast`, `selectedVessel`, `selectedThreat` props when passing to `MapContainer` | `MapWorkspace` previously omitted `selectedForecast`, `selectedVessel`, `selectedThreat` props when passing to `MapContainer` |

---

## 2. Root Cause Analysis of Reported Bugs

### Bug 1: Forecast Trajectory Visible on Map Tab but Missing on Incidents Tab
- **Root Cause:** `MapWorkspace.tsx` did not forward `selectedForecast` to `MapContainer.tsx`. On `IncidentDetailPage`, selecting "View Forecast" or clicking a horizon button (+6h, +12h, +24h, +48h) updated `selectedForecast` in `AppShell` context, but `MapContainer` maintained an isolated `forecastVisible` state that defaulted to `false` or remained out of sync.
- **Fix:** Pass `selectedForecast`, `selectedVessel`, `selectedThreat` props into `MapContainer.tsx`. In `MapContainer.tsx`, when `selectedForecast` is non-null, automatically force `forecastVisible` to `true` and apply layout visibility to all forecast layers.

### Bug 2: Timestep Clickability (+24h, +48h) & Selection Halo Stuck on +6h
- **Root Cause 1 (Label Layer Interception):** Click handlers were bound to `forecast-timesteps-layer` (circle), but NOT to `forecast-timesteps-label-layer` (symbol label). Clicking on or near the text labels `+24h` or `+48h` hit the label symbol layer instead of the circle layer.
- **Root Cause 2 (Fallback to +6h):** In `MapContainer.tsx`, `forecast.timesteps.find(...) || forecast.timesteps[0]` defaulted to `forecast.timesteps[0]` (+6h) whenever property lookup failed or returned `NaN`.
- **Root Cause 3 (Missing Feature IDs):** Timestep GeoJSON point features lacked explicit `id` attributes matching `horizon_hours`.
- **Fix:**
  1. Add explicit `id: ts.horizon_hours` to every timestep GeoJSON point feature.
  2. Bind click handlers to BOTH `forecast-timesteps-layer` AND `forecast-timesteps-label-layer` (and `forecast-selected-timestep-halo`).
  3. Robustly resolve `horizon_hours` without defaulting to `forecast.timesteps[0]`.

### Bug 3: First-Toggle Race Condition for Vessel and Threat Layers
- **Root Cause:** Initial state variables (`vesselsVisible`, `threatVisible`) in `MapContainer.tsx` defaulted to `true`, but telemetry fixtures (`aisObservations`, `threatAssessment`) were `null` / `[]` during the initial 300-400ms fetch delay.
  - On map load, `updateVesselLayers()` and `updateThreatLayers()` ran with empty features.
  - When the user clicked the button for the first time, the toggle handler flipped visibility from `true` to `false` (OFF).
  - On the second click, visibility flipped from `false` to `true` (ON), making the layer finally appear.
- **Fix:** Initialize `vesselsVisible`, `threatVisible`, and `forecastVisible` cleanly. When data arrives or when state is toggled ON, idempotently ensure sources/layers are registered AND layout property visibility is explicitly set to `'visible'`.

---

## 3. Minimal Repair Plan

1. **`frontend/src/layouts/MapWorkspace.tsx`:**
   - Forward `selectedSar`, `selectedVessel`, `selectedForecast`, `selectedThreat` to `MapContainer`.
2. **`frontend/src/map/MapContainer.tsx`:**
   - Add `selectedSar`, `selectedVessel`, `selectedForecast`, `selectedThreat` to `MapContainerProps`.
   - In `useEffect`, if `selectedForecast` is active, sync `forecastVisible = true` and `activeTimestep`.
   - Update `forecast-timesteps-source` features with `id: ts.horizon_hours`.
   - Attach click handlers to `forecast-timesteps-layer`, `forecast-timesteps-label-layer`, and `forecast-selected-timestep-halo`.
   - Ensure first click on Vessel or Threat toggle immediately sets layout visibility to `'visible'` and updates layers.
3. **`frontend/src/pages/IncidentDetailPage.tsx`:**
   - Ensure horizon buttons (+6h, +12h, +24h, +48h) pass the selected timestep cleanly into `setSelectedForecast`.

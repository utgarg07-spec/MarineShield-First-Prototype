# Default Layer State Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Identify exact state variable declarations causing WebGIS intelligence layers (Threat, Forecast, Vessels, SAR Layer) to initialize ON by default.  
**Audit Timestamp:** 2026-08-23 (UTC)  

---

## 1. Initialized Visibility State Variables

All layer visibility state variables are defined inside `frontend/src/map/MapContainer.tsx`:

| State Variable Name | Target Layer Control | Previous Initial Value | Proposed Initial Value |
| :--- | :--- | :---: | :---: |
| `sarVisible` | SAR Coverage Polygon Layer | `true` | `false` |
| `vesselsVisible` | AIS & SAR Vessel Markers | `true` | `false` |
| `forecastVisible` | PyGNOME Trajectory Line & Timesteps | `true` | `false` |
| `threatVisible` | Sensitive Asset & Intersection Polygons | `true` | `false` |

---

## 2. Root Cause Analysis of Default-ON Behavior

1. **Explicit `true` Defaults in `useState` Hook:**  
   In `MapContainer.tsx` (lines 67, 69, 77, 80), the initial state values were explicitly set to `useState<boolean>(true)` for all four intelligence domains.
2. **Initial Layer Construction:**  
   When the map component mounted and MapLibre layers were created (`updateSarFootprintLayers`, `updateVesselLayers`, `updateForecastLayers`, `updateThreatLayers`), layout property visibility was evaluated using the default `true` state, setting MapLibre layer visibility to `'visible'`.

---

## 3. Minimal Solution Plan

- Modify the default value of `sarVisible`, `vesselsVisible`, `forecastVisible`, and `threatVisible` in `frontend/src/map/MapContainer.tsx` from `true` to `false`.
- Ensure MapLibre layers initialize with layout property `visibility: 'none'`.
- Ensure that clicking any layer control once turns the layer `ON` (`true`) and sets MapLibre layout property `visibility: 'visible'` immediately on the first click.

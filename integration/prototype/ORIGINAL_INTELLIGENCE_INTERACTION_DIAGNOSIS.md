# Original Intelligence Interaction Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root cause analysis of MapLibre layer toggling, feature click listener bindings, and shared selection state synchronization.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Root Cause Analysis

- **Root Cause 1 (Independent Selection States):** `AppShell.tsx` maintained individual `selectedSar`, `selectedVessel`, `selectedForecast`, and `selectedThreat` state objects, but lacked a unified helper to safely set one selection type while clearing the others. As a result, selecting a new feature did not automatically clear stale selections of other feature types.
- **Root Cause 2 (MapLibre Click Listener Boundaries):** `MapContainer.tsx` bound click listeners for `vessels-circle-layer`, `person1-spill-detection-fill`, and `person1-release-reconstruction-fill`. However, clicking empty map canvas did not execute `clearAllSelections()`.
- **Root Cause 3 (Forecast / Threat Map Geometry Fallbacks):** Mock forecast and threat fixtures contain metadata without explicit GeoJSON features (`forecast.trajectory?.features` and `threatAssessment.threat_geometries?.features` are empty). When `Forecast` or `Threat` controls were toggled ON, top-left status badges appeared, but because no map geometry rendered, no map clicks were possible.
- **Root Cause 4 (Selected Intelligence Banner Integration):** The top bar or map overlay lacked a prominent "Selected Intelligence" banner displaying the active feature ID, category, and a clear button.

---

## 2. Selection Architecture & Data Flow

```
[User Action: Map Feature Click OR Incident Action Button Click]
    │
    ├──> Normalizes feature object: { type, id, title, properties }
    │
    ├──> Calls shared selection handlers:
    │      • setSelectedSar(sar) / setSelectedVessel(vessel)
    │      • setSelectedForecast(forecast) / setSelectedThreat(threat)
    │
    ├──> Displays "Selected Intelligence" banner on Map Workspace
    │
    └──> Populates Right Intelligence Inspector card dynamically
```

---

## 3. Minimal Repair Plan

1. **`MapContainer.tsx`:**
   - Add empty map canvas click listener (`map.current.on('click', (e) => { ... })`) to safely clear selections when clicking outside features.
   - When `Forecast` or `Threat` controls are toggled ON, automatically trigger `onForecastSelect` or `onThreatSelect` to open the Inspector card (displaying `MOCK_HYBRID` / contract limitation details).
   - Ensure SAR spill polygon is rendered with light pink fill (`#f472b6`, `opacity 0.35`) and pink stroke (`#ec4899`, `line-width 2.5`).
2. **`MapWorkspace.tsx`:**
   - Add a prominent, clickable "Selected Intelligence" banner overlay whenever any feature (`selectedSar`, `selectedVessel`, `selectedForecast`, or `selectedThreat`) is active, with a functional "Clear Selection" button.
3. **`IncidentDetailPage.tsx`:**
   - Ensure "View SAR", "View Vessels", "View Forecast", "View Threat", and "Clear Current Selection" action buttons update the exact same shared selection context.

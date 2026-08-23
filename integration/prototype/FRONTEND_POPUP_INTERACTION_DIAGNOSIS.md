# Person 4 Frontend Popup Interaction Diagnosis Report

**Target System:** Main MarineShield Project (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root cause analysis of empty Intelligence Inspector & non-responsive map feature popups.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Root Cause Analysis

- **Fixture & Client Sources:**
  - **Incidents:** `MockApiClient.getIncidents()` / `getIncident()` returns approved incident `MS-PHASE6-DEV-001`.
  - **Vessels:** `MockApiClient.getVessels()`, `getSARDetections()`, `getVesselMatches()`, `getUnmatchedVessels()`, `getAnomalies()` returning Person 2 telemetry and match objects.
  - **Forecasts:** `MockApiClient.getForecast()` returning Person 4 forecast mock objects.
  - **Threats:** `MockApiClient.getThreatAssessment()` returning Person 4 threat mock objects.
- **Root Cause of Empty Inspector & Broken Popups:**
  1. **Unpassed Event Callbacks in `MapContainer`:** In `MapContainer.tsx`, the component parameters `onSarSelect`, `onVesselSelect`, `onForecastSelect`, and `onThreatSelect` were declared in props but dropped in the function signature destructuring. Consequently, MapLibre layer click events (`'click'`, `'vessels-circle-layer'`) could not trigger parent selection handlers.
  2. **Unbound MapLibre Click Listeners:** `MapContainer.tsx` was missing click event bindings for Person 1 spill geometry polygons (`person1-spill-detection-fill`) and release reconstruction region polygons (`person1-release-reconstruction-fill`).
  3. **RightInspector Props Wiring:** `AppShell.tsx` renders `RightInspector` passing `selectedSar`, `selectedVessel`, `selectedForecast`, and `selectedThreat`. However, `RightInspector.tsx` only rendered incident header details and did not bind `selectedVessel`, `selectedSar`, `selectedForecast`, or `selectedThreat` payload fields to its UI sections.

---

## 2. Component Selection State Ownership

```
[AppShell.tsx] (Holds selection state: selectedSar, selectedVessel, selectedForecast, selectedThreat)
  │
  ├──> Passes state via Outlet context to pages (IncidentDetailPage.tsx, MapPage.tsx)
  │      │
  │      └──> [MapWorkspace.tsx]
  │             │
  │             └──> [MapContainer.tsx] (Fires onSarSelect, onVesselSelect, onForecastSelect, onThreatSelect on MapLibre click)
  │
  └──> Passes state as props to [RightInspector.tsx] (Renders selected feature intelligence details)
```

---

## 3. Minimal Fix Plan

- **`MapContainer.tsx`:**
  - Destructure `onSarSelect`, `onVesselSelect`, `onForecastSelect`, `onThreatSelect` from props.
  - Restore MapLibre click listeners for `sar-fill-layer`, `vessels-circle-layer`, `forecast-trajectory-layer`, `threat-asset-layer`, `person1-spill-detection-fill`, and `person1-release-reconstruction-fill`.
- **`RightInspector.tsx`:**
  - Add rendering logic for `selectedVessel` (MMSI, speed/heading, match confidence, supporting evidence, contradictions, non-guilt clause).
  - Add rendering logic for `selectedSar` (granule ID, mission, footprint bounds, acquisition timestamp).
  - Add rendering logic for `selectedForecast` (horizon, status, PyGNOME engine label, contract limitation notice).
  - Add rendering logic for `selectedThreat` (threat level, threatened assets, contract limitation notice).
- **`IncidentDetailPage.tsx`:**
  - Connect domain selection buttons ("View SAR", "View Vessels", "View Forecast", "View Threat") to update context state.

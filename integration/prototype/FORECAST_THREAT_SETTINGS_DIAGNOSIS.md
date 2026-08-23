# Forecast, Threat, & Settings Interaction Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root cause analysis of Forecast/Threat visibility toggling, inspector state delivery, and Settings page integration.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Root Cause Analysis

- **Root Cause 1 (Forecast / Threat Map Visibility):** `MapContainer.tsx` maintained `forecastVisible` and `threatVisible` state flags. However, because mock forecast/threat data in `MockApiClient` contains status metadata without spatial GeoJSON line/polygon geometries (`hasForecastGeometry` & `hasThreatGeometry` evaluate to `false`), toggling the buttons displayed only top-left text warning badges rather than opening explicit inspector cards or development overlay panels.
- **Root Cause 2 (Incident Detail Actions Wiring):** In `IncidentDetailPage.tsx`, clicking "View Forecast" or "View Threat" updated selection state. However, if `forecast` or `threat` objects were set, `RightInspector.tsx` rendered forecast/threat cards only if those state variables were non-null, but lacked explicit contract limitation callouts explaining why spatial geometry was absent.
- **Root Cause 3 (Settings Route Fallback):** In `App.tsx`, `/settings` was routed to `PlaceholderPage`. A fully functional `SettingsPage.tsx` component is required to manage demo data mode display, map label toggling, content density preferences, and system status disclosures.

---

## 2. Shared Selection & State Delivery Mapping

```
[User Action: Toggle Forecast / Threat or Click Feature]
    │
    ├──> [MapContainer.tsx] / [IncidentDetailPage.tsx]
    │      │
    │      └──> Updates context: setSelectedForecast(forecast) / setSelectedThreat(threat)
    │             │
    │             └──> [RightInspector.tsx]
    │                    │
    │                    └──> Visually updates card with:
    │                         • Feature Type & ID (truncated with title tooltip)
    │                         • Fixture Metadata (Horizons: +6h, +12h, +24h, +48h / Overall Level: HIGH)
    │                         • Data Mode Badge (MOCK_HYBRID / SYNTHETIC_DEVELOPMENT_FIXTURE)
    │                         • Contract Limitation Banner ("Forecast contract unapproved / geometry unavailable")
```

---

## 3. Minimal Repair Plan

1. **`MapContainer.tsx`:**
   - When `Forecast` or `Threat` controls are toggled ON, automatically dispatch `onForecastSelect(forecast)` or `onThreatSelect(threat)` to open the corresponding intelligence card in `RightInspector`.
   - When toggled OFF, clear the active selection (`onForecastSelect(null)` / `onThreatSelect(null)`).
2. **`RightInspector.tsx`:**
   - Ensure `selectedForecast` and `selectedThreat` render clear, contract-faithful card layouts with truncation, data mode badges, and unavailable geometry explanations.
3. **`SettingsPage.tsx` & Router:**
   - Create `SettingsPage.tsx` with:
     - Read-only **Data Mode Display** (`SYNTHETIC_DEVELOPMENT_FIXTURE / MOCK_HYBRID`).
     - Disabled **Live API Mode Toggle** with tooltip ("Live FastAPI backend is unmounted / returning 501").
     - Functional **Map Labels Toggle** (persisted in `localStorage`).
     - Functional **Compact View / Panel Density Toggle** (persisted in `localStorage`).
     - Functional **Reset UI Preferences** button (resets `localStorage` and confirms reset).
     - Read-only **System Status** dashboard.
   - Update `App.tsx` route for `/settings` to use `SettingsPage.tsx`.

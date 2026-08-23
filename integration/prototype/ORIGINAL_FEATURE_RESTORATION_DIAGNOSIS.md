# Original Feature Restoration Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Inventory of sidebar navigation routes, page implementations, mock fixtures, and inspector cards for prototype restoration.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Page Inventory

- **Existing Functional Pages:**
  - `DashboardPage.tsx` (`/dashboard`) — Active
  - `IncidentListPage.tsx` (`/incidents`) — Active
  - `IncidentDetailPage.tsx` (`/incidents/:incidentId`) — Active
  - `MapPage.tsx` (`/map`) — Active
  - `LandingPage.tsx` (`/`), `LoginPage.tsx` (`/login`), `DesignSystemPage.tsx` (`/design-system`) — Active
- **Placeholder Pages:**
  - `VesselsPage` (`/vessels`) — Renders generic `PlaceholderPage`
  - `EvidencePage` (`/evidence`) — Renders generic `PlaceholderPage`
  - `ForecastPage` (`/forecast`) — Renders generic `PlaceholderPage`
  - `ThreatsPage` (`/threats`) — Renders generic `PlaceholderPage`
  - `ReportsPage` (`/reports`) — Renders generic `PlaceholderPage`
  - `ReplayPage` (`/replay`) — Renders generic `PlaceholderPage`
  - `SettingsPage` (`/settings`) — Renders generic `PlaceholderPage`

---

## 2. Mock Fixture & Data Availability Audit

| Domain | Mock Data Source | Fixture Status | Data Mode Label |
| :--- | :--- | :--- | :--- |
| **Incidents** | `MockApiClient.getIncidents()` | Available (`MS-PHASE6-DEV-001`) | `SYNTHETIC_DEVELOPMENT_FIXTURE` |
| **Vessels** | `MockApiClient.getVessels()`, `getVesselMatches()`, `getUnmatchedVessels()` | Available (Person 2 vessel telemetry) | `SYNTHETIC_DEVELOPMENT_FIXTURE` / `MOCK_HYBRID` |
| **SAR Imagery** | `MockApiClient.getSARScenes()` | Available (Sentinel-1 GRD metadata) | `SYNTHETIC_DEVELOPMENT_FIXTURE` |
| **Forecast** | `MockApiClient.getForecast()` | Available (PyGNOME +48h mock) | `MOCK_HYBRID` |
| **Threat** | `MockApiClient.getThreatAssessment()` | Available (Risk scoring mock) | `MOCK_HYBRID` |
| **Reports** | `MockApiClient.getReports()` | Missing / Partial | `DEVELOPMENT / AWAITING CONTRACT` |
| **Replay** | `MockApiClient.getReplayTimeline()` | Missing / Partial | `DEVELOPMENT / AWAITING CONTRACT` |

---

## 3. Component & Router Restoration Plan

1. **`App.tsx` Router Updates:**
   - Implement dedicated component views for `VesselsPage`, `EvidencePage`, `ForecastPage`, `ThreatsPage`, `ReportsPage`, and `ReplayPage` replacing raw `PlaceholderPage` fallbacks.
2. **Dedicated Page Implementations:**
   - **`VesselsPage.tsx`:** Renders vessel table/cards from `MockApiClient.getVessels()`, `getVesselMatches()`, `getUnmatchedVessels()`. Selecting a vessel updates context state and populates `RightInspector`.
   - **`EvidencePage.tsx`:** Renders SAR scene metadata and Person 1 candidate hypothesis evidence cards (`spill_detection_run1.json`). Selecting evidence populates `RightInspector`.
   - **`ForecastPage.tsx`:** Renders PyGNOME forecast initialization, available timestep horizons (+6h, +12h, +24h, +48h), and contract limitation banner (`MOCK_HYBRID`).
   - **`ThreatsPage.tsx`:** Renders threat summary, sensitive area risk scores, and contract limitation banner (`MOCK_HYBRID`).
   - **`ReportsPage.tsx`:** Renders interactive incident investigation report preview with data-mode limitations.
   - **`ReplayPage.tsx`:** Renders historical incident timeline controls with explicit no-future-data compliance notice.
3. **Data Integrity & Legal Safeguards:**
   - Retain `SYNTHETIC_DEVELOPMENT_FIXTURE` / `MOCK_HYBRID` labels across all restored views.
   - Preserve non-guilt legal disclaimers on vessel and attribution panels.

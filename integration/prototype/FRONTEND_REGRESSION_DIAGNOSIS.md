# Person 4 Frontend Regression Diagnosis Report

**Target System:** Main MarineShield Project (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root cause analysis of "Error Loading Data — Failed to fetch" in Vite dev mode.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Root Cause Analysis

- **Selected Client at Runtime:** In `frontend/src/api/index.ts`, `api` was initialized using:
  ```typescript
  export const api: ApiClient = 
    import.meta.env.VITE_API_MODE === 'mock' 
      ? new MockApiClient() 
      : new FastApiClient();
  ```
- **Root Cause of "Failed to fetch":** When running `npm run dev`, Vite does not define `VITE_API_MODE` by default, causing `import.meta.env.VITE_API_MODE` to evaluate to `undefined`. Consequently, `index.ts` defaults to instantiating `FastApiClient` (`http://localhost:8000`). Because the FastAPI backend server is not running (and backend routes return 501), browser `fetch()` calls fail with a network error (`TypeError: Failed to fetch`).
- **Map Page Behavior:** `MapPage.tsx` mounts `MapWorkspace` which renders `MapContainer`. When `incident` is `null` due to failed API fetches, `MapContainer` displays only the base MapLibre canvas without incident center markers or spatial overlay layers.

---

## 2. Code Path Mapping

1. **Incident Loading Path (`IncidentListPage.tsx`):**
   - Calls `api.getIncidents(searchQuery)`.
   - Passes through `FastApiClient.getIncidents()`, triggering `fetch('http://localhost:8000/api/v1/incidents')`.
   - Throws network exception -> Caught by `catch(err)` -> Sets `setError('Failed to fetch')` -> Renders `ErrorState` UI.
2. **Incident Detail Path (`IncidentDetailPage.tsx`):**
   - Calls `api.getIncident(incidentId)`, `api.getSARScenes()`, `api.getVessels()`, etc.
   - All network calls fail -> Leaves `incident` state as `null`.
3. **Map Layer Path (`MapContainer.tsx`):**
   - Depends on `incident` and API queries (`api.getSARScenes`, `api.getVessels`).
   - Fails silently to load features -> Renders base map canvas without layers.

---

## 3. Minimal Fix Plan

- **File to Modify:** `frontend/src/api/index.ts`
- **Safe Client Selection Logic:**
  - Default to `MockApiClient` when `VITE_API_MODE` is not explicitly set to `'live'` or `'fastapi'`.
  - Instantiate `FastApiClient` ONLY when `import.meta.env.VITE_API_MODE === 'live'` or `import.meta.env.VITE_API_MODE === 'fastapi'`.
- **Data Mode Integrity:** Preserve `SYNTHETIC_DEVELOPMENT_FIXTURE` and `MOCK_HYBRID` labels across all mock client responses.
- **Contract Boundary Safeguard:** Preserve Person 1 presentation contracts (`SpillDetectionResponse`, `InvestigationResult`, `CounterfactualResult`) and keep forecast/threat layers marked as contract-blocked.

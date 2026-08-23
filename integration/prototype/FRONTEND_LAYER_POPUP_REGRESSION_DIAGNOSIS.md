# Frontend Layer & Popup Regression Diagnosis Report

**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Root cause analysis of map layer visibility toggles, SAR polygon styling, and inspector popup interactions.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** DIAGNOSIS COMPLETE

---

## 1. Executive Summary & Root Cause Analysis

- **Root Cause 1 (SAR Layer Fill Styling & Visibility):** In `MapContainer.tsx`, Person 1 spill detection polygon was rendered with a dark red fill (`#ef4444`, `opacity 0.45`) instead of the required light pink translucent fill (`rgba(244, 114, 182, 0.35)` or `#f472b6`) with a visible outline (`#ec4899`). Additionally, toggling the `SAR Layer` button updated internal state but did not apply `setLayoutProperty('visibility', ...)` to the active MapLibre layers.
- **Root Cause 2 (Vessels & Feature Visibility Toggling):** Toggling `Vessels`, `Forecast`, or `Threat` buttons modified React state variables (`vesselsVisible`, `forecastVisible`, `threatVisible`), but `MapContainer.tsx` did not explicitly execute MapLibre `setLayoutProperty(layerId, 'visibility', 'visible' | 'none')` on existing sources.
- **Root Cause 3 (Long ID Overflow in Intelligence Inspector):** In `RightInspector.tsx`, long UUID strings (e.g. granule IDs, incident UUIDs, forecast IDs) rendered without CSS truncation or tooltip wrapping (`truncate`, `break-all`), causing horizontal layout overflow on narrow inspector panels.
- **Root Cause 4 (Map Attribution Compliance):** MapLibre attribution was rendered with CARTO copyright text. Per provider terms, CARTO tile basemaps require attribution. Replacing full text with a compact, compliant attribution control (`customAttribution: '&copy; CARTO'`) ensures legal compliance without cluttering the WebGIS canvas.

---

## 2. Minimal Fix Plan

1. **`MapContainer.tsx`:**
   - Update `person1-spill-detection-fill` paint properties to use light pink translucent fill (`rgba(244, 114, 182, 0.35)`) and distinct pink outline (`#ec4899`, `line-width: 2.5`).
   - Implement explicit MapLibre `setLayoutProperty(layerId, 'visibility', sarVisible ? 'visible' : 'none')` for SAR, Vessel, Forecast, and Threat layers upon state changes.
   - Update MapLibre attribution control to compact compliant format.
2. **`RightInspector.tsx`:**
   - Apply `truncate`, `max-w-[200px]`, `font-mono`, and `title={fullId}` tooltips to all long identifier strings.
3. **Selection & Popup Pipeline:**
   - Verify feature selection works across both Incidents tab and Map tab using stable IDs.

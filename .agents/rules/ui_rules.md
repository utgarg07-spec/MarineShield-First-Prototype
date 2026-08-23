---
trigger: always_on
---

# MarineShield WebGIS UI & UX Rules

## 1. Visual Command Center Principles
- **Visual-First WebGIS**: Interactive map (MapLibre GL / Leaflet) is the primary user workspace. Coordinates must be visualized on map layers, never raw coordinate text lists.
- **No Business Logic on Frontend**: UI components receive processed JSON/GeoJSON payload data from backend APIs. All geometry processing, drift forecasting, and evidence scoring occur on backend services.
- **Explainability First**: Every attribution panel must clearly present supporting evidence, contradictory evidence, data quality status, and support the status `UNKNOWN`.

## 2. Accessibility & Field Usability
- **Status Indicators**: Status levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) must use clear text labels and distinct icons in addition to color-coding to support color-blind users.
- **Responsive & Field Mode**: WebGIS must provide a low-bandwidth / field mode toggle that reduces tile resolution, caches recent incident data, and optimizes rendering for mobile/tablet devices in low-connectivity coastal zones.
- **Keyboard Navigation & High Contrast**: Ensure keyboard focus visibility, ARIA attributes for map controls, and high-contrast dark/light mode UI themes.

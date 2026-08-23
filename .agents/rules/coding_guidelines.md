---
trigger: always_on
---

# Agent Execution Guidelines

1. **Reasoning & Planning:**
   - For complex architectural or DSA tasks, use `sequentialthinking` before generating files.
   - Store critical architectural decisions in `memory` to avoid context drift.

2. **Design to Code:**
   - Pull UI specs using `stitch` (`get_screen_code`) or `figma`.
   - Refactor raw layout code into modular `shadcn/ui` + Tailwind CSS v4 components.

3. **Backend & Database:**
   - Validate PostgreSQL schemas via `supabase` MCP before writing queries.
   - Enforce Row-Level Security (RLS) on every table mutation.

4. **Testing & QA Loop:**
   - Launch the local preview server (`pnpm dev`).
   - Use `playwright` to navigate and verify frontend interactivity.
   - Run `testsprite` to autonomously scan for security vulnerabilities, API edge cases, and run fixes.

5. **MarineShield Project Rules:**
   - Refer to `.agents/rules/agent_core.md` for core architectural, scientific, and responsible-AI constraints.
   - Enforce strict workstream separation as defined in `docs/architecture/WORKSTREAMS.md`.
   - All spatial geometries must be stored in EPSG:4326 (WGS84) via PostGIS and formatted as standard GeoJSON for API layers.
   - Never implement product functionality without prior architectural signoff recorded in `docs/decisions/DECISION_LOG.md`.
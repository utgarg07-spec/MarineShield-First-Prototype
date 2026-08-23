---
trigger: always_on
---

# MarineShield API Contract Guidelines

## 1. REST & Schema Conventions
- All backend services must be exposed via FastAPI using standard Pydantic models for request and response validation.
- API base path: `/api/v1`
- OpenAPI (Swagger) documentation must automatically generate at `/api/v1/docs`.

## 2. Standard Response Payloads
All endpoints must return structured JSON response formats:

```json
{
  "status": "success | error",
  "data": { ... },
  "metadata": {
    "timestamp": "2026-08-20T11:41:00Z",
    "request_id": "req-12345",
    "execution_time_ms": 142
  },
  "error": null
}
```

## 3. Mandatory Field Standards
- **Timestamps**: Always ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SSZ`).
- **Geospatial Objects**: GeoJSON Feature or FeatureCollection format with coordinates in WGS84 (`EPSG:4326` `[longitude, latitude]`).
- **Attribution Payloads**: Candidate hypothesis lists must explicitly include supporting evidence, contradictory evidence, data quality index, counterfactual result, and support the status `UNKNOWN`.
- **Response Priority**: Returned values must include both numeric score (`0-100`) and ordinal urgency level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

## 4. Error Handling
- Standard HTTP status codes (`400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`).
- Error details must include code, message, and diagnostic context without exposing internal stack traces or secrets to clients.

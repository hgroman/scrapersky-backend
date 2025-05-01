# Google Maps API Versioning Implementation

## Overview

This document explains the implementation of API versioning for the Google Maps API endpoints in ScraperSky. Following the API versioning strategy outlined in the API-Versioning-Endpoint-Map.md document, we have created both backward-compatible v1 endpoints and truthfully-named v2 endpoints.

## Implementation Details

### 1. Dual Versioned Router

We've implemented the API versioning pattern by creating a dual versioned router that exposes the same functionality through two different endpoint paths:

- **v1 Endpoints**: `/api/v1/places/*` (maintains backward compatibility)
- **v2 Endpoints**: `/api/v2/google_maps_api/*` (uses truthful naming)

Both endpoint sets point to the same handler functions, ensuring consistent behavior while allowing for a seamless transition to the new naming convention.

### 2. Endpoint Mapping

| Legacy Endpoint (v1)      | Truthful Endpoint (v2)             | Functionality            |
| ------------------------- | ---------------------------------- | ------------------------ |
| `/api/v1/places/search`   | `/api/v2/google_maps_api/search`   | Google Places API search |
| `/api/v1/places/status/*` | `/api/v2/google_maps_api/status/*` | Job status checking      |
| `/api/v1/places/staging`  | `/api/v2/google_maps_api/staging`  | Retrieve staging places  |
| `/api/v1/places/update-*` | `/api/v2/google_maps_api/update-*` | Update place status      |

### 3. Implementation Approach

1. **New Router File**: Created `google_maps_api.py` which uses the `api_version_factory` to create both v1 and v2 routers.

2. **Same Handler Functions**: Both v1 and v2 endpoints use the same handler functions, ensuring consistent behavior.

3. **Deprecation Headers**: The v1 endpoints include deprecation headers to notify clients of the future transition.

4. **Router Registration**: Both v1 and v2 routers are registered in `src/routers/__init__.py`.

### 4. Service Integration

The router uses the modernized services from the places services directory:

- `PlacesService`: Core database operations for places
- `PlacesSearchService`: Google Places API integration
- `PlacesStorageService`: Storage operations for places

## Usage Examples

### 1. API Search (Legacy v1 Endpoint)

```bash
curl -X POST "http://localhost:8000/api/v1/places/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "business_type": "restaurant",
    "location": "New York",
    "radius_km": 10
  }'
```

### 2. API Search (Truthful v2 Endpoint)

```bash
curl -X POST "http://localhost:8000/api/v2/google_maps_api/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "business_type": "restaurant",
    "location": "New York",
    "radius_km": 10
  }'
```

## Migration Plan

1. **Immediate**: Both v1 and v2 endpoints are available simultaneously.

2. **Short Term (1-2 months)**: Update frontend applications to use v2 endpoints.

3. **Medium Term (3-6 months)**: Mark v1 endpoints as deprecated with headers and documentation.

4. **Long Term (6+ months)**: Remove v1 endpoints entirely.

## Testing Strategy

Both endpoint versions should be tested identically to ensure consistent behavior:

1. **Functional Testing**: Test all endpoint functionality using both URL patterns.

2. **Integration Testing**: Ensure services interact properly regardless of which endpoint is used.

3. **Deprecation Header Testing**: Verify that v1 endpoints correctly return deprecation headers.

## Conclusion

The dual versioning implementation allows for a smooth transition from the misleadingly-named places endpoints to the truthfully-named Google Maps API endpoints. This approach ensures backward compatibility while enabling a clear path forward for new development.

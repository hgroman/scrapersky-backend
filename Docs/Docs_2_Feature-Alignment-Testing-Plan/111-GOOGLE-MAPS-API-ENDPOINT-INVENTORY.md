# Google Maps API Endpoint Inventory

## Overview

The Google Maps API integration provides endpoints for searching business locations via Google Places API, monitoring job status, and managing search results. This document catalogs each endpoint's functionality, permissions, database interactions, and RBAC requirements.

## Endpoint List

| Method | Path | Description | Permission | RBAC Feature | Min Role |
|--------|------|-------------|------------|--------------|----------|
| POST | /api/v3/google_maps_api/search | Search for places | places:search | google_maps_api | USER |
| GET | /api/v3/google_maps_api/status/{job_id} | Get search job status | places:search | google_maps_api | USER |
| GET | /api/v3/google_maps_api/staging | Get places in staging | places:view | google_maps_api | USER |
| POST | /api/v3/google_maps_api/update-status | Update place status | places:update | google_maps_api | ADMIN |
| POST | /api/v3/google_maps_api/batch-update-status | Batch update place status | places:update | google_maps_api | SUPER_ADMIN |
| GET | /api/v3/google_maps_api/debug/test-job-creation | Test job creation (debug) | places:search | google_maps_api | USER |

## Detailed Endpoint Documentation

### 1. POST /api/v3/google_maps_api/search

**Purpose**: Initiates a search for businesses of a specific type in a location using Google Maps API.

**Request Parameters**:
```json
{
  "business_type": "string",  // Required: Type of business to search for
  "location": "string",       // Required: Location to search in
  "radius_km": 10,            // Optional: Search radius in kilometers
  "tenant_id": "string"       // Optional: Tenant ID (defaults to user's tenant)
}
```

**Response**:
```json
{
  "job_id": "string",         // UUID of the created job
  "status": "pending",        // Initial job status
  "status_url": "string"      // URL to check job status
}
```

**CURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v3/google_maps_api/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "business_type": "dentist",
    "location": "Houston, TX",
    "radius_km": 10,
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Permission Requirements**:
- Basic permission: `places:search`
- Feature: `google_maps_api` must be enabled for tenant
- Minimum role: `USER`

**Database Interactions**:
- Creates a job record in the `jobs` table
- Later stores results in the `places` table (background task)

**Error Cases**:
- 400: Missing required fields
- 403: Insufficient permissions
- 500: Server error during job creation

### 2. GET /api/v3/google_maps_api/status/{job_id}

**Purpose**: Checks the status of a previously initiated place search job.

**Path Parameters**:
- `job_id`: UUID of the job to check

**Response**:
```json
{
  "job_id": "string",
  "status": "string",         // pending, running, storing, completed, failed
  "progress": 0.5,            // Progress between 0.0 and 1.0
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "error": null,              // Error message if failed
  "search_query": "string",
  "search_location": "string",
  "user_id": "string",
  "user_name": "string",
  "total_places": 0,
  "stored_places": 0
}
```

**CURL Example**:
```bash
curl -X GET "http://localhost:8000/api/v3/google_maps_api/status/{job_id}" \
  -H "Authorization: Bearer {jwt_token}"
```

**Permission Requirements**:
- Basic permission: `places:search`

**Database Interactions**:
- Reads from the `jobs` table

**Error Cases**:
- 403: Insufficient permissions
- 404: Job not found
- 500: Server error during retrieval

### 3. GET /api/v3/google_maps_api/staging

**Purpose**: Retrieves places in staging area with optional filtering.

**Query Parameters**:
- `tenant_id`: Optional tenant ID filter
- `status`: Optional status filter
- `limit`: Maximum number of results (1-1000, default 100)
- `offset`: Pagination offset (default 0)

**Response**:
```json
{
  "places": [
    {
      "id": "string",
      "place_id": "string",
      "name": "string",
      "formatted_address": "string",
      "business_type": "string",
      "latitude": 0.0,
      "longitude": 0.0,
      "vicinity": "string",
      "rating": 0.0,
      "user_ratings_total": 0,
      "price_level": 0,
      "status": "string",
      "tenant_id": "string",
      "search_query": "string",
      "search_location": "string",
      "search_time": "timestamp",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total_count": 0,
  "limit": 100,
  "offset": 0
}
```

**CURL Example**:
```bash
curl -X GET "http://localhost:8000/api/v3/google_maps_api/staging?tenant_id=550e8400-e29b-41d4-a716-446655440000&status=new&limit=50&offset=0" \
  -H "Authorization: Bearer {jwt_token}"
```

**Permission Requirements**:
- Basic permission: `places:view`
- Feature: `google_maps_api` must be enabled for tenant
- Tab permission: `review-organize` within the `google_maps_api` feature

**Database Interactions**:
- Reads from the `places` table

**Error Cases**:
- 403: Insufficient permissions
- 500: Server error during retrieval

### 4. POST /api/v3/google_maps_api/update-status

**Purpose**: Updates the status of a specific place.

**Request Parameters**:
```json
{
  "place_id": "string",      // Required: ID of place to update
  "status": "string",        // Required: New status value
  "tenant_id": "string"      // Optional: Tenant ID (defaults to user's tenant)
}
```

**Response**:
```json
{
  "success": true,
  "message": "Status updated to {status}"
}
```

**CURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v3/google_maps_api/update-status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "place_id": "place123",
    "status": "selected",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Permission Requirements**:
- Basic permission: `places:update`
- Feature: `google_maps_api` must be enabled for tenant
- Minimum role: `ADMIN`

**Database Interactions**:
- Updates the `status` field in the `places` table

**Error Cases**:
- 400: Missing required fields
- 403: Insufficient permissions
- 404: Place not found
- 500: Server error during update

### 5. POST /api/v3/google_maps_api/batch-update-status

**Purpose**: Updates the status of multiple places in a single operation.

**Request Parameters**:
```json
{
  "status_updates": [
    {
      "place_id": "string",
      "status": "string"
    }
  ],
  "tenant_id": "string"      // Optional: Tenant ID (defaults to user's tenant)
}
```

**Response**:
```json
{
  "success": true,
  "message": "Batch update completed with {success_count} successes and {failed_count} failures",
  "success_count": 0,
  "failed_count": 0,
  "failed_ids": ["string"]
}
```

**CURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v3/google_maps_api/batch-update-status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "status_updates": [
      {"place_id": "place123", "status": "selected"},
      {"place_id": "place456", "status": "not_a_fit"}
    ],
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Permission Requirements**:
- Basic permission: `places:update`
- Feature: `google_maps_api` must be enabled for tenant
- Minimum role: `SUPER_ADMIN`
- Tab permission: `control-center` within the `google_maps_api` feature

**Database Interactions**:
- Updates multiple `status` fields in the `places` table in a single transaction

**Error Cases**:
- 400: Missing required fields
- 403: Insufficient permissions
- 500: Server error during update

### 6. GET /api/v3/google_maps_api/debug/test-job-creation

**Purpose**: Test endpoint for job creation used for debugging.

**Response**:
```json
{
  "success": true,
  "message": "Job created and retrieved successfully",
  "job_id": "string",
  "numeric_id": 0,
  "job_uuid": "string",
  "status": "pending",
  "exists": true
}
```

**CURL Example**:
```bash
curl -X GET "http://localhost:8000/api/v3/google_maps_api/debug/test-job-creation" \
  -H "Authorization: Bearer {jwt_token}"
```

**Permission Requirements**:
- Development users only (typically)

**Database Interactions**:
- Creates and reads from the `jobs` table

**Error Cases**:
- 403: Insufficient permissions
- 500: Server error during job creation/retrieval

## Database Schema

### Primary Tables

#### 1. places

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| place_id | String | Google Places ID |
| name | String | Business name |
| formatted_address | String | Full address |
| business_type | String | Business type/category |
| latitude | Float | Geographic latitude |
| longitude | Float | Geographic longitude |
| vicinity | String | Neighborhood info |
| rating | Float | Google rating (0-5) |
| user_ratings_total | Integer | Number of ratings |
| price_level | Integer | Price level (0-4) |
| status | String | Processing status (new, selected, maybe, not_a_fit, archived) |
| tenant_id | UUID | Tenant that owns this record |
| search_query | String | Original search query |
| search_location | String | Original search location |
| search_time | Timestamp | When search was performed |
| created_at | Timestamp | Record creation time |
| updated_at | Timestamp | Record update time |

#### 2. jobs

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-incrementing primary key |
| job_id | UUID | Unique job identifier |
| job_type | String | Type of job (places_search) |
| status | String | Job status (pending, running, storing, completed, failed) |
| progress | Float | Progress from 0.0 to 1.0 |
| tenant_id | UUID | Tenant that owns this job |
| job_metadata | JSON | Job parameters and metadata |
| result_data | JSON | Results summary data |
| error | String | Error message if failed |
| created_at | Timestamp | Job creation time |
| updated_at | Timestamp | Job update time |

## RBAC Requirements

### Permissions

| Permission | Description |
|------------|-------------|
| places:search | Allows searching for places |
| places:view | Allows viewing search results |
| places:update | Allows updating place status |

### Feature Flag

The Google Maps API feature must be enabled for a tenant in the `tenant_features` table.

### Role Hierarchy

- `USER`: Can search and view places
- `ADMIN`: Can update individual place status
- `SUPER_ADMIN`: Can perform batch updates

### Tab Permissions

- `review-organize`: Required for viewing staging results
- `control-center`: Required for batch operations

## Related Frontend Components

- Places Search Form
- Job Status Monitor
- Results Viewer/Grid
- Status Update Form
- Batch Update Interface

## Testing Considerations

1. Test with and without appropriate permissions
2. Verify tenant isolation (users from one tenant cannot see another tenant's data)
3. Test with various search parameters
4. Verify job status updates occur correctly
5. Test error handling for various scenarios

# Batch Page Scraper Endpoint Inventory

## Overview

The Batch Page Scraper component provides functionality for scanning domain pages, both individually and in batch operations. It handles the extraction of metadata, content analysis, and site structure information from web domains.

This inventory documents all endpoints, their parameters, permission requirements, database interactions, and RBAC implications. It serves as both implementation documentation and a guide for frontend integration.

## API Endpoints

### 1. Single Domain Scan (`POST /api/v3/batch_page_scraper/scan`)

#### Description
Scans a single domain to extract metadata from its pages. This initiates a background process that crawls the domain and processes page content.

#### Endpoint Metadata
- **Method**: POST
- **URL**: `/api/v3/batch_page_scraper/scan`
- **Controller**: `batch_page_scraper.py:scan_domain`
- **Deprecation Status**: Active (current version)
- **Legacy Equivalent**: `/api/v1/scrapersky` (deprecated, will be removed in v4.0)

#### Request Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| base_url | string | Yes | Domain to scan (e.g., "example.com") | - |
| tenant_id | string | No | Tenant identifier (UUID) | "550e8400-e29b-41d4-a716-446655440000" |
| max_pages | integer | No | Maximum number of pages to scan | 1000 |

#### Sample Request
```json
{
  "base_url": "example.com",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "max_pages": 500
}
```

#### Response Format
```json
{
  "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status_url": "/api/v3/batch_page_scraper/status/d290f1ee-6c54-4b01-90e6-d701748f0851"
}
```

#### RBAC Requirements
- **Permission**: `domain:scan`
- **Feature Flag**: `batch_page_scraper`
- **Minimum Role**: `USER`
- **Tab Permission**: `discovery-scan`

#### Database Interactions
- **Tables**: 
  - `jobs`: Creates a job record to track processing
  - `domains`: Stores domain metadata
  - `pages`: Stores extracted page data
  - `sitemaps`: Records sitemap structure

#### Technical Notes
- Uses background tasks to process the domain asynchronously
- Creates a separate database session for background processing
- Employs the batch processor service for standardized processing

#### Technical Debt
- The endpoint accepts both direct and nested request formats (for backward compatibility)
- Uses a default tenant ID for requests without authentication

---

### 2. Batch Domain Scan (`POST /api/v3/batch_page_scraper/batch`)

#### Description
Process a batch of domains for page content extraction. This endpoint handles multiple domains at once, performing parallel processing with controlled concurrency.

#### Endpoint Metadata
- **Method**: POST
- **URL**: `/api/v3/batch_page_scraper/batch`
- **Controller**: `batch_page_scraper.py:batch_scan_domains`
- **Deprecation Status**: Active (current version)
- **Legacy Equivalent**: None (introduced in v3.0)

#### Request Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| domains | array of strings | Yes | List of domains to scan | - |
| tenant_id | string | No | Tenant identifier (UUID) | "550e8400-e29b-41d4-a716-446655440000" |
| max_pages | integer | No | Maximum pages per domain | 1000 |

#### Sample Request
```json
{
  "domains": ["example.com", "example.org", "example.net"],
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "max_pages": 500
}
```

#### Response Format
```json
{
  "batch_id": "b290f1ee-6c54-4b01-90e6-d701748f0851",
  "status_url": "/api/v3/batch_page_scraper/batch/b290f1ee-6c54-4b01-90e6-d701748f0851/status",
  "job_count": 3
}
```

#### RBAC Requirements
- **Permission**: `domain:scan`
- **Feature Flag**: `batch_page_scraper`
- **Minimum Role**: `ADMIN` (higher access requirement than single domain scan)
- **Tab Permission**: `deep-analysis`

#### Database Interactions
- **Tables**: 
  - `batch_jobs`: Creates a batch record 
  - `jobs`: Creates job records for each domain
  - `domains`: Stores domain metadata
  - `pages`: Stores extracted page data
  - `sitemaps`: Records sitemap structure

#### Technical Notes
- No immediate database operations in the main handler - just creates an ID and sets up background tasks
- Background processing with separate session, ensuring proper transaction boundaries
- Higher permission requirement (ADMIN role) due to potential resource impact

#### Technical Debt
- No rate limiting based on tenant usage metrics
- No prioritization mechanism for handling batch jobs from different tenants

---

### 3. Job Status Check (`GET /api/v3/batch_page_scraper/status/{job_id}`)

#### Description
Check the status of a single domain processing job. This provides detailed information about the progress, results, and any errors encountered during processing.

#### Endpoint Metadata
- **Method**: GET
- **URL**: `/api/v3/batch_page_scraper/status/{job_id}`
- **Controller**: `batch_page_scraper.py:get_job_status`
- **Deprecation Status**: Active (current version)
- **Legacy Equivalent**: `/api/v1/status/{job_id}` (deprecated, will be removed in v4.0)

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| job_id | string (path parameter) | Yes | ID of the job to check |

#### Response Format
```json
{
  "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "completed",
  "domain": "example.com",
  "created_at": "2023-10-15T14:32:19.387Z",
  "started_at": "2023-10-15T14:32:19.567Z",
  "completed_at": "2023-10-15T14:34:01.123Z",
  "progress": 1.0,
  "total_pages": 42,
  "successful_pages": 40,
  "failed_pages": 2,
  "error": null,
  "metadata": {
    "has_sitemap": true,
    "sitemap_urls": ["https://example.com/sitemap.xml"],
    "content_types": {
      "html": 39,
      "pdf": 1,
      "other": 2
    }
  }
}
```

#### RBAC Requirements
- **Permission**: `domain:scan`
- **Feature Flag**: `batch_page_scraper`
- **Minimum Role**: `USER`

#### Database Interactions
- **Tables**: 
  - `jobs`: Reads job status and metadata

#### Technical Notes
- Uses router-owned transaction boundary pattern
- Safe error handling and detailed error reporting

#### Technical Debt
- No caching mechanism for frequent status checks
- Limited pagination for large result sets

---

### 4. Batch Status Check (`GET /api/v3/batch_page_scraper/batch/{batch_id}/status`)

#### Description
Check the status of a batch processing job. Provides aggregated information about all domains in the batch, including overall progress and per-domain status.

#### Endpoint Metadata
- **Method**: GET
- **URL**: `/api/v3/batch_page_scraper/batch/{batch_id}/status`
- **Controller**: `batch_page_scraper.py:get_batch_status`
- **Deprecation Status**: Active (current version)
- **Legacy Equivalent**: None (introduced in v3.0)

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| batch_id | string (path parameter) | Yes | ID of the batch to check |

#### Response Format
```json
{
  "batch_id": "b290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "in_progress",
  "total_domains": 3,
  "completed_domains": 1,
  "failed_domains": 0,
  "created_at": "2023-10-15T14:32:19.387Z",
  "started_at": "2023-10-15T14:32:19.567Z",
  "completed_at": null,
  "progress": 0.33,
  "job_statuses": {
    "d290f1ee-6c54-4b01-90e6-d701748f0851": "completed",
    "e290f1ee-6c54-4b01-90e6-d701748f0852": "running",
    "f290f1ee-6c54-4b01-90e6-d701748f0853": "pending"
  }
}
```

#### RBAC Requirements
- **Permission**: `domain:scan`
- **Feature Flag**: `batch_page_scraper`
- **Minimum Role**: `ADMIN`

#### Database Interactions
- **Tables**: 
  - `batch_jobs`: Reads batch status information
  - `jobs`: Reads individual job statuses related to the batch

#### Technical Notes
- Uses router-owned transaction boundary pattern
- Aggregates information from multiple job records

#### Technical Debt
- No caching mechanism for frequent status checks
- No pagination for very large batches

---

### 5. Health Check (`GET /api/v3/batch_page_scraper/health`)

#### Description
Simple health check endpoint for the batch page scraper service.

#### Endpoint Metadata
- **Method**: GET
- **URL**: `/api/v3/batch_page_scraper/health`
- **Controller**: `batch_page_scraper.py:health_check`
- **Deprecation Status**: Active (current version)
- **Legacy Equivalent**: None

#### Response Format
```json
{
  "status": "healthy"
}
```

#### RBAC Requirements
- None (open endpoint)

#### Database Interactions
- None

#### Technical Notes
- Simple synchronous endpoint, no authentication required
- Used for infrastructure monitoring and service availability checks

#### Technical Debt
- Limited depth of health checking (does not verify database connectivity or dependent services)

---

## Database Schema

### Key Tables

#### `jobs` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| job_type | string | Type of job (e.g., "domain_scan") |
| tenant_id | UUID | Tenant identifier |
| status | string | Job status (pending, running, completed, failed) |
| progress | float | Completion progress (0.0 to 1.0) |
| created_at | timestamp | Job creation time |
| started_at | timestamp | Job start time |
| completed_at | timestamp | Job completion time |
| job_metadata | jsonb | Metadata and configuration for the job |
| created_by | UUID | User who created the job |
| result | jsonb | Job results upon completion |
| error | string | Error message if failed |

#### `batch_jobs` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (batch_id) |
| job_id | UUID | Associated main job ID |
| tenant_id | UUID | Tenant identifier |
| processor_type | string | Type of batch processing |
| total_domains | integer | Total number of domains in batch |
| completed_domains | integer | Completed domain count |
| failed_domains | integer | Failed domain count |
| status | string | Batch status |
| progress | float | Overall completion progress (0.0 to 1.0) |
| created_at | timestamp | Batch creation time |
| start_time | timestamp | Processing start time |
| end_time | timestamp | Processing end time |
| options | jsonb | Configuration options |
| error | string | Error details if failed |

## RBAC Implementation

### Permission Hierarchy

The Batch Page Scraper component follows the standard four-layer RBAC check pattern:

1. **Basic Permission Check**: `domain:scan`
   - Required for all operations within the Batch Page Scraper component

2. **Feature Enablement Check**: `batch_page_scraper`
   - Tenant-level feature flag that must be enabled
   - Can be overridden by users with the wildcard permission `*`

3. **Role Level Check**:
   - Single domain operations: Minimum `USER` role
   - Batch operations: Minimum `ADMIN` role
   - Status checks inherit the same role requirements as their operations

4. **Tab Permission Check**:
   - Single domain operations: Requires `discovery-scan` tab access
   - Batch operations: Requires `deep-analysis` tab access

### Implementation Notes

- Permission checks are implemented using utility functions in `utils/permissions.py`
- Feature flags are stored in the `tenant_features` table and checked at runtime
- Role hierarchy is defined in `constants/rbac.py`
- Tab permissions are stored in the database and linked to features

## Technical Debt & Deprecation Plan

### Identified Technical Debt

1. **Request Format Inconsistency**: The scan endpoint accepts both direct and nested request formats for backward compatibility, which should be standardized in v4.0.

2. **Default Tenant ID**: Hard-coded default tenant ID should be removed in favor of a proper fallback mechanism.

3. **Limited Resource Management**: No proper rate limiting or prioritization for tenant resource usage.

4. **Status Check Inefficiency**: No caching mechanism for frequent status checks, potentially causing database load.

5. **Dev Mode Authentication Bypass**: The development user for local testing should be removed or secured better.

### Deprecation Timeline

| Endpoint | Current Status | Deprecation Plan |
|----------|----------------|------------------|
| `/api/v1/scrapersky` | Deprecated | Remove in v4.0 |
| `/api/v1/status/{job_id}` | Deprecated | Remove in v4.0 |
| `/api/v3/batch_page_scraper/*` | Active | Will become legacy in v4.0 |

## Frontend Integration Guide

### Authentication Requirements

All endpoints (except health check) require proper authentication:

1. **JWT Token**: Must be included in the `Authorization` header with format `Bearer {token}`
2. **Tenant Context**: Must match the tenant_id in the request or the user's assigned tenant

### Error Handling

Endpoints return standard HTTP status codes:

- `200` - Operation successful
- `400` - Invalid input parameters
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Resource not found
- `500` - Server error

Error responses follow a standard format:

```json
{
  "detail": {
    "error": "error_code",
    "message": "Human-readable error message",
    "timestamp": "2023-10-15T14:32:19.387Z",
    "operation": "batch_page_scraper.scan"
  }
}
```

### Example API Usage

#### Single Domain Scan

```javascript
const response = await fetch('/api/v3/batch_page_scraper/scan', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    base_url: 'example.com',
    tenant_id: '550e8400-e29b-41d4-a716-446655440000',
    max_pages: 500
  })
});

const data = await response.json();
const jobId = data.job_id;
```

#### Check Job Status

```javascript
const pollStatus = async (jobId) => {
  const response = await fetch(`/api/v3/batch_page_scraper/status/${jobId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  const data = await response.json();
  if (data.status === 'completed' || data.status === 'failed') {
    return data;
  }
  
  // Poll again after delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  return pollStatus(jobId);
};
```

## Testing CURL Commands

### Single Domain Scan

```bash
curl -X POST "http://localhost:8000/api/v3/batch_page_scraper/scan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "base_url": "example.com",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "max_pages": 500
  }'
```

### Batch Domain Scan

```bash
curl -X POST "http://localhost:8000/api/v3/batch_page_scraper/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "domains": ["example.com", "example.org", "example.net"],
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "max_pages": 500
  }'
```

### Check Job Status

```bash
curl -X GET "http://localhost:8000/api/v3/batch_page_scraper/status/{job_id}" \
  -H "Authorization: Bearer {jwt_token}"
```

### Check Batch Status

```bash
curl -X GET "http://localhost:8000/api/v3/batch_page_scraper/batch/{batch_id}/status" \
  -H "Authorization: Bearer {jwt_token}"
```

### Health Check

```bash
curl -X GET "http://localhost:8000/api/v3/batch_page_scraper/health"
```

## Migration Guide from Legacy Endpoints

### From `/api/v1/scrapersky` to `/api/v3/batch_page_scraper/scan`

**Legacy Request:**
```json
{
  "url": "https://example.com",
  "tenant": "550e8400-e29b-41d4-a716-446655440000"
}
```

**New Request:**
```json
{
  "base_url": "example.com", 
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "max_pages": 1000
}
```

**Key Differences:**
1. `url` parameter renamed to `base_url` and protocol is handled automatically
2. `tenant` parameter renamed to `tenant_id`
3. Added `max_pages` parameter for controlling scan depth
4. More robust RBAC requirements with feature flags and tab permissions

### From `/api/v1/status/{job_id}` to `/api/v3/batch_page_scraper/status/{job_id}`

The response format has been enhanced to include more detailed information, but all fields from the legacy response are preserved for backward compatibility.
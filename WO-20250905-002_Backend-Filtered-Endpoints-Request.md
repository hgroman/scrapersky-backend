# Backend Work Order: Filtered "Update ALL" Endpoints

**Date**: 2025-09-05  
**Requestor**: Frontend Team  
**Priority**: High  
**Type**: API Enhancement  

## Executive Summary

Request to implement 6 new "filtered update" endpoints that mirror the successful `/api/v3/pages/status/filtered` pattern. These endpoints will enable bulk operations on entire filtered datasets rather than requiring explicit ID lists.

## Business Justification

**Problem**: Current batch endpoints require explicit ID arrays, limiting users to updating only visible items (15-50 per page). Users need to update hundreds or thousands of records matching filter criteria.

**Solution**: Add `/filtered` variants that accept filter criteria instead of ID lists, enabling true "Select All" functionality across entire datasets.

**Impact**: Dramatically improves user efficiency for bulk curation operations across all workflow components.

## Implementation Requirements

### Pattern Reference
**Successful Implementation**: `/api/v3/pages/status/filtered`
- Accepts filter criteria instead of ID arrays
- Returns same response format as batch endpoints
- Maintains authentication and tenant isolation
- Includes confirmation safety measures

### Required Endpoints (Priority Order)

#### 1. **LOCAL BUSINESS CURATION** - `/api/v3/local-businesses/status/filtered`
**Priority**: HIGH (Most user impact)
**Existing Endpoint**: `/api/v3/local-businesses/status`

```json
// Request Body
{
  "status": "Selected",
  "filters": {
    "status": "New",
    "business_name": "restaurant"
  }
}

// Response (same as existing batch endpoint)
{
  "updated_count": 150,
  "queued_count": 150
}
```

**Filter Parameters** (from existing GET endpoint):
- `status`: Filter by main business status
- `business_name`: Case-insensitive partial match
- `sort_by`: Field to sort by
- `sort_dir`: Sort direction

#### 2. **DOMAIN CURATION** - `/api/v3/domains/sitemap-curation/status/filtered`
**Priority**: HIGH (Critical workflow)
**Existing Endpoint**: `/api/v3/domains/sitemap-curation/status`

```json
// Request Body
{
  "sitemap_curation_status": "Selected",
  "filters": {
    "sitemap_curation_status": "New",
    "domain_filter": "example.com"
  }
}

// Response
{
  "updated_count": 75,
  "queued_count": 75
}
```

**Filter Parameters**:
- `sitemap_curation_status`: Filter by curation status
- `domain_filter`: Case-insensitive domain name match
- `sort_by`: Field to sort by
- `sort_desc`: Sort in descending order

#### 3. **SITEMAP IMPORT (WF6)** - `/api/v3/sitemap-files/sitemap_import_curation/status/filtered`
**Priority**: MEDIUM (Already has good patterns)
**Existing Endpoint**: `/api/v3/sitemap-files/sitemap_import_curation/status`

```json
// Request Body
{
  "deep_scrape_curation_status": "Selected",
  "filters": {
    "domain_id": "uuid-here",
    "deep_scrape_curation_status": "New",
    "url_contains": "products",
    "sitemap_type": "Standard"
  }
}

// Response
{
  "updated_count": 200,
  "queued_count": 200
}
```

**Filter Parameters**:
- `domain_id`: Filter by domain UUID
- `deep_scrape_curation_status`: Filter by curation status
- `url_contains`: Case-insensitive URL content match
- `sitemap_type`: Filter by sitemap type
- `discovery_method`: Filter by discovery method

#### 4. **STAGING EDITOR** - `/api/v3/places/staging/status/filtered`
**Priority**: MEDIUM (Specialized use case)
**Existing Endpoint**: `/api/v3/places/staging/status`

```json
// Request Body
{
  "status": "approved",
  "filters": {
    "status": "pending",
    "discovery_job_id": "uuid-here"
  }
}

// Response
{
  "updated_count": 50
}
```

**Filter Parameters**:
- `status`: Filter by staging status
- `discovery_job_id`: Filter by specific job
- `tenant_id`: Tenant isolation

#### 5. **SITEMAP CURATION** - `/api/v3/sitemap-files/sitemap_import_curation/status/filtered`
**Priority**: LOW (Same as Sitemap Import - may be duplicate)
**Note**: This appears to use the same endpoint as Sitemap Import. Verify if separate endpoint needed.

#### 6. **RESULTS VIEWER** - `/api/v3/places/staging/status/filtered`
**Priority**: LOW (Same as Staging Editor - may be duplicate)
**Note**: This appears to use the same endpoint as Staging Editor. Verify if separate endpoint needed.

## Technical Specifications

### Authentication & Security
- **Authentication**: Bearer token (same as existing endpoints)
- **Tenant Isolation**: Automatic filtering by user's tenant_id
- **Permissions**: Same RBAC rules as existing batch endpoints

### Request/Response Format
```typescript
// Standard Request Interface
interface FilteredUpdateRequest {
  status: string;                    // Target status to set
  filters: Record<string, any>;      // Filter criteria object
}

// Standard Response Interface  
interface FilteredUpdateResponse {
  updated_count: number;             // Number of records updated
  queued_count?: number;             // Number of records queued (if applicable)
}
```

### Implementation Pattern
1. **Validate Request**: Check authentication, tenant access, status values
2. **Build Query**: Convert filter criteria to database query with tenant isolation
3. **Execute Update**: Bulk update matching records
4. **Trigger Processing**: Queue records for processing if status is "Selected"
5. **Return Counts**: Provide feedback on operation scope

### Error Handling
```json
// No matching records
{
  "detail": "No records found matching the provided filter criteria"
}

// Invalid filter parameters
{
  "detail": "Invalid filter parameter: invalid_field"
}

// Invalid status value
{
  "detail": "Invalid status value: InvalidStatus"
}
```

## Database Considerations

### Performance
- **Indexing**: Ensure proper indexes on filtered columns
- **Batch Size**: Consider chunking for very large updates (>10,000 records)
- **Timeouts**: Implement reasonable timeout limits

### Data Integrity
- **Tenant Isolation**: Always include tenant_id in WHERE clauses
- **Status Validation**: Validate status values against allowed enums
- **Atomic Operations**: Use transactions for consistency

## Testing Requirements

### Unit Tests
- Filter criteria parsing and validation
- Tenant isolation enforcement
- Status value validation
- Error handling scenarios

### Integration Tests
- End-to-end filtered update operations
- Large dataset performance testing
- Concurrent operation handling
- Authentication and authorization

### Test Scenarios
```json
// Test Case 1: Basic filtered update
{
  "filters": {"status": "New"},
  "expected_behavior": "Updates all New records for tenant"
}

// Test Case 2: Multiple filter criteria
{
  "filters": {"status": "New", "name_contains": "test"},
  "expected_behavior": "Updates records matching both criteria"
}

// Test Case 3: No matching records
{
  "filters": {"status": "NonExistent"},
  "expected_behavior": "Returns 0 updated_count, no error"
}

// Test Case 4: Large dataset
{
  "filters": {"status": "New"},
  "dataset_size": 50000,
  "expected_behavior": "Handles large updates efficiently"
}
```

## Implementation Timeline

### Phase 1 (Week 1): High Priority Endpoints
1. **Local Business Curation** - `/api/v3/local-businesses/status/filtered`
2. **Domain Curation** - `/api/v3/domains/sitemap-curation/status/filtered`

### Phase 2 (Week 2): Medium Priority Endpoints  
3. **Sitemap Import** - `/api/v3/sitemap-files/sitemap_import_curation/status/filtered`
4. **Staging Editor** - `/api/v3/places/staging/status/filtered`

### Phase 3 (Week 3): Verification & Cleanup
5. Verify duplicate endpoint requirements
6. Performance optimization
7. Documentation updates

## Success Criteria

### Functional Requirements
- ✅ All endpoints accept filter criteria instead of ID arrays
- ✅ Maintain same response format as existing batch endpoints
- ✅ Proper tenant isolation and authentication
- ✅ Performance acceptable for datasets up to 100,000 records

### Non-Functional Requirements  
- ✅ Response time < 30 seconds for 10,000 record updates
- ✅ Proper error messages for all failure scenarios
- ✅ Comprehensive test coverage (>90%)
- ✅ API documentation updated

## Frontend Integration Notes

### Expected Frontend Changes
Each endpoint will enable adding a "Update ALL Filtered Results" button similar to the Page Curation implementation:

```typescript
// Frontend pattern for each component
const handleFilteredUpdate = async () => {
  const response = await fetch(`${API_BASE}/api/v3/endpoint/status/filtered`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ 
      status: targetStatus,
      filters: currentFilterCriteria 
    })
  });
};
```

### UI Enhancement Pattern
- Always-visible bulk update panel
- Clear distinction between "Update Selected" vs "Update ALL Filtered"
- Confirmation dialogs for bulk operations
- Real-time count display showing affected records

## Questions for Backend Team

1. **Performance Limits**: What's the recommended maximum record count for single filtered update?
2. **Chunking Strategy**: Should we implement automatic chunking for large datasets?
3. **Rate Limiting**: Any rate limiting considerations for bulk operations?
4. **Monitoring**: What metrics should we track for these endpoints?
5. **Rollback**: Any rollback mechanisms needed for failed bulk operations?

## Documentation Requirements

- **API Spec Updates**: Add new endpoints to OpenAPI/FastAPI documentation
- **Filter Reference**: Document all available filter parameters per endpoint
- **Examples**: Provide request/response examples for each endpoint
- **Error Codes**: Document all possible error scenarios

---

**Next Steps**: 
1. Backend team reviews and estimates implementation effort
2. Clarify any duplicate endpoint requirements  
3. Confirm priority order and timeline
4. Begin Phase 1 implementation

# Job ID Standardization Work Order - 2025-03-25

## Overview

Following our database schema type fix (07-13-database-schema-type-fix-2025-03-25.md), we need to standardize all job*id generation in the codebase to use proper UUID format instead of prefixed strings like `sitemap*{uuid}`or`places\_{uuid}`.

## Current Status

We have updated the database schema to properly use UUID type for job_id fields, but our code still contains instances where job_ids are generated with prefixes. This causes type incompatibility with the database schema.

### Fixed Code Locations:

✅ `/src/services/sitemap/processing_service.py`:

```python
# BEFORE:
job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

# AFTER:
job_id = str(uuid.uuid4())
```

✅ `/src/routers/modernized_sitemap.py`:

```python
# BEFORE:
job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

# AFTER:
job_id = str(uuid.uuid4())
```

✅ `/src/models.py` (SitemapAnalyzerResponse):

```python
# BEFORE:
job_id: str = Field(default_factory=lambda: f"sitemap_{uuid.uuid4().hex}")

# AFTER:
job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

✅ `/src/models.py` (SitemapAnalyzerBatchResponse):

```python
# BEFORE:
batch_id: str = Field(default_factory=lambda: f"batch_{uuid.uuid4().hex}")

# AFTER:
batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

✅ `/src/routers/google_maps_api.py` (already using standard UUID format):

```python
job_id = str(uuid.uuid4())
```

## URL Path Compatibility

Because our URLs include job_id parameters (like `/api/v3/sitemap/status/{job_id}`), the change from prefixed IDs to standard UUIDs may affect URL formatting. However, since we're using UUID strings in both cases, the paths should continue to work correctly.

## Testing Plan

After making these changes, we need to test:

1. **Sitemap Scanning Flow**:

   - `/api/v3/sitemap/scan` - Verify job_id creation
   - `/api/v3/sitemap/status/{job_id}` - Verify status retrieval with new UUID format

2. **Places Search Flow**:

   - `/api/v3/google_maps_api/search` - Verify job_id creation
   - `/api/v3/google_maps_api/status/{job_id}` - Verify status retrieval with UUID format

3. **Batch Processing**:
   - Verify batch_id creation and associated job tracking

## Implementation Checklist

1. ✅ Update `sitemap_files` and `jobs` tables to use UUID type for job_id
2. ✅ Fix job_id generation in sitemap services
3. ✅ Fix job_id generation in models
4. ✅ Fix batch_id generation in models
5. ⬜ Test all API endpoints that use job_id in paths
6. ⬜ Update any frontend code that might expect prefixed job_ids

## Impact Assessment

### What Changed

- Job IDs now use standard UUID format (e.g., `123e4567-e89b-12d3-a456-426614174000`) instead of prefixed format (e.g., `sitemap_123e4567e89b12d3a456426614174000`)
- Database schema now correctly uses UUID type for these fields
- Code is more consistent and properly typed

### Potential Issues

- Any code that parses job*ids expecting a prefix (like `str.startswith("sitemap*")`) will need to be updated
- Frontend code might need updates if it's processing or displaying job_ids with the expectation of a prefix

## References

- [Database Schema Type Fix](./07-13-database-schema-type-fix-2025-03-25.md)
- [Enhanced Database Connection Audit](./07-06-enhanced-database-connection-audit-plan.md)

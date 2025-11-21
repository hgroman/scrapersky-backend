# Work Order: Add Sorting Fields to Sitemap CRUD Endpoint

## Priority
Medium

## Context
The sitemap files CRUD endpoint (`/api/sitemap_files`) currently lacks sorting capabilities, making it difficult for the React frontend to provide flexible data views.

## Requirements
Add query parameters to enable frontend sorting:
- `sort_by`: Field name to sort by (e.g., `created_at`, `updated_at`, `url`, `domain_name`, `deep_scrape_curation_status`)
- `sort_order`: `asc` or `desc` (default: `desc`)

## Affected Files
- `src/routers/sitemap_files.py` - Add query parameters to GET endpoint
- `src/services/sitemap_files_service.py` - Update `get_all()` method to accept sorting params
- `src/schemas/sitemap_file.py` - Consider adding sort validation schema

## Implementation Notes
- Default sort should remain `updated_at DESC` for backwards compatibility
- Validate `sort_by` against allowed fields to prevent SQL injection
- Support sorting by joined fields (e.g., `domain_name` from the domain relationship)

## Acceptance Criteria
- [ ] Frontend can sort by any relevant field
- [ ] Invalid sort fields return 400 with clear error message
- [ ] Default behavior unchanged when no sort params provided
- [ ] API documentation updated

## Related
- Part of broader React frontend enhancement initiative
- Similar sorting needed for other CRUD endpoints (domains, pages, contacts)

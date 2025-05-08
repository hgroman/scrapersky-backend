# Services Directory Inventory

This document catalogs all services in the ScraperSky Backend and evaluates them against our architectural principles.

## Core Services

| Service            | File                 | Description                             | Compliance Status             |
| ------------------ | -------------------- | --------------------------------------- | ----------------------------- |
| Job Service        | `job_service.py`     | Manages job status tracking and updates | ⚠️ Needs UUID standardization |
| Profile Service    | `profile_service.py` | Manages user profiles                   | ✅ Compliant                  |
| Domain Service     | `domain_service.py`  | Manages domain information              | ⚠️ Check UUID handling        |
| Database Inspector | `db_inspector.py`    | Tools for database inspection           | ✅ Compliant                  |

## Sitemap Services

| Service            | File                            | Description                        | Compliance Status   |
| ------------------ | ------------------------------- | ---------------------------------- | ------------------- |
| Sitemap Service    | `sitemap_service.py`            | Main sitemap functionality         | ✅ Fixed and tested |
| Sitemap Processing | `sitemap/processing_service.py` | Processes sitemap data             | ✅ Fixed and tested |
| Sitemap Background | `sitemap/background_service.py` | Background processing for sitemaps | ✅ Fixed and tested |
| Sitemap Analyzer   | `sitemap/analyzer_service.py`   | Analyzes sitemap data              | ✅ Compliant        |

## Other Service Directories

| Directory       | Purpose                        | Compliance Status |
| --------------- | ------------------------------ | ----------------- |
| `core/`         | Core services and utilities    | ⚠️ Needs review   |
| `places/`       | Google Places API integration  | ⚠️ Needs review   |
| `page_scraper/` | Webpage content extraction     | ⚠️ Needs review   |
| `job/`          | Job-related services           | ⚠️ Needs review   |
| `batch/`        | Batch processing functionality | ⚠️ Needs review   |
| `scraping/`     | Web scraping functionality     | ⚠️ Needs review   |
| `storage/`      | Data storage management        | ⚠️ Needs review   |

## Priority Service Improvements

Based on our architectural principles and the inventory above, here are the priorities for service improvements:

1. **UUID Standardization**

   - Job service needs to be updated to use standard UUIDs
   - Check domain service for UUID handling
   - Ensure all services use PGUUID type in SQLAlchemy models

2. **Transaction Management**

   - Verify all services follow the transaction-aware pattern
   - Ensure background jobs create their own sessions
   - Make sure routers are properly managing transactions

3. **Connection Pooling**

   - Verify all services are using the Supavisor connection pooling
   - Add connection pooling parameters to database-intensive endpoints
   - Remove any direct database connections

4. **Error Handling**
   - Improve error messages and logging
   - Add context information to error logs
   - Ensure proper validation of inputs

## Next Steps

1. Implement fixes for the job service to standardize UUID handling
2. Review and update domain service if needed
3. Systematically review each service directory based on priority
4. Update documentation as changes are made
5. Create test scripts for each service similar to the sitemap test

## Testing Strategy

For each service:

1. Create a test script using real user credentials
2. Test happy path functionality
3. Test error conditions
4. Verify results in the database

## Documentation Updates

As each service is reviewed and updated:

1. Update the compliance status in this inventory
2. Document any architectural decisions made
3. Create or update test scripts
4. Update AI_GUIDES as needed
# WF6 - Sitemap Import Linear Steps

This document provides a detailed step-by-step breakdown of the Sitemap Import workflow, chronicling how sitemap files are processed to extract URLs.

## Workflow Overview

The Sitemap Import workflow automatically processes queued sitemap files (XML documents containing URLs), extracting the URLs and creating Page records for each. It operates as a background service and is triggered by status changes in the sitemap curation process.

## Linear Steps

### Phase 1: Scheduler Initialization

1. **Scheduler Setup**
   - System initializes through `src/main.py` lifespan event
   - `setup_sitemap_import_scheduler()` is called during application startup
   - Scheduler creates a recurring job to run `process_pending_sitemap_imports()`
   - Logging captures successful scheduler initialization

### Phase 2: Polling for Queued Sitemap Files

2. **Job Execution**
   - Scheduler triggers `process_pending_sitemap_imports()` at configured intervals
   - Log entry records job start with timestamp
   - Service imports settings to determine batch size

3. **Database Polling**
   - `run_job_loop()` from curation SDK executes 
   - Service queries database for SitemapFile records with `sitemap_import_status = Queued`
   - Records are sorted by `updated_at` (oldest first)
   - Batch size is limited by configuration settings

### Phase 3: Processing Individual Sitemap Files

4. **Status Update - Processing**
   - For each queued SitemapFile:
     - `sitemap_import_status` is updated to `Processing`
     - `run_job_loop()` handles this state change automatically

5. **Individual File Processing**
   - `SitemapImportService.process_single_sitemap_file()` is called with the sitemap file ID
   - Service retrieves the SitemapFile record from the database
   - Additional status validation performed as a safety check

6. **HTTP Request - Fetch Sitemap Content**
   - Service initiates HTTP request to the sitemap URL with httpx client
   - Request includes timeout settings and redirect following
   - Response is validated (raises error for 4xx/5xx status codes)
   - Sitemap content is extracted from response

7. **Sitemap Parsing**
   - Content is passed to SitemapParser to extract URLs
   - Parser identifies and extracts URLs (loc), lastmod, and other metadata
   - Returns list of SitemapURL objects with extracted data

8. **URL Processing**
   - Service creates a Page record for each extracted URL:
     - Maps URL to Page.url
     - Sets domain_id from parent sitemap
     - Sets last_modified from sitemap lastmod (if available)
     - Sets sitemap_file_id to create relationship
     - Sets lead_source to "sitemap_import"
   - Duplicate URLs within the same sitemap are skipped
   - Records with missing URLs are logged and skipped

9. **Database Operations**
   - Service attempts bulk insert of Page records
   - On IntegrityError (e.g., duplicates), falls back to individual inserts
   - Counts successful inserts for logging

10. **Status Update - Completion**
    - If successful, updates `sitemap_import_status` to `Completed`
    - Clears any previous error message
    - If no URLs were found, still marks as `Completed` with appropriate logging
    - Database transaction is committed

### Phase 4: Error Handling

11. **Error Handling - HTTP Errors**
    - On HTTP status errors (4xx, 5xx):
      - Transaction is rolled back
      - `sitemap_import_status` is set to `Error`
      - `sitemap_import_error` is set with status code and message
      - Error is logged

12. **Error Handling - Network Errors**
    - On request errors (timeouts, DNS failures, etc.):
      - Transaction is rolled back
      - `sitemap_import_status` is set to `Error`
      - `sitemap_import_error` is set with error message
      - Error is logged

13. **Error Handling - General Errors**
    - On other exceptions:
      - Transaction is rolled back
      - `sitemap_import_status` is set to `Error`
      - `sitemap_import_error` is set with exception details
      - Full stack trace is logged

### Phase 5: Job Completion

14. **Job Finalization**
    - Service logs job completion
    - Scheduler notes completion time
    - Next job execution is scheduled based on interval settings

## Integration Points

- **WF5 → WF6**: SitemapFile records are queued for import during the Sitemap Curation process (WF5)
- **WF6 → Future Workflows**: Created Page records may be used in future page scraping workflows

## Observability

The workflow provides detailed logging at each step:
- Job start/end
- File processing start/end
- URL counts
- Error conditions with details
- Performance metrics (processing time)

## Manual Intervention Points

- **Development Tools**: `src/routers/dev_tools.py` provides endpoints to manually trigger import for specific sitemap files
- **Database Access**: Administrators can modify sitemap_import_status to requeue failed imports

## Notes

- The workflow is designed to be idempotent - reprocessing the same sitemap will not create duplicate Page records
- Error handling is robust with comprehensive logging and status tracking
- The process is fully asynchronous for better performance and resource utilization

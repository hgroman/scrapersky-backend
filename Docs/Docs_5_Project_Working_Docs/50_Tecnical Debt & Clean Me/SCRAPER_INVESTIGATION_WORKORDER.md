# ScraperSky Metadata Extraction System Investigation

## URGENT WORK ORDER: Web Scraper Data Flow Investigation

**Priority**: High
**Issue Type**: Data Processing Failure
**System**: ScraperSky Backend - Page Scraper Module

## Overview

The page scraper system is failing to extract and display metadata when triggered through the web interface, but works correctly when triggered via direct API calls with curl. This inconsistency suggests a fundamental issue in the data flow or authentication pathway. **Your task is to isolate and fix the root cause of this discrepancy.**

## System Context

ScraperSky is a web scraping platform with several key components:

1. **Frontend Interface** (`single-domain-scanner.html`) - Allows users to input a domain and trigger a scan
2. **API Endpoints**:
   - `/api/v3/modernized_page_scraper/scan` - Initiates a new scan
   - `/api/v3/modernized_page_scraper/status/{job_id}` - Returns job status and results
   - `/api/v3/batch_page_scraper/status/{job_id}` - Alternative endpoint for status checks
3. **Background Processing System**:
   - `process_domain_with_own_session()` - Main processing function
   - `detect_site_metadata()` - Extracts metadata from websites
   - `update_job_with_results()` - Updates job with results
4. **Database**:
   - `jobs` table - Contains job records with `result` and `result_data` fields
   - `domains` table - Contains domain information

## Issue Description

When a user triggers a scan through the web interface, the system:

1. Successfully creates a job
2. Successfully processes the domain (confirmed via logs)
3. Fails to populate the `result_data` field in the database

However, when the same scan is initiated via curl, both the `result` and `result_data` fields are properly populated.

## Diagnostic Data

### Database Observation

The `jobs` table has two relevant columns:

- `result`: JSONB field (used by API responses)
- `result_data`: JSONB field (where extraction data should be stored)

When triggered through the webpage, both remain NULL. When triggered via curl, both are populated with metadata.

### Code Modifications Already Attempted

1. **API Response Fix**: Modified `processing_service.py` to map `result_data` to `result` in API responses:

```python
"result": job.result_data if hasattr(job, 'result_data') else None,
```

This was later reverted as it caused regressions.

2. **Storage Fix**: Modified `domain_processor.py` to store data in both fields:

```python
update_query = text("""
    UPDATE jobs
    SET status = :status,
        result = :result_json,
        result_data = :result_json,
        completed_at = NOW()
    WHERE job_id = :job_id
""").execution_options(prepared=False)
```

3. **Frontend URL Fix**: Updated the frontend to use the provided status_url instead of constructing its own:

```javascript
// Poll using the status_url provided by the API
pollStatus(data.job_id, data.status_url);
```

### API Call Discrepancy

The system provides:

```
"status_url": "/api/v3/batch_page_scraper/status/{job_id}"
```

But frontend was originally using:

```
"/api/v3/modernized_page_scraper/status/{job_id}"
```

## Current Hypothesis

There are several possible causes for this issue:

1. **Authentication Problem (70% confidence)**: The web interface may not be passing authentication correctly to the ScraperAPI service that performs the actual scraping. When using curl, the proper headers may be included automatically.

2. **URL/Endpoint Mismatch (60% confidence)**: Despite fixing the frontend to use the correct status_url, there might be a deeper issue with how the scan is initiated or which processing function is called.

3. **Session Management (50% confidence)**: The background task might be losing context or session information when initiated from the web vs. curl.

4. **Data Store Timing (40% confidence)**: There could be a race condition where the frontend checks for results before they're fully stored.

## Available Investigation Tools

1. **Database Inspection**:

   - The `/scripts/db` directory contains tools for database inspection
   - `simple_inspect.py` can list tables and display data
   - `inspect_table.py` provides more detailed analysis

2. **API Testing**:

   - Direct curl calls to endpoints
   - Browser dev tools for monitoring network requests

3. **Logging**:
   - Docker logs for backend services
   - Application logs for detailed processing information

## Investigation Steps Recommended

1. **Compare Network Traffic**: Capture and compare the full request/response cycle between:

   - The web interface making a scan request
   - A curl command making the same request

2. **Authentication Verification**: Check if there are different authentication tokens or headers being used between the web and curl approaches.

3. **Processing Path Analysis**: Instrument key functions with additional logging to trace exactly which code paths are being executed in each case.

4. **Database Transaction Analysis**: Investigate if transactions are being properly committed in both scenarios.

5. **Endpoint Consistency Check**: Verify all endpoint URLs are consistent across the codebase and properly handled by both API and function handlers.

## Success Criteria

The investigation will be considered successful when:

1. The root cause is identified with evidence
2. A fix is implemented that allows the web interface to properly store and display scraped metadata
3. The system is verified working from both curl and web interface approaches

## Communication Notes

The current understanding is incomplete. You are encouraged to explore other hypotheses and diagnostic approaches. Document all findings thoroughly, including failed approaches, as they may provide valuable clues.

Please provide regular updates with:

- Current hypotheses and confidence levels
- Attempted solutions and results
- Recommended next steps

## Additional Context

The system uses FastAPI with background tasks, SQLAlchemy for database access, and ScraperAPI as the external service for actual web scraping. The fields in the metadata include title, description, language, and various platform-specific details.

Your access to the codebase should reveal more specific implementation details as needed.

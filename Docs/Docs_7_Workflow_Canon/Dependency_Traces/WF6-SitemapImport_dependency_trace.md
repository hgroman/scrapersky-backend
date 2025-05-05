# WF6 - Sitemap Import Dependency Trace

This document traces all components involved in the Sitemap Import workflow.

## Overview

The Sitemap Import workflow handles the automated processing of sitemap files that have been queued for URL extraction. It's responsible for fetching sitemap content, parsing URLs, and creating Page records for each extracted URL. This workflow operates as a background service and is a crucial part of the site discovery and content extraction pipeline.

## Component List

### Main Components

13A. Sitemap Import Scheduler (Background Service)
- `src/services/sitemap_import_scheduler.py` - Sets up and runs the background processing job
- `src/services/sitemap_import_service.py` - Core processing logic for sitemap import
- `src/models/sitemap.py` - SitemapFile model and status enums
- `src/models/page.py` - Page model for storing extracted URLs
- `src/scheduler_instance.py` - Shared scheduler for background jobs
- `src/config/settings.py` - Configuration settings for the scheduler
- `src/common/curation_sdk/scheduler_loop.py` - Reusable job processing loop
- `src/common/sitemap_parser.py` - Parser for sitemap XML content

### Secondary Components

#### Testing and Development
- `src/routers/dev_tools.py` - Development endpoints for manually triggering sitemap import

#### Database and Session Management
- `src/session/async_session.py` - Session management for database operations

## Dependencies and References

### External Dependencies
- `httpx` - Used for HTTP requests to fetch sitemap content
- `sqlalchemy` - ORM for database operations

### Internal Dependencies
- WF5-Sitemap Curation - The sitemap import process is triggered by status changes made in the Sitemap Curation workflow

## Detailed Component Descriptions

### 13A. `src/services/sitemap_import_scheduler.py`

This component is responsible for setting up and running the background job that processes sitemap files queued for URL extraction. It:
- Sets up the scheduler job with appropriate intervals and configuration
- Polls the database for sitemap files with `sitemap_import_status = Queued`
- Uses the shared scheduler instance for job management
- Uses the curation SDK's `run_job_loop` for standardized batch processing

### 13A.1. `src/services/sitemap_import_service.py`

The core service component that handles the processing of individual sitemap files. It:
- Fetches sitemap content using HTTP requests
- Parses the sitemap XML to extract URLs
- Creates Page records for each extracted URL
- Updates the SitemapFile status upon completion or error
- Handles error scenarios and provides appropriate logging

### 13A.2. `src/models/sitemap.py`

Defines the data models and enums for sitemap processing:
- `SitemapFile` - Represents a sitemap file discovered in the system
- `SitemapImportProcessStatusEnum` - Status values for the import process
- `SitemapImportCurationStatusEnum` - Status values for curation

### 13A.3. `src/models/page.py`

Defines the Page model for storing URLs extracted from sitemaps.

### 13A.4. `src/common/sitemap_parser.py`

A utility class for parsing sitemap XML content and extracting URLs.

### 13A.5. `src/common/curation_sdk/scheduler_loop.py`

A reusable utility for standardized batch processing of database records.

### 13A.6. `src/routers/dev_tools.py`

Provides development endpoints for manually triggering the sitemap import process for testing and troubleshooting.

## Database Tables
- `sitemap_files` - Stores sitemap file information and processing status
- `pages` - Stores URLs extracted from sitemaps

## Key Fields
- `sitemap_files.sitemap_import_status` - Current processing status of the sitemap import
- `sitemap_files.url` - URL of the sitemap file to be processed
- `pages.url` - URL extracted from the sitemap
- `pages.sitemap_file_id` - Reference to the source sitemap file

## Configuration
The scheduler settings are defined in `src/config/settings.py`:
- `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES` - How often to poll for new sitemap files
- `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE` - How many sitemap files to process in each batch
- `SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES` - Maximum number of concurrent scheduler jobs

## Notes
- The import process is fully asynchronous, leveraging asyncio and SQLAlchemy's async capabilities
- The workflow uses a "status transition" pattern for tracking progress and error states
- Error handling is robust with comprehensive logging

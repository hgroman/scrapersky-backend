# Page Curation Workflow Knowledge Base

## Overview

The Page Curation Workflow is a multi-phase system for content extraction and processing, implemented as part of the ScraperSky backend.

## Components

### 1. Domain Content Service (`domain_content_service.py`)

- **Status**: Implemented but not registered
- **Purpose**: Initial content extraction from domain homepages
- **Features**:
  - Uses `crawl4ai` with async support
  - Configurable concurrency (max 5 tasks)
  - Robots.txt compliance
  - Custom user agent

### 2. Page Curation Service (`page_curation_service.py`)

- **Status**: Planned (Phantom)
- **Purpose**: Process and curate extracted content
- **Features**:
  - Content processing pipeline
  - Status management
  - Error handling
  - Integration with vector search

### 3. Page Curation Scheduler (`page_curation_scheduler.py`)

- **Status**: Planned (Phantom)
- **Purpose**: Background processing management
- **Features**:
  - Batch processing
  - Rate limiting
  - Error recovery
  - Progress tracking

## Implementation Status

### Phase 0 (Completed: 2025-05-07)

- ✅ Model updates (`PageCurationStatus`, `PageProcessingStatus`)
- ✅ API Schemas
- ✅ Basic router implementation

### Phase 1 (In Progress)

- 🔄 Service layer implementation
- 🔄 Scheduler implementation
- 🔄 UI components

## Database Integration

- Uses Supabase with pgvector for vector search
- Implements RLS for security
- Uses Supavisor for connection pooling

## JIRA Integration

- Project: ScraperSky Backend
- Epic: Page Curation Workflow
- Components:
  - Content Extraction
  - Curation Processing
  - Background Tasks

## Related Documentation

- Work Order: `47.0-Work-Order-Page_Curation.md`
- Comprehensive Plan: `47.4-FINAL-COMPREHENSIVE-PLAN.md`
- Workflow Builder: `47.3-ScraperSky Workflow-Builder-Cheat-Sheet-New-Template.md`

## Notes

- System designed for scalability
- Implements modern async patterns
- Follows ScraperSky architectural principles
- Integrates with existing monitoring

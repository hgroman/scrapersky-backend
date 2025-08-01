# WF0: Critical File Index - System Architecture Map

**MISSION CRITICAL: Complete mapping of all workflow components across the entire system**

**Version**: 1.0 DRAFT  
**Created**: 2025-07-28  
**Purpose**: Prevent architectural disasters through clear component ownership  
**Emergency Context**: Created after June 28th file deletion disaster  

---

## CANONICAL COMPONENT ARCHITECTURE

Every workflow MUST follow this 5-component structure:

- **WFx.1**: UI Layer (User Interface - Router/Frontend)
- **WFx.2**: Dual-Purpose Endpoint (Status Update + Queue Trigger)  
- **WFx.3**: Background Queuing Service (Scheduler/Processor)
- **WFx.4**: Core Business Logic (The Heart - What This WF Actually Does)
- **WFx.5**: Storage Layer (Database Operations)

---

## WF1: SINGLE SEARCH DISCOVERY

### WF1.1: UI Layer ✅
- **Current File**: `/src/routers/google_maps_api.py`
- **Proposed File**: `WF1_1_single_search_ui.py`
- **Purpose**: FastAPI router for single place searches
- **Function**: `search_places()` - handles user search requests
- **Critical Level**: SAFE (UI modifications allowed)

### WF1.2: Dual-Purpose Endpoint 🤔
- **Status**: ❓ NOT APPLICABLE - WF1 is immediate processing, no dual status
- **Note**: WF1 creates jobs but doesn't use dual-status pattern

### WF1.3: Background Queuing Service ✅
- **Current File**: `/src/routers/google_maps_api.py` (background task)
- **Proposed File**: `WF1_3_background_processor.py`
- **Purpose**: Processes Google Places API searches in background
- **Function**: `process_places_search_background()`
- **Critical Level**: IMPORTANT

### WF1.4: Core Business Logic ✅
- **Current File**: `/src/services/places/places_search_service.py`
- **Proposed File**: `WF1_4_google_places_engine.py`
- **Purpose**: Orchestrates Google Places API integration
- **Function**: `search_and_store()` - THE HEART OF WF1
- **Critical Level**: CRITICAL

### WF1.5: Storage Layer ✅
- **Current File**: `/src/services/places/places_storage_service.py`
- **Proposed File**: `WF1_5_places_storage.py`
- **Purpose**: Stores Place records in database
- **Function**: `store_places()` - ORM operations
- **Critical Level**: IMPORTANT

**WF1 STATUS**: ✅ COMPLETE ARCHITECTURE

---

## WF2: STAGING EDITOR

### WF2.1: UI Layer ✅
- **Current File**: `/src/routers/places_staging.py`
- **Proposed File**: `WF2_1_staging_editor_ui.py`
- **Purpose**: Place selection and status management interface
- **Critical Level**: SAFE

### WF2.2: Dual-Purpose Endpoint ✅
- **Current File**: `/src/routers/places_staging.py`
- **Function**: `update_places_status_batch()` - Sets status='Selected' + deep_scan_status='Queued'
- **Purpose**: THE DUAL-STATUS PATTERN IMPLEMENTATION
- **Critical Level**: CRITICAL

### WF2.3: Background Queuing Service ✅
- **Current File**: `/src/services/sitemap_scheduler.py` (SHARED)
- **Proposed File**: `WF2_3_deep_scan_processor.py` (EXTRACT FROM SHARED)
- **Purpose**: Processes places with deep_scan_status='Queued'
- **Function**: `process_pending_jobs()` - processes deep scan queue
- **Critical Level**: NUCLEAR (shared with other workflows)

### WF2.4: Core Business Logic ✅
- **Current File**: `/src/services/places/places_deep_service.py`
- **Proposed File**: `WF2_4_deep_scan_engine.py`
- **Purpose**: Performs detailed place analysis
- **Function**: `process_single_deep_scan()` - THE HEART OF WF2
- **Critical Level**: CRITICAL

### WF2.5: Storage Layer ✅
- **Current File**: Built into router (ORM compliant)
- **Proposed File**: `WF2_5_staging_storage.py`
- **Purpose**: Updates place status and deep scan results
- **Critical Level**: IMPORTANT

**WF2 STATUS**: ✅ COMPLETE ARCHITECTURE

---

## WF3: LOCAL BUSINESS CURATION

### WF3.1: UI Layer ✅
- **Current File**: `/src/routers/local_businesses.py`
- **Proposed File**: `WF3_1_business_curation_ui.py`
- **Purpose**: Local business selection interface
- **Critical Level**: SAFE

### WF3.2: Dual-Purpose Endpoint ✅
- **Current File**: `/src/routers/local_businesses.py`
- **Function**: `update_local_business_batch()` - Sets status='Selected' + domain_extraction_status='Queued'
- **Purpose**: THE DUAL-STATUS PATTERN IMPLEMENTATION
- **Critical Level**: CRITICAL

### WF3.3: Background Queuing Service ✅
- **Current File**: `/src/services/sitemap_scheduler.py` (SHARED)
- **Proposed File**: `WF3_3_domain_extraction_processor.py` (EXTRACT FROM SHARED)
- **Purpose**: Processes businesses with domain_extraction_status='Queued'
- **Function**: `process_pending_jobs()` - processes domain extraction queue
- **Critical Level**: NUCLEAR (shared with other workflows)

### WF3.4: Core Business Logic ✅
- **Current File**: `/src/services/business_to_domain_service.py`
- **Proposed File**: `WF3_4_domain_creation_engine.py`
- **Purpose**: Creates Domain records from LocalBusiness data
- **Function**: `create_pending_domain_from_local_business()` - THE HEART OF WF3
- **Critical Level**: CRITICAL

### WF3.5: Storage Layer ✅
- **Current File**: Built into router and service (ORM compliant)
- **Proposed File**: `WF3_5_business_storage.py`
- **Purpose**: Updates business status and creates domains
- **Critical Level**: IMPORTANT

**WF3 STATUS**: ✅ COMPLETE ARCHITECTURE

---

## WF4: DOMAIN CURATION ⚠️

### WF4.1: UI Layer ✅
- **Current File**: `/src/routers/domains.py`
- **Proposed File**: `WF4_1_domain_curation_ui.py`
- **Purpose**: Domain selection interface
- **Critical Level**: SAFE

### WF4.2: Dual-Purpose Endpoint ✅
- **Current File**: `/src/routers/domains.py`
- **Function**: `update_domains_batch()` - Sets sitemap_curation_status='Selected' + sitemap_analysis_status='queued'
- **Purpose**: THE DUAL-STATUS PATTERN IMPLEMENTATION
- **Critical Level**: CRITICAL

### WF4.3: Background Queuing Service ✅ RESTORED
- **Current File**: `/src/services/domain_sitemap_submission_scheduler.py`
- **Proposed File**: `WF4_3_sitemap_submission_processor.py`
- **Purpose**: Processes domains with sitemap_analysis_status='queued'
- **Function**: `process_pending_domain_sitemap_submissions()` - polls and submits
- **Critical Level**: NUCLEAR
- **DISASTER HISTORY**: ❌ DELETED JUNE 28TH - RESTORED 2025-07-28

### WF4.4: Core Business Logic ✅ RESTORED
- **Current File**: `/src/services/domain_to_sitemap_adapter_service.py`
- **Proposed File**: `WF4_4_sitemap_adapter_engine.py`
- **Purpose**: Submits domains to sitemap processing via HTTP
- **Function**: `submit_domain_to_legacy_sitemap()` - THE HEART OF WF4
- **Critical Level**: NUCLEAR
- **DISASTER HISTORY**: ❌ DELETED JUNE 28TH - RESTORED 2025-07-28

### WF4.5: Storage Layer ✅
- **Current File**: Built into router and adapter (ORM compliant)
- **Proposed File**: `WF4_5_domain_storage.py`
- **Purpose**: Updates domain curation and analysis status
- **Critical Level**: IMPORTANT

**WF4 STATUS**: ✅ COMPLETE ARCHITECTURE (RECENTLY RESTORED FROM DISASTER)

---

## WF5: SITEMAP CURATION ❌

### WF5.1: UI Layer ❌
- **Status**: MISSING - No dedicated UI found
- **Expected File**: `WF5_1_sitemap_curation_ui.py`
- **Purpose**: Should provide sitemap file selection interface
- **Impact**: Users cannot manually curate sitemap files

### WF5.2: Dual-Purpose Endpoint ❌
- **Status**: MISSING - No dual-status endpoint found
- **Expected Function**: Set sitemap_curation_status='Selected' + sitemap_import_status='Queued'
- **Impact**: No way to trigger sitemap URL extraction

### WF5.3: Background Queuing Service ✅
- **Current File**: `/src/services/sitemap_import_scheduler.py`
- **Proposed File**: `WF5_3_url_extraction_processor.py`
- **Purpose**: Processes sitemap files with sitemap_import_status='Queued'
- **Function**: `process_pending_sitemap_imports()`
- **Critical Level**: CRITICAL

### WF5.4: Core Business Logic ✅
- **Current File**: `/src/services/sitemap_import_service.py`
- **Proposed File**: `WF5_4_url_extraction_engine.py`
- **Purpose**: Extracts URLs from sitemap files
- **Function**: Imports URLs into sitemap_urls table - THE HEART OF WF5
- **Critical Level**: CRITICAL

### WF5.5: Storage Layer ✅
- **Current File**: Built into service
- **Proposed File**: `WF5_5_sitemap_storage.py`
- **Purpose**: Stores extracted URLs in sitemap_urls table
- **Critical Level**: IMPORTANT

**WF5 STATUS**: ❌ INCOMPLETE ARCHITECTURE (Missing UI and dual-endpoint)

---

## WF6: DOMAIN ANALYSIS ⚠️

### WF6.1: UI Layer ❓
- **Status**: UNKNOWN - May not exist yet
- **Expected File**: `WF6_1_domain_analysis_ui.py`
- **Purpose**: Domain metadata analysis interface

### WF6.2: Dual-Purpose Endpoint ❓
- **Status**: UNKNOWN - May not be implemented
- **Expected Function**: Trigger domain metadata extraction

### WF6.3: Background Queuing Service ✅
- **Current File**: `/src/services/domain_scheduler.py`
- **Proposed File**: `WF6_3_metadata_extraction_processor.py`
- **Purpose**: Processes domains with status='pending'
- **Function**: `process_pending_domains()`
- **Critical Level**: IMPORTANT

### WF6.4: Core Business Logic ✅
- **Current File**: `/src/scraper/metadata_extractor.py`
- **Proposed File**: `WF6_4_metadata_analysis_engine.py`
- **Purpose**: Extracts domain metadata (WordPress, tech stack, etc.)
- **Function**: `detect_site_metadata()` - THE HEART OF WF6
- **Critical Level**: IMPORTANT

### WF6.5: Storage Layer ✅
- **Current File**: Built into scheduler
- **Proposed File**: `WF6_5_domain_metadata_storage.py`
- **Purpose**: Updates domain records with metadata
- **Critical Level**: IMPORTANT

**WF6 STATUS**: ⚠️ PARTIAL ARCHITECTURE (Backend complete, UI unknown)

---

## SHARED INFRASTRUCTURE (NUCLEAR LEVEL)

### SHARED.1: Scheduler Engine 🚨
- **Current File**: `/src/scheduler_instance.py`
- **Purpose**: APScheduler core - ALL background processing
- **Critical Level**: NUCLEAR (deletion breaks ALL workflows)

### SHARED.2: Multi-Workflow Processor 🚨
- **Current File**: `/src/services/sitemap_scheduler.py`
- **Purpose**: Shared processor for WF2, WF3, WF5
- **Critical Level**: NUCLEAR (deletion breaks 3 workflows)
- **URGENT**: Needs to be split into workflow-specific processors

### SHARED.3: Database Sessions
- **Current File**: `/src/session/async_session.py`
- **Purpose**: Database connection management
- **Critical Level**: NUCLEAR

### SHARED.4: Authentication
- **Current File**: `/src/auth/jwt_auth.py`
- **Purpose**: JWT authentication for all workflows
- **Critical Level**: NUCLEAR

---

## CRITICAL FINDINGS

### 🚨 DISASTER VULNERABILITIES
1. **SHARED PROCESSOR RISK**: `sitemap_scheduler.py` serves 3 workflows - single failure breaks multiple systems
2. **MISSING WF5 UI**: Sitemap curation has no user interface
3. **JUNE 28TH PATTERN**: WF4 disaster could repeat with any workflow lacking clear ownership

### ✅ ARCHITECTURAL COMPLETENESS
- **WF1**: ✅ Complete (5/5 components)
- **WF2**: ✅ Complete (5/5 components)  
- **WF3**: ✅ Complete (5/5 components)
- **WF4**: ✅ Complete (5/5 components - RESTORED)
- **WF5**: ❌ Incomplete (3/5 components - MISSING UI)
- **WF6**: ⚠️ Partial (Backend only)

### 🎯 IMMEDIATE PRIORITIES
1. **PROTECT SHARED SERVICES**: Add deletion protection to nuclear files
2. **COMPLETE WF5**: Build missing UI and dual-endpoint
3. **SPLIT SHARED PROCESSOR**: Extract workflow-specific logic from sitemap_scheduler.py
4. **SYSTEMATIC RENAMING**: Implement clear file ownership naming

---

## NEXT STEPS

### Phase 1: IMMEDIATE PROTECTION (This Week)
- Add protective headers to all NUCLEAR and CRITICAL files
- Create git hooks to prevent unauthorized deletions
- Document all shared dependencies

### Phase 2: ARCHITECTURE COMPLETION (Next 2 Weeks)
- Build missing WF5 UI components
- Split shared processor into workflow-specific services
- Verify WF6 completeness

### Phase 3: SYSTEMATIC RENAMING (Following Month)
- Implement proposed file naming across all workflows
- Update all imports and dependencies
- Create architectural governance tools

**The fate of system stability depends on completing this architectural mapping and protection.**
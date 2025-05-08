# Micro Work Order: WF2-StagingEditor Workflow Audit

_Last updated: 2025-05-05T08:55:23-07:00_

## Objective
Perform a comprehensive audit of the WF2-StagingEditor workflow to document its producer-consumer relationships with other workflows, identify architectural compliance issues, and ensure all documentation follows the enhanced standards established in recent workflow audits.

---

## Step-by-Step Protocol

## Protocol Followed

### 1. Code Analysis
- [x] Examined `src/routers/places_staging.py` to understand the API endpoints and database interactions
- [x] Analyzed `src/services/sitemap_scheduler.py` to verify background job processing
- [x] Reviewed `src/services/places/places_deep_service.py` to understand the deep scan process
- [x] Identified producer-consumer relationships with other workflows
- [x] Verified transaction management and ORM usage patterns

### 2. Documentation Review and Enhancement
- [x] Updated workflow name consistency (fixed WF-StagingEditor → WF2-StagingEditor)
- [x] Added workflow_connections section documenting relationships with WF1 and WF3
- [x] Added actionable_todos section with specific ticket references and line numbers
- [x] Verified existing known_issues section accuracy
- [x] Updated timestamp and reviewer information

### 3. Cross-System Analysis
- [x] Traced data flow from WF1-SingleSearch → WF2-StagingEditor → WF3-LocalBusinessCuration
- [x] Identified status fields used as workflow triggers (status, deep_scan_status)
- [x] Verified scheduler polling mechanism for background processing
- [x] Confirmed dual status update pattern implementation in the code

---

## DB/ORM Audit Findings (2025-05-04T23:46:15-07:00)

| File                               | ORM Only | Raw SQL Present | Notes                |
|-------------------------------------|----------|-----------------|----------------------|
| src/services/places_staging_service.py | ✅        | ❌              | Service layer, clean |
| src/services/sitemap_scheduler.py      | ✅        | ❌              | Scheduler, clean     |
| src/services/places_deep_service.py    | ✅        | ❌              | Deep scan, clean     |
| src/routers/places_staging.py          | ❌        | ✅              | Raw SQL in router    |
| src/models/place.py                    | ✅        | ❌              | Models only          |
| src/models/api_models.py               | ✅        | ❌              | API validation models|

- **Action:** Raw SQL in `src/routers/places_staging.py` has been documented in the canonical YAML with a detailed remediation plan. This includes JIRA ticket SCRSKY-224 for tracking the ORM refactoring work.
- **Issue:** The `trigger_deep_scan` parameter in the API is completely ignored in the implementation, creating a potentially misleading API contract. This has been documented as SCRSKY-225.
- **Next:** Implement ORM refactoring for places_staging.py by 2025-05-15 and address the parameter mismatch issue.
- **Timestamp:** 2025-05-04T23:46:15-07:00



---

## Findings

### Producer-Consumer Pattern Analysis

1. **Consumer Relationship with WF1**
   - WF2 directly consumes Place records with status='New' created by WF1
   - The Staging Editor UI displays these records for human review
   - The handoff occurs via the Place.status field in the places table
   - **Evidence**: Found in places_staging.py where it queries for Place records

2. **Producer Relationship with WF3**
   - WF2 produces LocalBusiness records that feed into WF3
   - Deep scan process in PlacesDeepService creates LocalBusiness objects
   - The handoff occurs via created_at timestamps in LocalBusiness table
   - **Evidence**: Found in places_deep_service.py where it creates LocalBusiness objects

### Critical Issues

1. **Raw SQL Violation**: (Added to Known Issues)
   - **Severity**: CRITICAL
   - **Description**: Direct SQL used to update Place status instead of proper ORM
   - **Location**: src/routers/places_staging.py:300-350
   - **Impact**: Violates ABSOLUTE_ORM_REQUIREMENT, creates maintenance issues
   - **Ticket**: SCRSKY-224
   - **Target Date**: 2025-05-15

2. **Misleading API Parameter**: (Added to Known Issues)
   - **Severity**: MEDIUM
   - **Description**: API defines trigger_deep_scan parameter, but implementation ignores it
   - **Location**: src/routers/places_staging.py:240-243
   - **Impact**: Creates misleading API documentation and confusing developer experience
   - **Ticket**: SCRSKY-225
   - **Target Date**: 2025-05-20

3. **Incomplete Job Tracking**: (Added to Known Issues)
   - **Severity**: LOW
   - **Description**: JobService integration commented out in PlacesDeepService
   - **Location**: src/services/places/places_deep_service.py:65-70
   - **Impact**: Reduced observability for deep scan processing
   - **Ticket**: SCRSKY-226
   - **Target Date**: 2025-05-30

### Implementation Strengths

1. **Transaction Management**
   - **Status**: EXCELLENT
   - **Description**: Router correctly uses async with session.begin() pattern
   - **Location**: src/routers/places_staging.py:305
   - **Evidence**: Follows transaction boundary ownership pattern perfectly

2. **Dual Status Update Pattern**
   - **Status**: WELL-IMPLEMENTED
   - **Description**: Status updates correctly set both status and deep_scan_status
   - **Location**: src/routers/places_staging.py:335-342
   - **Evidence**: When status=Selected, deep_scan_status automatically set to Queued

3. **Status-Based Triggering**
   - **Status**: WELL-IMPLEMENTED
   - **Description**: Scheduler uses status field as trigger for background processing
   - **Location**: src/services/sitemap_scheduler.py:208-212
   - **Evidence**: Correctly queries for Place.deep_scan_status=Queued to find items to process

## Documentation Improvements Made

1. **Enhanced Canonical YAML**
   - Added workflow_connections section documenting producer-consumer relationships
   - Added structured actionable_todos with ticket references
   - Fixed workflow name consistency throughout documentation

2. **Flow Visualization Added**
   - Documented exactly how data flows between WF1 → WF2 → WF3
   - Clarified the handoff fields used between workflows
   - Added evidence of implementations in specific code locations

## Next Steps

1. Fix critical ORM violation in places_staging.py (SCRSKY-224)
2. Address misleading API parameter (SCRSKY-225)
3. Complete JobService integration (SCRSKY-226)
4. Update dependency trace with producer-consumer annotations (SCRSKY-260)

---

## Notes for Future Auditors
- **No context is assumed**—all instructions are explicit and reference authoritative templates and mapping files
- The "Dual-Status Update" pattern (where updating status to Selected automatically triggers deep_scan_status=Queued) is a key architectural pattern that appears in multiple workflows
- Raw SQL in places_staging.py needs priority attention as it violates the Absolute ORM Requirement
- The unused parameter `trigger_deep_scan` creates misleading API documentation - this needs to be addressed
- Reference the CI Enforcement Work Order for schema validation and automated checks
- If any ambiguity arises, update this micro work order and the cheat sheet for future clarity

---

**Reviewer:** Cascade AI  
**Date:** 2025-05-05T08:55:23-07:00

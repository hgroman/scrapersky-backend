# Product Requirements Document: WF7 V3 - The Extractor

**Version:** 3.0 (Complete Rebuild)  
**Date:** 2025-08-05  
**Requestor:** ScraperSky Product Owner  
**Target Architect:** The Architect Persona  
**Compliance Target:** 100% (No Exceptions)  

---

## Executive Summary

WF7 "The Extractor" requires complete rebuilding to achieve 100% architectural compliance. The previous V2 implementation achieved only 78% compliance due to systematic violations of established patterns. This PRD mandates a full V3 rebuild under The Architect's supervision with mandatory Layer Guardian approvals.

---

## Business Requirements

### Primary Objective
Transform queued Page records into structured Contact records by extracting contact information from web page content.

### Business Value
- Completes the ScraperSky value chain by extracting actionable business data
- Enables sales teams to access contact information from discovered web pages
- Provides the final transformation step in the 7-workflow pipeline

### Success Criteria
1. Process all Pages with `page_curation_status = "Selected"`
2. Extract and store contact information (name, email, phone)
3. Update page processing status to track progress
4. Handle errors gracefully without blocking pipeline
5. **Achieve 100% architectural compliance** (NEW)

---

## Functional Requirements

### Input
- Page records with:
  - `page_curation_status = "Selected"`
  - `page_processing_status = "Pending"` or error states
  - Valid URL for content extraction

### Processing
1. Fetch page content using existing `DomainContentExtractor` service
2. Parse HTML to extract contact information
3. Create Contact records linked to Page and Domain
4. Update page processing status throughout lifecycle
5. Handle extraction failures with error logging

### Output
- Contact records with:
  - `name` (nullable)
  - `email` (nullable, indexed)
  - `phone_number` (nullable)
  - `domain_id` (foreign key)
  - `page_id` (foreign key)
  - Standard timestamps

### Status Transitions
```
page_curation_status: "Selected" → (triggers) → page_processing_status: "Queued"
page_processing_status: "Queued" → "Processing" → "Complete" | "Error"
```

---

## Technical Requirements

### Architecture Compliance (MANDATORY)
1. **Layer Separation:** Each layer component in dedicated file
2. **Naming Convention:** `WFx-V3-L[Layer#]-[Seq#ofTotal#]-[DescriptiveName].py`
3. **API Version:** All endpoints use `/api/v3/` prefix
4. **Pattern Compliance:** 100% adherence to all Layer blueprints

### Component Requirements

#### Layer 1: Model
- Contact model with proper relationships
- UUID primary keys
- Snake_case naming
- Proper indexes on searchable fields

#### Layer 2: Schemas  
- Dedicated schema file: `src/schemas/page_curation.py`
- Proper workflow prefixes: `PageCuration*Request/Response`
- ORM configuration: `from_attributes = True`
- ENUM integration from Layer 1

#### Layer 3: Router
- API prefix: `/api/v3/pages`
- Transaction ownership: `async with session.begin():`
- Schema imports from Layer 2 (NO inline definitions)
- Authentication dependency integration

#### Layer 4: Services & Scheduler
- Service accepts AsyncSession (never creates)
- Scheduler uses `run_job_loop` SDK
- Proper settings import: `from ..config.settings import settings`
- Status-driven workflow implementation

#### Layer 5: Configuration
- Environment variables for intervals/batch sizes
- Proper main.py integration
- Scheduler registration in lifespan events

---

## Anti-Patterns to Avoid (MANDATORY READING)

Based on V2 failures, the following are FORBIDDEN:

1. ❌ Inline schema definitions in routers
2. ❌ Using `/api/v2/` prefix (must be v3)
3. ❌ Missing workflow prefixes in schema names  
4. ❌ Skipping Layer Guardian consultations
5. ❌ Direct settings imports (use relative)
6. ❌ Missing authentication dependencies
7. ❌ Post-hoc documentation claiming compliance
8. ❌ Any deviation from Layer blueprints

---

## Delivery Requirements

### The Architect Must:
1. Load all Constitutional documents and Layer blueprints
2. Create architectural specification for each layer
3. Obtain written approval from all 7 Layer Guardians
4. Coordinate implementation with verified compliance
5. Document all Guardian interactions in approval matrix

### Approval Gates (MANDATORY)
- [ ] L1 Data Sentinel approval for models
- [ ] L2 Schema Guardian approval for API contracts  
- [ ] L3 Router Guardian approval for endpoints
- [ ] L4 Arbiter approval for services/scheduler
- [ ] L5 Config Conductor approval for integration
- [ ] L6 UI Virtuoso approval (if UI needed)
- [ ] L7 Test Sentinel approval for testing strategy

### Deliverables
1. Complete architectural specification document
2. Layer approval matrix with signatures
3. Implementation blueprint with component names
4. Compliance verification report (must show 100%)
5. Six-tier validation test results

---

## Timeline

- Requirements Analysis: 2 hours
- Architectural Design: 4 hours  
- Layer Guardian Reviews: 4 hours
- Implementation: 8 hours
- Testing & Validation: 4 hours
- **Total: 22 hours**

---

## Risk Mitigation

### Primary Risk: Compliance Drift
**Mitigation:** Mandatory checkpoint verification at each layer with kill switches

### Secondary Risk: Guardian Rejection  
**Mitigation:** Iterative review cycles until consensus achieved

### Tertiary Risk: Integration Failures
**Mitigation:** Docker-first testing with complete isolation

---

## Acceptance Criteria

The V3 implementation will be accepted when:
1. ✅ All Layer Guardians have signed approvals
2. ✅ 100% architectural compliance verified
3. ✅ Six-tier validation passes
4. ✅ End-to-end workflow test successful
5. ✅ Zero anti-patterns detected
6. ✅ Production deployment ready

---

## Notes for The Architect

This rebuild is not just about functionality - it's about proving that our architectural framework can deliver perfection when properly enforced. The previous 78% compliance is unacceptable. 

Your success will set the standard for rebuilding workflows 6 through 1.

**From chaos, order. From requirements, architecture. From design, excellence.**

---

*PRD Version 3.0 - The Standards Restoration Edition*
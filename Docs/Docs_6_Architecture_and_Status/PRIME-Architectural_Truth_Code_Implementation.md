# Context Prime: ScraperSky Architectural Truth Code Implementation

## Project Summary & Current Status

The ScraperSky backend is a FastAPI-based web scraping and analytics platform implementing a progressive data enrichment workflow through 7 distinct architectural layers. The platform has undergone comprehensive architectural documentation standardization resulting in a clear Architectural Truth Statement hierarchy (1.0-ARCH-TRUTH through 4.0-ARCH-TRUTH).

Current implementation metrics show:
- Transaction boundary compliance: 82% (routers) / 11% (services)
- API versioning standardization: Gaps identified (sitemap_analyzer.py still on v1)
- Tenant isolation removal: In progress (5+ key files modified)
- Background service standardization: Audit completed, remediation planning in progress

## Core Architectural Principles (Non-Negotiable)

1. **Layer 1 (Models & ENUMs)**: SQLAlchemy ORM exclusively, no raw SQL permitted
2. **Layer 2 (Schemas)**: Pydantic models for request/response validation
3. **Layer 3 (Routers)**: Own transaction boundaries via `async with session.begin()`
4. **Layer 4 (Services)**: Transaction-aware but do not create transactions
5. **Layer 5 (Configuration)**: JWT auth only at API gateway, not in database operations
6. **Producer-Consumer Pattern**: Status-driven workflow with consistent state transitions
7. **Layer Separation**: Layer 3 (Routers) focuses on HTTP/auth, Layer 4 (Services) on business logic

## Critical Implementation Targets

1. **Service Transaction Compliance (11% → 95%+)**:
   - Services must accept session parameters
   - Services must not create their own transactions
   - Reference: `src/services/sitemap/sitemap_service.py`

2. **Tenant Isolation Removal (Ongoing)**:
   - Remove all tenant-related checks, references, and foreign keys
   - Files already modified: src/services/sitemap/processing_service.py, src/routers/modernized_sitemap.py, src/db/session.py, src/services/core/auth_service.py, src/services/sitemap/sitemap_service.py

3. **API Versioning Standardization**:
   - All routes should use v3 API endpoints (`/api/v3/`)
   - sitemap_analyzer.py uses deprecated v1 and needs to be updated

4. **Background Service Standardization**:
   - Fix session management in background tasks
   - Implement consistent Producer-Consumer pattern
   - Background tasks must manage their own sessions via `get_background_session()`

## Workflow Architecture Map

The ScraperSky backend implements 7 core workflows:
1. **WF1**: Single Search (Google Maps API integration)
2. **WF2**: Staging Editor (Result staging and processing)
3. **WF3**: Local Business Curation (Business metadata enrichment)
4. **WF4**: Domain Curation (Domain verification and processing)
5. **WF5**: Sitemap Curation (Sitemap discovery and processing)
6. **WF6**: Sitemap Import (Background sitemap processing)
7. **WF7**: Page Curation (Page-level content analysis)

Each workflow follows a consistent pattern across all 7 architectural layers, as documented in `workflow-comparison-structured.yaml`.

## Implementation Strategy

1. **Cross-cutting first**: Address API versioning and tenant isolation for all components
2. **Target compliance gaps**: Focus on service layer transaction awareness (11% compliance)
3. **Reference implementations**: Use exemplary files as templates for standardization
4. **Layer-by-layer approach**: Implement standards systematically across architectural layers
5. **Verification**: Maintain and update compliance metrics as changes are implemented

## Reference Documentation

Key documents for implementation guidance:
- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy
- **[CONVENTIONS_AND_PATTERNS_GUIDE.md](./CONVENTIONS_AND_PATTERNS_GUIDE.md)** - Naming conventions and patterns
- **[WO5.0-ARCH-TRUTH-Code_Implementation_Work_Order.md](./WO5.0-ARCH-TRUTH-Code_Implementation_Work_Order.md)** - Detailed implementation plan
- **[workflow-comparison-structured.yaml](../Docs_7_Workflow_Canon/workflow-comparison-structured.yaml)** - Comprehensive workflow audit

## Success Metrics

Implementation success will be measured by:
1. Transaction boundary compliance for both routers (>95%) and services (>95%)
2. Complete removal of tenant isolation
3. 100% API versioning standardization
4. Consistent background task session management
5. Proper transaction boundary ownership

## Next Actions

1. Scan and inventory all router files for API versioning compliance
2. Continue tenant isolation removal with focus on remaining high-priority files
3. Begin systematic service retrofitting to accept session parameters
4. Implement proper transaction boundary management in non-compliant routers
5. Standardize background task session management

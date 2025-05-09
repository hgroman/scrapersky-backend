# ScraperSky Standardization Project Context

## Critical Implementation Note

**IMPORTANT: The Google Maps API implementation is the EXACT reference model to follow.**

Study these ACTUAL, WORKING FILES in the codebase:

- `/src/routers/google_maps_api.py` - Router implementation
- `/src/services/places/places_service.py` - Primary service
- `/src/services/places/places_search_service.py` - Search service
- `/src/services/places/places_storage_service.py` - Storage service

These are not theoretical examples - they are working code that shows the exact patterns to implement.

## Core Architecture Diagram

```
┌───────────────────────────────────────┐
│              HTTP Request             │
└───────────────────────┬───────────────┘
                        ▼
┌───────────────────────────────────────┐
│            FastAPI Router             │◄────┐
│   (`../../src/routers/google_maps_api.py`)   │     │
└───────────────────────┬───────────────┘     │
                        │                      │
        ┌───────────────┴───────────────┐      │
        ▼                               ▼      │
┌───────────────────┐         ┌───────────────────┐
│  RBAC Permission  │         │    Transaction    │
│      Checks       │         │    Boundaries     │
└───────────────────┘         └─────────┬─────────┘
        │                               │
        └───────────────┬───────────────┘
                        ▼
┌───────────────────────────────────────┐
│            Service Layer              │
│    (`../../src/services/places/*.py`)        │
└───────────────────────┬───────────────┘
                        ▼
┌───────────────────────────────────────┐
│           Data Access Layer           │
│      (ORM Models / SQLAlchemy)        │
└───────────────────────┬───────────────┘
                        ▼
┌───────────────────────────────────────┐
│              Database                 │
└───────────────────────────────────────┘
```

## Overview

This document provides the necessary context for the ScraperSky API Standardization Project. We're undertaking a comprehensive standardization of all routes and services in the ScraperSky backend to ensure consistent architectural patterns, proper RBAC integration, and standardized transaction management.

## Problem Statement

The ScraperSky backend has evolved with various components implemented by different developers at different times. While we've successfully standardized transaction management in key components, we still need to ensure all routes:

1. Follow proper architectural patterns
2. Integrate RBAC consistently
3. Manage transactions correctly
4. Handle errors uniformly
5. Maintain proper modularity between routes and services

## Project Goals

Our goal is to standardize 100% of the backend routes and services by applying the architectural patterns demonstrated in the Google Maps API component (our reference implementation) to all other components. Specifically, we will:

1. Audit all existing routes for compliance with our architectural patterns
2. Implement consistent RBAC integration across all routes
3. Ensure all components follow the "Routers own transaction boundaries, services do not" pattern
4. Apply proper service modularization where needed
5. Create comprehensive tests for all standardized components

## Key Documents

This standardization project is guided by three key documents:

1. **01-REFERENCE-IMPLEMENTATION.md**

   - Documents the Google Maps API as our concrete reference implementation
   - Outlines 8 architectural patterns all components should follow
   - Provides concrete code examples for each pattern with exact file references
   - Includes implementation checklists

2. **02-IMPLEMENTATION-PLAN.md**

   - Provides a detailed phase-by-phase implementation plan
   - Lists all components requiring standardization
   - Breaks down specific tasks for each component
   - Includes timeline, risks, and acceptance criteria

3. **03-RBAC-INTEGRATION-GUIDE.md**
   - Details the new Unified RBAC system implementation
   - Shows how to integrate all four layers of permission checks
   - Aligns with frontend RBAC expectations
   - Provides concrete examples from the Google Maps API implementation

## Components to Standardize

We need to standardize the following components:

### High Priority

- **Batch Page Scraper** - Needs RBAC integration following `/src/routers/google_maps_api.py` pattern
- **RBAC Admin** - Needs transaction management standardization
- **RBAC Features** - Needs transaction management standardization
- **RBAC Permissions** - Needs transaction management standardization

### Medium Priority

- **Domain Manager** - Needs service modularization
- **DevTools** - Needs RBAC integration

### Low Priority

- **Legacy routers** - Needs to be phased out

## Implementation Approach

We will follow a systematic phase-by-phase approach:

1. Address transaction management in RBAC components

   - Follow `/src/routers/google_maps_api.py` (lines 301-377) for transaction boundaries
   - Follow `/src/services/places/places_service.py` for transaction awareness patterns

2. Implement proper RBAC integration in batch scrapers

   - Follow `/src/routers/google_maps_api.py` (lines 323-345) for layered permission checks

3. Modularize services where needed

   - Follow the Places services directory structure as a model

4. Create comprehensive tests

   - Follow `/tests/transaction/test_transaction_*.py` patterns

5. Update documentation

## RBAC Integration Diagram

```
┌────────────────────────────────────────────────┐
│              FastAPI Route Handler              │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│ 1. Basic Permission Check (synchronous)         │
│    require_permission(current_user, "perm:name")│
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│ 2. Feature Enablement Check (async)             │
│    await require_feature_enabled(...)           │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│ 3. Role Level Check (async)                     │
│    await require_role_level(...)                │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│ 4. Tab Permission Check (async, if applicable)  │
│    await require_tab_permission(...)            │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│          Business Logic / Data Access           │
└────────────────────────────────────────────────┘
```

## Transaction Management Diagram

```
┌────────────────────────────────────────────────┐
│              FastAPI Route Handler              │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│           RBAC Permission Checks                │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│       Router-Owned Transaction Boundary         │
│       async with session.begin():               │
│       ┌────────────────────────────────────┐   │
│       │  Service Method Calls              │   │
│       │  (Services check if in transaction)│   │
│       └────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

## Success Criteria

The project will be considered successful when:

1. All routes follow the standardized architectural patterns
2. All components have proper RBAC integration
3. All services are properly modularized
4. All components have comprehensive tests
5. Transaction management is standardized across the application
6. Documentation is updated to reflect the standardized architecture

## Code Reference Templates

### Router Transaction Management (from `/src/routers/google_maps_api.py`)

```python
@router.get("/endpoint")
async def route_handler(session: AsyncSession = Depends(get_session)):
    # Permission checks first (BEFORE transaction)
    require_permission(current_user, "permission:name")

    # Router owns the transaction boundary
    async with session.begin():
        result = await service.get_something(session, params)

    return result
```

### Service Transaction Awareness (from `/src/services/places/places_service.py`)

```python
async def service_method(self, session: AsyncSession, ...):
    # Check if in transaction
    in_transaction = session.in_transaction()
    logger.debug(f"Session transaction state: {in_transaction}")

    # Implement service logic WITHOUT managing transactions
    # No session.commit() or session.rollback() here
```

## Important Notes

- This is a comprehensive project that touches all backend routes
- Changes should be made incrementally, one component at a time
- Each change must be accompanied by appropriate tests
- No functionality should be lost during standardization
- RBAC integration is particularly important for security

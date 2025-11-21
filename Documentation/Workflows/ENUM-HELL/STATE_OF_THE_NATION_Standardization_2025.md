# State of the Nation: Architectural Standardization 2025

> [!IMPORTANT]
> **Status**: 100% Standardized
> **Date**: November 2025
> **Scope**: Service Layer, Data Access, Schema Definitions

## Executive Summary

We have successfully achieved **100% Architectural Standardization** across the core backend services. This milestone marks the completion of a rigorous refactoring campaign driven by the "Guardian's Paradox" principles: **Stability, Uniformity, and Fault Isolation.**

The codebase has transitioned from a mixed-pattern state to a strictly enforced, layered architecture. This ensures maintainability, testability, and scalability for the future.

## Key Achievements

### 1. Service Layer Standardization (100% Compliant)
**Principle**: "Router/Scheduler Owns Session"
-   **Achievement**: Every service method in `src/services/` now accepts `session: AsyncSession` as a dependency.
-   **Impact**:
    -   **Zero Internal Session Creation**: Services no longer manage their own database connections.
    -   **Transactional Integrity**: Callers (Routers/Schedulers) control transaction boundaries (`begin`/`commit`/`rollback`).
    -   **Testability**: Database sessions can be easily mocked in unit tests (verified by `tests/verification_deep_scan_refactor.py`).

### 2. Schema Extraction (100% Compliant)
**Principle**: "Separation of Concerns"
-   **Achievement**: All Pydantic models have been extracted from `src/routers/` into dedicated `src/schemas/` files.
-   **Impact**:
    -   **Clean Routers**: Routers now focus solely on request/response handling.
    -   **Reusable Models**: Schemas can be shared across services and tests without circular imports.
    -   **Verified**: `LocalBusiness` and `PlaceStaging` schemas fully extracted.

### 3. ORM Standardization (100% Compliant)
**Principle**: "ORM First, Raw SQL Only When Necessary"
-   **Achievement**: Legacy usage of raw `sqlalchemy.update()` and `insert()` in business logic has been replaced with ORM object manipulation.
-   **Impact**:
    -   **Audit Trails**: Changes to objects are tracked by the session.
    -   **Safety**: Prevents SQL injection and ensures proper type handling.
    -   **Supavisor Compatibility**: Strict adherence to connection pooling requirements (`raw_sql=True`, `no_prepare=True`).

### 4. Fault Isolation (The "Nuclear Split")
**Principle**: "No Single Point of Failure"
-   **Achievement**: The monolithic `sitemap_scheduler.py` has been decommissioned.
-   **Impact**:
    -   **Independent Schedulers**: `deep_scan_scheduler` and `domain_extraction_scheduler` run independently.
    -   **Resilience**: A failure in one workflow no longer crashes the entire scheduling system.

## The "Guardian's Paradox" in Action

We have adhered to the mandate: *Improve the system without changing its behavior.*

-   **No Database Schema Changes**: Tables and columns remain untouched.
-   **No Feature Creep**: Only architectural patterns were refactored.
-   **Verification First**: Every change was verified with isolated tests before deployment.

## Path Forward: Automated Enforcement

To maintain this pristine state, the next phase (Option B) will focus on **Automated Enforcement**:
-   **Linting Rules**: Custom checks to prevent `get_session()` calls inside `src/services/` (excluding task wrappers).
-   **CI/CD Gates**: Blocking builds that introduce inline schemas or raw SQL in prohibited areas.

This document serves as the baseline for all future development. **We do not regress.**

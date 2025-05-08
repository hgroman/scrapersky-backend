# SCRAPERSKY SERVICE CONSOLIDATION PLAN

## OVERVIEW & HISTORY

The ScraperSky backend underwent a modernization process that attempted to:
1. Migrate from direct database calls to SQLAlchemy ORM
2. Implement a separation of concerns architecture
3. Remove RBAC (which is now completely removed)
4. Eliminate tenant isolation (now also removed)
5. Fix database transaction handling

During this modernization, multiple parallel implementations of core services were created, leading to fragmentation and inconsistency across routers. This plan establishes a standardized approach.

## CANONICAL SERVICE IMPLEMENTATIONS

For each service type, we'll standardize on ONE implementation:

### 1. AUTHORIZATION
**KEEP**: `services/core/auth_service.py`
- JWT-based authentication only
- No RBAC dependencies
- Minimal tenant awareness (using default tenant ID)

### 2. ERROR HANDLING
**KEEP**: `services/error/error_service.py`
- Most comprehensive implementation
- Handles Database exceptions
- Used by sitemap_analyzer.py

### 3. DATABASE ACCESS
**KEEP**: `services/core/db_service.py` + `db/session.py` + `db/engine.py`
- Standardized SQLAlchemy session management
- Proper connection pooling
- Follows transaction boundaries (routers own transactions)

### 4. SITEMAP PROCESSING
**KEEP**: `services/sitemap/processing_service.py`
- Current production implementation
- Used by modernized_sitemap.py
- Follows transaction patterns

### 5. VALIDATION
**KEEP**: `services/validation/validation_service.py`
- Return-value based validation (not exception-based)
- More comprehensive validation methods

## CONSOLIDATION STEPS

### PHASE 1: ERROR & VALIDATION SERVICES (LOW RISK)
1. Identify all imports of error services
2. Standardize on `services/error/error_service.py`
3. Update all import statements
4. Apply consistent error handling patterns

### PHASE 2: AUTH SERVICES (MEDIUM RISK)
1. Inventory JWT auth usage across all routers
2. Standardize on `services/core/auth_service.py`
3. Ensure consistent JWT handling
4. Remove any tenant isolation remnants

### PHASE 3: DATABASE SERVICES (HIGH RISK)
1. Establish consistent transaction pattern:
   - Routers own transactions
   - Services are transaction-aware
   - Background tasks manage own sessions
2. Update all routers to follow this pattern
3. Standardize on unified DB service approach
4. Test database operations thoroughly

### PHASE 4: SITEMAP SERVICES (MEDIUM RISK)
1. Choose between competing implementations
2. Update imports in all dependent routers
3. Fix any broken dependencies

## ROUTER-SPECIFIC CHANGES

### modernized_sitemap.py (CRITICAL PATH)
- Currently uses: auth_service from core, processing_service from sitemap
- Changes needed: Minimal - already follows patterns

### batch_page_scraper.py
- Currently uses: Mixed auth, batch_processor_service
- Changes needed: Standardize auth imports, transaction handling

### google_maps_api.py
- Currently uses: auth_service, error_service, places services
- Changes needed: Transaction pattern enforcement

### sitemap_analyzer.py
- Currently uses: jwt_auth, db_service, error_service
- Changes needed: Update auth handling, keep other implementations

### dev_tools.py
- Currently uses: jwt_auth, various services
- Changes needed: Standardize on core services

### profile.py
- Currently uses: jwt_auth, tenant_isolation, profile_service
- Changes needed: Remove tenant isolation

## TESTING STRATEGY

1. Start with low-risk consolidations
2. Test each service change individually
3. For database changes, create specific transaction tests
4. Document failures and side effects

## EXPECTED OUTCOMES

After consolidation:
- 5 standard service implementations instead of 13+
- Consistent transaction management
- Clear architectural boundaries
- Simplified dependency tree
- Easier onboarding for new developers
- Better maintainability

## IMPLEMENTATION PLAN

1. For each service type:
   - Document all usage across router files
   - Select canonical implementation
   - Update import statements
   - Test functionality

2. For each router:
   - Apply standardized service imports
   - Ensure transaction pattern compliance
   - Verify functionality through API testing

Progress will be tracked in this document as each service and router is consolidated.

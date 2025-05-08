# ScraperSky Standardization Implementation Plan

## ACTUAL IMPLEMENTATION REFERENCE

**CRITICAL: The Google Maps API is a fully implemented, working reference in the codebase with specific code sections to study:**

- **Router with RBAC & Transaction Management:**
  - File: `/src/routers/google_maps_api.py`
  - Key sections:
    - RBAC integration: lines 323-345
    - Transaction boundaries: lines 301-377
    - Background tasks: lines 154-300
   
- **Transaction-Aware Services:**
  - `/src/services/places/places_service.py`
  - `/src/services/places/places_search_service.py`
  - `/src/services/places/places_storage_service.py`

These are actual, working files that demonstrate the exact patterns to implement, not theoretical examples.

This document outlines the comprehensive implementation plan to standardize all routes and services in the ScraperSky backend according to the architectural patterns defined in our reference implementation (Google Maps API).

## 1. Current Status Assessment

### 1.1 Successfully Standardized Components

The following components have already been successfully standardized:

- **Google Maps API** (reference implementation)
- **FrontendScout** (transaction management fixed)
- **EmailHunter** (transaction management fixed)
- **SocialRadar** (transaction management fixed)
- **ActionQueue** (transaction management fixed)
- **ContentMap** (transaction management fixed)

### 1.2 Components Requiring Standardization

Based on our analysis, these components need standardization:

#### High Priority
- **Batch Page Scraper** (needs RBAC integration)
- **RBAC Admin** (needs transaction management standardization)
- **RBAC Features** (needs transaction management standardization)
- **RBAC Permissions** (needs transaction management standardization)

#### Medium Priority
- **Domain Manager** (needs service modularization)
- **DevTools** (needs RBAC integration)

#### Low Priority
- **Legacy routers** (needs to be phased out)

## 2. Implementation Phases

### Phase 1: RBAC Admin Component Standardization (2 days)

#### Files to Modify:
- `/src/routers/rbac_admin.py`
- `/src/services/rbac/rbac_service.py`

#### Tasks:
1. **Transaction Management**
   - [ ] Update router methods to own transaction boundaries
   - [ ] Make service methods transaction-aware
   - [ ] Add transaction state checking with appropriate logging
   - [ ] Create transaction tests

2. **RBAC Integration**
   - [ ] Add proper permission checking to all routes
   - [ ] Document permission requirements in docstrings
   - [ ] Create RBAC tests

#### Expected Deliverables:
- Updated router and service files
- New test files for transaction and RBAC
- Documentation updates

### Phase 2: RBAC Features Component Standardization (2 days)

#### Files to Modify:
- `/src/routers/rbac_features.py`
- `/src/services/rbac/feature_service.py`

#### Tasks:
1. **Transaction Management**
   - [ ] Update router methods to own transaction boundaries
   - [ ] Make service methods transaction-aware
   - [ ] Add transaction state checking with appropriate logging
   - [ ] Create transaction tests

2. **Service Modularization**
   - [ ] Extract business logic from router to service
   - [ ] Implement clean dependency injection
   - [ ] Create service unit tests

#### Expected Deliverables:
- Updated router and service files
- New test files
- Documentation updates

### Phase 3: RBAC Permissions Component Standardization (2 days)

#### Files to Modify:
- `/src/routers/rbac_permissions.py`
- `/src/services/rbac/rbac_service.py`

#### Tasks:
1. **Transaction Management**
   - [ ] Update router methods to own transaction boundaries
   - [ ] Make service methods transaction-aware
   - [ ] Create transaction tests

2. **Error Handling**
   - [ ] Implement consistent error handling
   - [ ] Add appropriate logging
   - [ ] Create error handling tests

#### Expected Deliverables:
- Updated router and service files
- New test files
- Documentation updates

### Phase 4: Batch Page Scraper Component Standardization (3 days)

#### Files to Modify:
- `/src/routers/batch_page_scraper.py`
- `/src/services/page_scraper/processing_service.py`

#### Tasks:
1. **RBAC Integration**
   - [ ] Add all four levels of permission checking
   - [ ] Document permissions in route docstrings
   - [ ] Create RBAC tests

2. **Service Modularization**
   - [ ] Separate concerns between layers
   - [ ] Refactor business logic into services
   - [ ] Create service unit tests

#### Expected Deliverables:
- Updated router and service files
- New test files
- Documentation updates

### Phase 5: Domain Manager Component Standardization (2 days)

#### Files to Modify:
- `/src/routers/modernized_sitemap.py`
- `/src/services/domain_service.py`

#### Tasks:
1. **Service Modularization**
   - [ ] Refactor monolithic services
   - [ ] Implement dependency injection
   - [ ] Create service unit tests

2. **Transaction Management**
   - [ ] Make services transaction-aware
   - [ ] Update routers to manage transactions
   - [ ] Create transaction tests

#### Expected Deliverables:
- Updated router and service files
- New test files
- Documentation updates

### Phase 6: DevTools Component Standardization (1 day)

#### Files to Modify:
- `/src/routers/dev_tools.py`

#### Tasks:
1. **RBAC Integration**
   - [ ] Add permission checking to sensitive operations
   - [ ] Document permissions
   - [ ] Create RBAC tests

#### Expected Deliverables:
- Updated router file
- New test files
- Documentation updates

### Phase 7: Integration Testing and Verification (3 days)

#### Tasks:
1. **Cross-Component Testing**
   - [ ] Test interactions between components
   - [ ] Verify transaction behaviors across boundaries
   - [ ] Validate RBAC enforcement system-wide

2. **Performance Testing**
   - [ ] Measure impact of changes on performance
   - [ ] Optimize if needed

3. **Documentation Update**
   - [ ] Update API documentation
   - [ ] Document architectural patterns

#### Expected Deliverables:
- Integration test suite
- Performance test results
- Updated documentation

## 3. Standardization Process for Each Component

For each component, follow this standardization process:

### Step 1: Analysis
- Review current implementation
- Identify deviations from reference patterns
- Create detailed task list

### Step 2: Transaction Management Standardization
- Ensure routers own transaction boundaries with `async with session.begin():`
- Make services transaction-aware with `in_transaction = session.in_transaction()`
- Update background tasks to create their own sessions

### Step 3: RBAC Integration Standardization
- Add layered permission checking
- Document permissions
- Test RBAC enforcement

### Step 4: Service Modularization
- Move business logic from routers to services
- Implement clean dependency injection
- Standardize response formats

### Step 5: Testing
- Create transaction tests
- Create RBAC tests
- Create service unit tests
- Create integration tests

### Step 6: Documentation
- Update API documentation
- Document architectural patterns

## 4. Risks and Mitigations

### 4.1 Risks

1. **Regression Risks:**
   - Changes might break existing functionality
   - RBAC changes might block legitimate access

2. **Performance Risks:**
   - Additional permission checks might impact performance
   - Transaction changes might affect throughput

3. **Integration Risks:**
   - Components might not work together after changes
   - Changes might affect external integrations

### 4.2 Mitigations

1. **Regression Mitigations:**
   - Comprehensive test coverage
   - Phased rollout with monitoring
   - Rollback plan

2. **Performance Mitigations:**
   - Performance testing before/after changes
   - Optimization opportunities
   - Monitoring plan

3. **Integration Mitigations:**
   - Integration tests
   - Staged deployment
   - Client communication plan

## 5. Acceptance Criteria

For each component, standardization is complete when:

1. **Architecture Criteria:**
   - Proper layering (router → service → repository)
   - No business logic in routers
   - Clean dependency injection

2. **Transaction Management Criteria:**
   - Routers explicitly manage transaction boundaries
   - Services are transaction-aware but don't create transactions
   - Background tasks properly create their own sessions
   - All transaction tests pass

3. **RBAC Criteria:**
   - All routes perform proper permission checks
   - Permissions are documented
   - All RBAC tests pass

4. **Quality Criteria:**
   - All tests pass
   - Documentation is updated
   - Code review completed

## 6. Timeline

Total estimated time: **15 working days**

- Phase 1 (RBAC Admin): Days 1-2
- Phase 2 (RBAC Features): Days 3-4
- Phase 3 (RBAC Permissions): Days 5-6
- Phase 4 (Batch Page Scraper): Days 7-9
- Phase 5 (Domain Manager): Days 10-11
- Phase 6 (DevTools): Day 12
- Phase 7 (Integration Testing): Days 13-15

## 7. Success Tracking

Track progress using these metrics:

1. **Component Completion:**
   - Number of components standardized / Total components
   - Percentage of routes standardized

2. **Test Coverage:**
   - Transaction test coverage
   - RBAC test coverage
   - Service test coverage

3. **Quality Metrics:**
   - Number of regressions
   - Performance impact

## 8. Conclusion

This implementation plan provides a systematic approach to standardizing all components in the ScraperSky backend. By following this plan, we will achieve a more consistent, maintainable, and secure application architecture based on the patterns demonstrated in our reference implementation.
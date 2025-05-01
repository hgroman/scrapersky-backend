# ScraperSky Legacy Code Cleanup Plan

## Overview

This document outlines the plan for identifying and cleaning up legacy code in the ScraperSky backend. Based on testing conducted on March 19, 2025, several areas of the codebase require cleanup to improve maintainability and reduce technical debt.

## Identified Legacy Areas

### 1. Duplicate API Versions

The system contains duplicate endpoint implementations across API versions:

- `/api/v2/google_maps_api/*` and `/api/v3/google_maps_api/*`
- Potential other v1/v2/v3 endpoint duplications

**Recommended Action**: Consolidate API versions, deprecate older versions, and provide migration paths for clients.

### 2. Outdated Authentication Mechanisms

The authentication system has inconsistencies:

- Development token works on some endpoints but not others
- Different authentication handling across API versions
- Potential duplicate auth middleware implementations

**Recommended Action**: Standardize authentication across all endpoints and remove deprecated auth mechanisms.

### 3. Database Session Handling

The database session management shows signs of legacy implementation:

- Transaction errors indicating improper session handling
- Inconsistent use of connection pooling parameters
- Possible use of both legacy and modern SQLAlchemy patterns

**Recommended Action**: Refactor database session handling to consistently use modern SQLAlchemy 2.0 async patterns.

## Code Cleanup Prioritization

### High Priority (Immediate)

1. **Database Transaction Handling** - Fix session management issues causing transaction errors
2. **Authentication Standardization** - Ensure consistent auth across endpoints
3. **Remove Direct Database URLs** - Replace any direct database connections with Supavisor pooler

### Medium Priority (Next Sprint)

1. **Consolidate API Versions** - Deprecate v1/v2 endpoints in favor of v3
2. **Standardize Error Handling** - Implement consistent error responses
3. **Clean Up Duplicated Business Logic** - Identify and refactor repeated code

### Low Priority (Future Work)

1. **Remove Testing/Debug Code** - Remove code only used for testing/debugging
2. **Clean Up Unused Imports/Dependencies** - Remove unused imports and dependencies
3. **Optimize Static Content Delivery** - Improve static file serving

## Legacy Code Identification Method

To identify legacy code, we will:

1. Search for deprecated imports and patterns:

   - `from sqlalchemy.ext.declarative import declarative_base` (legacy SQLAlchemy)
   - Non-async database operations
   - Old-style route definitions

2. Look for duplicate implementations:

   - Multiple implementations of similar functionality across API versions
   - Redundant utility functions

3. Identify inconsistent patterns:
   - Mixed auth mechanisms
   - Inconsistent error handling
   - Varying database access patterns

## Implementation Plan

### Phase 1: Documentation and Assessment

- Complete API endpoint testing to identify all problematic areas
- Document all legacy code areas with specific file locations
- Create migration guides for any breaking changes

### Phase 2: Critical Fixes

- Fix database transaction issues
- Standardize authentication
- Fix connection pooling usage

### Phase 3: Cleanup and Consolidation

- Deprecate v1/v2 endpoints
- Remove duplicate code
- Standardize error handling

### Phase 4: Optimization

- Performance improvements
- Code structure refinements
- Documentation updates

## Success Criteria

The legacy code cleanup will be considered successful when:

1. No database transaction errors occur during normal operation
2. Authentication is consistent across all endpoints
3. All endpoints use Supavisor connection pooling correctly
4. API versions are consolidated with clear deprecation notices
5. Code duplication is minimized
6. Error handling is standardized across the application

## Next Steps

1. Complete the full API endpoint assessment
2. Identify specific files and code blocks for cleanup
3. Create detailed tickets for each cleanup task
4. Establish testing procedures to ensure changes don't break functionality

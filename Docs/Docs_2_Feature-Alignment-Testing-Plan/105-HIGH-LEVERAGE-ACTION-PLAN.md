# ScraperSky High-Leverage Action Plan

## Overview

This plan identifies the highest-leverage issues to address in ScraperSky, prioritized by impact and fixability. It focuses exclusively on **making existing functionality work reliably**, not developing new features.

## Core Principles

1. **Fix, Don't Add**: Focus solely on making existing code work correctly
2. **Measurable Success**: Each task has specific success criteria
3. **Leverage First**: Prioritize fixes that unblock multiple features
4. **Minimize Changes**: Make targeted fixes with minimal codebase disruption

## Phase 2: Highest-Leverage Fixes

### 1. Database Transaction Handling (HIGHEST PRIORITY)

**Problem**: Database transaction errors are preventing multiple endpoints from functioning, including core scraper functionality.

**Specific Issues**:
- "A transaction is already begun on this Session" errors
- "Current transaction is aborted, commands ignored" errors
- Improper session handling in async contexts

**Action Items**:
1. Identify session management patterns in `src/db/session.py` and related files
2. Create a standardized session handler that properly manages transactions
3. Apply the fix to 2-3 key endpoints as a proof of concept
4. Roll out the fix to remaining endpoints

**Success Metrics**:
- ✅ Single domain scanner endpoint works without transaction errors
- ✅ RBAC user endpoints function correctly
- ✅ Transaction errors are eliminated in server logs

**Estimated Effort**: 1-2 days

### 2. Connection Pooling Parameter Standardization

**Problem**: Inconsistent application of required connection pooling parameters is causing database reliability issues.

**Specific Issues**:
- Some endpoints use connection pooling parameters, others don't
- Required parameters: `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`

**Action Items**:
1. Create a middleware or utility function that automatically applies these parameters
2. Apply to all database-intensive endpoints
3. Document the solution for all developers

**Success Metrics**:
- ✅ All database-intensive endpoints use the required parameters
- ✅ No database connection errors in logs
- ✅ Documentation clearly explains the parameter requirements

**Estimated Effort**: 4-6 hours

### 3. Authentication Standardization

**Problem**: Inconsistent authentication handling across API versions prevents reliable API usage.

**Specific Issues**:
- Development token works on some endpoints but not others
- Different auth implementations across v2/v3 endpoints

**Action Items**:
1. Audit all endpoint authentication implementations
2. Standardize JWT token validation across routes
3. Ensure development token works consistently in development mode
4. Fix tenant isolation header handling

**Success Metrics**:
- ✅ Development token works on all endpoints in development mode
- ✅ Authentication errors are consistent and clear
- ✅ Tenant isolation header is properly respected

**Estimated Effort**: 1 day

## Implementation Approach

### Week 1: Critical Fixes

| Day | Focus Area | Tasks | Success Criteria |
|-----|------------|-------|------------------|
| 1   | Database Transactions | Analyze and fix session management | Single domain scanner works |
| 2   | Connection Pooling | Standardize connection parameters | No database connection errors |
| 3   | Authentication | Fix token validation | Dev token works consistently |
| 4   | Testing | Verify fixes across all endpoints | All core endpoints function |
| 5   | Documentation | Update technical documentation | Documentation reflects actual system behavior |

### Execution Guidelines

1. **Focus on Fixes**: Resist the temptation to refactor or enhance - just make it work
2. **Test Incrementally**: Test each fix immediately
3. **Document Clearly**: Note every change with before/after evidence
4. **Keep Changes Minimal**: Make the smallest effective change

## Phase 3: Contingency Plan (Only If Needed)

If time permits after addressing the high-leverage issues:

1. **API Version Consistency**: Standardize on v3 endpoints
2. **Error Response Standardization**: Ensure consistent error formats
3. **Legacy Code Removal**: Remove clearly deprecated endpoints

## Management Checkpoints

- **Daily**: Brief status check on blocker resolution
- **End of Week 1**: Verify all critical fixes are complete
- **Final Checkpoint**: Confirm all high-leverage issues resolved

## Definition of Success

This plan will be considered successful when:

1. All core scraper functionality works without error
2. Authentication works consistently across endpoints
3. Database connections are reliable without transaction errors
4. Documentation accurately reflects the system state

By focusing on these high-leverage issues, we can make the existing system reliable without scope creep or unnecessary development.

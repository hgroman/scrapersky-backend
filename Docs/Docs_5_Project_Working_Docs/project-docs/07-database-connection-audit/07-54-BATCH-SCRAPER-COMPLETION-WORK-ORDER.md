# 07-54 Batch Scraper Completion Work Order

## Executive Summary

This work order outlines the completion of the Batch Page Scraper component, focusing on three critical architectural improvements:

1. **Database Connection Standardization**

   - Implement Supavisor connection pooling across all layers
   - Remove direct session creation and PgBouncer compatibility code
   - Standardize transaction management patterns

2. **Authentication & Authorization**

   - Remove tenant isolation from all database operations
   - Implement proper API key validation at router level
   - Standardize error responses and handling

3. **Background Task Reliability**
   - Fix silently failing background tasks
   - Implement proper session management
   - Add comprehensive error handling and status updates

**Timeline**: 5 working days (April 1-5, 2025)
**Priority**: CRITICAL - Affects core batch processing functionality

## Scope and Objectives

### In Scope

- Batch Page Scraper component
- Database connection standardization
- Tenant isolation removal
- Background task reliability
- Transaction management

### Out of Scope

- Frontend changes
- API version changes
- New feature additions
- Performance optimizations

## Critical Documentation References

1. **Database Standards**

   - [README.md](../README.md) - Core connection requirements
     - MUST use Supavisor connection pooler
     - Connection string format: `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
     - Pool size: min 5, recommended 10
     - Required parameters: `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`
   - [07-DATABASE_CONNECTION_STANDARDS.md](../Docs/Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md) - Implementation guidelines

2. **Architecture Standards**
   - [13-TRANSACTION_MANAGEMENT_GUIDE.md](../Docs/Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md) - Transaction patterns
     - Use proper transaction boundaries
     - Implement rollback procedures
     - Follow isolation level guidelines
   - [11-AUTHENTICATION_BOUNDARY.md](../Docs/Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md) - Authentication rules
     - Remove tenant-specific authentication
     - Implement API key validation
     - Standardize error responses
   - [09-TENANT_ISOLATION_REMOVED.md](../Docs/Docs_1_AI_GUIDES/09-TENANT_ISOLATION_REMOVED.md) - Tenant removal requirements

## Architecture Overview

```mermaid
graph TD
    A[Client] -->|HTTP Request| B[Router Layer]
    B -->|Transaction Boundary| C[Service Layer]
    C -->|Transaction Aware| D[Data Access Layer]
    D -->|Supavisor Pool| E[Database]

    F[Background Tasks] -->|Own Session| D
    F -->|Status Updates| C

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style F fill:#fbb,stroke:#333,stroke-width:2px
```

## Current Status

### Completed Work

1. ✅ Removed tenant isolation from `batch_processor_service.py`
2. ✅ Implemented Supavisor connection settings
3. ✅ Verified batch creation and status checking
4. ✅ Identified proper flow through all layers
5. ✅ Removed tenant isolation from `job_service.py` batch operations
6. ✅ Implemented transaction-aware design in batch job methods
7. ✅ Updated error handling to propagate exceptions for transaction management
8. ✅ Leveraged `BatchJob` class methods with default tenant ID

### Open/Remaining Issues

1. 🔴 Domains remaining in "pending" state
2. 🟡 Related files still contain tenant isolation (partially addressed in `job_service.py`)
3. 🟡 Need to follow proper flow through all layers (partially addressed in batch operations)
4. 🔴 Background task session management needs standardization
5. 🟡 Transaction boundaries need verification (partially addressed in batch methods)

### Resolved Issues

1. ✅ Tenant isolation violations in method signatures
2. ✅ Database connection standards violations
3. ✅ UUID standardization issues
4. ✅ Architectural flow violations
5. ✅ Removed tenant_id parameter from batch operations in job_service.py

## Implementation Plan

### Phase 1: API/Router Layer (Day 1)

- Remove tenant_id from request handling
- Update transaction boundaries (See **Appendix A** for patterns)
- Test endpoints
- **Addresses Open Issues**: #2 (Related files tenant isolation), #5 (Transaction boundaries)

### Phase 2: Service Layer (Day 2)

- Update processing service
- Implement error handling
- Test service layer
- **Addresses Open Issues**: #3 (Proper flow), #4 (Background task standardization)
- **See Appendix B** for background task standards
- **Progress Update**: Completed BatchJob operations in job_service.py including:
  - Removed tenant_id parameter from all batch methods
  - Implemented transaction-aware pattern
  - Added proper error handling
  - Leveraged BatchJob class methods

### Phase 3: Domain Processing (Day 3)

- Update domain validation
- Implement URL normalization
- Test domain processing
- **Addresses Open Issues**: #1 (Domains in pending state), #3 (Proper flow)

### Phase 4: Data Access Layer (Day 4)

- Update database queries
- Implement transaction management (See **Appendix A** for patterns)
- Test data access
- **Addresses Open Issues**: #2 (Related files tenant isolation), #5 (Transaction boundaries)
- **See Appendix C** for database connection standards

### Phase 5: Testing & Documentation (Day 5)

- Comprehensive testing
- Update documentation
- Final verification
- **Addresses Open Issues**: All issues require final verification

### Timeline Notes

- **Base Timeline**: 5 working days (April 1-5, 2025)
- **Buffer Days**: 2 days (April 6-7, 2025) reserved for:
  - Complex background task changes
  - Unexpected tenant isolation issues
  - Additional testing if needed

## Technical Requirements

### 1. Database Connection Standards ⚠️ CRITICAL

- **ONE AND ONLY ONE** acceptable method for database connections
- **MUST** use Supavisor connection pooling (See **Appendix C** for details)
- **NO** direct session creation allowed
- **Required Parameters**:
  - `raw_sql=true`
  - `no_prepare=true`
  - `statement_cache_size=0`

### 2. Authentication Boundary ⚠️ CRITICAL

- JWT authentication happens **ONLY** at API gateway/router level
- Database operations must **NEVER** handle JWT authentication
- Services must be authentication-agnostic
- Pass user IDs, not tokens, to services

### 3. Transaction Management ⚠️ CRITICAL

- **Routers OWN transactions** - They begin, commit, and rollback (See **Appendix A** for patterns)
- **Services are transaction-AWARE** - They work within existing transactions
- **Background tasks manage OWN sessions** - They create sessions for their lifecycle (See **Appendix B** for standards)

### 4. UUID Standardization

- All UUIDs must be proper PostgreSQL UUIDs
- No custom formats or prefixes
- Handle type conversion gracefully
- Use PGUUID SQLAlchemy type

## Testing & Validation

### Test Objectives

1. **Batch Creation**

   - Verify successful creation without tenant isolation
   - Test with various domain configurations
   - Validate response formats

2. **Domain Processing**

   - Test individual domain processing
   - Verify concurrent processing
   - Check error handling

3. **Background Tasks**
   - Verify proper session management
   - Test error recovery
   - Validate status updates

### Test Types

1. **Unit Tests**

   - Individual component testing
   - Mock database interactions
   - Error handling verification

2. **Integration Tests**

   - Layer interaction testing
   - Transaction boundary verification
   - Authentication flow testing

3. **End-to-End Tests**
   - Complete batch processing flow
   - Error recovery scenarios
   - Status update verification

## Rollback & Issue Tracking

### Backup Procedures

- Maintain code backups
- Document all changes
- Keep database backups

### Issue Tracking

- Document new issues
- Track resolution status
- Update documentation

## Appendices

### A. Standard Transaction Patterns

See [Transaction Patterns Reference](./07-04-transaction-patterns-reference.md)

### B. Background Task Standards

See [Background Task Standardization](./07-49-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-WORK-ORDER.md)

### C. Database Connection Standards

See [Database Connection Standards](../Docs/Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md)

## References and Key Mandates

### Database Standards

- [README.md](../README.md) - Core connection requirements
  - Supavisor connection pooler configuration
  - Connection string format and parameters
  - Pool size recommendations

### Transaction Management

- [13-TRANSACTION_MANAGEMENT_GUIDE.md](../Docs/Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md)
  - Transaction boundary patterns
  - Rollback procedures
  - Isolation level guidelines

### Authentication

- [11-AUTHENTICATION_BOUNDARY.md](../Docs/Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md)
  - API key validation
  - Error response standardization
  - Authentication flow

### Tenant Isolation

- [09-TENANT_ISOLATION_REMOVED.md](../Docs/Docs_1_AI_GUIDES/09-TENANT_ISOLATION_REMOVED.md)
  - Removal requirements
  - Migration guidelines
  - Verification steps

## Conclusion and Next Steps

### Sign-off Requirements

- Technical Lead: [Name] - Due: April 5, 2025
- Security Review: [Name] - Due: April 5, 2025
- Documentation Review: [Name] - Due: April 5, 2025

### At-a-Glance Phase Summary

1. **API/Router Layer (Day 1)**

   - Remove tenant isolation, update transactions, test endpoints
   - **Key Deliverable**: Clean router layer with proper transaction boundaries

2. **Service Layer (Day 2)**

   - Update processing service, implement error handling, test
   - **Key Deliverable**: Standardized background task management

3. **Domain Processing (Day 3)**

   - Update validation, implement URL normalization, test
   - **Key Deliverable**: Fixed domain state management

4. **Data Access Layer (Day 4)**

   - Update queries, implement transactions, test
   - **Key Deliverable**: Clean database access without tenant isolation

5. **Testing & Documentation (Day 5)**
   - Comprehensive testing, documentation updates, final verification
   - **Key Deliverable**: Complete test coverage and updated docs

### Success Criteria Checklist

- [ ] All tenant isolation removed
- [x] Tenant isolation removed from batch job operations
- [ ] Supavisor connection pooling implemented
- [ ] Transaction boundaries verified
- [x] Transaction boundaries implemented in batch job operations
- [ ] Background tasks standardized
- [ ] Error handling comprehensive
- [x] Error handling implemented in batch job operations
- [ ] Documentation updated
- [ ] Tests passing
- [ ] Security review completed

### Next Actions

1. Review this work order with the team
2. Begin Phase 1 implementation
3. Daily status updates in stand-up
4. Document any deviations or new issues
5. Complete sign-off by April 5, 2025
6. **Buffer Days**: April 6-7, 2025 (if needed)

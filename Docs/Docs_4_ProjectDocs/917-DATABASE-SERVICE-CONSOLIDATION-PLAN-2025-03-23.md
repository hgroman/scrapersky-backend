# Database Service Consolidation Plan

**Date:** 2025-03-23 (UPDATED)

This document outlines the detailed plan for standardizing on `services/core/db_service.py` across the ScraperSky codebase. This is the third phase of our service consolidation effort, following the successful completion of auth service and error service consolidation.

## ⚠️ MANDATORY DIRECTIVES ⚠️

**THE PRIMARY OBJECTIVE IS SIMPLIFICATION AND STANDARDIZATION:**

1. **SIMPLIFY** - Reduce code, not add more
2. **STANDARDIZE** - One consistent database connectivity pattern everywhere
3. **ELIMINATE REDUNDANCY** - Remove duplicate functionality, not create more
4. **CONSOLIDATE** - Use `services/core/db_service.py` as the single standard

**STRICTLY PROHIBITED:**
- Adding new functionality
- Creating new patterns
- Any form of scope creep
- Inventing new approaches

**THIS IS A CLEANUP AND STANDARDIZATION EFFORT ONLY**

## Goals

1. **Standardize on `services/core/db_service.py`**
   - All database access should go through this service
   - Remove direct SQL execution where possible

2. **Enforce consistent transaction patterns**
   - Routers own transaction boundaries
   - Services are transaction-aware but don't create transactions
   - Background tasks manage their own sessions but follow same pattern

3. **Simplify the codebase**
   - Remove redundant database access code
   - Consolidate similar functionality
   - Make database operations more consistent and maintainable

4. **⚠️ CRITICAL: Ensure Supavisor connection pooling**
   - ONLY use Supavisor connection strings with proper format:
     `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
   - NEVER use direct database connections or PgBouncer configurations
   - ALWAYS configure proper pool parameters:
     ```python
     pool_pre_ping=True
     pool_size=5 (minimum)
     max_overflow=10 (recommended)
     ```
   - ALL database-intensive endpoints MUST support connection pooling parameters

## Current State Analysis

The codebase currently contains several competing database access patterns:

1. **Direct SQL execution**
   - Found in: sitemap_analyzer.py, dev_tools.py
   - Issues: Security risks, inconsistent error handling, no transaction management

2. **Custom handlers**
   - Found in: sitemap_analyzer.py (SitemapDBHandler)
   - Issues: Not standardized, inconsistent with service architecture

3. **ORM with inconsistent transaction boundaries**
   - Found in: Most router files with varying approaches
   - Issues: Some routers own transactions, some don't

4. **Service-managed transactions**
   - Found in: multiple services creating their own transactions
   - Issues: Creates nested transactions, boundary confusion

## Implementation Strategy

### 1. Documentation

- ✅ Create this document as a guide
- ✅ Document transaction pattern
- ✅ Identify target files
- ✅ Create implementation guide (see [02-02-implementation-guide-2025-03-24.md](./02-02-implementation-guide-2025-03-24.md))

### 2. File-by-File Standardization

For each file needing standardization, follow the steps in the implementation guide:

1. Ensure session dependency injection
2. Add router-owned transaction boundaries
3. Update service calls to pass session
4. Fix background task handling
5. Test thoroughly

### 3. Code Removal

After standardization, remove or archive:

- Duplicate database service implementations
- Custom database handlers
- Direct database connection utilities

### 4. Prioritization

1. **Security Critical**
   - sitemap_analyzer.py - Replace raw SQL with string concatenation

2. **High Risk/Impact**
   - db_portal.py - Add router-owned transaction boundaries
   - modernized_sitemap.py - Update transaction ownership

3. **Standard Alignment**
   - dev_tools.py - Standardize session management
   - modernized_page_scraper.py - Align with router transaction pattern

## Rollout Plan

### Phase 1: Core Standardization

1. Update session.py to ensure Supavisor connection pooling
2. Update google_maps_api.py as reference implementation for documentation
3. Update db_service.py to ensure it follows all pattern requirements

### Phase 2: Security Critical Updates

1. Fix sitemap_analyzer.py SQL injection risks
2. Update with parameterized queries
3. Implement proper transaction management

### Phase 3: Systematic File Updates

1. Work through prioritized list of files
2. Update according to implementation guide
3. Test each change thoroughly
4. Document progress in tracker

### Phase 4: Cleanup

1. Remove redundant code
2. Archive or delete unused database handlers
3. Ensure all files use standardized approach

## Verification

After updates, all files should:

- Use session dependency injection
- Have router-owned transaction boundaries
- Pass sessions to services
- Handle background tasks properly
- Use proper connection pooling

## Reporting

Progress will be tracked in [02-04-db-consolidation-progress-2025-03-24.md](./02-04-db-consolidation-progress-2025-03-24.md) with detailed status for each file.

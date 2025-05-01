# ScraperSky Architectural Audit Plan

## Purpose & Approach

This document outlines a structured top-down architectural audit plan for the ScraperSky backend, designed to identify inconsistencies, map dependencies, and establish consistent patterns across the codebase.

The audit will start with no assumptions, focusing on tracing actual code paths rather than relying on documentation. This audit is critical for addressing architectural drift - where multiple implementation approaches have been added over time, creating conflicts and technical debt.

## Phase 1: Route Mapping & Service Dependency Analysis

### Step 1: Main Application Entry Point Analysis

- Start with `src/main.py` and identify all registered routers
- Document how routers are loaded and registered
- Capture middleware and application-level configuration

```bash
# Example commands for analysis
grep -r "app.include_router" src/main.py
grep -r "middleware" src/main.py
```

### Step 2: Router Registration Audit

- Create a comprehensive inventory of all routes
- For each router file:
  - Extract route paths, HTTP methods, and handler functions
  - Note URL patterns and versioning approaches
  - Document dependencies (what services each route calls)

```
# Output format example
| Router File | Endpoint | HTTP Method | Handler Function | Service Dependencies |
|-------------|----------|-------------|------------------|----------------------|
| google_maps_api.py | /api/v3/google_maps_api/search | POST | search_places | PlacesSearchService, JobService |
```

### Step 3: Service Layer Mapping

- For each service identified in Step 2:
  - Document its purpose and responsibility
  - Identify which routers depend on it
  - Map its dependencies on other services
  - Note transaction management approaches

```
# Output format example
| Service | Purpose | Used By Routers | Dependencies | Transaction Pattern |
|---------|---------|----------------|--------------|---------------------|
| job_service | Job tracking | google_maps_api, batch_scraper | AsyncSession | Internal transaction management |
```

### Step 4: Transaction Flow Analysis

- For each router-service interaction:
  - Document how sessions/transactions are passed
  - Identify potential conflicts (like we found in Google Maps API)
  - Flag inconsistent patterns

```
# Output format example
| Router | Service Method | Transaction Pattern | Conflict Risk |
|--------|---------------|---------------------|---------------|
| google_maps_api | job_service.get_by_id | Router wraps service call in transaction | HIGH |
```

## Phase 2: Architectural Pattern Assessment

### Step 1: Identify Existing Patterns

- Document all architectural patterns currently in use:
  - HTTP request handling patterns
  - Error handling approaches
  - Authentication/authorization flows
  - Database transaction management
  - Background task processing

### Step 2: Categorize Inconsistencies

- Group inconsistencies by type:
  - Transaction management (as seen in Google Maps API)
  - Error handling approaches
  - Authentication flows
  - Data validation
  - Response formatting

### Step 3: Define Target Patterns

- For each category, define the correct pattern to use:
  - Document the pattern
  - Provide concrete code examples
  - Justify why this pattern is preferred

Example for transaction management:

```python
# CORRECT PATTERN
# Router owns transaction boundaries
@router.get("/endpoint")
async def endpoint(session: AsyncSession):
    # Pass session to service without transaction context
    result = await service.get_data(session)
    return result
```

## Phase 3: Dependency Overlap Analysis

### Step 1: Service Usage Heatmap

- Create a matrix showing which routers use which services
- Identify services with high usage across multiple routers
- These are critical services where changes could have widespread impacts

### Step 2: Service Interface Analysis

- For heavily-used services:
  - Document all method signatures
  - Note inconsistencies in parameter handling
  - Identify potential areas for standardization

### Step 3: Shared Resource Usage

- Map database table access patterns
- Identify tables accessed by multiple services
- Document transaction isolation requirements

## Phase 4: Migration Planning

### Step 1: Impact Classification

- Classify each inconsistency by impact:
  - Critical (causing errors in production)
  - Major (significant technical debt/maintenance burden)
  - Minor (inconsistent but functional)

### Step 2: Dependency-Aware Sequencing

- Create a migration sequence that minimizes risk:
  - Fix isolated components first
  - Address shared services strategically
  - Group related changes

### Step 3: Testing Strategy

- Define test coverage requirements for each change
- Create targeted tests for specific architectural patterns
- Establish regression testing approach

## Example: Google Maps API Case Study

The transaction management issue we discovered in Google Maps API serves as an excellent example of the types of issues this audit will uncover:

1. **Pattern Inconsistency**: The router was wrapping service calls in transaction contexts while services expected to manage their own transactions.

2. **Detection Approach**: Searching for transaction context patterns (`async with session.begin()`) in router files.

3. **Fix Implementation**: Removing transaction contexts from router functions, allowing services to handle transactions.

4. **Verification**: Targeted tests specifically checking for transaction resilience.

This pattern of discovery → classification → correction → verification should be applied to all architectural inconsistencies.

## Execution Plan

To perform this audit efficiently:

1. **Use Automated Tools**:

   - Static analysis to map dependencies
   - Code pattern searches for transaction blocks
   - Route extraction scripts

2. **Visualization**:

   - Generate dependency graphs
   - Create service usage heatmaps
   - Document flow diagrams for critical paths

3. **Iterative Approach**:

   - Start with one complete vertical slice (e.g., Google Maps API)
   - Document patterns and anti-patterns
   - Expand to related components
   - Apply learnings across the codebase

4. **Documentation Artifacts**:
   - Complete route inventory
   - Service dependency map
   - Architectural pattern guide
   - Migration sequence plan

## Next Steps

1. Begin with automated extraction of all routes and their handler functions
2. Map the service dependencies for each route
3. Create a transaction management pattern inventory
4. Expand the transaction management guide with examples from other routers
5. Develop targeted tests for each architectural pattern

By following this structured approach, we can systematically address architectural drift, establish consistent patterns, and create a more maintainable codebase.

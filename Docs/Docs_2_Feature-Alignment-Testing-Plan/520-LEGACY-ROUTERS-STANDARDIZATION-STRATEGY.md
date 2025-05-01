# Legacy Routers Standardization Strategy

## Overview

This document outlines the strategy for handling Legacy Routers in the ScraperSky backend. As the final component in our standardization effort, Legacy Routers present unique challenges due to their potential obsolescence, lack of modern patterns, and varying levels of importance.

## Analysis of Legacy Routers

The following routers are considered legacy and require evaluation:

1. `page_scraper.py` - Original page scraper (superseded by modernized versions)
2. `sitemap.py` - Original sitemap router (superseded by modernized versions)
3. Any other non-modernized routers

## Standardization Approach

Given that most of the critical functionality has already been modernized, we will apply a pragmatic "flag-and-defer" approach to remaining legacy routers.

### Classification Criteria

We will evaluate each legacy router along three dimensions:

1. **Usage Level**: Is the router currently being used by frontend or other components?
2. **Modernization Status**: Is there already a modernized version of this router?
3. **Technical Debt**: How much technical debt would be created by deferring standardization?

### Classification Categories

Based on these criteria, legacy routers will be assigned to one of the following categories:

#### Category A: Deprecate and Redirect
- Already has a modernized replacement
- Low current usage
- Plan: Add deprecation notices and redirect to modernized versions

#### Category B: Minimal Standardization
- No modernized version yet
- Medium current usage
- Plan: Apply only the most critical standardization patterns (transaction boundaries and basic RBAC)

#### Category C: Critical Legacy
- No modernized version
- High current usage
- Plan: Apply full standardization patterns, but with reduced test coverage

#### Category D: Obsolete
- No current usage
- Plan: Mark for removal in future releases

## Implementation Plan

### Phase 1: Inventory and Classification

1. Identify all legacy routers in the codebase
2. Classify each according to the criteria above
3. Document the classification and approach for each

### Phase 2: Implementation for Each Category

#### Category A (Deprecate and Redirect)
1. Add deprecation notices in comments and docs
2. Add deprecation warning logs on each endpoint
3. Implement redirection logic to modern endpoints where possible
4. Update API documentation to indicate deprecation

#### Category B (Minimal Standardization)
1. Add transaction boundaries to database-interacting methods
2. Implement basic permission checks
3. Skip comprehensive RBAC and test coverage
4. Add "TO-DO: Modernize" comments

#### Category C (Critical Legacy)
1. Apply full standardization patterns
2. Implement comprehensive RBAC checks
3. Add proper error handling
4. Add transaction boundaries
5. Document comprehensively for future reference

#### Category D (Obsolete)
1. Clearly mark as obsolete in comments and docs
2. Add "TO-DO: Remove in version X" comments
3. Optionally disable endpoints with 410 Gone status

### Phase 3: Documentation and Handoff

1. Update all relevant documentation about legacy routers
2. Create clear migration paths for any consumers of these APIs
3. Document technical debt and future plans

## Success Criteria

The Legacy Routers standardization will be considered successful when:

1. All legacy routers have been classified and appropriate action taken
2. Critical legacy routers have transaction boundaries and RBAC checks
3. Documentation clearly indicates deprecation status and migration paths
4. Technical debt is managed and documented
5. Frontend teams are aware of changes and migration paths

## Timeline and Effort Estimate

Given the pragmatic approach, this final phase should be completed with:

- 1-2 days for inventory and classification
- 2-3 days for implementing changes based on classification
- 1 day for documentation and handoff

Total: Approximately 4-6 days of effort

## Conclusion

This strategy allows us to complete the standardization project in a pragmatic way that balances technical excellence with project timeline constraints. By taking a differentiated approach to legacy routers, we can focus efforts on the most critical components while managing technical debt for the rest.
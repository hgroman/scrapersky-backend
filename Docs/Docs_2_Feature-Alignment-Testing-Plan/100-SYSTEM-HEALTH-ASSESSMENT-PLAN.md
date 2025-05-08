# ScraperSky System Health Assessment Plan

## Purpose

This document outlines a systematic plan to assess and verify the health of the ScraperSky backend system following extensive modernization efforts. The goal is to identify and document:

1. The current functional state of all API endpoints
2. Any remaining legacy code that should be cleaned up
3. Configuration issues affecting production vs. development environments
4. Authentication and permission system integrity

## Context

The ScraperSky backend has undergone significant modernization, including:
- Migrating to SQLAlchemy 2.0 with async support
- Implementing RBAC (Role-Based Access Control)
- Adding multi-tenant isolation
- Standardizing database connections with Supabase/Supavisor
- Modernizing router implementations

While most components should be working properly, the rapid pace of development may have introduced regressions or left certain components in an inconsistent state.

## Assessment Plan

### 1. Health Check Verification

- Test basic API health endpoints
  - `/health`
  - `/health/database`
- Verify Docker container operation
- Validate database connection pooling configuration

### 2. Authentication System Assessment

- Run authentication test scripts
- Verify development token functionality
- Test tenant isolation middleware
- Validate RBAC permission enforcement

### 3. Core API Endpoint Testing

#### 3.1 Scraper Functionality
- Test single domain scanner
- Test batch domain scanner
- Test sitemap analyzer
- Test Google Maps API integration

#### 3.2 RBAC System
- Test RBAC admin dashboard
- Verify role and permission management
- Test feature flag system

### 4. Documentation and Browser Testing

- Verify HTML test pages functionality
- Test authentication flows in UI
- Validate documentation accuracy

### 5. Legacy Code Analysis

- Identify deprecated routes and files
- Catalog code marked for removal in git status
- Document cleanup recommendations

## Testing Approach

For each component, we'll use a combination of:
1. Direct curl commands with appropriate headers
2. Browser testing of HTML interfaces
3. Examination of code for inconsistencies
4. Automated test scripts where available

### CURL Testing Reference

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8000/health/database

# Authentication (development token)
# Default dev token: scraper_sky_2024
# Default tenant ID: 550e8400-e29b-41d4-a716-446655440000

# Single domain scraper test
curl -X POST http://localhost:8000/api/v3/batch_page_scraper/scan \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"base_url":"example.com", "max_pages":10}'

# Batch scraper test
curl -X POST http://localhost:8000/api/v3/batch_page_scraper/batch \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"domains":["example.com", "example.org"], "max_pages":10}'

# Google Maps API test
curl -X POST http://localhost:8000/api/v2/google_maps_api/search \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"business_type":"restaurant", "location":"New York, NY", "radius_km":5}'
```

## Environment Considerations

The system supports both production and development environments:

- **Development Environment**:
  - Use development token: `scraper_sky_2024`
  - Use default tenant ID: `550e8400-e29b-41d4-a716-446655440000`
  - Set `ENVIRONMENT=development` in .env
  - Docker-based local testing

- **Production Environment**:
  - Deployed to render.com using configuration in `render.yaml`
  - Uses Supavisor connection pooling for Supabase
  - Requires proper JWT authentication
  - Enforces tenant isolation and RBAC

## Documentation

Results of this assessment will be documented in:
- `90.1-Health-Check-Results.md` - Basic health check outcomes
- `90.2-API-Endpoint-Assessment.md` - Detailed API endpoint testing results
- `90.3-Legacy-Code-Cleanup-Plan.md` - Plan for removing deprecated code
- `90.4-System-Integrity-Recommendations.md` - Recommendations for further improvements

## Success Criteria

The assessment will be considered successful when:
1. All core API endpoints are verified to be functional
2. Authentication and permission systems are confirmed working
3. A complete catalog of legacy code for cleanup is created
4. A path forward for system maintenance is established

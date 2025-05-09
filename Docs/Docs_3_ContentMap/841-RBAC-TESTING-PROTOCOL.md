# ScraperSky RBAC Removal: Definitive Testing Protocol

## CRITICAL INSTRUCTION: TEST ONLY - DO NOT MODIFY CODE

This document outlines the **strict testing protocol** for verifying the RBAC removal in the ScraperSky backend. Your task is **exclusively to test and document** - under no circumstances should you implement fixes, add functionality, or suggest code modifications during this phase.

## Required Background Reading

Before beginning testing, review these documents to understand the context:

1. `26-WORK ORDER ScraperSky RBAC Removal.md` - Original work order
2. `27-RBAC-Removal-Progress.md` - Current progress status
3. `33-RBAC-Removal-Implementation-Plan.md` - Implementation plan
4. `34-RBAC-Removal-Implementation-Results.md` - What's been done so far
5. `38-RBAC-Removal-Continuation-Guide.md` - Continuation context

## Test Environment Setup

1. Start the Docker environment:

   ```bash
   cd .
   docker-compose up -d
   ```

2. Test credentials to use:
   - Development token: `scraper_sky_2024`
   - Default tenant ID: `550e8400-e29b-41d4-a716-446655440000`

## Testing Protocol

### Phase 1: Application Startup Testing

1. Start the docker environment and observe logs:

   ```bash
   docker-compose up -d
   docker-compose logs --tail=100
   ```

2. Document in detail:
   - Any RBAC-related errors in logs
   - Any authentication-related errors
   - Success/failure of server startup

### Phase 2: JWT Authentication Testing

Test each of these cases and document results:

1. **Valid JWT Token**:

   ```bash
   curl -v -H "Authorization: Bearer scraper_sky_2024" http://localhost:8000/api/health
   ```

2. **Invalid JWT Token**:

   ```bash
   curl -v -H "Authorization: Bearer invalid_token" http://localhost:8000/api/health
   ```

3. **Missing JWT Token**:
   ```bash
   curl -v http://localhost:8000/api/health
   ```

### Phase 3: Core API Endpoint Testing

Test each endpoint with valid and invalid authentication:

#### 1. ContentMap (Sitemap) Endpoints

**Create Scan Job**:

```bash
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'
```

**Check Job Status** (use job_id from previous response):

```bash
curl -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  http://localhost:8000/api/v3/sitemap/status/{job_id}
```

#### 2. Google Maps API Endpoints

**Search Request**:

```bash
curl -X POST "http://localhost:8000/api/v3/google_maps_api/search" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"query": "coffee shop", "location": "New York", "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Status Check** (use job_id from previous response):

```bash
curl -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  http://localhost:8000/api/v3/google_maps_api/status/{job_id}
```

**Staging Request**:

```bash
curl -X POST "http://localhost:8000/api/v3/google_maps_api/staging" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "{job_id}", "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

#### 3. Batch Page Scraper Endpoints

**Create Batch Job**:

```bash
curl -X POST "http://localhost:8000/api/v3/batch_page_scraper/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Check Job Status** (use job_id from previous response):

```bash
curl -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  http://localhost:8000/api/v3/batch_page_scraper/status/{job_id}
```

#### 4. Page Scraper Endpoints

**Create Page Scraper Job**:

```bash
curl -X POST "http://localhost:8000/api/v3/page_scraper/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Check Job Status** (use job_id from previous response):

```bash
curl -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  http://localhost:8000/api/v3/page_scraper/status/{job_id}
```

### Phase 4: Tenant Isolation Testing

Test cross-tenant access prevention by attempting to access a resource from another tenant:

```bash
# Create a resource in tenant A
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'

# Then try to access it with a different tenant ID
curl -H "Authorization: Bearer scraper_sky_2024" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440001" \
  http://localhost:8000/api/v3/sitemap/status/{job_id}"
```

### Phase 5: Former RBAC Router Testing

Verify the RBAC routers have been properly removed by attempting to access them:

```bash
curl -v -H "Authorization: Bearer scraper_sky_2024" \
  http://localhost:8000/api/v3/rbac-admin/stats

curl -v -H "Authorization: Bearer scraper_sky_2024" \
  http://localhost:8000/api/v3/rbac-features

curl -v -H "Authorization: Bearer scraper_sky_2024" \
  http://localhost:8000/api/v3/rbac-permissions
```

These should all return 404 errors if properly removed.

## Test Results Documentation Format

Document your findings in a markdown file named `40-RBAC-Removal-Testing-Results.md` using this exact format:

```markdown
# RBAC Removal Testing Results

## Phase 1: Application Startup Testing

- **Status**: [Success/Failure]
- **Docker Logs**: [Include relevant log snippets]
- **RBAC-Related Errors**: [List any RBAC-related errors]
- **Authentication Errors**: [List any authentication-related errors]
- **Analysis**: [Brief analysis of what the logs indicate]

## Phase 2: JWT Authentication Testing

| Test Case   | Expected Result | Actual Result | Notes   |
| ----------- | --------------- | ------------- | ------- |
| Valid JWT   | 200 OK          | [Result]      | [Notes] |
| Invalid JWT | 403 Forbidden   | [Result]      | [Notes] |
| Missing JWT | 403 Forbidden   | [Result]      | [Notes] |

## Phase 3: Core API Endpoint Testing

| Endpoint                         | Method | Authentication | Expected Result | Actual Result | Notes   |
| -------------------------------- | ------ | -------------- | --------------- | ------------- | ------- |
| /api/v3/sitemap/scan             | POST   | Valid JWT      | 202 Accepted    | [Result]      | [Notes] |
| /api/v3/sitemap/status/{job_id}  | GET    | Valid JWT      | 200 OK          | [Result]      | [Notes] |
| [Add all other endpoints tested] |        |                |                 |               |         |

## Phase 4: Tenant Isolation Testing

| Test Case           | Expected Result | Actual Result | Notes   |
| ------------------- | --------------- | ------------- | ------- |
| Cross-tenant access | 403 Forbidden   | [Result]      | [Notes] |

## Phase 5: Former RBAC Router Testing

| RBAC Endpoint            | Expected Result | Actual Result | Notes   |
| ------------------------ | --------------- | ------------- | ------- |
| /api/v3/rbac-admin/stats | 404 Not Found   | [Result]      | [Notes] |
| /api/v3/rbac-features    | 404 Not Found   | [Result]      | [Notes] |
| /api/v3/rbac-permissions | 404 Not Found   | [Result]      | [Notes] |

## Overall Assessment

- **Is RBAC Successfully Removed?**: [Yes/No/Partially]
- **Is JWT Authentication Working?**: [Yes/No/Partially]
- **Is Tenant Isolation Maintained?**: [Yes/No/Partially]
- **Are All API Endpoints Functional?**: [Yes/No/Partially]

## Identified Issues

1. [Issue description, endpoint affected, and exact error message]
2. [Issue description, endpoint affected, and exact error message]
   ...

## Recommendations

This section should ONLY document issues found and NOT implement fixes.

1. [Recommendation for issue 1]
2. [Recommendation for issue 2]
   ...
```

## STRICT GUIDELINES FOR TESTING

1. **DO NOT IMPLEMENT ANY CODE CHANGES** during the testing phase - document issues only
2. **DO NOT ATTEMPT TO REINTRODUCE RBAC** or create an alternative permission system
3. **DOCUMENT EXACT COMMANDS** used and their full responses
4. **INCLUDE RAW ERROR MESSAGES** in the documentation
5. **TEST ALL ENDPOINTS** listed in the protocol
6. **DOCUMENT RESULTS OBJECTIVELY** without speculation or opinion
7. **KEEP RECOMMENDATIONS MINIMAL** and directly related to issues found
8. **AVOID SCOPE CREEP** in any recommendations - focus ONLY on making the application work without RBAC

## Testing Completion Checklist

- [ ] All startup tests completed and documented
- [ ] All JWT authentication tests completed and documented
- [ ] All core API endpoint tests completed and documented
- [ ] All tenant isolation tests completed and documented
- [ ] All former RBAC router tests completed and documented
- [ ] Test results formatted according to the specified template
- [ ] Issues documented with exact error messages
- [ ] No code changes implemented during testing

Remember, your goal is to verify that the application works with RBAC removed, not to create a new authentication system or implement fixes. Document what works, what doesn't work, and stick strictly to the testing protocol.

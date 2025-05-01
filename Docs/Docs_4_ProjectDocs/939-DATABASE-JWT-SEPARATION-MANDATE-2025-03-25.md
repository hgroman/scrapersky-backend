# DATABASE JWT SEPARATION MANDATE

## CRITICAL ARCHITECTURAL PRINCIPLE

**Authentication happens ONLY at API gateway endpoints. Database operations NEVER handle JWT or tenant authentication.**

## The Problem

The codebase currently has a critical architectural flaw where JWT authentication and tenant-level security is being incorrectly applied at the database connection level. This creates multiple issues:

1. **Redundant Authentication**: We're authenticating twice - once at the API gateway and again at the database level
2. **Overengineered Complexity**: Adding JWT/tenant logic to database connections creates unnecessary complexity
3. **Performance Impact**: Multiple authentication layers slow down operations
4. **Maintenance Nightmare**: Changes to authentication requirements must be updated in multiple places
5. **Debugging Difficulty**: "Tenant or user not found" errors that are difficult to diagnose

## The Correct Architecture

```
┌─────────────┐     JWT Auth     ┌─────────────┐     No JWT      ┌─────────────┐
│   Client    │ ───────────────> │ API Gateway │ ───────────────>│  Database   │
│  (Browser)  │                  │  Endpoints  │                  │ Operations  │
└─────────────┘                  └─────────────┘                  └─────────────┘
                                      │                                │
                                      │                                │
                                      ▼                                ▼
                                JWT Validation                  Simple Pooled
                                User Authorization              Connections
```

## Immediate Action Required

1. **Remove ALL JWT/tenant authentication from database connections**
   - Database connections should use simple pooling without JWT/tenant logic
   - No `role` settings in server_settings except where absolutely necessary
   - No JWT claims in database connection parameters

2. **Audit ALL database operations**
   - Identify and remove any JWT/tenant logic from database operations
   - Ensure all database connections use the simplified approach

3. **Enforce API Gateway Authentication Only**
   - JWT authentication should ONLY happen at API gateway endpoints
   - Once a request passes the gateway, internal services should trust each other

## Implementation Guidelines

### Database Connection Code

```python
# CORRECT APPROACH - Simple pooled connections
connect_args = {
    "statement_cache_size": 0,        # Important for Supavisor compatibility
    "prepared_statement_cache_size": 0,  # Important for Supavisor compatibility
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",  # Avoid prepared statement name conflicts
}

# WRONG APPROACH - DO NOT DO THIS
connect_args = {
    "server_settings": {
        "role": "authenticated",  # NO ROLES
        "request.jwt.claims": token,  # NO JWT
        "request.jwt.claim.tenant_id": tenant_id  # NO TENANT ID
    }
}
```

### API Endpoint Authentication

```python
# CORRECT APPROACH - Authentication at API gateway only
@router.post("/api/v3/sitemap/scan")
async def sitemap_scan(
    request: SitemapScanRequest,
    current_user: User = Depends(get_current_user)  # JWT auth here only
):
    # Process authenticated request
    job_id = await background_tasks.start_sitemap_scan(request.domain)
    return {"job_id": job_id, "status_url": f"/api/v3/sitemap/status/{job_id}"}
```

## Audit Checklist

For each endpoint and database operation:

- [ ] Is JWT authentication happening ONLY at the API gateway?
- [ ] Are database connections using simple pooling WITHOUT JWT/tenant logic?
- [ ] Have all references to JWT/tenant in database connections been removed?
- [ ] Are background tasks operating without redundant authentication?

## Enforcement

This architectural principle is MANDATORY and non-negotiable. All code must adhere to this separation of concerns.

**NO EXCEPTIONS will be permitted without explicit approval and documentation.**
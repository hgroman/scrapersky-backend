# Authentication and Data Flow Diagram

```
┌─────────────────────────────────────┐
│ RBAC Dashboard (HTML/JavaScript)    │
│ http://localhost:8000/static/...    │
└───────────────┬─────────────────────┘
                │
                │ HTTP Request with:
                │ - Authorization: Bearer scraper_sky_2024
                │ - X-Tenant-ID: 00000000-0000-0000-0000-000000000000
                ▼
┌─────────────────────────────────────┐
│ FastAPI Web Server                  │
│ (Uvicorn running on port 8000)      │
└───────────────┬─────────────────────┘
                │
                │ Request passes through middleware
                ▼
┌─────────────────────────────────────┐
│ Permission Middleware               │
│ (permission_middleware.py)          │
└───────────────┬─────────────────────┘
                │
                │ Checks if path is public or needs auth
                │ For dev token, creates mock admin user
                ▼
┌─────────────────────────────────────┐
│ API Route Handler                   │
│ (rbac_router.py)                    │
└───────────────┬─────────────────────┘
                │
                │ Processes request with user context
                │ Prepares database query
                ▼
┌─────────────────────────────────────┐
│ SQLAlchemy Session                  │
│ (async_session.py)                  │
└───────────────┬─────────────────────┘
                │
                │ Opens connection to database
                │ Executes SQL query
                ▼
┌─────────────────────────────────────┐
│ PostgreSQL Database                 │
│ (Hosted on Supabase)                │
└───────────────┬─────────────────────┘
                │
                │ Returns query results
                ▼
┌─────────────────────────────────────┐
│ API Response                        │
│ (JSON data returned to client)      │
└───────────────┬─────────────────────┘
                │
                │ JSON data (roles, permissions, etc.)
                ▼
┌─────────────────────────────────────┐
│ RBAC Dashboard UI                   │
│ (Renders data in tables)            │
└─────────────────────────────────────┘
```

## Explanation of Each Component

1. **RBAC Dashboard (Frontend)**

   - A static HTML/JS file served from the FastAPI server
   - Makes API requests to endpoints like `/api/v2/role_based_access_control/roles`
   - Includes the development token in all requests

2. **FastAPI Web Server**

   - Runs on port 8000 using Uvicorn
   - Serves static files and API endpoints
   - Routes requests to appropriate handlers

3. **Permission Middleware**

   - Intercepts all incoming requests
   - Checks if the path is in PUBLIC_PATHS (no auth needed)
   - For protected paths, validates the token
   - For "scraper_sky_2024", creates a mock admin user with full permissions

4. **API Route Handler**

   - Specific endpoint function (e.g., get_all_roles_endpoint)
   - Receives the authenticated request with user information
   - Prepares to query the database for requested data

5. **SQLAlchemy Session**

   - Creates a database connection session
   - Manages transactions and connection pooling
   - Provides an interface for executing SQL queries

6. **PostgreSQL Database**

   - Hosted on Supabase
   - Stores all application data including roles and permissions
   - Executes SQL queries and returns results

7. **API Response**

   - JSON data returned from the database
   - Formatted according to API specifications
   - Sent back to the client

8. **RBAC Dashboard UI**
   - Receives the JSON response
   - Renders the data in tables
   - Provides UI for managing roles and permissions

The development token "scraper_sky_2024" is recognized at the Permission Middleware level, which then creates a mock admin user with full permissions. This bypasses normal authentication but still follows the same flow for database access.

# RBAC Modernization Task - Final Phase of ScraperSky Modernization Project

## Project Context

You're working on the final phase of the ScraperSky backend modernization project. We've successfully modernized several key components (Google Maps API, Sitemap Analyzer, Page Scraper) using our established patterns, and now we need to implement the RBAC (Role-Based Access Control) modernization following the same approach.

## Current Status

We've already:

1. Analyzed the database structure for RBAC tables
2. Identified the SQLAlchemy models in `src/models/rbac.py`
3. Examined the existing RBAC router in `src/router_factory/rbac_router.py`
4. Verified the database schema through direct queries

## Database Structure

The RBAC system uses these tables:

- **roles**: `id` (integer), `name` (text), `description` (text), `created_at` (timestamp)
- **permissions**: `id` (uuid), `name` (text), `description` (text), `created_at/updated_at` (timestamps)
- **role_permissions**: `id` (uuid), `role` (text), `permission_id` (uuid), `created_at` (timestamp)
- **user_tenants**: Maps users to roles within tenants (`user_id`, `tenant_id`, `role_id`)
- **features**: Feature flags with `id`, `title`, `description`, etc.
- **tenant_features**: Maps features to tenants with enablement status
- **sidebar_features**: UI navigation elements with permission requirements

## Your Task

Implement the RBAC dashboard following our established modernization patterns:

1. **Apply the GMA Pattern** (Google Maps API Pattern):

   - Dual versioned router with truthful naming (v1: `/api/v1/rbac/*`, v2: `/api/v2/role_based_access_control/*`)
   - Router factory pattern implementation
   - Complete SQLAlchemy integration
   - Standardized error handling

2. **Create the RBAC Dashboard**:
   - Create `static/rbac-dashboard.html` that matches our admin dashboard style
   - Implement tabs for each RBAC entity (roles, permissions, role_permissions, etc.)
   - Create JavaScript to interact with the modernized API endpoints
   - Ensure proper authentication and authorization

## Implementation Requirements

Follow these specific patterns from our modernization project:

1. **Router Factory Pattern**:

```python
def create_router(prefix: str, tags: List[str], dependencies: List[Depends] = None) -> APIRouter:
    """Create a standardized router with consistent configuration"""
    return APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies or [],
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
        }
    )
```

2. **API Versioning Pattern**:

```python
from src.factories.api_version_factory import ApiVersionFactory

# Create dual versioned routers
routers = ApiVersionFactory.create_versioned_routers(
    v1_prefix="/api/v1/rbac",
    v2_prefix="/api/v2/role_based_access_control",
    tags=["role_based_access_control"]
)

# Register routes to both versions
@routers["v1"].post("/roles")
@routers["v2"].post("/roles")
async def create_role():
    # Implementation that serves both v1 and v2
    pass
```

3. **Extract Value Pattern** for SQLAlchemy Column Types:

```python
def extract_value(obj: Any, attr_name: str, default: Any = None) -> Any:
    """Safely extract a value from an object attribute, handling SQLAlchemy columns."""
    if obj is None:
        return default
    # ... rest of implementation
```

4. **Session and Transaction Management Pattern**:

```python
async with get_session() as session:
    async with session.begin():
        # Database operations with automatic commit/rollback
```

## Modernization Sequence

Follow this exact sequence:

1. **SQLAlchemy Implementation First**: Ensure all models are properly defined
2. **Service Integration Second**: Implement service layer using SQLAlchemy models
3. **Router Factory Pattern Implementation**: Apply consistent router creation
4. **API Versioning with 100% Truthful Naming**: Create properly named endpoints
5. **Complete Implementation and Validation**: Finish with no shortcuts

## Success Criteria

Your implementation will be successful when:

1. **Zero Direct DB Operations**: No direct database operations in any routes
2. **100% SQLAlchemy Usage**: Complete elimination of raw SQL
3. **Standardized Error Handling**: All routes using error_service consistently
4. **Router Factory Usage**: All routes created using the router factory pattern
5. **Truthful Naming Conventions**: All v2 API endpoints accurately reflect their functionality
6. **Functional Dashboard**: A working RBAC dashboard that interacts with the API

## Reference Documents

- **Document 25**: ScraperSky Context Reset - The master document for the modernization project
- **Document 41**: RBAC Modernization Plan - Specific plan for RBAC modernization
- **Document 46**: RBAC System Analysis - Database structure and implementation details

## Final Notes

This is the final phase of our modernization project. The RBAC system is critical for security and user management, so it's essential to implement it correctly following all our established patterns. The Google Maps API implementation (GMA Pattern) should be your primary reference for how to structure the code and implement dual versioning with truthful naming.

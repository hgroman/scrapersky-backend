# ScraperSky RBAC Implementation - Synthesized Documentation Suite

I'll create a new set of four comprehensive documents that distill the most critical information from all sources, organized by function rather than chronology. This will give you a "single source of truth" for the project.

## Document 1: Technical Architecture and Patterns

```markdown
# ScraperSky Technical Architecture and Patterns

## System Architecture Overview

ScraperSky follows a layered architecture with clean separation of concerns:
```

┌───────────────────────────────────────┐
│ Presentation Layer │
│ (API Routers, Request/Response) │
├───────────────────────────────────────┤
│ Business Logic Layer │
│ (Services) │
├───────────────────────────────────────┤
│ Data Access Layer │
│ (SQLAlchemy Models) │
├───────────────────────────────────────┤
│ Database Layer │
│ (PostgreSQL) │
└───────────────────────────────────────┘

```

### Component Relationships

```

┌────────────────┐ ┌────────────────┐
│ API Client │ │ Fast API App │
└───────┬────────┘ └───────┬────────┘
│ │
│ ▼
┌───────▼──────────────────────────────┐
│ Router Factory │
├─────────┬─────────────────┬──────────┤
│ V1 │ │ │ V2 │
│ Router │ │ │ Router │
└─────────┘ │ └──────────┘
▼
┌──────────────────────────────────────┐
│ Services │
├──────────────────────────────────────┤
│ Validation │ Core │ Domain │
│ Service │ Services │ Services │
└──────────────┴──────────┴────────────┘
│
▼
┌──────────────────────────────────────┐
│ SQLAlchemy Models │
└──────────────────────────────────────┘
│
▼
┌──────────────────────────────────────┐
│ Database │
└──────────────────────────────────────┘

````

## Key Architectural Patterns

### 1. Router Factory Pattern

The Router Factory creates standardized routes with consistent error handling:

```python
class RouterFactory:
    @staticmethod
    def create_get_route(
        router: APIRouter,
        path: str,
        endpoint: Callable,
        response_model: Type[Any] = None,
        ...
    ) -> None:
        # Standardized route creation
````

This pattern ensures:

- Consistent error handling across all endpoints
- Standardized response formatting
- Uniform authentication and validation
- Reduced code duplication

### 2. API Versioning Strategy

Dual versioning with truthful naming:

```python
# Legacy route (v1)
@router.get("/api/v1/places/search")
async def search_places():
    # Implementation

# Truthful naming route (v2)
@router.get("/api/v2/google_maps_api/search")
async def search_places():
    # Same implementation
```

Both v1 and v2 endpoints point to the same handler functions, ensuring:

- Backward compatibility through v1 endpoints
- More descriptive naming through v2 endpoints
- Simple transition path for API consumers
- No code duplication for different versions

### 3. Service Organization Pattern

Services are organized into domain-specific directories:

```
src/
  services/
    core/
      auth_service.py
      validation_service.py
      error_service.py
    rbac/
      rbac_service.py
      feature_service.py
    sitemap/
      processing_service.py
      metadata_service.py
    google_maps_api/
      search_service.py
      details_service.py
```

Each service:

- Encapsulates domain-specific business logic
- Is independent of the presentation layer
- Follows consistent interface patterns
- Has a single responsibility

## Database Connectivity

### Supabase Connection Configuration

The application connects to Supabase using:

```python
# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    connect_args=connect_args
)
```

Important considerations:

- Supabase has migrated from PgBouncer to Supavisor
- Different configuration is required for Supavisor vs. PgBouncer
- Environment-specific settings optimize for development or production
- The `.env` file contains all necessary credentials and MUST NOT be modified

### Session Management

Async session management ensures proper database connection handling:

```python
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()
```

Key advantages:

- Proper resource cleanup with context managers
- Automatic transaction management
- Non-blocking I/O with async/await
- Consistent error handling

## Error Handling Strategy

Centralized error handling through the `error_service`:

```python
class ErrorService:
    """Service for standardized error handling."""

    @staticmethod
    def handle_exception(
        exception: Exception,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        log_error: bool = True
    ) -> Dict[str, Any]:
        # Implementation...

    @staticmethod
    def format_error_response(error_details: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation...

    # Convenience methods for common errors
    @staticmethod
    def not_found(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Implementation...
```

Benefits:

- Consistent error response structure
- Appropriate HTTP status codes
- Detailed error messages for debugging
- Centralized logging

## Authentication Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Client/User    │────▶│  Authentication │────▶│  Permission     │────▶│  Protected      │
│  Request        │     │  Verification   │     │  Verification   │     │  Resource       │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### JWT Token Structure

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  JWT Token                                                    │
│                                                               │
│  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐  │
│  │             │       │             │      │             │  │
│  │  Header     │       │  Payload    │      │  Signature  │  │
│  │  - alg      │       │  - user_id  │      │  HMACSHA256 │  │
│  │  - typ      │       │  - tenant_id│      │  (secret)   │  │
│  │             │       │  - exp      │      │             │  │
│  │             │       │  - roles    │      │             │  │
│  │             │       │  - perms    │      │             │  │
│  └─────────────┘       └─────────────┘      └─────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Authentication Middleware Process

The permission middleware:

1. Intercepts all requests
2. Checks if the path is public (bypasses auth)
3. For protected paths, validates the JWT token
4. Extracts user and tenant information
5. For "scraper_sky_2024" dev token, creates a mock admin user
6. Checks required permissions for the endpoint
7. Allows or denies access based on permissions

### Development Mode Considerations

For development and testing, the system accepts a hardcoded token:

```python
# Special case for development token
if settings.ENVIRONMENT == "development" and token == "scraper_sky_2024":
    # Create a development user with admin permissions
    request.state.user = {
        "id": "dev_admin_user",
        "tenant_id": DEFAULT_TENANT_ID,
        "is_dev_token": True,
        "permissions": ["rbac_admin", "manage_roles", "manage_permissions", "view_roles", "view_permissions", "view_users"]
    }
    return await call_next(request)
```

## Conclusion

The ScraperSky architecture follows modern FastAPI best practices with a clear separation of concerns. The Router Factory pattern ensures consistent API behavior, while the service-oriented design provides modularity and maintainability. The dual API versioning strategy allows for both backward compatibility and more descriptive endpoint naming.

Database connectivity is optimized for Supabase's Supavisor, with careful session management and error handling. The authentication system uses JWT tokens with a comprehensive permission checking system that supports both production and development environments.

````

## Document 2: RBAC Implementation Guide

```markdown
# RBAC Implementation Guide

## Database Schema

### Core Tables

#### 1. `roles` Table

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
````

- **Purpose**: Stores role definitions (USER, ADMIN, SUPER_ADMIN, GLOBAL_ADMIN)
- **Note**: Uses SERIAL (integer) primary key for better performance, not UUID

#### 2. `permissions` Table

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

- **Purpose**: Stores granular permissions for actions
- **Note**: Uses UUID primary key for global uniqueness

#### 3. `role_permissions` Table

```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id INTEGER NOT NULL,
    permission_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE (role_id, permission_id)
);
```

- **Purpose**: Maps roles to their assigned permissions
- **Note**: Uses INTEGER for role_id (referencing roles.id) and UUID for permission_id

#### 4. `user_roles` Table

```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE (user_id, role_id)
);
```

- **Purpose**: Assigns roles to users
- **Note**: This table was previously missing and had to be created

### Feature Management Tables

#### 5. `feature_flags` Table

```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    default_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

- **Purpose**: Defines available features/services
- **Core Features**:
  - LocalMiner: Google Maps scraping and analysis
  - ContentMap: Sitemap analyzer
  - FrontendScout: Homepage scraping
  - SiteHarvest: Full-site scraper
  - EmailHunter: Email scraping
  - ActionQueue: Follow-up manager
  - SocialRadar: Social media scraping
  - ContactLaunchpad: Contact management

#### 6. `tenant_features` Table

```sql
CREATE TABLE tenant_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    feature_id UUID NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (feature_id) REFERENCES feature_flags(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    UNIQUE (tenant_id, feature_id)
);
```

- **Purpose**: Controls which features are enabled for each tenant

#### 7. `sidebar_features` Table

```sql
CREATE TABLE sidebar_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID NOT NULL,
    sidebar_name TEXT NOT NULL,
    url_path TEXT NOT NULL,
    icon TEXT,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (feature_id) REFERENCES feature_flags(id) ON DELETE CASCADE
);
```

- **Purpose**: Defines UI navigation for features
- **Standard Tabs** (per feature):
  1. Control Center
  2. Discovery Scan
  3. Deep Analysis
  4. Review & Export
  5. Smart Alerts
  6. Performance Insights

## SQLAlchemy Models Implementation

### Role Model

```python
class Role(Base):
    """Role model for RBAC."""
    __tablename__ = 'roles'

    # Note: Using Integer, not UUID
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")
```

### Permission Model

```python
class Permission(Base):
    """Permission model for RBAC."""
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False, onupdate=func.now())

    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
```

### RolePermission Model

```python
class RolePermission(Base):
    """Association model for role permissions."""
    __tablename__ = 'role_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Add unique constraint
    __table_args__ = (UniqueConstraint('role_id', 'permission_id'),)
```

### UserRole Model

```python
class UserRole(Base):
    """Model for assigning roles to users."""
    __tablename__ = 'user_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    role = relationship("Role", back_populates="user_roles")

    # Add unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'role_id'),)
```

### Feature Flag Models

Similar models should be implemented for `feature_flags`, `tenant_features`, and `sidebar_features` tables.

## API Endpoints

### V2 Endpoint Structure

All RBAC endpoints follow the pattern `/api/v2/role_based_access_control/*`:

- `GET /api/v2/role_based_access_control/roles` - Get all roles
- `GET /api/v2/role_based_access_control/roles/{id}` - Get role by ID
- `POST /api/v2/role_based_access_control/roles` - Create a new role
- `PUT /api/v2/role_based_access_control/roles/{id}` - Update a role
- `DELETE /api/v2/role_based_access_control/roles/{id}` - Delete a role

Similar endpoints exist for permissions, user-roles, features, tenant-features, and sidebar-features.

### Router Implementation

```python
# Create versioned routers
routers = api_version_factory.create_versioned_routers(
    v1_prefix="/api/v1/rbac",
    v2_prefix="/api/v2/role_based_access_control",
    tags=["role_based_access_control"]
)

# Register role endpoints
router_factory.create_get_route(
    router=routers["v2"],
    path="/roles",
    response_model=RolesResponse,
    endpoint=get_roles,
    summary="Get all roles",
    description="Returns a list of all roles in the system"
)

# Additional endpoints for CRUD operations on other RBAC entities
```

## Permission Middleware

The permission middleware checks if users have the required permissions for each request:

```python
async def permission_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """Middleware to check if user has permission to access endpoint."""
    # Get the path and method
    path = request.url.path
    method = request.method

    # Skip permission check for public endpoints
    if is_public_path(path):
        return await call_next(request)

    # Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")

    # Special case for development token
    if token == "scraper_sky_2024" and settings.environment.lower() in ["development", "dev"]:
        # Create a dev admin user with permissions
        request.state.user = {
            "id": "dev_admin_user",
            "tenant_id": DEFAULT_TENANT_ID,
            "permissions": ["rbac_admin", "manage_roles", "manage_permissions", ...]
        }
        return await call_next(request)

    # Regular token validation and permission checking
    try:
        # Decode and validate token
        user = await authorization_service.validate_token(token)

        # Check permission
        required_permission = get_required_permission(method, path)
        if required_permission:
            has_permission = await authorization_service.check_permission(
                user_id=user.id,
                permission=required_permission
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Not authorized - Missing permission: {required_permission}"
                )

        # Continue with the request
        request.state.user = user
        return await call_next(request)
    except Exception as e:
        # Handle errors
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")
```

## RBAC Dashboard Implementation

The RBAC dashboard (`/static/rbac-dashboard-fixed.html`) provides a UI for managing:

- Roles and their permissions
- User role assignments
- Feature flags
- Sidebar feature configuration

The dashboard makes API calls to the RBAC endpoints to perform CRUD operations.

## Integration with Existing Systems

### User Authentication

1. User logs in and receives a JWT token
2. Token contains user ID and tenant ID
3. User makes requests with the token in the Authorization header
4. Permission middleware validates the token and checks permissions
5. If authorized, the request proceeds; otherwise, a 403 error is returned

### Feature Management

1. Features are defined in the `feature_flags` table
2. Features can be enabled/disabled per tenant via `tenant_features`
3. UI navigation is configured in `sidebar_features`
4. Permission middleware checks if required features are enabled

## Common Database Queries

### Check User Permissions

```sql
SELECT EXISTS (
    SELECT 1
    FROM permissions p
    JOIN role_permissions rp ON p.id = rp.permission_id
    JOIN roles r ON r.id = rp.role_id
    JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = 'user-uuid-here'
    AND p.name = 'permission-name-here'
);
```

### Check Feature Availability

```sql
SELECT EXISTS (
    SELECT 1
    FROM tenant_features tf
    JOIN feature_flags ff ON tf.feature_id = ff.id
    WHERE tf.tenant_id = 'tenant-uuid-here'
    AND ff.name = 'feature-name-here'
    AND tf.is_enabled = true
);
```

### Get User Roles

```sql
SELECT r.name
FROM roles r
JOIN user_roles ur ON r.id = ur.role_id
WHERE ur.user_id = 'user-uuid-here';
```

### Get Sidebar Items

```sql
SELECT sf.*
FROM sidebar_features sf
JOIN feature_flags ff ON sf.feature_id = ff.id
JOIN tenant_features tf ON ff.id = tf.feature_id
WHERE tf.tenant_id = 'tenant-uuid-here'
AND tf.is_enabled = true
ORDER BY sf.display_order;
```

````

## Document 3: Implementation Checklist and Roadmap

```markdown
# RBAC Implementation Checklist and Roadmap

## Current Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| RBAC Models | ✅ 95% Complete | Models created but may need further refinement |
| Database Connection | ✅ 90% Complete | Using Supabase with SQLAlchemy successfully |
| RBAC Router | ✅ 85% Complete | Backend API endpoints implemented but need refinement |
| API Endpoints | ✅ 85% Complete | Truthful naming implemented but need better error handling |
| Dashboard Interface | 🚧 75% Complete | RBAC dashboard interface created but needs integration |
| React Components | 🚧 30% Complete | Basic components started, needs full implementation |
| Authentication System | 🚧 50% Complete | Development token mechanism needs improvement |
| Permission Middleware | 🚧 40% Complete | Issues with user ID extraction and permission checking |

## Phase 1: Database Setup and Verification (2 days)

### 1.1 Database Schema Verification

- [ ] Connect to Supabase database using credentials in `.env`
- [ ] Verify `roles` table structure and columns (using SERIAL primary key)
- [ ] Verify `permissions` table structure and columns (using UUID primary key)
- [ ] Verify `role_permissions` table structure (proper foreign keys)
- [ ] Verify `user_roles` table structure
- [ ] Verify `feature_flags`, `tenant_features`, and `sidebar_features` tables

### 1.2 Sample Data Population

- [ ] Run `populate_rbac_sample_data.py` to add test data
- [ ] Verify role data insertion
- [ ] Verify permission data insertion
- [ ] Verify role-permission mappings
- [ ] Verify feature flags and tenant features
- [ ] Verify sidebar features for each service

## Phase 2: Code Updates (3 days)

### 2.1 SQLAlchemy Model Updates

- [ ] Update `Role` model to use Integer primary key
- [ ] Update `Permission` model with proper UUID handling
- [ ] Update `RolePermission` model to use role_id (not role)
- [ ] Implement `UserRole` model
- [ ] Update feature models to match new schema

### 2.2 API Endpoint Implementation

- [ ] Complete `GET /roles` endpoint
- [ ] Complete `GET /roles/{id}` endpoint
- [ ] Complete `POST /roles` endpoint
- [ ] Complete `PUT /roles/{id}` endpoint
- [ ] Complete `DELETE /roles/{id}` endpoint
- [ ] Repeat for permissions, user-roles, and features

### 2.3 Service Layer Implementation

- [ ] Implement RBAC service methods
- [ ] Implement permission checking functionality
- [ ] Implement feature flag service
- [ ] Implement user role management
- [ ] Add caching for performance optimization

## Phase 3: Authentication and Middleware (2 days)

### 3.1 Authentication Improvements

- [ ] Refine JWT token generation and validation
- [ ] Improve development token mechanism
- [ ] Add proper error handling for authentication failures
- [ ] Implement token refresh mechanism

### 3.2 Permission Middleware Enhancements

- [ ] Fix user ID extraction from tokens
- [ ] Improve permission checking logic
- [ ] Add feature flag enforcement
- [ ] Ensure tenant isolation
- [ ] Add better logging for troubleshooting

## Phase 4: Dashboard Integration (3-4 days)

### 4.1 Dashboard Updates

- [ ] Update API endpoint paths in dashboard
- [ ] Fix role display in dashboard
- [ ] Implement role-permission assignment UI
- [ ] Add user role management
- [ ] Implement feature flag management
- [ ] Add sidebar feature configuration

### 4.2 React Component Implementation

- [ ] Create permission-based UI components
- [ ] Implement JWT authentication in React
- [ ] Create role management components
- [ ] Add feature flag components
- [ ] Implement sidebar based on enabled features

## Phase 5: Testing and Verification (2-3 days)

### 5.1 Unit Testing

- [ ] Test role CRUD operations
- [ ] Test permission assignments
- [ ] Test user role management
- [ ] Test feature flag operations
- [ ] Test authentication functions

### 5.2 Integration Testing

- [ ] Test complete authentication flow
- [ ] Test permission middleware
- [ ] Test feature flag enforcement
- [ ] Test API endpoints
- [ ] Test dashboard functionality

### 5.3 Performance Testing

- [ ] Check database query performance
- [ ] Evaluate caching effectiveness
- [ ] Measure API response times
- [ ] Identify bottlenecks
- [ ] Optimize critical paths

## Phase 6: Documentation and Handover (1-2 days)

### 6.1 Documentation Updates

- [ ] Update API documentation
- [ ] Document database schema
- [ ] Create user guide for dashboard
- [ ] Document authentication flow
- [ ] Add troubleshooting guide

### 6.2 Handover Activities

- [ ] Knowledge transfer sessions
- [ ] Review open issues
- [ ] Conduct final testing
- [ ] Prepare production deployment plan

## Critical Validation Points

To ensure the RBAC implementation is successful, verify:

1. **Role Assignment**:
   - Can create roles
   - Can assign permissions to roles
   - Can assign roles to users
   - Can verify user permissions

2. **Permission Checks**:
   - API endpoints correctly check permissions
   - Users without permissions are denied access
   - Permission inheritance works as expected
   - Development token has appropriate permissions

3. **Feature Management**:
   - Features can be enabled/disabled per tenant
   - Disabled features are inaccessible
   - UI adapts to enabled features
   - Sidebar shows correct navigation

4. **Dashboard Functionality**:
   - All CRUD operations work
   - Changes take effect immediately
   - Error handling is appropriate
   - UI is intuitive and usable

## Timeline Summary

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1 | Database Setup and Verification | 2 days | None |
| 2 | Code Updates | 3 days | Phase 1 |
| 3 | Authentication and Middleware | 2 days | Phase 2 |
| 4 | Dashboard Integration | 3-4 days | Phase 3 |
| 5 | Testing and Verification | 2-3 days | Phase 4 |
| 6 | Documentation and Handover | 1-2 days | Phase 5 |

Total estimated time: 13-16 days
````

## Document 4: Known Issues and Solutions

````markdown
# RBAC Implementation: Known Issues and Solutions

## Database Connection Challenges

### Issue 1: Model-Schema Mismatches

**Problem**: SQLAlchemy models included columns that didn't exist in the actual database tables.

**Examples**:

- The `Role` model included a `tenant_id` column, but the actual `roles` table doesn't have this column.
- The `BaseModel` class added an `updated_at` column, but some tables like `roles` don't have this column.

**Solution**: Create custom base models for tables that don't follow the standard schema:

```python
# Custom base model for Role that doesn't include updated_at
class RoleBaseModel:
    """
    Custom base model for Role that doesn't include updated_at.
    The actual roles table in the database doesn't have an updated_at column.
    """
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Role(Base, RoleBaseModel):
    """Role model for RBAC."""
    __tablename__ = 'roles'

    name = Column(String, nullable=False)
    description = Column(String)
    # Note: tenant_id column removed as it doesn't exist in the actual database schema
```
````

### Issue 2: Supavisor Compatibility Issues

**Problem**: Supabase has migrated from PgBouncer to their own connection pooler called Supavisor, which requires different configuration.

**Examples**:

- The `statement_cache_size=0` parameter was required for PgBouncer but causes errors with Supavisor.
- Using `NullPool` is not appropriate for Supavisor; a proper connection pool should be used.

**Solution**: Update the SQLAlchemy connection configuration to be compatible with Supavisor:

```python
# Connect args for Supavisor
connect_args = {
    "ssl": ssl_context,
    "timeout": settings.db_connection_timeout,
    # Generate unique prepared statement names to avoid conflicts
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    # Don't use statement_cache_size=0 with Supavisor
}

# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    connect_args=connect_args,
    # Use a proper connection pool for Supavisor instead of NullPool
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    isolation_level="AUTOCOMMIT"  # AUTOCOMMIT is still recommended for Supavisor
)
```

### Issue 3: Relationship Configuration Issues

**Problem**: The self-referential relationship in `SidebarFeature.children` was missing the `single_parent=True` parameter, causing cascade issues.

**Solution**: Properly configure relationships with appropriate parameters:

```python
# Self-referential relationship with single_parent=True to fix the cascade issue
children = relationship(
    "SidebarFeature",
    backref=backref("parent", remote_side=[id]),
    cascade="all, delete-orphan",
    single_parent=True  # Add this to fix the cascade issue
)
```

## Authentication System Challenges

### Issue 1: Development Token Limitations

**Problem**: The development token "scraper_sky_2024" has a fixed set of permissions that may not cover all required permissions.

**Solution**: Expand the permission list for the development token:

```python
# In permission_middleware.py
if token == "scraper_sky_2024" and settings.environment.lower() in ["development", "dev"]:
    logger.info("Using development token for authentication")
    user = {
        "id": "dev-admin-id",
        "tenant_id": DEFAULT_TENANT_ID,
        "roles": ["admin"],
        "permissions": [
            "rbac_admin",
            "manage_roles",
            "manage_permissions",
            "view_roles",
            "view_permissions",
            "view_users",
            "start_localminer",
            "view_localminer",
            "start_contentmap",
            "view_contentmap",
            # Add all required permissions here
        ],
    }
```

### Issue 2: Environment Detection Problems

**Problem**: Inconsistent environment settings may cause the development token to fail.

**Solution**: Improve environment detection logic:

```python
# More robust environment detection
is_development = (
    settings.environment.lower() in ["development", "dev"] or
    os.environ.get("ENVIRONMENT", "").lower() in ["development", "dev"] or
    os.environ.get("ENV", "").lower() in ["development", "dev"]
)

if token == "scraper_sky_2024" and is_development:
    # Development token handling
```

### Issue 3: Public Path Regex Limitations

**Problem**: Regex patterns may not match all endpoint variations with parameters.

**Solution**: Use more robust regex patterns and add explicit paths:

```python
PUBLIC_PATHS = [
    # Explicit public endpoints
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",

    # Regex patterns with parameter handling
    r"^/api/v[12]/public/.*",
    r"^/api/v[12]/auth/login.*",
    r"^/api/v[12]/auth/register.*",
]

def is_public_path(path: str) -> bool:
    """Check if a path is public (no auth required)."""
    # Check explicit paths first
    if path in PUBLIC_PATHS:
        return True

    # Then check regex patterns
    return any(re.match(pattern, path) for pattern in PUBLIC_PATHS if pattern.startswith('^'))
```

## Server Process Management Issues

### Issue: Port Binding Errors

**Problem**: Repeated "address already in use" errors indicate process management problems.

**Solution**: Create a development script that properly manages the server process:

```bash
#!/bin/bash
# run_server.sh

# Kill any existing server processes
pkill -f "python -m src.main" || true

# Wait for the port to be released
sleep 1

# Start the server
python -m src.main

# Trap Ctrl+C to kill the server process
trap "pkill -f 'python -m src.main'" SIGINT SIGTERM
```

## Dashboard Integration Issues

### Issue 1: Endpoint Path Mismatches

**Problem**: The dashboard was using incorrect V2 endpoint paths.

**Solution**: Update the API endpoints in the dashboard:

```javascript
// In static/rbac-dashboard-fixed.html
const API_ENDPOINTS = {
  roles: `${API_BASE_URL}/v2/role_based_access_control/roles`,
  permissions: `${API_BASE_URL}/v2/role_based_access_control/permissions`,
  assignments: `${API_BASE_URL}/v2/role_based_access_control/role-permissions`,
};
```

### Issue 2: Role-Permission Assignments Not Working

**Problem**: Error "Error loading assignments: API Error (404): Not found" indicates the assignments endpoint may not be implemented correctly.

**Solution**: Verify the endpoint implementation and path:

```javascript
// Check if the endpoint is correctly implemented
fetch("/api/v2/role_based_access_control/role-permissions")
  .then((response) => {
    if (!response.ok) {
      console.error(`API Error (${response.status}): ${response.statusText}`);
      // Try alternative endpoint name
      return fetch("/api/v2/role_based_access_control/role_permissions");
    }
    return response;
  })
  .then((response) => response.json())
  .then((data) => console.log("Assignments data:", data))
  .catch((error) => console.error("Error loading assignments:", error));
```

## Code Quality and Technical Debt Issues

### Issue 1: Pydantic V2 Migration Incomplete

**Problem**: Warnings about 'orm_mode' being renamed to 'from_attributes' indicate partial migration to Pydantic V2.

**Solution**: Update all Pydantic models:

```python
# Before (Pydantic V1)
class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

# After (Pydantic V2)
class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
```

### Issue 2: Deprecated FastAPI Patterns

**Problem**: Warning about on_event being deprecated indicates outdated lifecycle management approaches.

**Solution**: Update to modern lifespan event handlers:

```python
# Before (deprecated)
@app.on_event("startup")
async def startup_event():
    # Startup code

# After (modern approach)
@app.lifespan
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Shutdown code
```

## Security Implementation Challenges

### Issue 1: JWT Token Validation

**Problem**: JWT token validation may not handle all edge cases properly.

**Solution**: Implement more robust token validation:

```python
def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    """
    try:
        # 1. Decode the token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2. Extract user ID from subject claim
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user ID",
            )

        # 3. Check token expiration explicitly
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing expiration",
            )

        # 4. Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

        # 5. Return the decoded payload
        return payload

    except JWTError as e:
        # 6. Handle invalid tokens
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
```

### Issue 2: Role-based Route Protection

**Problem**: Some routes may not be properly protected by permission checks.

**Solution**: Implement a decorator for requiring specific permissions:

```python
def require_permission(permission: str):
    """
    Dependency to require a specific permission.

    Usage:
        @app.get("/admin/users")
        async def get_users(
            _: None = Depends(require_permission("view_users"))
        ):
            # Implementation
    """
    async def dependency(
        request: Request,
    ):
        # Get user from request state
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )

        # Check if user has the required permission
        user_permissions = user.get("permissions", [])
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission} required"
            )

        # Return None - this dependency is just for validation
        return None

    return dependency
```

## Troubleshooting Approaches

### Database Schema Verification

To verify the database schema:

```sql
-- Get table columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'roles';

-- Get foreign keys
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'role_permissions';
```

### Authentication Debugging

To debug authentication issues:

1. Check JWT token contents:

```python
import jwt
token = "your_token_here"
try:
    decoded = jwt.decode(token, options={"verify_signature": False})
    print("Token content:", decoded)
except Exception as e:
    print("Error decoding token:", str(e))
```

2. Test permissions directly:

```python
async def test_permission(user_id: str, permission: str):
    """Test if a user has a specific permission."""
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN roles r ON r.id = rp.role_id
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = :user_id
        AND p.name = :permission
    )
    """
    async with get_session() as session:
        result = await session.execute(
            text(query),
            {"user_id": user_id, "permission": permission}
        )
        has_permission = result.scalar()
        print(f"User {user_id} has permission {permission}: {has_permission}")
```

### API Endpoint Testing

Use curl to test API endpoints directly:

```bash
# Test permissions endpoint
curl -s -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 00000000-0000-0000-0000-000000000000" http://localhost:8000/api/v2/role_based_access_control/permissions

# Test roles endpoint
curl -s -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 00000000-0000-0000-0000-000000000000" http://localhost:8000/api/v2/role_based_access_control/roles

# Test role-permissions endpoint
curl -s -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 00000000-0000-0000-0000-000000000000" http://localhost:8000/api/v2/role_based_access_control/role-permissions
```

### Dashboard Debugging

To debug dashboard issues:

1. Open the browser developer console while using the dashboard
2. Check for JavaScript errors
3. Use the Network tab to see API requests and responses
4. Add debugging outputs to the dashboard code:

```javascript
// Add debugging to API calls
fetch(API_ENDPOINTS.roles)
  .then((response) => {
    console.log("Roles response:", response);
    return response.json();
  })
  .then((data) => {
    console.log("Roles data:", data);
    // Process data
  })
  .catch((error) => {
    console.error("Error loading roles:", error);
  });
```

```

I believe these four documents together provide a comprehensive, non-redundant overview of the ScraperSky RBAC implementation project. They cover:

1. **Technical Architecture and Patterns**: The foundational architectural patterns and system design
2. **RBAC Implementation Guide**: Detailed database schema, models, and API endpoints
3. **Implementation Checklist and Roadmap**: A concrete plan with timeline estimates
4. **Known Issues and Solutions**: Critical challenges and their solutions

These documents eliminate duplication while preserving all the critical information needed to successfully complete the RBAC implementation.
```

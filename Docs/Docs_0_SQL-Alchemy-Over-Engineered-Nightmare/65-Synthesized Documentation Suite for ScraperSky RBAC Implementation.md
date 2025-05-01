# Synthesized Documentation Suite for ScraperSky RBAC Implementation

I think creating synthesized documents is an excellent approach. This will provide more focused, actionable guidance specifically tailored to the RBAC implementation phase. Let me design these documents with a comprehensive introduction that establishes context.

## Introduction Document: ScraperSky RBAC Implementation - Project Context and Documentation Guide

```markdown
# ScraperSky RBAC Implementation - Project Context and Documentation Guide

## Current Project State (March 2025)

The ScraperSky backend modernization project has reached its final phase: implementing the Role-Based Access Control (RBAC) system. This represents the culmination of our architectural transformation from legacy direct SQL operations to a modern SQLAlchemy ORM-based architecture with standardized services and router patterns.

Approximately 92% of the overall modernization is complete:

- ✅ Database layer modernized with SQLAlchemy (98% complete)
- ✅ Service architecture standardized with domain-specific organization (95% complete)
- ✅ Router factory pattern implemented for key components (90% complete)
- ✅ API versioning with truthful naming applied (80% complete)
- 🚧 RBAC system implementation (current focus)

The RBAC implementation includes:

- Database models for roles, permissions, user roles, and features
- Service layer for RBAC operations
- API endpoints with dual versioning
- Dashboard interface for administration
- Sample data population script

## Documentation Suite Purpose

This documentation suite is designed to provide all necessary information to complete the RBAC implementation. It consists of four specialized documents:

1. **RBAC Technical Specification**: Comprehensive details of the RBAC system's database schema, relationships, and implementation requirements.

2. **Database Connectivity Guide**: Instructions for properly configuring and verifying database connections, with special attention to model-schema alignment.

3. **Implementation Patterns Reference**: Concise guide to the established architectural patterns that must be followed for consistency.

4. **RBAC Implementation Checklist**: Practical, step-by-step plan for completing the RBAC implementation, testing, and deployment.

## How to Use This Documentation

1. Start by thoroughly reviewing the **RBAC Technical Specification** to understand the system's design.

2. Ensure proper database connectivity using the **Database Connectivity Guide**.

3. Reference the **Implementation Patterns** document when implementing any new components.

4. Follow the **Implementation Checklist** as your actionable plan, checking off items as you complete them.

## Critical Warnings

- The `.env` file is properly configured - DO NOT MODIFY IT
- Some RBAC tables use UUID primary keys while others use SERIAL - be mindful of this distinction
- Tenant isolation must be maintained throughout all implementations
- Follow established naming conventions and code patterns
- Always use transactions for database operations

This documentation suite represents the distilled knowledge from the entire modernization project, focused specifically on completing the RBAC implementation.
```

## Document 1: RBAC Technical Specification

````markdown
# RBAC Technical Specification

## 1. Database Schema

### 1.1 Core Tables

#### roles

| Column      | Type      | Description        | Notes                                |
| ----------- | --------- | ------------------ | ------------------------------------ |
| id          | integer   | Primary key        | SERIAL, not UUID                     |
| name        | text      | Role name          | e.g., 'USER', 'ADMIN', 'SUPER_ADMIN' |
| description | text      | Role description   | Optional                             |
| created_at  | timestamp | Creation timestamp | Default: now()                       |

#### permissions

| Column      | Type      | Description            | Notes                      |
| ----------- | --------- | ---------------------- | -------------------------- |
| id          | uuid      | Primary key            | UUID, not SERIAL           |
| name        | text      | Permission name        | e.g., 'configure_features' |
| description | text      | Permission description | Optional                   |
| created_at  | timestamp | Creation timestamp     | Default: now()             |
| updated_at  | timestamp | Last update timestamp  | Default: now()             |

#### role_permissions (association table)

| Column        | Type         | Description                | Notes                     |
| ------------- | ------------ | -------------------------- | ------------------------- |
| id            | uuid         | Primary key                | UUID, not SERIAL          |
| role          | USER-DEFINED | Role reference             | e.g., 'basic', 'admin'    |
| permission_id | uuid         | Foreign key to permissions | References permissions.id |
| created_at    | timestamp    | Creation timestamp         | Default: now()            |

#### user_tenants (user-role-tenant association)

| Column     | Type      | Description           | Notes                   |
| ---------- | --------- | --------------------- | ----------------------- |
| user_id    | uuid      | User ID               | No explicit foreign key |
| tenant_id  | uuid      | Tenant ID             | No explicit foreign key |
| role_id    | integer   | Foreign key to roles  | References roles.id     |
| created_at | timestamp | Creation timestamp    | Default: now()          |
| updated_at | timestamp | Last update timestamp | Default: now()          |

### 1.2 Feature Management Tables

#### features

| Column       | Type         | Description                | Notes                         |
| ------------ | ------------ | -------------------------- | ----------------------------- |
| id           | uuid         | Primary key                | UUID, not SERIAL              |
| title        | text         | Feature title              |                               |
| description  | text         | Feature description        | Optional                      |
| priority     | USER-DEFINED | Feature priority           | e.g., 'HIGH', 'MEDIUM', 'LOW' |
| status       | USER-DEFINED | Feature status             | e.g., 'ACTIVE', 'INACTIVE'    |
| requested_by | uuid         | User who requested feature | Optional                      |
| reviewed_by  | uuid         | User who reviewed feature  | Optional                      |
| votes        | integer      | Number of votes            | Default: 0                    |
| page_path    | text         | Page path for feature      | Optional                      |
| page_tab     | text         | Page tab for feature       | Optional                      |
| created_at   | timestamp    | Creation timestamp         | Default: now()                |
| updated_at   | timestamp    | Last update timestamp      | Default: now()                |

#### tenant_features

| Column     | Type      | Description                | Notes                  |
| ---------- | --------- | -------------------------- | ---------------------- |
| id         | uuid      | Primary key                | UUID, not SERIAL       |
| tenant_id  | uuid      | Tenant ID                  | Required               |
| feature_id | uuid      | Foreign key to features    | References features.id |
| is_enabled | boolean   | Whether feature is enabled | Default: false         |
| created_at | timestamp | Creation timestamp         | Default: now()         |
| updated_at | timestamp | Last update timestamp      | Default: now()         |

#### sidebar_features

| Column        | Type      | Description             | Notes                  |
| ------------- | --------- | ----------------------- | ---------------------- |
| id            | uuid      | Primary key             | UUID, not SERIAL       |
| feature_id    | uuid      | Feature ID              | References features.id |
| sidebar_name  | text      | Display name in sidebar |                        |
| url_path      | text      | URL path for navigation |                        |
| icon          | text      | Icon name or class      | Optional               |
| display_order | integer   | Order in sidebar        | Default: 0             |
| created_at    | timestamp | Creation timestamp      | Default: now()         |
| updated_at    | timestamp | Last update timestamp   | Default: now()         |

## 2. Key Relationships

### 2.1 Role-Permission Relationship

- One role can have many permissions
- One permission can belong to many roles
- The relationship is managed through the `role_permissions` association table

### 2.2 User-Role-Tenant Relationship

- Users are assigned roles within the context of specific tenants
- This creates a three-way relationship managed through the `user_tenants` table
- A user can have different roles in different tenants

### 2.3 Feature Management

- Features are defined globally in the `features` table
- Feature enablement is managed per-tenant in the `tenant_features` table
- UI navigation is controlled through the `sidebar_features` table

## 3. SQLAlchemy Models Implementation

### 3.1 Role Model

```python
class Role(Base):
    """Role model for RBAC."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")
```
````

### 3.2 Permission Model

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
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
```

### 3.3 Other Models

[Additional model implementations for UserRole, Feature, TenantFeature, and SidebarFeature...]

## 4. API Endpoints

### 4.1 Roles API

- `GET /api/v2/role_based_access_control/roles` - List all roles
- `GET /api/v2/role_based_access_control/roles/{id}` - Get role by ID
- `POST /api/v2/role_based_access_control/roles` - Create a new role
- `PUT /api/v2/role_based_access_control/roles/{id}` - Update a role
- `DELETE /api/v2/role_based_access_control/roles/{id}` - Delete a role

### 4.2 Permissions API

- `GET /api/v2/role_based_access_control/permissions` - List all permissions
- `GET /api/v2/role_based_access_control/permissions/{id}` - Get permission by ID
- `POST /api/v2/role_based_access_control/permissions` - Create a new permission
- `PUT /api/v2/role_based_access_control/permissions/{id}` - Update a permission
- `DELETE /api/v2/role_based_access_control/permissions/{id}` - Delete a permission

### 4.3 User Roles API

- `GET /api/v2/role_based_access_control/user-roles` - List all user roles
- `GET /api/v2/role_based_access_control/user-roles/user/{user_id}` - Get roles for a user
- `POST /api/v2/role_based_access_control/user-roles` - Assign a role to a user
- `DELETE /api/v2/role_based_access_control/user-roles/{id}` - Remove a role from a user

### 4.4 Features API

[Additional endpoint documentation for feature management...]

## 5. Dashboard Interface

The RBAC dashboard interface (`/static/rbac-dashboard-fixed.html`) provides a UI for managing:

- Roles and their permissions
- User role assignments
- Feature flags and their enablement per tenant
- Sidebar feature configuration

Dashboard features include:

- Role creation, editing, and deletion
- Permission assignment to roles
- User role management
- Feature flag toggling
- Sidebar feature configuration

````

## Document 2: Database Connectivity Guide

```markdown
# Database Connectivity Guide for RBAC Implementation

## 1. Database Connection Configuration

### 1.1 Supabase Connection Details

The application connects to Supabase using the following configurations:

````

Host: aws-0-us-west-1.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.ddfldwzhdhhzhxywqnyz

````

**CRITICAL**: All these details are already configured in the `.env` file - DO NOT MODIFY this file.

### 1.2 Supavisor Connection Pooler

Supabase has migrated from PgBouncer to their own connection pooler called Supavisor, which requires specific configuration:

```python
# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    # Use different pool sizes based on environment
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    connect_args=connect_args
)
````

### 1.3 SSL Configuration

SSL configuration is environment-dependent:

```python
# Configure SSL context based on environment
if IS_DEVELOPMENT:
    # Development: Disable SSL verification for easier local development
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    # Production: Use proper SSL verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
```

## 2. Model-Schema Alignment

### 2.1 Model-Schema Mismatch Issues

The primary challenge in the RBAC implementation is aligning SQLAlchemy models with the actual database schema:

1. **Primary Key Type Mismatches**: Some tables use `UUID` primary keys while others use `Integer` (SERIAL):

   - `roles`: Uses `Integer` primary key
   - `permissions`: Uses `UUID` primary key

2. **Column Mismatches**: Some models include columns that don't exist in the database:

   - The `Role` model must not include `tenant_id` or `updated_at` columns
   - The `Permission` model must include both `created_at` and `updated_at`

3. **Relationship Configuration**: Self-referential relationships require special handling:
   - `SidebarFeature.children` needs `single_parent=True` to fix cascade issues

### 2.2 Custom Base Models

Create custom base models for tables that don't follow the standard schema:

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

### 2.3 Proper Relationship Configuration

For self-referential relationships:

```python
# Self-referential relationship with single_parent=True to fix cascade issues
children = relationship(
    "SidebarFeature",
    backref=backref("parent", remote_side=[id]),
    cascade="all, delete-orphan",
    single_parent=True  # Add this to fix the cascade issue
)
```

## 3. Database Verification Process

### 3.1 Verification Steps

1. **Schema Validation**:

   - Connect to the database using psql or a database tool
   - Check the actual schema of each RBAC table
   - Verify column names, types, and constraints
   - Compare with your SQLAlchemy models

2. **Sample Data Testing**:

   - Execute `populate_rbac_sample_data.py` to add test data
   - Verify data is correctly inserted
   - Check relationships are properly established

3. **Query Testing**:
   - Test basic CRUD operations
   - Verify relationship loading works correctly
   - Test more complex queries like permission checking

### 3.2 Common Issues and Solutions

#### Issue: "column does not exist" errors

**Solution**: Check your model against the actual database schema and remove any columns that don't exist.

#### Issue: Foreign key constraint violations

**Solution**: Ensure you're inserting parent records before child records and that foreign key values match existing primary keys.

#### Issue: Cascade delete errors

**Solution**: Check relationship configurations, especially for self-referential relationships.

## 4. Health Check Implementation

Implement database health checks to verify connectivity:

```python
async def check_database_connection(session: AsyncSession) -> bool:
    """
    Check if the database connection is working.

    Args:
        session: SQLAlchemy async session

    Returns:
        True if connection is working, False otherwise
    """
    try:
        # Execute a simple query to check connection
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

@app.get("/health/database", tags=["health"])
async def database_health():
    """Check database connection health."""
    async with get_session() as session:
        is_healthy = await check_database_connection(session)
        if not is_healthy:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Database connection failed"}
            )
        return {"status": "ok", "message": "Database connection successful"}
```

## 5. Transaction Management

Always use transactions for database operations:

```python
async with get_session() as session:
    async with session.begin():
        # All operations within this block are in a transaction
        # The transaction is automatically committed if no exceptions occur
        # or rolled back if an exception is raised
        role = Role(name="Admin", description="Administrator role")
        permission = Permission(name="manage_users", description="Can manage users")
        role.permissions.append(permission)
        session.add(role)
        session.add(permission)
```

## 6. Troubleshooting

### 6.1 Connection Issues

- Verify the `.env` file contains correct Supabase credentials
- Check network connectivity to the Supabase host
- Verify that the database user has proper permissions

### 6.2 Model-Schema Issues

- Use database inspection tools to compare the actual schema with your models
- Create custom base models for tables with non-standard schemas
- Use Alembic to generate migrations for schema changes (if needed)

### 6.3 Relationship Issues

- Check that the foreign key columns exist in both models and the database
- Verify the relationship configuration in both directions
- Use eager loading with `selectinload()` for complex relationships

````

## Document 3: Implementation Patterns Reference

```markdown
# Implementation Patterns Reference

## 1. Router Factory Pattern

### 1.1 Core Factory Methods

```python
class RouterFactory:
    """
    Factory for creating standardized FastAPI routes with consistent configuration.
    """

    @staticmethod
    def create_get_route(
        router: APIRouter,
        path: str,
        endpoint: Callable,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 200,
        description: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        operation_id: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
    ) -> None:
        """
        Create a standardized GET route.
        """
        router.get(
            path=path,
            response_model=response_model,
            status_code=status_code,
            description=description,
            summary=summary,
            tags=tags,
            operation_id=operation_id,
            dependencies=dependencies or [],
        )(endpoint)

    # Similar methods for POST, PUT, DELETE...
````

### 1.2 Usage Example

```python
# Define the endpoint function
async def get_roles(session: AsyncSession = Depends(get_session_dependency)):
    """Get all roles."""
    return await rbac_service.get_roles(session)

# Use the router factory to create a route
router_factory.create_get_route(
    router=router,
    path="/roles",
    response_model=RolesResponse,
    endpoint=get_roles,
    summary="Get all roles",
    description="Returns a list of all roles in the system"
)
```

## 2. API Versioning Pattern

### 2.1 Creating Versioned Routers

```python
class ApiVersionFactory:
    """
    Factory for creating versioned FastAPI routers.
    """

    @classmethod
    def create_versioned_routers(
        cls,
        v1_prefix: str,
        v2_prefix: str,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Depends]] = None,
        include_in_schema: bool = True,
        deprecated_in_days: int = 180,
    ) -> Dict[str, APIRouter]:
        """
        Create v1 and v2 routers with proper versioning headers.
        """
        # Implementation...
        return {
            "v1": v1_router,
            "v2": v2_router
        }
```

### 2.2 Usage Example

```python
# Create versioned routers
routers = api_version_factory.create_versioned_routers(
    v1_prefix="/api/v1/rbac",
    v2_prefix="/api/v2/role_based_access_control",
    tags=["role_based_access_control"]
)

# Register routes using RouterFactory
router_factory.create_get_route(
    router=routers["v1"],
    path="/roles",
    response_model=RolesResponse,
    endpoint=get_roles
)

router_factory.create_get_route(
    router=routers["v2"],
    path="/roles",
    response_model=RolesResponse,
    endpoint=get_roles
)
```

### 2.3 Registering Multiple Routes

```python
# Register multiple routes at once
api_version_factory.register_versioned_routes(
    routers=routers,
    v1_path="/roles",
    v2_path="/roles",
    endpoint_function=get_roles,
    response_model=RolesResponse,
    methods=["GET"]
)
```

## 3. Service Organization Pattern

### 3.1 Directory Structure

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
```

### 3.2 Service Implementation Pattern

```python
# src/services/rbac/rbac_service.py

class RbacService:
    """Service for RBAC operations."""

    @staticmethod
    async def get_roles(session: AsyncSession) -> List[Role]:
        """Get all roles."""
        query = select(Role)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_role_by_id(session: AsyncSession, role_id: int) -> Optional[Role]:
        """Get a role by ID."""
        query = select(Role).where(Role.id == role_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_role(session: AsyncSession, data: Dict[str, Any]) -> Role:
        """Create a new role."""
        role = Role(**data)
        session.add(role)
        await session.flush()  # To get the ID
        return role

    # Additional methods for updating, deleting roles, etc.
```

### 3.3 Service Usage Pattern

```python
# In a router function
async def create_role(
    request: RoleCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    """Create a new role."""
    try:
        role = await rbac_service.create_role(session, request.dict())
        await session.commit()
        return {"id": role.id, "name": role.name}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

## 4. Error Handling Pattern

### 4.1 Error Service Implementation

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
        """
        Handle an exception and return structured error details.
        """
        error_details = {
            "error_code": error_code,
            "error_message": str(exception),
            "context": context or {}
        }

        if log_error:
            logger.error(
                f"Error {error_code}: {str(exception)}, Context: {context or {}}",
                exc_info=exception
            )

        return error_details

    @staticmethod
    def format_error_response(error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format error details into a standard error response.
        """
        return {
            "success": False,
            "error": error_details
        }

    # Convenience methods for common errors
    @staticmethod
    def not_found(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resource not found error."""
        error_details = {
            "error_code": "NOT_FOUND",
            "error_message": message,
            "context": context or {}
        }
        logger.info(f"Not found: {message}, Context: {context or {}}")
        return error_details
```

### 4.2 Error Handling Usage Pattern

```python
@router.get("/roles/{role_id}")
async def get_role(
    role_id: int,
    session: AsyncSession = Depends(get_session_dependency)
):
    """Get a role by ID."""
    try:
        role = await rbac_service.get_role_by_id(session, role_id)
        if not role:
            return JSONResponse(
                status_code=404,
                content=error_service.format_error_response(
                    error_service.not_found(f"Role with ID {role_id} not found")
                )
            )
        return {"id": role.id, "name": role.name}
    except Exception as e:
        error_details = error_service.handle_exception(
            e,
            "get_role_error",
            context={"role_id": role_id},
            log_error=True
        )
        return JSONResponse(
            status_code=500,
            content=error_service.format_error_response(error_details)
        )
```

## 5. Session Management Pattern

### 5.1 Session Factory Implementation

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

async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session for use as a FastAPI dependency.
    """
    async with get_session() as session:
        yield session
```

### 5.2 Session Usage Pattern

```python
# In a service method
async def create_role(session: AsyncSession, data: Dict[str, Any]) -> Role:
    """Create a new role."""
    role = Role(**data)
    session.add(role)
    await session.flush()  # To get the ID
    return role

# In a router function
@router.post("/roles")
async def create_role(
    request: RoleCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    """Create a new role."""
    try:
        role = await rbac_service.create_role(session, request.dict())
        await session.commit()
        return {"id": role.id, "name": role.name}
    except Exception as e:
        # No need to explicitly rollback - the dependency handles it
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. Dashboard Implementation Pattern

### 6.1 HTML Structure Pattern

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Standard head elements -->
  </head>
  <body>
    <!-- Header -->
    <header
      class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow"
    >
      <!-- Header content -->
    </header>

    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar navigation -->
        <nav
          id="sidebarMenu"
          class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"
        >
          <!-- Sidebar content -->
        </nav>

        <!-- Main content -->
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
          <!-- Tab content -->
          <div class="tab-content">
            <!-- Role management tab -->
            <div class="tab-pane fade show active" id="roles-tab">
              <!-- Role management content -->
            </div>

            <!-- Other tabs -->
          </div>
        </main>
      </div>
    </div>

    <!-- Modals for adding/editing entities -->

    <!-- Scripts -->
    <script src="js/rbac-dashboard.js"></script>
  </body>
</html>
```

### 6.2 JavaScript Pattern

```javascript
// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  // Load data
  loadRoles();
  loadPermissions();

  // Add event listeners
  document
    .querySelector("#add-role-form")
    .addEventListener("submit", handleAddRole);
});

// API call pattern
async function loadRoles() {
  try {
    const response = await fetch("/api/v2/role_based_access_control/roles", {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    displayRoles(data);
  } catch (error) {
    showError("Failed to load roles", error);
  }
}

// Display pattern
function displayRoles(data) {
  const rolesTable = document.querySelector("#roles-table tbody");
  rolesTable.innerHTML = "";

  data.forEach((role) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${role.id}</td>
            <td>${role.name}</td>
            <td>${role.description || ""}</td>
            <td>
                <button class="btn btn-sm btn-primary edit-role" data-id="${
                  role.id
                }">Edit</button>
                <button class="btn btn-sm btn-danger delete-role" data-id="${
                  role.id
                }">Delete</button>
            </td>
        `;
    rolesTable.appendChild(row);
  });

  // Add event listeners to buttons
  document.querySelectorAll(".edit-role").forEach((button) => {
    button.addEventListener("click", (e) =>
      handleEditRole(e.target.dataset.id)
    );
  });
}
```

## 7. Authentication Pattern

### 7.1 JWT Authentication Implementation

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session_dependency)
) -> Dict[str, Any]:
    """
    Get the current user from a JWT token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        # Get user from database
        user = await user_service.get_user_by_id(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
```

### 7.2 Permission Checking Pattern

```python
async def check_permission(
    user: Dict[str, Any],
    permission: str,
    session: AsyncSession
) -> bool:
    """
    Check if a user has a specific permission.
    """
    # Get user roles
    user_roles = await rbac_service.get_user_roles(session, user["id"])

    # Get permissions for these roles
    permissions = set()
    for user_role in user_roles:
        role_permissions = await rbac_service.get_role_permissions(session, user_role.role_id)
        permissions.update([p.name for p in role_permissions])

    return permission in permissions
```

### 7.3 Route Protection Pattern

```python
async def require_permission(
    permission: str,
    user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_dependency)
) -> None:
    """
    Dependency to require a specific permission.
    """
    has_permission = await check_permission(user, permission, session)
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission} required"
        )

# Usage in route
@router.post("/roles")
async def create_role(
    request: RoleCreate,
    session: AsyncSession = Depends(get_session_dependency),
    _: None = Depends(lambda: require_permission("create_role"))
):
    """Create a new role."""
    # Implementation...
```

````

## Document 4: RBAC Implementation Checklist

```markdown
# RBAC Implementation Checklist

## 1. Database Setup and Verification

### 1.1 Database Schema Verification
- [ ] Connect to Supabase database using credentials in `.env`
- [ ] Verify `roles` table structure and columns
- [ ] Verify `permissions` table structure and columns
- [ ] Verify `role_permissions` table structure and columns
- [ ] Verify `user_tenants` table structure and columns
- [ ] Verify `features` table structure and columns
- [ ] Verify `tenant_features` table structure and columns
- [ ] Verify `sidebar_features` table structure and columns

### 1.2 Sample Data Population
- [ ] Examine `populate_rbac_sample_data.py` to understand its operation
- [ ] Create a database backup before running the script
- [ ] Execute `populate_rbac_sample_data.py` to populate sample data
- [ ] Verify data insertion in all RBAC tables
- [ ] Check relationships between entities (e.g., roles and permissions)
- [ ] Document any issues encountered during data population

## 2. SQLAlchemy Models Implementation

### 2.1 Core Table Models
- [ ] Implement or verify `Role` model (with correct primary key type)
- [ ] Implement or verify `Permission` model (with correct primary key type)
- [ ] Implement or verify `RolePermission` association model
- [ ] Implement or verify `UserRole` model (for the `user_tenants` table)

### 2.2 Feature Management Models
- [ ] Implement or verify `Feature` model
- [ ] Implement or verify `TenantFeature` model
- [ ] Implement or verify `SidebarFeature` model (with correct relationship configuration)

### 2.3 Model Testing
- [ ] Test basic CRUD operations for each model
- [ ] Test relationship loading for related models
- [ ] Verify model-to-database schema alignment
- [ ] Fix any mismatches between models and database schema

## 3. Service Layer Implementation

### 3.1 RBAC Service Implementation
- [ ] Implement or verify `RbacService` for role and permission management
- [ ] Implement methods for role CRUD operations
- [ ] Implement methods for permission CRUD operations
- [ ] Implement methods for role-permission management
- [ ] Implement methods for user-role management
- [ ] Implement permission checking functionality

### 3.2 Feature Service Implementation
- [ ] Implement or verify `FeatureService` for feature management
- [ ] Implement methods for feature CRUD operations
- [ ] Implement methods for tenant feature management
- [ ] Implement methods for sidebar feature management
- [ ] Implement feature flag checking functionality

### 3.3 Service Testing
- [ ] Test role management functionality
- [ ] Test permission management functionality
- [ ] Test user-role assignment functionality
- [ ] Test feature management functionality
- [ ] Test permission checking logic
- [ ] Test feature flag checking logic

## 4. API Endpoints Implementation

### 4.1 Router Setup
- [ ] Create versioned routers using `ApiVersionFactory`
- [ ] Set up v1 router at `/api/v1/rbac`
- [ ] Set up v2 router at `/api/v2/role_based_access_control`
- [ ] Add proper router tags and documentation

### 4.2 Role Management Endpoints
- [ ] Implement `GET /roles` to list all roles
- [ ] Implement `GET /roles/{id}` to get a specific role
- [ ] Implement `POST /roles` to create a new role
- [ ] Implement `PUT /roles/{id}` to update a role
- [ ] Implement `DELETE /roles/{id}` to delete a role

### 4.3 Permission Management Endpoints
- [ ] Implement `GET /permissions` to list all permissions
- [ ] Implement `GET /permissions/{id}` to get a specific permission
- [ ] Implement `POST /permissions` to create a new permission
- [ ] Implement `PUT /permissions/{id}` to update a permission
- [ ] Implement `DELETE /permissions/{id}` to delete a permission

### 4.4 User Role Management Endpoints
- [ ] Implement `GET /user-roles` to list all user roles
- [ ] Implement `GET /user-roles/user/{user_id}` to get roles for a user
- [ ] Implement `POST /user-roles` to assign a role to a user
- [ ] Implement `DELETE /user-roles/{id}` to remove a role from a user

### 4.5 Feature Management Endpoints
- [ ] Implement endpoints for feature management
- [ ] Implement endpoints for tenant feature management
- [ ] Implement endpoints for sidebar feature management

### 4.6 API Testing
- [ ] Test role management endpoints
- [ ] Test permission management endpoints
- [ ] Test user role management endpoints
- [ ] Test feature management endpoints

## 5. Dashboard Implementation

### 5.1 Dashboard Setup
- [ ] Review `static/rbac-dashboard-fixed.html` to understand its structure
- [ ] Check the integration with API endpoints
- [ ] Verify JavaScript functionality for data loading

### 5.2 Dashboard Features Implementation
- [ ] Implement role management UI components
- [ ] Implement permission management UI components
- [ ] Implement user role management UI components
- [ ] Implement feature management UI components

### 5.3 Dashboard Testing
- [ ] Test role creation, editing, and deletion
- [ ] Test permission assignment to roles
- [ ] Test user role assignment
- [ ] Test feature flag toggling
- [ ] Test error handling and feedback mechanisms

## 6. Security Implementation

### 6.1 Authentication Integration
- [ ] Implement JWT token validation
- [ ] Integrate with user authentication service
- [ ] Verify token handling in dashboard

### 6.2 Authorization Implementation
- [ ] Implement permission checking for protected routes
- [ ] Enforce tenant isolation in queries
- [ ] Implement feature flag enforcement

### 6.3 Security Testing
- [ ] Test authentication flow
- [ ] Test permission-based access control
- [ ] Test tenant isolation enforcement
- [ ] Test feature flag enforcement

## 7. Docker Implementation

### 7.1 Docker Configuration
- [ ] Verify Docker configuration in `docker-compose.yml`
- [ ] Configure proper volume mounting for RBAC data
- [ ] Set up health checks for RBAC endpoints
- [ ] Configure environment variables for containers

### 7.2 Docker Testing
- [ ] Build and run Docker containers
- [ ] Test RBAC functionality in containerized environment
- [ ] Verify container networking and communication
- [ ] Test health checks and monitoring

## 8. Documentation and Deployment

### 8.1 Documentation
- [ ] Update API documentation for RBAC endpoints
- [ ] Document RBAC database schema and relationships
- [ ] Document dashboard functionality and usage
- [ ] Document authentication and authorization flow

### 8.2 Deployment
- [ ] Prepare deployment plan for RBAC components
- [ ] Verify environment configuration for production
- [ ] Create database backup before deployment
- [ ] Deploy RBAC components to production

## 9. Final Validation

### 9.1 Functional Validation
- [ ] Validate all RBAC functionality in production
- [ ] Verify role and permission management
- [ ] Verify user role assignment
- [ ] Verify feature management

### 9.2 Performance Validation
- [ ] Monitor database performance
- [ ] Check API endpoint response times
- [ ] Verify dashboard loading performance
- [ ] Identify and address any bottlenecks

### 9.3 Security Validation
- [ ] Verify access control enforcement
- [ ] Test tenant isolation in production
- [ ] Validate JWT token handling
- [ ] Verify permission checking logic

## 10. Handover and Documentation

### 10.1 Knowledge Transfer
- [ ] Document all implementation details
- [ ] Create user guides for RBAC dashboard
- [ ] Document troubleshooting procedures
- [ ] Schedule knowledge transfer sessions

### 10.2 Future Enhancements
- [ ] Document potential future enhancements
- [ ] Identify performance optimization opportunities
- [ ] Note security improvement possibilities
- [ ] Suggest feature enhancements
````

These synthesized documents provide a comprehensive, focused guide specifically for the RBAC implementation phase of the project. The introduction establishes clear context, while each document addresses a specific aspect of the implementation with actionable guidance.

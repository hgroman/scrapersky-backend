# RBAC Modernization Plan

## Overview

This document outlines the plan for modernizing the Role-Based Access Control (RBAC) system in ScraperSky. The RBAC system is a critical security component that manages user permissions, roles, and feature access across the application. Following the successful modernization of the sitemap_analyzer and Google Maps API components, RBAC is the next high-priority component to modernize.

## Current State Analysis

The current RBAC implementation is contained in `src/routers/rbac.py` and has the following characteristics:

- **Legacy Router Structure**: Uses the traditional FastAPI router without the router factory pattern
- **Direct Database Access**: Contains direct database queries without a service layer
- **Legacy API Paths**: Uses `/api/v1/rbac/*` endpoints without truthful naming
- **No SQLAlchemy Integration**: Uses raw SQL queries instead of SQLAlchemy ORM
- **Tightly Coupled with Auth Service**: Functionality is split between the router and `auth_service.py`

The RBAC router currently provides the following key functionality:

1. **Permission Management**: Checking and assigning permissions
2. **Role Management**: Creating, updating, and assigning roles
3. **Feature Flag Management**: Managing feature flags for tenants
4. **Sidebar Feature Management**: Controlling UI sidebar features

## Modernization Goals

The modernization of the RBAC system will achieve the following goals:

1. **Service Layer Separation**: Create dedicated RBAC services with clear responsibilities
2. **SQLAlchemy Integration**: Replace raw SQL with SQLAlchemy ORM models and queries
3. **API Versioning**: Implement dual versioning with truthful naming
4. **Enhanced Type Safety**: Use Pydantic models for request/response validation
5. **Improved Testability**: Structure code to facilitate unit and integration testing
6. **Tenant Isolation**: Ensure proper tenant isolation for all RBAC operations

## Implementation Plan

### 1. Service Layer Creation

#### 1.1 Create Directory Structure

```bash
mkdir -p src/services/rbac
touch src/services/rbac/__init__.py
```

#### 1.2 Create Core RBAC Service

Create `src/services/rbac/rbac_service.py` with the following components:

```python
"""
RBAC Service Module

This module provides service methods for Role-Based Access Control (RBAC) operations.
"""

from typing import Dict, List, Optional, Set, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ...db.models.rbac_models import Role, Permission, UserRole, Feature, TenantFeature, SidebarFeature
from ...db.session import get_db_session
from ...utils.extract_value import extract_value

logger = logging.getLogger(__name__)

class RbacService:
    """Service for RBAC operations including roles, permissions, and features."""

    @staticmethod
    async def get_user_permissions(user_id: str, tenant_id: str, session: Optional[AsyncSession] = None) -> List[str]:
        """
        Get permissions for a user based on their roles.

        Args:
            user_id: The user ID
            tenant_id: The tenant ID
            session: Optional database session

        Returns:
            List of permission names
        """
        async with get_db_session(session) as session:
            # Implementation using SQLAlchemy
            # ...

    # Additional methods for role management
    # ...

    # Methods for feature flag management
    # ...

    # Methods for sidebar feature management
    # ...
```

#### 1.3 Create Feature Management Service

Create `src/services/rbac/feature_service.py` for feature flag management:

```python
"""
Feature Management Service

This module provides service methods for feature flag management.
"""

from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ...db.models.rbac_models import Feature, TenantFeature
from ...db.session import get_db_session
from ...utils.extract_value import extract_value

logger = logging.getLogger(__name__)

class FeatureService:
    """Service for feature flag management."""

    # Methods for feature flag operations
    # ...
```

### 2. SQLAlchemy Models

Create or update the following models in `src/db/models/rbac_models.py`:

```python
"""
RBAC Models

This module defines SQLAlchemy ORM models for RBAC entities.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..base import Base

# Role-Permission association table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Role(Base):
    """Role model for RBAC."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")

# Additional models for Permission, UserRole, Feature, TenantFeature, SidebarFeature
# ...
```

### 3. Router Factory Implementation

#### 3.1 Create Router Factory File

Create `src/router_factory/rbac_router.py`:

```python
"""
RBAC Router Factory

This module creates versioned routers for RBAC endpoints.
"""

from fastapi import Depends, HTTPException, Query, Path, Body
from typing import Dict, List, Any, Optional

from ..api_version_factory import ApiVersionFactory
from ..services.rbac.rbac_service import RbacService
from ..services.rbac.feature_service import FeatureService
from ..auth.jwt_auth import get_current_user
from ..auth.tenant_isolation import validate_tenant_id

# Create versioned routers
api_version_factory = ApiVersionFactory()

# Create v1 router (legacy path)
v1_router = api_version_factory.create_api_router(
    version="v1",
    prefix="rbac",
    tags=["rbac"],
    responses={404: {"description": "Not found"}}
)

# Create v2 router (truthful naming)
v2_router = api_version_factory.create_api_router(
    version="v2",
    prefix="role_based_access_control",
    tags=["role_based_access_control"],
    responses={404: {"description": "Not found"}}
)

# Helper function to check if user has RBAC admin privileges
async def verify_rbac_admin_access(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Verify that the current user has RBAC admin privileges.
    """
    # Implementation
    # ...

# Define route handlers
# ...

# Register routes for both v1 and v2 routers
# ...
```

### 4. Integration with Auth Service

Update `src/auth/auth_service.py` to use the new RBAC service:

```python
"""
Authentication Service Module

This module provides role-based access control (RBAC) for the application.
"""

from fastapi import Depends, HTTPException
from typing import Dict, List, Callable, Optional, Set
import logging

from .jwt_auth import get_current_user
from ..services.rbac.rbac_service import RbacService

# Configure logging
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for role-based access control.
    """

    @staticmethod
    async def check_permission(user: Dict, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user: The user dictionary
            permission: The permission to check

        Returns:
            True if the user has the permission, False otherwise
        """
        # Use the RBAC service
        # ...

    # Additional methods
    # ...
```

### 5. Testing Strategy

Create comprehensive tests for the RBAC system:

1. **Unit Tests**:

   - Test each service method in isolation
   - Mock database interactions

2. **Integration Tests**:

   - Test the interaction between services and routers
   - Use a test database

3. **API Tests**:
   - Test both v1 and v2 endpoints
   - Verify correct behavior for different user roles

## Migration Plan

1. **Phase 1: Service Layer Implementation**

   - Create RBAC services with SQLAlchemy integration
   - Update auth_service.py to use the new services
   - Keep the existing router unchanged

2. **Phase 2: Router Factory Implementation**

   - Create versioned routers using the router factory pattern
   - Implement dual versioning with truthful naming
   - Test both v1 and v2 endpoints

3. **Phase 3: Frontend Integration**

   - Update frontend components to use the new endpoints
   - Test the integration with the UI

4. **Phase 4: Deprecation**
   - Add deprecation headers to v1 endpoints
   - Document migration path for clients

## Implementation Timeline

| Task                          | Estimated Time | Dependencies                  |
| ----------------------------- | -------------- | ----------------------------- |
| Service Layer Creation        | 1-2 days       | None                          |
| SQLAlchemy Models             | 1 day          | None                          |
| Router Factory Implementation | 1-2 days       | Service Layer, Models         |
| Integration with Auth Service | 1 day          | Service Layer                 |
| Testing                       | 2-3 days       | All implementation tasks      |
| Frontend Integration          | 1-2 days       | Router Factory Implementation |

## Appendix A: Remaining Components After RBAC

After completing the RBAC modernization, the following components still need to be modernized:

### 1. Admin Router Modernization

The admin router (`src/routers/admin.py`) should be modernized immediately after RBAC:

1. **Service Creation**:

   - Create `admin_service.py` in `services/admin/` directory
   - Implement user management operations

2. **Router Factory Implementation**:
   - Create versioned routers using the router factory pattern
   - Implement dual versioning with truthful naming

### 2. Email Scanner Modernization

The email scanner router (`src/routers/email_scanner.py`) is a smaller component:

1. **Service Creation**:

   - Create `email_scanner_service.py` in `services/email/` directory
   - Implement email scanning operations

2. **Router Factory Implementation**:
   - Create versioned routers using the router factory pattern
   - Implement dual versioning with truthful naming

### 3. Batch Processing Router

Create a dedicated router for the already modernized batch service:

1. **Router Creation**:
   - Create `batch_router.py` using the router factory pattern
   - Implement dual versioning with truthful naming
   - Integrate with the existing batch service

### 4. Remaining Routers

After completing the above components, the following routers will still need modernization:

- `page_scraper.py`
- `domain_manager.py`
- `job_manager.py`

## Appendix B: Key Reference Documents

For the next developer continuing this work, the following documents provide essential context:

1. **[25-ScraperSky-Context-Reset.md](./25-ScraperSky-Context-Reset.md)** - The master document providing overall project context, status, and priorities.

2. **[38-GoogleMapsAPI-Versioning-Implementation.md](./38-GoogleMapsAPI-Versioning-Implementation.md)** - The definitive template for router modernization with dual versioning.

3. **[51-ScraperSky-Architecture-Design-Considerations.md](./51-ScraperSky-Architecture-Design-Considerations.md)** - Architectural patterns and design considerations for the modernized system.

4. **[29-Router-Factory-Implementation.md](./29-Router-Factory-Implementation.md)** - Details of the router factory pattern implementation.

5. **[API-Versioning-Endpoint-Map.md](./API-Versioning-Endpoint-Map.md)** - Mapping of legacy endpoints to truthful naming.

6. **[37-Router-Modernization-Audit.md](./37-Router-Modernization-Audit.md)** - Audit of router modernization status and priorities.

## Appendix C: Guidance for Next Developer

When continuing this modernization effort, follow these guidelines:

1. **Start with Document Review**:

   - Begin by reviewing Document #25 (Context Reset) for overall project status
   - Study Document #38 (GoogleMapsAPI Implementation) as the template for router modernization
   - Review Document #51 (Architecture Design Considerations) for architectural patterns

2. **Follow the Established Workflow**:

   - Create services first, then models, then routers
   - Implement dual versioning with truthful naming
   - Test both v1 and v2 endpoints

3. **Maintain Documentation**:

   - Update Document #25 as components are modernized
   - Create component-specific documentation for complex implementations

4. **Prioritize Security Components**:

   - RBAC and Admin are highest priority due to their security implications
   - Ensure proper tenant isolation in all implementations

5. **Leverage Docker Environment**:
   - Use the Docker environment for testing
   - Verify health checks and endpoint functionality after changes

By following this guidance and referring to the key documents, you'll be able to continue the modernization effort seamlessly and maintain the architectural integrity of the system.

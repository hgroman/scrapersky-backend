# RBAC Model Relationships Documentation

This document provides a comprehensive overview of the RBAC model relationships in the ScraperSky backend system. These relationships are preserved in the codebase for future RBAC reintegration, but the models themselves are currently not actively imported or used.

## Core RBAC Models

The RBAC system consists of these primary models:

- **Role**: Defines user roles in the system
- **Permission**: Defines granular permissions for system actions
- **RolePermission**: Associates roles with specific permissions
- **UserRole**: Associates users with specific roles in specific tenants
- **FeatureFlag**: Defines feature toggles that can be enabled/disabled
- **TenantFeature**: Associates tenants with enabled features
- **SidebarFeature**: Defines UI navigation elements with permission controls

## Model Relationships Diagram

```
Profile <---> UserRole <---> Role <---> RolePermission <---> Permission
   ^                           ^
   |                           |
   v                           v
Tenant <---> TenantFeature <---> FeatureFlag <---> SidebarFeature
                                                        ^
                                                        |
                                                        v
                                                      Tenant
```

## Detailed Relationship Descriptions

### Profile Relationships

- **Profile → UserRole**: One-to-many relationship
  - A profile can have multiple user roles
  - Each user role is associated with one profile
  - Defined in `profile.py` via `user_roles = relationship("UserRole", back_populates="profile")`
  - Used for determining which roles a user has in the system

### Tenant Relationships

- **Tenant → Profile**: One-to-many relationship
  - A tenant can have multiple profiles
  - Each profile belongs to one tenant
  - Enforces multi-tenancy isolation

- **Tenant → UserRole**: One-to-many relationship
  - A tenant can have multiple user roles
  - Each user role can be associated with a specific tenant
  - Allows tenant-specific role assignments

- **Tenant → TenantFeature**: One-to-many relationship
  - A tenant can have multiple feature flags enabled/disabled
  - Each tenant feature is associated with one tenant
  - Used for toggling features on a per-tenant basis

- **Tenant → SidebarFeature**: One-to-many relationship
  - A tenant can have multiple custom sidebar items
  - Each sidebar feature can be associated with a specific tenant
  - Allows tenant-specific UI navigation

### Role and Permission Relationships

- **Role → UserRole**: One-to-many relationship
  - A role can be assigned to multiple users
  - Each user role is associated with one role

- **Role ↔ Permission**: Many-to-many relationship
  - A role can have multiple permissions
  - A permission can be assigned to multiple roles
  - Connected via the RolePermission join table

### Feature and Sidebar Relationships

- **FeatureFlag → TenantFeature**: One-to-many relationship
  - A feature flag can be enabled for multiple tenants
  - Each tenant feature is associated with one feature flag

- **FeatureFlag → SidebarFeature**: One-to-many relationship
  - A feature flag can be associated with multiple sidebar features
  - Each sidebar feature can be associated with a feature flag
  - Controls visibility of UI elements based on feature toggles

## SQL Schema References

The following tables define these relationships in the database:

- **profiles**: Contains user profile data
- **tenants**: Contains tenant information
- **roles**: Contains role definitions
- **permissions**: Contains permission definitions
- **role_permissions**: Junction table connecting roles and permissions
- **user_roles**: Junction table connecting users/profiles to roles
- **feature_flags**: Contains feature toggle definitions
- **tenant_features**: Junction table connecting tenants to features
- **sidebar_features**: Contains sidebar navigation items

## Future Reintegration Notes

When reintegrating RBAC functionality:

1. Uncomment the RBAC model imports in `models/__init__.py`
2. Restore any commented-out RBAC functionality in services
3. Restore any commented-out RBAC functionality in routers
4. Ensure database schema is compatible with model definitions
5. Test relationships to ensure they function as expected

The current code preserves all relationship definitions but does not actively use them since the models themselves are not imported. This approach allows for future reintegration without requiring database schema changes.
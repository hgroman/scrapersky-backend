# Authentication Database Architecture

## Overview

This document details the database architecture for the multi-tenant authentication and authorization system. It covers the tables, relationships, and data flow that support user authentication, tenant isolation, and role-based access control.

## Database Tables

### Core Authentication Tables

| Table              | Description                                                  | Status                             |
| ------------------ | ------------------------------------------------------------ | ---------------------------------- |
| `profiles`         | Stores user profile information including tenant association | Existing, in use                   |
| `tenants`          | Stores tenant information                                    | Existing, in use                   |
| `user_tenants`     | Maps users to tenants with roles                             | Existing, not used (now populated) |
| `roles`            | Defines available roles in the system                        | Existing, not used (now leveraged) |
| `permissions`      | Defines available permissions in the system                  | Existing, not used (now leveraged) |
| `role_permissions` | Maps roles to permissions                                    | Existing, not used (now leveraged) |

### Data Tables with Tenant Isolation

| Table                            | Description                              | Tenant ID Type |
| -------------------------------- | ---------------------------------------- | -------------- |
| `domains`                        | Stores domain information                | UUID           |
| `google_maps_businesses_details` | Stores Google Maps business details      | Text           |
| `google_maps_businesses_staging` | Staging table for Google Maps businesses | Text           |
| `local_businesses`               | Stores local business information        | UUID           |
| `pages`                          | Stores page information                  | UUID           |
| `places_staging`                 | Staging table for places                 | Text           |
| `task_analytics`                 | Stores task analytics                    | UUID           |
| `task_history`                   | Stores task history                      | UUID           |
| `tasks`                          | Stores task information                  | UUID           |

## Table Structures

### profiles

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT '550e8400-e29b-41d4-a716-446655440000',
    name TEXT,
    email TEXT,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    role USER-DEFINED
);
```

This table stores user profile information and is directly linked to Supabase Auth. The `id` field corresponds to the Supabase Auth user ID. The `tenant_id` field associates the user with a tenant, and the `role` field defines the user's role within the system.

### tenants

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

This table stores tenant information. Each tenant represents a separate organization or client in the multi-tenant system.

### user_tenants

```sql
CREATE TABLE user_tenants (
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    role_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, tenant_id)
);
```

This table maps users to tenants with specific roles. It allows a user to belong to multiple tenants with different roles in each.

### roles

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

This table defines the available roles in the system. The system includes the following roles:

- USER: Regular tenant user
- ADMIN: Tenant-level admin
- SUPER_ADMIN: Manages tenant users
- HOLY_CRAP: System-level god mode

### permissions

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

This table defines the available permissions in the system. The system includes the following permissions:

- view_reports: View reports and dashboards
- manage_users: Invite and manage users
- configure_features: Enable or disable features
- manage_api_keys: Manage API keys and services
- manage_tenants: Manage all tenants (system admin only)

### role_permissions

```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role USER-DEFINED NOT NULL,
    permission_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

This table maps roles to permissions, defining which permissions are granted to each role.

## Database Relationships

### Entity Relationship Diagram

```
+-------------+       +---------------+       +-------------+
|             |       |               |       |             |
|  profiles   +-------+ user_tenants  +-------+   tenants   |
|             |       |               |       |             |
+------+------+       +-------+-------+       +-------------+
       |                      |
       |                      |
       |                      |
       |              +-------v-------+
       |              |               |
       |              |     roles     |
       |              |               |
       |              +-------+-------+
       |                      |
       |                      |
       |              +-------v-------+
       |              |               |
       +------------->+ role_permissions
                      |               |
                      +-------+-------+
                              |
                              |
                      +-------v-------+
                      |               |
                      |  permissions  |
                      |               |
                      +---------------+
```

### Key Relationships

1. **User to Tenant**:

   - A user (profile) belongs to one primary tenant (profiles.tenant_id)
   - A user can also belong to multiple tenants through the user_tenants table
   - A tenant can have multiple users

2. **User to Role**:

   - A user has a role defined in their profile (profiles.role)
   - A user can have different roles in different tenants (user_tenants.role_id)

3. **Role to Permission**:

   - A role has multiple permissions through the role_permissions table
   - A permission can be assigned to multiple roles

4. **Tenant Data Isolation**:
   - All data tables include a tenant_id column for data isolation
   - Queries filter by tenant_id to ensure users only see data for their tenants

## Data Flow

### Authentication Flow

1. User authenticates with Supabase Auth
2. Supabase Auth issues a JWT token with the user's ID (sub claim)
3. The backend validates the JWT token and retrieves the user's profile from the profiles table
4. The user's tenant_id and role are extracted from the profile
5. The user's permissions are determined based on their role

### Tenant Isolation Flow

1. User makes a request to an API endpoint
2. The backend authenticates the user and determines their tenant_id
3. The tenant_id is used to filter data in all database queries
4. The user only sees data for their tenant

### Permission Checking Flow

1. User attempts to access a protected resource
2. The backend checks if the user's role has the required permission
3. If the user has the permission, access is granted
4. If the user does not have the permission, access is denied with a 403 Forbidden response

## Data Type Standardization

To ensure consistency and proper foreign key relationships, we standardized the tenant_id data type across all tables:

1. **UUID Type**: All tenant_id columns should be of type UUID
2. **Foreign Key Constraints**: All tenant_id columns should have a foreign key constraint to tenants.id
3. **Default Value**: The default tenant_id is '550e8400-e29b-41d4-a716-446655440000' (Last Apple)

## Conclusion

The database architecture provides a solid foundation for multi-tenant operations with proper role-based access control. The existing tables were leveraged and enhanced to support the new authentication and authorization system.

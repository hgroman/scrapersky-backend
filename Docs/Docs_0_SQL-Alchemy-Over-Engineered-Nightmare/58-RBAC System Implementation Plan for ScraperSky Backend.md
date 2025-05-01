# RBAC System Implementation Plan for ScraperSky Backend

## Overview

We're implementing a Role-Based Access Control (RBAC) system that integrates with your existing database structure. This document explains the complete implementation plan, including database schema, relationships, and how it will work with your current application.

## Current Database Structure

Based on our analysis, your application currently uses:

1. **`tenants` Table**: Stores organization information
   - Used in TenantConfig.tsx for tenant selection
   - Tenant IDs are stored in localStorage for filtering data

2. **`profiles` Table**: Stores user profile information
   - Connected to your authentication system
   - Created automatically when users sign up

3. **`user_tenants` Table**: Links users to tenants
   - Currently underutilized
   - Designed for many-to-many relationships between users and tenants

## RBAC Database Schema

We'll implement the following tables to create a comprehensive RBAC system:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│   roles     │◄────┤role_permissions├───┤permissions  │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲
       │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  user_roles │◄────┤  profiles   │     │   tenants   │
│             │     │  (existing) │     │  (existing) │
└─────────────┘     └─────────────┘     └─────────────┘
                                               ▲
                                               │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│feature_flags│◄────┤tenant_features├────┤user_tenants │
│             │     │             │     │ (existing)  │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲
       │
┌─────────────┐
│             │
│sidebar_features
│             │
└─────────────┘
```

### New Tables to Create

1. **`roles` Table**
   - **Purpose**: Define roles like USER, ADMIN, SUPER_ADMIN
   - **Structure**:
     ```sql
     CREATE TABLE roles (
         id SERIAL PRIMARY KEY,
         name TEXT NOT NULL UNIQUE,
         description TEXT,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
     );
     ```
   - **Default Data**: USER, ADMIN, SUPER_ADMIN roles

2. **`permissions` Table**
   - **Purpose**: Define granular permissions for actions in the system
   - **Structure**:
     ```sql
     CREATE TABLE permissions (
         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
         name TEXT NOT NULL UNIQUE,
         description TEXT,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
         updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
     );
     ```
   - **Default Data**: Permissions like view_dashboard, manage_users, etc.

3. **`role_permissions` Table**
   - **Purpose**: Map roles to permissions (many-to-many)
   - **Structure**:
     ```sql
     CREATE TABLE role_permissions (
         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
         role_id INTEGER NOT NULL REFERENCES roles(id),
         permission_id UUID NOT NULL REFERENCES permissions(id),
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
         UNIQUE (role_id, permission_id)
     );
     ```

4. **`user_roles` Table**
   - **Purpose**: Assign roles to users (many-to-many)
   - **Structure**:
     ```sql
     CREATE TABLE user_roles (
         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
         user_id UUID NOT NULL,
         role_id INTEGER NOT NULL REFERENCES roles(id),
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
         UNIQUE (user_id, role_id)
     );
     ```
   - **Note**: `user_id` references the auth.users table from Supabase Auth

5. **`feature_flags` Table**
   - **Purpose**: Define feature toggles for the application
   - **Structure**:
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

6. **`tenant_features` Table**
   - **Purpose**: Enable/disable features per tenant
   - **Structure**:
     ```sql
     CREATE TABLE tenant_features (
         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
         tenant_id UUID NOT NULL REFERENCES tenants(id),
         feature_id UUID NOT NULL REFERENCES feature_flags(id),
         is_enabled BOOLEAN DEFAULT FALSE,
         created_at TIMESTAMPTZ DEFAULT NOW(),
         updated_at TIMESTAMPTZ DEFAULT NOW(),
         UNIQUE (tenant_id, feature_id)
     );
     ```

7. **`sidebar_features` Table**
   - **Purpose**: Define sidebar UI elements for features
   - **Structure**:
     ```sql
     CREATE TABLE sidebar_features (
         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
         feature_id UUID NOT NULL REFERENCES feature_flags(id),
         sidebar_name TEXT NOT NULL,
         url_path TEXT NOT NULL,
         icon TEXT,
         display_order INTEGER,
         created_at TIMESTAMPTZ DEFAULT NOW(),
         updated_at TIMESTAMPTZ DEFAULT NOW()
     );
     ```

## How It All Works Together

### User Authentication and Authorization Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  User       │────▶│  Login      │────▶│  Get User   │────▶│  Get User   │
│  Request    │     │  (Supabase) │     │  Profile    │     │  Roles      │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Access     │◀────│  Check      │◀────│  Get Role   │◀────│  Get User   │
│  Granted/   │     │  Permission │     │  Permissions│     │  Tenant     │
│  Denied     │     │  Required   │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Key Relationships and Flows

1. **User to Roles**:
   - Users are assigned roles through the `user_roles` table
   - A user can have multiple roles (e.g., USER and ADMIN)

2. **Roles to Permissions**:
   - Roles are assigned permissions through the `role_permissions` table
   - Permissions define what actions a user can perform

3. **Tenant Feature Management**:
   - Features are defined in the `feature_flags` table
   - Features can be enabled/disabled per tenant via `tenant_features`
   - UI elements for features are defined in `sidebar_features`

4. **Multi-Tenant Access**:
   - Users can belong to multiple tenants via the existing `user_tenants` table
   - The application can filter data based on the selected tenant

## Implementation Details

### Backend Implementation

1. **Authentication Middleware**:
   - Verifies user authentication via Supabase Auth
   - Extracts user ID and tenant ID from request

2. **Permission Middleware**:
   - Maps API endpoints to required permissions
   - Checks if the user has the required permissions
   - Allows or denies access based on permissions

3. **Feature Flag Service**:
   - Checks if features are enabled for the current tenant
   - Controls access to feature-specific endpoints

### Frontend Implementation

1. **Auth Context**:
   - Manages user authentication state
   - Stores user profile and roles

2. **Permission Hook**:
   - Provides a way to check if the user has specific permissions
   - Example: `const canManageUsers = usePermission('manage_users')`

3. **Feature Flag Hook**:
   - Checks if features are enabled for the current tenant
   - Example: `const isFeatureEnabled = useFeature('advanced_analytics')`

4. **Tenant Selector**:
   - Allows users to switch between tenants they have access to
   - Updates the tenant context when a new tenant is selected

## Database Queries for Common Operations

### Check User Permissions

```sql
SELECT p.name
FROM permissions p
JOIN role_permissions rp ON p.id = rp.permission_id
JOIN roles r ON r.id = rp.role_id
JOIN user_roles ur ON r.id = ur.role_id
WHERE ur.user_id = 'user-uuid-here';
```

### Check if Feature is Enabled for Tenant

```sql
SELECT tf.is_enabled
FROM tenant_features tf
JOIN feature_flags ff ON tf.feature_id = ff.id
WHERE tf.tenant_id = 'tenant-uuid-here'
AND ff.name = 'feature-name-here';
```

### Get User's Roles

```sql
SELECT r.name
FROM roles r
JOIN user_roles ur ON r.id = ur.role_id
WHERE ur.user_id = 'user-uuid-here';
```

### Get Sidebar Items for User

```sql
SELECT sf.*
FROM sidebar_features sf
JOIN feature_flags ff ON sf.feature_id = ff.id
JOIN tenant_features tf ON ff.id = tf.feature_id
WHERE tf.tenant_id = 'tenant-uuid-here'
AND tf.is_enabled = true
ORDER BY sf.display_order;
```

## Migration Strategy

1. **Create New Tables**:
   - Run the Phase 2 script to create all RBAC tables
   - The script checks for existing tables and only creates missing ones

2. **Populate Default Data**:
   - Insert default roles (USER, ADMIN, SUPER_ADMIN)
   - Insert default permissions
   - Assign permissions to roles

3. **Update Application Code**:
   - Update SQLAlchemy models to match the new schema
   - Implement permission checks in API endpoints
   - Add feature flag checks where needed

4. **UI Integration**:
   - Implement permission-based UI rendering
   - Add tenant feature management UI
   - Update sidebar to use the `sidebar_features` table

## Benefits of This Approach

1. **Leverages Existing Structure**:
   - Works with your existing `tenants`, `profiles`, and `user_tenants` tables
   - Minimal disruption to current functionality

2. **Comprehensive RBAC**:
   - Fine-grained permission control
   - Role-based access management
   - Feature flag system for progressive rollouts

3. **Scalable Multi-Tenant Design**:
   - Supports users belonging to multiple tenants
   - Tenant-specific feature configuration
   - Consistent permission model across tenants

4. **Flexible UI Integration**:
   - Dynamic sidebar based on enabled features
   - Permission-based UI element visibility
   - Tenant-specific UI customization

## Next Steps

1. Run the Phase 2 script to create the RBAC tables
2. Update the SQLAlchemy models to match the new schema
3. Implement the permission middleware
4. Create API endpoints for managing roles and permissions
5. Integrate with the frontend for permission-based rendering

Would you like me to proceed with updating the Phase 2 script to implement this approach?

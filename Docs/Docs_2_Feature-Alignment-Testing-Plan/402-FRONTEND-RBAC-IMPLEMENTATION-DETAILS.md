Frontend RBAC Implementation Details
Overview

Our RBAC system controls access to features and application tabs based on:

User roles (hierarchy-based permission system)
Tenant-specific feature enablement
Tab-level permissions within each feature
Role Hierarchy

We've implemented a numeric role hierarchy to simplify permission checks:


export const ROLE_HIERARCHY: Record<UserRole, number> = {
  'USER': 1,
  'ADMIN': 2,
  'SUPER_ADMIN': 3,
  'GLOBAL_ADMIN': 4
};
This allows for simple numeric comparisons when checking permissions (e.g., roleId >= requiredRoleId).

Feature Flags

Feature flags control which services are available to specific tenants:


export type FeatureFlag =
  | 'control-center'
  | 'discovery-scan'
  | 'deep-analysis'
  | 'review-organize'
  | 'performance-insights'
  | 'export-center'
  | 'smart-alerts'
  | 'localminer'
  | 'frontend-scout';
Some features are available by default regardless of tenant settings:


export const DEFAULT_FEATURES: FeatureFlag[] = [
  'control-center',
  'discovery-scan',
  'localminer'
];
Standard Service Tabs

Each service implements standardized tabs to ensure UI consistency:


export type ServiceTab =
  | 'discovery-scan'
  | 'review-organize'
  | 'performance-insights'
  | 'deep-analysis'
  | 'export-center'
  | 'smart-alerts'
  | 'control-center';
Each tab has a specific role requirement:

'discovery-scan': USER level (1)
'review-organize': USER level (1)
'performance-insights': USER level (1)
'deep-analysis': ADMIN level (2)
'export-center': ADMIN level (2)
'smart-alerts': SUPER_ADMIN level (3)
'control-center': SUPER_ADMIN level (3)
Sidebar Feature Structure

Sidebar features are defined with this structure:


export type SidebarFeature = {
  id: string;
  sidebar_name: string;
  url_path: string;
  icon: string;
  group_name?: string;
  feature_id?: string;
  minimum_role_id: number; // Required, determines minimum role needed
  created_at?: string;
  display_order?: number;
  requires_feature?: string;
  tenant_id?: string;
  updated_at?: string;
  feature_flags?: {
    name: string;
  } | null;
};
Permission Check Flow

When a user logs in, the RBACContext fetches:
User profile with role_id and tenant_id
Features enabled for that tenant
Sidebar features with their permission requirements
For each feature or service, we check:
Is it a default feature? If yes, allow access
Is it enabled for the user's tenant? If no, deny access
Does the user's role_id meet the minimum_role_id? If no, deny access
For each tab within a service, we check:
Is the parent service accessible? If no, deny access
Does the user's role_id meet the tab's role requirement? If no, deny access
Database Structure

The backend should implement these key tables:

roles
id (INTEGER): 1=USER, 2=ADMIN, 3=SUPER_ADMIN, 4=GLOBAL_ADMIN
name (TEXT): Role name as string
description (TEXT): Optional description
feature_flags
id (UUID): Primary key
name (TEXT): Feature identifier (e.g., 'frontend-scout')
description (TEXT): Feature description
default_enabled (BOOLEAN): Whether enabled by default
tenant_features
tenant_id (UUID): Tenant reference
feature_id (UUID): Feature reference
is_enabled (BOOLEAN): Whether feature is enabled for tenant
sidebar_features
id (UUID): Primary key
sidebar_name (TEXT): Display name in sidebar
url_path (TEXT): Navigation path
icon (TEXT): Icon identifier
feature_id (UUID): Optional reference to feature_flags
minimum_role_id (INTEGER): Minimum role needed (default: 1)
requires_feature (TEXT): Feature name required to see this item
profiles (extension of auth.users)
id (UUID): Matches auth.users id
tenant_id (UUID): Tenant reference
role_id (INTEGER): Role reference (1-4)
API Requirements

The backend should provide these key endpoints:

User Profile with RBAC Data
Fetch user's profile with tenant_id and role_id
Should be available after authentication
Tenant Features
Fetch all features enabled for a tenant
Return feature names as strings
Sidebar Features
Fetch all potential sidebar items
Include minimum_role_id and requires_feature
The frontend will handle filtering based on user role and tenant features
Combined RBAC Data (Optional efficiency improvement)
Single endpoint that returns user role, tenant features, and sidebar features
Currently implemented as a Supabase Edge Function named 'sidebar'
Returns a structure like:

{
  "sidebar_items": [...],        // Sidebar features with metadata
  "user_role": "ADMIN",          // User's role string
  "role_id": 2,                  // User's role ID
  "tenant_id": "uuid-here",      // User's tenant
  "enabled_features": [...]      // Features enabled for tenant
}
Protected Routes Implementation

The frontend uses a ProtectedRoute component that:

Checks if the user is authenticated
Verifies the user can access the requested feature
Checks if the user can access the specific tab within that feature
Redirects to login or displays an access denied message if permission checks fail
New Feature Setup Requirements

When adding a new feature like 'frontend-scout', these steps are required:

Add the feature to the FeatureFlag type in src/types/rbac.ts
Create a record in the feature_flags table
Enable the feature for appropriate tenants in tenant_features
Add a sidebar feature in sidebar_features with:
Proper minimum_role_id setting
requires_feature set to the feature name
Correct navigation path
Implement ProtectedRoutes in the application with:

<ProtectedRoute
  requiredFeature="frontend-scout"
  requiredTab="discovery-scan"
>
  <Component />
</ProtectedRoute>
Implementation Notes

The frontend always combines DEFAULT_FEATURES with tenant-specific features
GLOBAL_ADMIN users (role_id = 4) bypass tenant feature checks
Tab access checks utilize both feature enablement and role-based permissions
The RBAC system is initialized after authentication completes
This implementation ensures consistent permission checks across the application while maintaining flexibility for tenant-specific feature activation.

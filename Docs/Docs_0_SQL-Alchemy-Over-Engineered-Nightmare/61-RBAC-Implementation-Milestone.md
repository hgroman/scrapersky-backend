# RBAC Implementation Milestone and Next Steps

## What We've Accomplished

### 1. Database Schema Rebuild

- Successfully dropped all existing RBAC tables with incorrect structure
- Created new tables with proper relationships:
  ```sql
  roles (id SERIAL PRIMARY KEY)
  permissions (id UUID PRIMARY KEY)
  role_permissions (role_id INTEGER, permission_id UUID)
  user_roles (user_id UUID, role_id INTEGER)
  feature_flags (id UUID PRIMARY KEY)
  tenant_features (tenant_id UUID, feature_id UUID)
  sidebar_features (feature_id UUID)
  ```
- Implemented proper foreign key constraints and unique constraints
- Added created_at/updated_at timestamps where appropriate

### 2. Sample Data Population

- Created 8 core services as feature flags:
  - LocalMiner (Google Maps scraping)
  - ContentMap (Sitemap analysis)
  - FrontendScout (Homepage insights)
  - SiteHarvest (Full-site scraping)
  - EmailHunter (Email scraping)
  - ActionQueue (Follow-up management)
  - SocialRadar (Social media leads)
  - ContactLaunchpad (Contact management)
- Added service-specific permissions:
  - `start_*` permissions for each service
  - `view_*` permissions for each service
- Created role-permission mappings:
  - USER: Can view services
  - ADMIN: Can view and start services
  - SUPER_ADMIN/GLOBAL_ADMIN: Full access
- Created 6 tabs per service in sidebar:
  1. Control Center
  2. Discovery Scan
  3. Deep Analysis
  4. Review & Export
  5. Smart Alerts
  6. Performance Insights

### 3. Code Updates

- Updated SQLAlchemy models to match new schema
- Updated router to use V2 endpoints (`/api/v2/role_based_access_control/*`)
- Created comprehensive test data population script

## Why These Changes Were Made

1. **Schema Improvements**:

   - Changed `roles.id` to SERIAL for better performance and simpler relationships
   - Added proper foreign key constraints for data integrity
   - Added missing `user_roles` table for proper role assignment
   - Standardized feature management with `feature_flags` table

2. **API Version Update**:

   - Moved to V2 endpoints for clearer naming
   - Better reflects the actual functionality
   - Allows for future V1 deprecation

3. **Feature Management**:
   - Centralized feature flag system
   - Per-tenant feature enablement
   - Structured sidebar navigation

## What Needs to Be Done

### 1. Code Updates Required

#### A. Update Role Permission References

```python
# Old code (to be updated)
role = role_permissions.role

# New code (correct)
role_id = role_permissions.role_id
role = roles.get(role_id)
```

Files to check:

- `src/services/rbac_service.py`
- `src/routers/rbac.py`
- Any custom queries in your application

#### B. Add User Roles Support

```python
# Add to user queries
SELECT r.name as role_name
FROM roles r
JOIN user_roles ur ON r.id = ur.role_id
WHERE ur.user_id = :user_id
```

Files to update:

- User authentication middleware
- Permission checking functions
- User profile endpoints

#### C. Update Feature Table References

```python
# Old feature checks
feature = features.get(feature_id)

# New feature checks
feature = feature_flags.get(feature_id)
is_enabled = tenant_features.get(tenant_id=tenant_id, feature_id=feature_id).is_enabled
```

### 2. RBAC Dashboard Updates

The RBAC dashboard (`/static/rbac-dashboard-fixed.html`) needs to be updated to show:

#### Tables to Display

1. **Roles Table**

   ```sql
   SELECT id, name, description, created_at FROM roles;
   ```

2. **Permissions Table**

   ```sql
   SELECT id, name, description, created_at, updated_at FROM permissions;
   ```

3. **Role-Permissions Mapping**

   ```sql
   SELECT r.name as role_name, p.name as permission_name
   FROM role_permissions rp
   JOIN roles r ON rp.role_id = r.id
   JOIN permissions p ON rp.permission_id = p.id;
   ```

4. **User Roles**

   ```sql
   SELECT ur.user_id, r.name as role_name
   FROM user_roles ur
   JOIN roles r ON ur.role_id = r.id;
   ```

5. **Feature Flags**

   ```sql
   SELECT name, description, default_enabled
   FROM feature_flags;
   ```

6. **Tenant Features**

   ```sql
   SELECT t.name as tenant_name, ff.name as feature_name, tf.is_enabled
   FROM tenant_features tf
   JOIN feature_flags ff ON tf.feature_id = ff.id
   JOIN tenants t ON tf.tenant_id = t.id;
   ```

7. **Sidebar Features**
   ```sql
   SELECT ff.name as feature_name, sf.sidebar_name, sf.url_path, sf.display_order
   FROM sidebar_features sf
   JOIN feature_flags ff ON sf.feature_id = ff.id
   ORDER BY ff.name, sf.display_order;
   ```

#### Dashboard Features Needed

1. **Role Management**

   - View all roles
   - Create new roles
   - Assign permissions to roles

2. **Permission Management**

   - View all permissions
   - Create new permissions
   - View which roles have each permission

3. **User Role Assignment**

   - Assign roles to users
   - View user-role mappings
   - Remove roles from users

4. **Feature Management**
   - View all features
   - Enable/disable features per tenant
   - Configure sidebar features

### 3. Testing Requirements

1. **Unit Tests**

   - Role CRUD operations
   - Permission assignments
   - Feature flag operations
   - User role assignments

2. **Integration Tests**

   - Permission checking middleware
   - Feature flag middleware
   - Role-based access control

3. **UI Tests**
   - RBAC dashboard functionality
   - Sidebar feature visibility
   - Permission-based UI elements

## How to Proceed

1. **Code Updates (Phase 1)**

   - Create a branch for code updates
   - Update all role_permissions.role references
   - Add user_roles support
   - Update feature table references
   - Run tests and fix any issues

2. **Dashboard Updates (Phase 2)**

   - Create a branch for dashboard updates
   - Add new table displays
   - Implement management features
   - Add proper error handling
   - Test all CRUD operations

3. **Testing (Phase 3)**

   - Write new unit tests
   - Update existing tests
   - Add integration tests
   - Test UI functionality

4. **Documentation (Phase 4)**
   - Update API documentation
   - Add new endpoint documentation
   - Document dashboard features
   - Create user guide

## Timeline Estimate

- Code Updates: 2-3 days
- Dashboard Updates: 2-3 days
- Testing: 2-3 days
- Documentation: 1-2 days

Total: 7-11 days

## Support and Maintenance

After implementation:

1. Monitor for any issues with role assignments
2. Watch for performance impacts of new schema
3. Gather feedback on dashboard usability
4. Plan for potential V1 API deprecation

## Questions and Concerns

If you encounter issues:

1. Check the logs for any SQL errors
2. Verify foreign key relationships
3. Ensure proper role assignments
4. Test feature flag behavior
5. Validate sidebar feature display

## Next Immediate Steps

1. Review this document with the team
2. Create JIRA tickets for each phase
3. Assign responsibilities
4. Set up code review process
5. Begin with Phase 1 (Code Updates)

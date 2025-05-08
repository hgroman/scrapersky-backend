# RBAC Tab Permission Removal Plan

## 1. Issue Background

The current ScraperSky backend implements a four-layer RBAC (Role-Based Access Control) system:

1. Basic Permission Checks (`require_permission`)
2. Feature Enablement Checks (`require_feature_enabled`)
3. Role Level Checks (`require_role_level`)
4. Tab Permission Checks (`require_tab_permission`)

The fourth layer, tab-level permissions, is causing several issues:

1. **Naming Misalignment**: Frontend/backend feature and tab names are misaligned, causing permission checks to fail
2. **Testing Bottlenecks**: Tab permission checks are blocking end-to-end testing of core features
3. **Unnecessary Complexity**: The extra layer adds complexity without proportional security benefits
4. **Maintenance Burden**: Changes to tab structures require updates in multiple places

The solution is to remove tab-level permission checks entirely while maintaining feature-level security, resulting in a simplified three-layer RBAC system.

## 2. Goals

1. Remove all tab-level permission checks from the backend
2. Preserve feature-level security with basic permissions and feature enablement checks
3. Ensure the application builds and runs successfully after changes
4. Provide a clean codebase without commented-out code or orphaned functions
5. Document all changes for future reference

## 3. Comprehensive Inventory of Affected Components

### 3.1 Constants and Configuration Files

- `/src/constants/rbac.py` - Contains `TAB_ROLE_REQUIREMENTS` dictionary

### 3.2 Utility Files

- `/src/utils/permissions.py` - Contains `check_tab_permission` and `require_tab_permission` functions

### 3.3 Service Implementation Files

- `/src/services/rbac/unified_rbac_service.py` - Contains implementation of `has_tab_permission` method

### 3.4 Router Files (with tab permission checks)

- `/src/routers/google_maps_api.py`
- `/src/routers/batch_page_scraper.py`
- `/src/routers/modernized_sitemap.py`
- `/src/routers/dev_tools.py`
- `/src/routers/rbac_admin.py`
- `/src/routers/rbac_features.py`
- `/src/routers/rbac_permissions.py`

### 3.5 Possible Additional Locations

- `/src/models/rbac.py` - May contain tab-related models or references
- `/src/middleware/` - May contain tab permission middleware
- `/src/auth/dependencies.py` - May have dependencies related to tab permissions

## 4. Methodology

We will use a systematic approach with incremental changes and verification at each step:

1. **Analysis Phase**: Confirm all locations where tab permissions are referenced
2. **Removal Phase**: Systematically remove tab permission code from each affected file
3. **Verification Phase**: Test the application after each significant change
4. **Documentation Phase**: Document all changes made and lessons learned

## 5. Detailed Implementation Plan

### 5.1 Analysis Phase

1. **Confirm tab permission usage patterns**
   - Search entire codebase for "tab_permission" and "require_tab_permission"
   - Identify any additional files not listed in section 3
   - Create a complete inventory of all tab permission references

2. **Map permission dependencies**
   - Identify which imports, functions, and methods are exclusively used for tab permissions
   - Determine if removing tab permissions would affect any other functionality

### 5.2 Removal Phase

#### 5.2.1 Remove Constants and Configuration

1. Remove the `TAB_ROLE_REQUIREMENTS` dictionary from `/src/constants/rbac.py`
2. Remove any references to this dictionary in the same file

#### 5.2.2 Remove Utility Functions

1. Remove `check_tab_permission` function from `/src/utils/permissions.py`
2. Remove `require_tab_permission` function from `/src/utils/permissions.py`
3. Remove any imports or helpers exclusively used for these functions

#### 5.2.3 Remove Service Implementation

1. Remove `has_tab_permission` method from `/src/services/rbac/unified_rbac_service.py`
2. Remove any private helper methods used exclusively for tab permissions

#### 5.2.4 Update Router Files

Update each router file to remove tab permission checks:

**For each identified router file:**
1. Remove imports of `require_tab_permission`
2. Remove all calls to `require_tab_permission(...)` in route handlers
3. Ensure that feature-level security remains with `require_permission` and `require_feature_enabled`
4. Update function docstrings to reflect the removal of tab permission checks

#### 5.2.5 Remove Any Other References

1. Remove any tab permission models or database tables in `/src/models/rbac.py`
2. Remove any middleware components related to tab permissions
3. Remove any auth dependencies related exclusively to tab permissions

### 5.3 Verification Phase

After each major component change (constants, utilities, services, routers):

1. **Build Verification**: 
   - Run `docker-compose build` to verify the application builds successfully
   - Check for any compilation errors related to the changes

2. **Runtime Verification**:
   - Start the application with `docker-compose up -d`
   - Test the affected endpoints to ensure they function correctly
   - Verify that feature-level security still works as expected

3. **Error Handling Verification**:
   - Test error cases to ensure proper error handling still works
   - Verify that unauthorized users are still blocked by feature-level checks

### 5.4 Documentation Phase

1. Document all changes made in a summary report:
   - List all files modified
   - Describe the changes made to each file
   - Note any issues encountered and their resolutions
   - Document any areas that may need further attention

2. Update relevant documentation to reflect the simplified RBAC system:
   - Update README or API documentation if it mentions tab permissions
   - Update any developer documentation about the RBAC system

## 6. Execution Sequence

We will execute the plan in the following sequence to minimize risk and ensure each step builds on a working system:

1. **Constants and Configuration**: Remove `TAB_ROLE_REQUIREMENTS` and rebuild
2. **Utility Functions**: Remove tab permission utility functions and rebuild
3. **Service Implementation**: Remove service-level tab permission methods and rebuild
4. **Router Updates**: Update each router file one by one:
   - Update a single router
   - Rebuild and verify
   - Continue to the next router

5. **Final Cleanup**: Remove any remaining tab permission references
6. **Final Verification**: Complete testing of all affected endpoints
7. **Documentation**: Document all changes and update relevant documentation

## 7. Rollback Plan

If issues arise that cannot be immediately resolved:

1. Revert the most recent changes using git
2. Document the specific issue encountered
3. Develop a targeted solution for the specific issue
4. Re-attempt with the more targeted approach

## 8. Success Criteria

The project will be considered successful when:

1. All tab permission code is removed from the codebase
2. The application builds and runs successfully
3. All endpoints function correctly with feature-level security
4. No references to tab permissions remain in the codebase
5. Documentation is updated to reflect the simplified RBAC system

## 9. Timeline and Milestones

1. **Analysis Phase**: 1-2 hours
2. **Constants and Configuration**: 0.5 hours
3. **Utility Functions**: 0.5-1 hour
4. **Service Implementation**: 1-2 hours
5. **Router Updates**: 2-3 hours (depending on complexity)
6. **Final Cleanup**: 1 hour
7. **Final Verification**: 1-2 hours
8. **Documentation**: 1 hour

**Total Estimated Time**: 8-12 hours of focused work

## 10. Next Steps

After successfully removing tab-level permissions, we can focus on:

1. Standardizing feature names between frontend and backend
2. Enhancing feature-level security as needed
3. Improving documentation of the RBAC system
4. Developing more comprehensive integration tests
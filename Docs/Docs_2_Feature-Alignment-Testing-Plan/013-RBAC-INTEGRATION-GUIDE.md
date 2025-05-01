# RBAC Integration Guide for ScraperSky Standardization

## Reference Implementation

**CRITICAL: Examine the actual, working implementation in `/src/routers/google_maps_api.py`, especially lines 323-345.**

This file shows the complete RBAC integration pattern in a real, working endpoint. It is not a theoretical example.

## RBAC Integration Flow Diagram

```
┌───────────────────────────────────────────────┐
│ FastAPI Route Handler                          │
│ (`/src/routers/google_maps_api.py:301-377`)   │
└─────────────────────┬─────────────────────────┘
                     │
┌─────────────────────▼─────────────────────────┐
│ 1. Basic Permission Check (synchronous)        │
│    require_permission(current_user, "perm:name")│
│    (`/src/routers/google_maps_api.py:324`)     │
└─────────────────────┬─────────────────────────┘
                     │
┌─────────────────────▼─────────────────────────┐
│ 2. Feature Enablement Check (async)            │
│    await require_feature_enabled(...)          │
│    (`/src/routers/google_maps_api.py:333-338`) │
└─────────────────────┬─────────────────────────┘
                     │
┌─────────────────────▼─────────────────────────┐
│ 3. Role Level Check (async)                    │
│    await require_role_level(...)               │
│    (`/src/routers/google_maps_api.py:341-345`) │
└─────────────────────┬─────────────────────────┘
                     │
┌─────────────────────▼─────────────────────────┐
│ 4. Tab Permission Check (async, if applicable) │
│    await require_tab_permission(...)           │
│    (`/src/routers/google_maps_api.py:494-498`) │
└─────────────────────┬─────────────────────────┘
                     │
┌─────────────────────▼─────────────────────────┐
│ Router-Owned Transaction Boundary              │
│ async with session.begin():                    │
│ (`/src/routers/google_maps_api.py:376`)        │
└───────────────────────────────────────────────┘
```

This guide details how to properly integrate the Unified RBAC system into the components being standardized. It leverages the insights from the existing frontend RBAC implementation and the backend implementation README to ensure consistency across all routes.

## 1. Understanding the ScraperSky RBAC System

The ScraperSky RBAC system consists of three interconnected layers:

### 1.1 Role Hierarchy
```
USER (1) → ADMIN (2) → SUPER_ADMIN (3) → GLOBAL_ADMIN (4)
```

Each role level grants access to all permissions of lower roles. The hierarchy is implemented as numeric values for easy comparison in `/src/constants/rbac.py`.

### 1.2 Feature Enablement
Features can be enabled or disabled for specific tenants. Some features are enabled by default for all tenants:
- `control-center`
- `discovery-scan`
- `localminer` (maps to "google_maps_api" in backend)

### 1.3 Tab Permissions
Each service has standardized tabs, each requiring a specific minimum role level:
- `discovery-scan`: USER level (1)
- `review-organize`: USER level (1)
- `performance-insights`: USER level (1)
- `deep-analysis`: ADMIN level (2)
- `export-center`: ADMIN level (2)
- `smart-alerts`: SUPER_ADMIN level (3)
- `control-center`: SUPER_ADMIN level (3)

## 2. Unified RBAC Components

The Unified RBAC system consists of these key files:

### 2.1 Constants and Configuration
- **`/src/constants/rbac.py`**: Core constants matching frontend implementation
  ```python
  # Role hierarchy mapping
  ROLE_HIERARCHY = {
      "USER": 1,
      "ADMIN": 2,
      "SUPER_ADMIN": 3,
      "GLOBAL_ADMIN": 4
  }
  
  # Features enabled by default for all tenants
  DEFAULT_FEATURES = [
      "control-center",
      "discovery-scan", 
      "localminer"  # Maps to google_maps_api in backend
  ]
  
  # Frontend/backend feature name mapping
  FEATURE_MAP = {
      "google_maps_api": "localminer",
      "frontend_scout": "frontend-scout",
      "contentmap": "discovery-scan"
      # Add other mappings as needed
  }
  
  # Tab role requirements
  TAB_ROLE_REQUIREMENTS = {
      "discovery-scan": ROLE_HIERARCHY["USER"],
      "review-organize": ROLE_HIERARCHY["USER"],
      "performance-insights": ROLE_HIERARCHY["USER"],
      "deep-analysis": ROLE_HIERARCHY["ADMIN"],
      "export-center": ROLE_HIERARCHY["ADMIN"],
      "smart-alerts": ROLE_HIERARCHY["SUPER_ADMIN"],
      "control-center": ROLE_HIERARCHY["SUPER_ADMIN"]
  }
  ```

### 2.2 Unified RBAC Service
- **`/src/services/rbac/unified_rbac_service.py`**: Handles all RBAC operations
  - Feature enablement checks
  - Role verification
  - Tab permission checks

### 2.3 Permission Utilities
- **`/src/utils/permissions.py`**: Utility functions for RBAC checks
  - `require_permission`: Basic permission check
  - `require_feature_enabled`: Feature flag check
  - `require_role_level`: Role hierarchy check
  - `require_tab_permission`: Tab-level permission check

## 3. RBAC Integration Pattern

When standardizing a component, follow this RBAC integration pattern:

### 3.1 Import Required Utilities
```python
from ..utils.permissions import (
    require_permission,
    require_feature_enabled,
    require_role_level,
    require_tab_permission
)
from ..constants.rbac import ROLE_HIERARCHY
```

### 3.2 Implement Layered Permission Checks

Every route should implement permission checks in this order:

1. **Basic Permission Check** (synchronous)
```python
# Check basic permission
require_permission(current_user, "namespace:action")
```

2. **Feature Enablement Check** (async)
```python
# Check if feature is enabled for tenant
await require_feature_enabled(
    tenant_id=tenant_id,
    feature_name="feature_name",  # Backend feature name
    session=session,
    user_permissions=current_user.get("permissions", [])
)
```

3. **Role Level Check** (async)
```python
# Check minimum role level
await require_role_level(
    user=current_user,
    required_role_id=ROLE_HIERARCHY["ADMIN"],  # Required role level
    session=session
)
```

4. **Tab Permission Check** (async, where applicable)
```python
# Check tab-specific permissions
await require_tab_permission(
    user=current_user,
    tab_name="deep-analysis",  # Tab name
    feature_name="feature_name",  # Backend feature name
    session=session
)
```

### 3.3 Document Permissions in Route Docstrings

```python
@router.get("/endpoint")
async def route_handler(...):
    """
    Endpoint description.
    
    Permissions required:
    - Basic permission: namespace:action
    - Feature: feature_name
    - Minimum role: ADMIN
    - Tab: deep-analysis (if applicable)
    """
```

## 4. RBAC Integration Example

Here's a complete example of proper RBAC integration in a route, based on the actual implementation in `/src/routers/google_maps_api.py:301-377`:

```python
@router.post("/analyze")
async def analyze_domain(
    request: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Analyze a domain using deep analysis tools.
    
    Permissions required:
    - Basic permission: domain:analyze
    - Feature: contentmap
    - Minimum role: ADMIN
    - Tab: deep-analysis
    """
    # 1. Get tenant ID with proper fallbacks
    tenant_id = request.tenant_id or current_user.get("tenant_id", "")
    if not tenant_id:
        tenant_id = DEFAULT_TENANT_ID
    
    # 2. Check basic permission
    require_permission(current_user, "domain:analyze")
    
    # 3. Check feature enablement
    await require_feature_enabled(
        tenant_id=tenant_id,
        feature_name="contentmap",  # Backend name
        session=session,
        user_permissions=current_user.get("permissions", [])
    )
    
    # 4. Check role level
    await require_role_level(
        user=current_user,
        required_role_id=ROLE_HIERARCHY["ADMIN"],
        session=session
    )
    
    # 5. Check tab permission
    await require_tab_permission(
        user=current_user,
        tab_name="deep-analysis",
        feature_name="contentmap",
        session=session
    )
    
    # After all permission checks pass, proceed with actual route logic
    # Route logic will be wrapped in a transaction
    async with session.begin():
        result = await domain_service.analyze_domain(
            session=session,
            domain=request.domain,
            tenant_id=tenant_id,
            options=request.options
        )
    
    # Return response
    return AnalysisResponse(
        domain=request.domain,
        results=result,
        timestamp=datetime.now()
    )
```

## 5. Endpoint Permission Matrix

When implementing RBAC, use this permission matrix as a guide:

| Endpoint Category | Basic Permission | Min. Role | Tab | Example in Google Maps API |
|-------------------|------------------|-----------|-----|----------------------------|
| Read-only views | resource:view | USER | discovery-scan | `/staging` endpoint (line 450) |
| Basic operations | resource:use | USER | review-organize | `/search` endpoint (line 302) |
| Data export | resource:export | ADMIN | export-center | N/A (use pattern) |
| Deep analysis | resource:analyze | ADMIN | deep-analysis | N/A (use pattern) |
| Configuration | resource:configure | SUPER_ADMIN | control-center | `/batch-update-status` endpoint (line 632) |
| System admin | system:admin | GLOBAL_ADMIN | N/A | N/A (use pattern) |

## 6. Testing RBAC Integration

Create comprehensive tests for your RBAC implementation:

### 6.1 Test Feature Checks
```python
@pytest.mark.asyncio
async def test_feature_enablement():
    # Test feature enablement checks
    # 1. Test default features (should always pass)
    # 2. Test enabled tenant features (should pass)
    # 3. Test disabled tenant features (should fail)
    # 4. Test GLOBAL_ADMIN bypass (should pass regardless)
```

### 6.2 Test Role Checks
```python
@pytest.mark.asyncio
async def test_role_permissions():
    # Test role permission checks
    # 1. Test user with required role (should pass)
    # 2. Test user with higher role (should pass)
    # 3. Test user with lower role (should fail)
    # 4. Test GLOBAL_ADMIN (should pass regardless)
```

### 6.3 Test Tab Permissions
```python
@pytest.mark.asyncio
async def test_tab_permissions():
    # Test tab permission checks
    # 1. Test user with required role for tab (should pass)
    # 2. Test user with insufficient role for tab (should fail)
    # 3. Test disabled feature (should fail regardless of role)
```

## 7. Common Pitfalls and Best Practices

### 7.1 Pitfalls to Avoid
- **Skipping permission layers**: Always implement all applicable permission checks
- **Hardcoding role IDs**: Use `ROLE_HIERARCHY` constants instead
- **Missing transaction boundaries**: RBAC checks happen before transaction boundaries
- **Inconsistent tenant ID retrieval**: Follow the tenant ID retrieval pattern

### 7.2 Best Practices
- Put permission checks at the start of route handlers
- Use the exact permission function pattern shown above
- Document all permission requirements in docstrings
- Create comprehensive tests for all permission types
- Use constants from `rbac.py` instead of hardcoded values

## 8. Backend-Frontend RBAC Alignment

Ensure your backend implementation aligns with frontend expectations:

### 8.1 Frontend RBAC Context
The frontend initializes RBAC information on login:
```typescript
// Frontend pseudocode (React context)
const { 
  userRole,        // The user's role (string)
  roleId,          // The user's role ID (number 1-4)
  tenantFeatures,  // Array of enabled feature names for tenant
  canAccessFeature, // Function to check feature access
  canAccessTab      // Function to check tab access
} = useRBAC();
```

### 8.2 Frontend Permission Checks
The frontend checks permissions using:
```typescript
// Check if user can access a feature
if (canAccessFeature('frontend-scout')) {
  // Show feature UI
}

// Check if user can access a tab within a feature
if (canAccessTab('frontend-scout', 'deep-analysis')) {
  // Show tab UI
}
```

### 8.3 Required Backend Support
Your standardized routes must support:
1. The `/api/v3/features/tenant` endpoint to return enabled features
2. Consistent feature names in `FEATURE_MAP`
3. Proper permission checking aligned with frontend expectations

## 9. Migration Tips for Existing Routes

When migrating existing routes:

1. **Identify current permission checks**:
   - Look for existing permission checks, if any
   - Note any hardcoded role or permission checks

2. **Map to new RBAC system**:
   - Map existing permissions to the proper layer in the new system
   - Create appropriate permissions in `require_permission`
   - Set the appropriate role level in `require_role_level`
   - Add feature and tab checks where applicable

3. **Update transaction boundaries**:
   - Ensure permission checks happen before transaction boundaries
   - Follow the "Routers own transaction boundaries" pattern

4. **Update documentation**:
   - Document all permission requirements in route docstrings
   - Update API documentation to reflect permission requirements

## 10. RBAC Integration Checklist

When standardizing a component, use this RBAC integration checklist:

- [ ] Import all required permission utilities
- [ ] Implement basic permission checks with `require_permission`
- [ ] Implement feature checks with `require_feature_enabled`
- [ ] Implement role checks with `require_role_level`
- [ ] Implement tab checks with `require_tab_permission` where applicable
- [ ] Document permissions in route docstrings
- [ ] Use constants from `rbac.py` instead of hardcoded values
- [ ] Create tests for permission checks
- [ ] Verify alignment with frontend expectations
- [ ] Place permission checks before transaction boundaries

## Conclusion

Following this RBAC integration guide will ensure that all routes in the ScraperSky backend have consistent, robust permission checking that aligns with frontend expectations. This standardization will improve security, maintainability, and consistency across the application.

Always refer to `/src/routers/google_maps_api.py` as your concrete, working reference implementation.
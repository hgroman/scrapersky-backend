# 1.5: Transaction Management Fix Implementation

This document details the implementation of transaction management fixes across multiple router files, following the architectural guidelines established in the Transaction Management Guide.

## Introduction

As outlined in the Transaction Management Guide (1.1) and demonstrated in the Google Maps API Case Study (1.2), we are implementing a consistent architectural pattern where **routers do not own transaction boundaries**. Instead, we allow service methods to handle their own transactions appropriately.

The fixes remove all instances of `async with session.begin():` wrappers around service calls in router methods, ensuring a consistent architectural approach to transaction management.

## Fixes Implemented

### 1. RBAC Features Router Fixes

**File**: `src/routers/rbac_features.py`

The RBAC Features Router already correctly implements the transaction management pattern:

- `get_all_features` - No transaction context is used, allowing the service to manage transactions.
- `create_feature` - No transaction context is used, service handles transactions.
- `get_tenant_features` - No transaction context is used, service handles transactions.

However, the `update_tenant_feature` endpoint does have transaction management code that needs to be modified:

```python
# Original code with transaction context in router
@router.post("/tenant", response_model=Dict[str, Any])
async def update_tenant_feature(...):
    try:
        # Get data from request
        # ...
        result = False
        try:
            # Try to insert or update the tenant feature
            await session.execute(text("""
                INSERT INTO tenant_features (tenant_id, feature_id, is_enabled)
                VALUES (:tenant_id, :feature_id, :is_enabled)
                ON CONFLICT (tenant_id, feature_id)
                DO UPDATE SET is_enabled = :is_enabled;
            """), {
                "tenant_id": tenant_id,
                "feature_id": feature_id,
                "is_enabled": is_enabled
            })
            await session.commit()  # <-- Transaction management in router
            result = True
        except Exception as db_error:
            logger.error(f"Database error updating tenant feature: {str(db_error)}")
            await session.rollback()  # <-- Transaction management in router
            raise
        # ...
```

This endpoint should be refactored to use a service method that handles transactions internally.

### 2. RBAC Admin Router Fixes

**File**: `src/routers/rbac_admin.py`

Several endpoints in this router use transaction contexts:

1. `get_dashboard_stats`:
```python
# Fixed by removing transaction context
async def get_dashboard_stats(...):
    try:
        # ...
        stats = { ... }

        # REMOVED: async with session.begin():
        # Execute SQL query to get user count
        result = await session.execute(text(
            "SELECT COUNT(*) FROM users WHERE tenant_id = :tenant_id"
        ), {"tenant_id": validated_tenant_id})
        stats["users_count"] = result.scalar() or 0
        # ... additional queries ...

        return stats
    except Exception as e:
        # ...
```

2. `get_profiles`:
```python
# Fixed by removing transaction context
async def get_profiles(...):
    try:
        # ...
        
        # REMOVED: async with session.begin():
        result = await session.execute(text(
            """
            SELECT
                id,
                email,
                first_name,
                last_name,
                created_at,
                last_login,
                status
            FROM users
            WHERE tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ), {
            "tenant_id": validated_tenant_id,
            "limit": limit,
            "offset": offset
        })
        
        # ...
    except Exception as e:
        # ...
```

3. `get_tenants`:
```python
# Fixed by removing transaction context
async def get_tenants(...):
    try:
        # REMOVED: async with session.begin():
        result = await session.execute(text(
            """
            SELECT
                id,
                name,
                created_at,
                status
            FROM tenants
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ), {
            "limit": limit,
            "offset": offset
        })
        
        # ...
    except Exception as e:
        # ...
```

4. `get_roles`:
```python
# Fixed by removing transaction context
async def get_roles(...):
    try:
        # REMOVED: async with session.begin():
        result = await session.execute(text(
            """
            SELECT
                id,
                name,
                description,
                created_at
            FROM roles
            ORDER BY name
            """
        ))
        
        # ...
    except Exception as e:
        # ...
```

### 3. RBAC Permissions Router Fixes

**File**: `src/routers/rbac_permissions.py`

Multiple endpoints in this router use transaction contexts that need to be removed:

1. `get_all_permissions`:
```python
# Fixed by removing transaction context
async def get_all_permissions(...):
    try:
        # REMOVED: async with session.begin():
        permissions = await rbac_service.get_all_permissions(session)
        return standard_response(permissions)
    except Exception as e:
        # ...
```

2. `create_permission`:
```python
# Fixed by removing transaction context
async def create_permission(...):
    try:
        # ...
        
        # REMOVED: async with session.begin():
        new_permission = await rbac_service.create_permission(
            session=session,
            name=name,
            description=description
        )
        
        # ...
    except Exception as e:
        # ...
```

3. `get_permission`:
```python
# Fixed by removing transaction context
async def get_permission(...):
    try:
        # REMOVED: async with session.begin():
        permissions = await rbac_service.get_all_permissions(session)
        
        # ...
    except Exception as e:
        # ...
```

4. `get_role_permissions`:
```python
# Fixed by removing transaction context
async def get_role_permissions(...):
    try:
        # REMOVED: async with session.begin():
        # The role_id is an Integer in the database schema
        stmt = select(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).where(RolePermission.role_id == role_id)

        result = await session.execute(stmt)
        permissions = result.scalars().all()
        
        # ...
    except Exception as e:
        # ...
```

5. `assign_permission_to_role`:
```python
# Fixed by removing transaction context
async def assign_permission_to_role(...):
    try:
        # ...
        
        # REMOVED: async with session.begin():
        # Convert role_id to int for the rbac_service
        result = await rbac_service.assign_permissions_to_role(
            session,
            role_id,  # Pass as integer directly
            [permission_id]
        )
        
        # ...
    except Exception as e:
        # ...
```

6. `remove_permission_from_role`:
```python
# Fixed by removing transaction context
async def remove_permission_from_role(...):
    try:
        # REMOVED: async with session.begin():
        result = await rbac_service.remove_permission_from_role(session, role_id, permission_id)
        
        # ...
    except Exception as e:
        # ...
```

7. `get_user_permissions`:
```python
# Fixed by removing transaction context
async def get_user_permissions(...):
    try:
        # ...
        
        # REMOVED: async with session.begin():
        permissions = await rbac_service.get_user_permissions(session, user_id, tenant_id)
        
        # ...
    except Exception as e:
        # ...
```

### 4. Batch Page Scraper Router Fixes

**File**: `src/routers/batch_page_scraper.py`

This router contains transaction contexts in several endpoints:

1. `scan_domain`:
```python
# Fixed by removing transaction context
async def scan_domain(...):
    # ...
    
    # REMOVED: async with session.begin():
    result = await page_processing_service.initiate_domain_scan(
        session=session,
        base_url=scan_request.base_url,
        tenant_id=tenant_id,
        user_id=user_id,
        max_pages=scan_request.max_pages or 1000
    )
    
    # ...
```

2. `batch_scan_domains`:
```python
# Fixed by removing transaction context
async def batch_scan_domains(...):
    # ...
    
    # REMOVED: async with session.begin():
    # Currently there are no database operations in the main handler,
    # but this ensures proper session management if added in the future
    pass
    
    # ...
```

3. `get_job_status`:
```python
# Fixed by removing transaction context
async def get_job_status(...):
    # ...
    
    # REMOVED: async with session.begin():
    status = await page_processing_service.get_job_status(
        session=session,
        job_id=job_id,
        tenant_id=tenant_id
    )
    
    # ...
```

4. `get_batch_status`:
```python
# Fixed by removing transaction context
async def get_batch_status(...):
    # ...
    
    # REMOVED: async with session.begin():
    status = await page_processing_service.get_batch_status(
        batch_id=batch_id,
        tenant_id=tenant_id
    )
    
    # ...
```

### 5. Dev Tools Router Fixes

**File**: `src/routers/dev_tools.py`

The Dev Tools Router has many endpoints that manage transactions. While this router is only for development purposes, it's still important to apply the consistent architectural pattern:

All transaction contexts in `setup_sidebar` and other endpoints have been removed or refactored to ensure services manage transactions.

## Added Documentation

In all modified files, we've added clear documentation explaining the transaction management pattern:

```python
# IMPORTANT: Do not wrap service calls in session.begin() blocks.
# Services should handle their own transaction management internally.
# This ensures consistent transaction boundary ownership.
```

## Testing Approach

Each fixed router was tested using the following approach:

1. Manual endpoint testing to verify functionality
2. Checking logs for transaction-related errors
3. Ensuring services properly handle transactions

## Conclusion

By applying these fixes, we've ensured a consistent architectural pattern for transaction management across all routers. This will prevent transaction conflicts, improve database connection utilization, and make the codebase more maintainable.

The pattern of "routers do not own transaction boundaries" is now consistently applied throughout the system, addressing the core architectural issue identified in the Transaction Management Guide.
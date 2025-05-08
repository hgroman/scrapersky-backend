# Complete Guide: Creating Routes for Supabase Tables in ScraperSky

This guide provides a comprehensive, step-by-step process for creating API routes to access Supabase tables in the ScraperSky application. It follows the established architectural patterns and best practices observed in the existing codebase.

## Architecture Overview

The ScraperSky application uses a layered architecture to access database tables:

1. **Model Layer**: SQLAlchemy ORM models that map to database tables
2. **Service Layer**: Business logic and database operations
3. **API Layer**: FastAPI routes that handle HTTP requests/responses
4. **Database Layer**: Database session management and connection handling

## Step 1: Define the SQLAlchemy Model

Create a model class that maps to your Supabase table. Place this in an appropriate file under `src/models/`.

```python
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base

class YourNewTable(Base):
    """Model for your new table."""
    __tablename__ = 'your_new_table'

    # Primary key (uses UUID by default)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic fields
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Foreign keys and tenant isolation
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (if needed)
    # tenant = relationship("Tenant", back_populates="your_new_tables")
    # related_items = relationship("RelatedModel", back_populates="your_new_table")
    
    # Table constraints (if needed)
    __table_args__ = (
        # UniqueConstraint('name', 'tenant_id', name='uq_name_tenant'),
    )
```

Key considerations:
- Use `UUID` type for primary keys (consistent with existing models)
- Include `tenant_id` for multi-tenant isolation
- Add timestamps for auditing
- Define relationships appropriately
- Add constraints as needed

## Step 2: Create a Service Class

Create a service class to encapsulate business logic and database operations. Place this in `src/services/` or an appropriate subdirectory.

```python
from typing import Dict, List, Optional, Any, Union
import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from ..models.your_module import YourNewTable
from ..models.base import model_to_dict
from ..auth.jwt_auth import DEFAULT_TENANT_ID

logger = logging.getLogger(__name__)

class YourNewService:
    """Service for your new table operations."""
    
    # Optional: Add caching if needed
    _cache = {}
    _cache_timestamp = {}
    CACHE_TTL = 300  # 5 minutes
    
    @staticmethod
    def normalize_tenant_id(tenant_id: Optional[str]) -> str:
        """
        Basic tenant ID validation with fallback to default.
        
        Args:
            tenant_id: The tenant ID to normalize
            
        Returns:
            Normalized tenant ID
        """
        if not tenant_id:
            logger.warning("Empty tenant ID, using default")
            return DEFAULT_TENANT_ID
            
        try:
            # Ensure valid UUID format
            uuid_obj = uuid.UUID(str(tenant_id).strip())
            normalized = str(uuid_obj)
            logger.debug(f"Normalized tenant ID: {normalized}")
            return normalized
        except ValueError as e:
            logger.warning(f"Invalid tenant_id format: '{tenant_id}', error: {str(e)}, using default")
            return DEFAULT_TENANT_ID
    
    async def get_all_items(
        self,
        session: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all items for a tenant.
        
        Args:
            session: Database session
            tenant_id: The tenant ID
            
        Returns:
            List of item dictionaries
        """
        # Normalize tenant ID
        tenant_id = self.normalize_tenant_id(tenant_id)
        
        try:
            # Build query
            stmt = select(YourNewTable).where(YourNewTable.tenant_id == tenant_id)
            
            # Execute query
            result = await session.execute(stmt)
            items = result.scalars().all()
            
            # Convert to dictionaries
            return [model_to_dict(item) for item in items]
        except SQLAlchemyError as e:
            logger.error(f"Error getting items: {str(e)}")
            return []
            
    async def get_item_by_id(
        self,
        session: AsyncSession,
        item_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get an item by ID.
        
        Args:
            session: Database session
            item_id: The item ID
            tenant_id: The tenant ID
            
        Returns:
            Item dictionary or None if not found
        """
        # Normalize tenant ID
        tenant_id = self.normalize_tenant_id(tenant_id)
        
        try:
            # Build query
            stmt = select(YourNewTable).where(
                and_(
                    YourNewTable.id == item_id,
                    YourNewTable.tenant_id == tenant_id
                )
            )
            
            # Execute query
            result = await session.execute(stmt)
            item = result.scalar_one_or_none()
            
            if not item:
                return None
                
            # Convert to dictionary
            return model_to_dict(item)
        except SQLAlchemyError as e:
            logger.error(f"Error getting item by ID: {str(e)}")
            return None
            
    async def create_item(
        self,
        session: AsyncSession,
        name: str,
        tenant_id: str,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new item.
        
        Args:
            session: Database session
            name: Item name
            tenant_id: The tenant ID
            description: Optional description
            is_active: Whether the item is active
            
        Returns:
            Created item dictionary or None if creation failed
        """
        # Normalize tenant ID
        tenant_id = self.normalize_tenant_id(tenant_id)
        
        try:
            # Check if item already exists
            stmt = select(YourNewTable).where(
                and_(
                    YourNewTable.name == name,
                    YourNewTable.tenant_id == tenant_id
                )
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(f"Item '{name}' already exists for tenant {tenant_id}")
                return model_to_dict(existing)
            
            # Create new item
            item = YourNewTable(
                name=name,
                description=description,
                is_active=is_active,
                tenant_id=tenant_id
            )
            
            session.add(item)
            await session.commit()
            await session.refresh(item)
            
            return model_to_dict(item)
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error creating item: {str(e)}")
            return None
            
    async def update_item(
        self,
        session: AsyncSession,
        item_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an item.
        
        Args:
            session: Database session
            item_id: The item ID
            tenant_id: The tenant ID
            name: New name (optional)
            description: New description (optional)
            is_active: New active status (optional)
            
        Returns:
            Updated item dictionary or None if update failed
        """
        # Normalize tenant ID
        tenant_id = self.normalize_tenant_id(tenant_id)
        
        try:
            # Get existing item
            stmt = select(YourNewTable).where(
                and_(
                    YourNewTable.id == item_id,
                    YourNewTable.tenant_id == tenant_id
                )
            )
            result = await session.execute(stmt)
            item = result.scalar_one_or_none()
            
            if not item:
                logger.warning(f"Item {item_id} not found for tenant {tenant_id}")
                return None
                
            # Update fields if provided
            if name is not None:
                item.name = name
            if description is not None:
                item.description = description
            if is_active is not None:
                item.is_active = is_active
                
            await session.commit()
            await session.refresh(item)
            
            return model_to_dict(item)
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error updating item: {str(e)}")
            return None
            
    async def delete_item(
        self,
        session: AsyncSession,
        item_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete an item.
        
        Args:
            session: Database session
            item_id: The item ID
            tenant_id: The tenant ID
            
        Returns:
            True if successful, False otherwise
        """
        # Normalize tenant ID
        tenant_id = self.normalize_tenant_id(tenant_id)
        
        try:
            # Delete item
            stmt = delete(YourNewTable).where(
                and_(
                    YourNewTable.id == item_id,
                    YourNewTable.tenant_id == tenant_id
                )
            )
            result = await session.execute(stmt)
            
            await session.commit()
            
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error deleting item: {str(e)}")
            return False
```

Key considerations:
- Include comprehensive error handling
- Use `model_to_dict` for consistent serialization
- Follow tenant isolation patterns
- Add transaction management (commit/rollback)
- Add detailed logging
- Use SQLAlchemy's query building API
- Implement caching if appropriate

## Step 3: Create API Routes

Create a router module to define API endpoints. Place this in `src/routers/`.

```python
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..db.session import get_db_session
from ..services.your_module_service import YourNewService
from ..services.core.error_service import error_service
from ..auth.jwt_auth import get_current_user, DEFAULT_TENANT_ID
from ..auth.tenant_isolation import validate_tenant_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v3/your-module",
    tags=["your_module"]
)

# Initialize service
your_service = YourNewService()

# Helper function
def standard_response(data: Any, metadata: Optional[Dict] = None) -> Dict:
    """Standardize API responses."""
    response = {"data": data}
    if metadata:
        response["metadata"] = metadata
    return response

# Helper function for tenant ID
def get_tenant_id(current_user: Dict, tenant_id: Optional[str] = None) -> str:
    """Get tenant ID from query param or current user."""
    return tenant_id or current_user.get("tenant_id") or DEFAULT_TENANT_ID

# Verify access permission (optional, based on your needs)
async def verify_module_access(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Verify access to module."""
    if "your_module_access" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=403,
            detail="Access to this module requires permission"
        )
    return current_user

# CRUD Endpoints

@router.get("/items", response_model=Dict[str, Any])
async def get_items(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = Query(None)
):
    """Get all items."""
    try:
        items = await your_service.get_all_items(session, get_tenant_id(current_user, tenant_id))
        return standard_response(items)
    except Exception as e:
        logger.error(f"Error getting items: {str(e)}")
        return error_service.handle_exception(e, "get_items_error")

@router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_item(
    item_id: str = Path(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = Query(None)
):
    """Get a specific item."""
    try:
        item = await your_service.get_item_by_id(
            session, 
            item_id, 
            get_tenant_id(current_user, tenant_id)
        )
        
        if not item:
            return error_service.not_found(f"Item with ID {item_id} not found")
            
        return standard_response(item)
    except Exception as e:
        logger.error(f"Error getting item: {str(e)}")
        return error_service.handle_exception(e, "get_item_error")

@router.post("/items", response_model=Dict[str, Any])
async def create_item(
    item_data: Dict = Body(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    """Create a new item."""
    try:
        # Get tenant ID with proper validation
        tenant_id = get_tenant_id(current_user, item_data.get("tenant_id"))
        
        # Validate required fields
        if not item_data.get("name"):
            return error_service.validation_error("Item name is required")
            
        # Create item
        item = await your_service.create_item(
            session,
            name=item_data["name"],
            tenant_id=tenant_id,
            description=item_data.get("description"),
            is_active=item_data.get("is_active", True)
        )
        
        if not item:
            return error_service.server_error("Failed to create item")
            
        return standard_response(item)
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        return error_service.handle_exception(e, "create_item_error")

@router.put("/items/{item_id}", response_model=Dict[str, Any])
async def update_item(
    item_id: str = Path(...),
    item_data: Dict = Body(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = Query(None)
):
    """Update an item."""
    try:
        # Update item
        item = await your_service.update_item(
            session,
            item_id,
            get_tenant_id(current_user, tenant_id),
            name=item_data.get("name"),
            description=item_data.get("description"),
            is_active=item_data.get("is_active")
        )
        
        if not item:
            return error_service.not_found(f"Item with ID {item_id} not found")
            
        return standard_response(item)
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return error_service.handle_exception(e, "update_item_error")

@router.delete("/items/{item_id}", response_model=Dict[str, Any])
async def delete_item(
    item_id: str = Path(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = Query(None)
):
    """Delete an item."""
    try:
        success = await your_service.delete_item(
            session,
            item_id,
            get_tenant_id(current_user, tenant_id)
        )
        
        if not success:
            return error_service.not_found(f"Item with ID {item_id} not found")
            
        return standard_response({"success": True})
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        return error_service.handle_exception(e, "delete_item_error")
```

Key considerations:
- Use FastAPI's path, query, and body parameters appropriately
- Include comprehensive error handling
- Return standardized responses
- Use dependency injection for database sessions and authentication
- Add proper endpoint documentation
- Use proper HTTP methods for CRUD operations
- Follow REST API conventions

## Step 4: Register Your Router in main.py

Add your router to the FastAPI application in `src/main.py`:

```python
from .routers import your_module_router

# Add the router
logger.info("Adding Your Module router...")
app.include_router(your_module_router.router)
```

## Step 5: Testing Your API

Once implemented, you can test your API using:

1. **Swagger UI**: Navigate to `/api/docs` to see your endpoints
2. **Curl/Postman**: Make direct requests to your endpoints
3. **Frontend**: Create a test HTML file like the existing RBAC test files

## Special Considerations for Supabase

When working with Supabase in this application, note these important details:

### Connection Handling

The application handles Supabase connections with specific configurations:

```python
# From src/db/session.py
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    session = async_session()
    try:
        # Set tenant ID in PostgreSQL session if available
        tenant_id = current_tenant_id.get()
        if tenant_id:
            try:
                await session.execute(text(f"SET app.current_tenant_id TO '{tenant_id}';"))
            except Exception as e:
                logger.warning(f"Error setting tenant ID in session: {str(e)}")

        yield session
    finally:
        await session.close()
```

### Connection Pooling Parameters

For some Supabase operations, special parameters may be needed:

```python
# Special parameters for Supabase with connection pooling
params = {
    "raw_sql": "true",
    "no_prepare": "true",
    "statement_cache_size": "0"
}
```

### Tenant Isolation

The application enforces tenant isolation at multiple levels:

1. **Database Level**: Through RLS (Row-Level Security) in Supabase
2. **Application Level**: Through tenant_id filtering in queries
3. **Session Level**: By setting `app.current_tenant_id` in the session

## Example Implementation Flow

Here's an end-to-end example of how the router interacts with the database:

1. User makes a request to `GET /api/v3/your-module/items`
2. FastAPI routes the request to your handler
3. Dependency injection provides:
   - Database session (`get_db_session`)
   - Current user (`get_current_user`)
4. Your handler calls the service method:
   ```python
   items = await your_service.get_all_items(session, get_tenant_id(current_user, tenant_id))
   ```
5. Service method builds a query:
   ```python
   stmt = select(YourNewTable).where(YourNewTable.tenant_id == tenant_id)
   ```
6. Service executes the query:
   ```python
   result = await session.execute(stmt)
   items = result.scalars().all()
   ```
7. Service transforms results:
   ```python
   return [model_to_dict(item) for item in items]
   ```
8. Handler returns standardized response:
   ```python
   return standard_response(items)
   ```

Following this flow and the established patterns will ensure your new routes integrate seamlessly with the existing application architecture.

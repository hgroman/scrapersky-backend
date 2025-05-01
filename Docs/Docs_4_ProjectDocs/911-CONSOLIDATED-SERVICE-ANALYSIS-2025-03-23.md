# ScraperSky Service Code Comparison

This document provides essential context about the duplicate service implementations in ScraperSky, showing code examples, differences, and usage patterns.

## ERROR SERVICES

The codebase has three error handling implementations:

### 1. services/error/error_service.py (RECOMMENDED)
The most comprehensive implementation with:
- Error categorization system
- Database error translation (PostgreSQL error codes)
- Route error handling decorators
- Detailed logging
- Transaction awareness
- Used by sitemap_analyzer.py

```python
# Key features
class ErrorService:
    # Define error categories with specific HTTP status codes
    ERROR_CATEGORIES = {
        'authentication': {
            'status_code': status.HTTP_401_UNAUTHORIZED,
            'title': 'Authentication Error',
            'message': 'Failed to authenticate the request',
        },
        # ... many more categories
    }
    
    # Comprehensive PostgreSQL error handling
    DB_ERROR_MESSAGES = {
        '23505': 'A record with this data already exists.',
        '23503': 'The referenced record does not exist.',
        # ... many more error codes
    }
    
    @classmethod
    def handle_exception(cls, exception, operation, include_traceback=False):
        # Categorizes exceptions and returns appropriate HTTP errors
        
    @classmethod
    def route_error_handler(cls, router):
        # Wraps all routes in a router with error handling
```

### 2. services/core/error_service.py (DUPLICATE)
Simpler implementation with:
- Method-based error responses
- Less comprehensive error categorization
- No route decorators
- Basic logging

```python
class ErrorService:
    def validation_error(self, message, details=None):
        # Create validation error response
        
    def not_found(self, message, resource_type=None, resource_id=None):
        # Create not found error response
        
    # Several more error methods
```

### 3. services/new/error_service.py (DUPLICATE)
Nearly identical to error/error_service.py but with some minor differences.

## AUTH SERVICES

The codebase has two competing authentication implementations:

### 1. services/core/auth_service.py (RECOMMENDED)
- Uses JWT for authentication
- Handles token validation and user extraction
- Has fallback mechanisms for development
- Used by multiple routers (modernized_sitemap.py, google_maps_api.py)

```python
class AuthService:
    def validate_tenant_id(self, tenant_id, current_user=None):
        # Tenant ID validation
        
    async def get_user_from_token(self, token):
        # Extract user information from JWT token
        
    # Dependency for current user
    async def get_current_user(request, credentials):
        # Extracts authenticated user from request
```

### 2. auth/jwt_auth.py (DUPLICATE)
- Similar JWT authentication
- References RBAC even though it's been removed
- Different function signatures and patterns
- Older implementation with tenant isolation remnants

```python
def create_access_token(data, expires_delta=None):
    # Create JWT token
    
def decode_token(token):
    # Decode and validate JWT token
    
async def get_current_user(token):
    # Get current user from token
    
def check_permissions(required_permissions):
    # Permission checking (simplified)
```

## DATABASE HANDLING

### 1. services/core/db_service.py (RECOMMENDED)
- Comprehensive database service with transaction awareness
- Handles SQLAlchemy session management
- Used by sitemap_analyzer.py

### 2. db/session.py
- Session factory and management
- Works with services/core/db_service.py

### 3. db/engine.py
- SQLAlchemy engine configuration
- Connection pooling settings
- Used by session.py

## SITEMAP PROCESSING

### 1. services/sitemap/processing_service.py (RECOMMENDED)
- Current sitemap processing implementation
- Used by modernized_sitemap.py
- Follows transaction patterns
- Clear separation of concerns

### 2. services/sitemap_service.py (DUPLICATE)
- Older implementation of sitemap services
- Some functionality overlaps with processing_service.py

## ROUTER USAGE PATTERNS

Each router file shows inconsistent service import and usage patterns:

### modernized_sitemap.py
```python
from ..services.core.auth_service import get_current_user
from ..services.sitemap.processing_service import sitemap_processing_service
```

### sitemap_analyzer.py
```python
from ..auth.jwt_auth import get_current_user
from ..services.error.error_service import ErrorService
```

### google_maps_api.py
```python
from ..services.core.auth_service import get_current_user
from ..services.places.places_service import PlacesService
```

## TRANSACTION PATTERNS

Routers should own transactions, but patterns are inconsistent:

### Correct Pattern (in modernized_sitemap.py)
```python
@router.post("/scan", response_model=SitemapScrapingResponse)
async def scan_domain(
    request: SitemapScrapingRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    async with session.begin():
        # Call service within transaction
        result = await sitemap_processing_service.process_domain(
            session=session,
            url=request.url,
            user_id=current_user["id"]
        )
    
    # Return response after transaction is committed
    return result
```

### Incorrect Pattern (found in some routers)
Services creating their own transactions or nested transactions.
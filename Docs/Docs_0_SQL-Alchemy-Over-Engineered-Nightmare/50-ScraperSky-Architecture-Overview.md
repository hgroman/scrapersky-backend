# ScraperSky Architecture Overview

This document provides a comprehensive overview of the modernized ScraperSky application architecture. It describes the architectural patterns, component relationships, and request flow through the system.

## Architectural Principles

ScraperSky follows a layered architecture with clean separation of concerns:

1. **Single Responsibility**: Each component has one clear responsibility
2. **Dependency Inversion**: Higher-level modules do not depend on lower-level modules directly
3. **Interface Segregation**: Components interact through well-defined interfaces
4. **Dependency Injection**: Dependencies are provided to components rather than created within them

## System Architecture

### Layered Architecture

ScraperSky uses a four-layer architecture:

```
┌───────────────────────────────────────┐
│            Presentation Layer         │
│   (API Routers, Request/Response)     │
├───────────────────────────────────────┤
│            Business Logic Layer       │
│              (Services)               │
├───────────────────────────────────────┤
│              Data Access Layer        │
│           (SQLAlchemy Models)         │
├───────────────────────────────────────┤
│              Database Layer           │
│            (PostgreSQL)               │
└───────────────────────────────────────┘
```

### Component Relationships

```
┌────────────────┐     ┌────────────────┐
│   API Client   │     │  Fast API App  │
└───────┬────────┘     └───────┬────────┘
        │                      │
        │                      ▼
┌───────▼──────────────────────────────┐
│           Router Factory             │
├─────────┬─────────────────┬──────────┤
│  V1     │        │        │   V2     │
│ Router  │        │        │  Router  │
└─────────┘        │        └──────────┘
                   ▼
┌──────────────────────────────────────┐
│              Services                │
├──────────────────────────────────────┤
│  Validation  │  Core    │  Domain    │
│  Service     │ Services │  Services  │
└──────────────┴──────────┴────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         SQLAlchemy Models            │
└──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             Database                 │
└──────────────────────────────────────┘
```

## Key Components

### 1. Router Factory

The Router Factory is responsible for creating standardized FastAPI router instances. It ensures consistent:

- Error handling
- Response formatting
- Authentication/authorization
- Parameter validation

```python
# Router Factory Example
def create_router(prefix: str, tags: List[str], dependencies: List[Depends] = None) -> APIRouter:
    """Create a standardized router with consistent configuration"""
    return APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies or [],
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
        }
    )
```

### 2. API Versioning Factory

The API Versioning Factory creates dual-versioned routers that maintain backward compatibility:

- v1 routes use legacy naming
- v2 routes use truthful naming
- Both point to the same implementation

```python
# API Versioning Factory Example
routers = ApiVersionFactory.create_versioned_routers(
    v1_prefix="/api/v1/places",
    v2_prefix="/api/v2/google_maps_api",
    tags=["google_maps_api"]
)
```

### 3. Services

Services encapsulate business logic and orchestrate operations:

- Core Services: Cross-cutting concerns (auth, validation)
- Domain Services: Domain-specific logic (sitemap, places)
- Integration Services: External system integrations

```python
# Service Example
class SitemapService:
    async def analyze_sitemap(self, url: str, tenant_id: str) -> Dict[str, Any]:
        # Business logic implementation
        # Calls to data access layer
        return result
```

### 4. SQLAlchemy Models

Models represent database entities and handle data access:

- Entity definitions
- Relationships
- Query methods
- Data validation

```python
# SQLAlchemy Model Example
class SitemapFile(Base, BaseModel):
    __tablename__ = "sitemap_files"

    domain_id = Column(String, nullable=False, index=True)
    url = Column(Text, nullable=False)
    # ...other fields...

    @classmethod
    async def get_by_id(cls, session, sitemap_id, tenant_id):
        # Data access implementation
```

## Request Flow

### Example: Analyzing a Sitemap

```
1. Client Request → /api/v2/sitemap_analyzer/scan
   ↓
2. FastAPI App routes to appropriate endpoint
   ↓
3. Router factory-created route handler:
   - Validates request parameters
   - Extracts tenant_id from authentication
   - Gets DB session
   ↓
4. Router calls SitemapService.analyze_sitemap()
   ↓
5. SitemapService:
   - Performs business logic
   - Uses ValidationService to validate inputs
   - Calls SitemapFile/SitemapUrl model methods for data access
   ↓
6. SQLAlchemy Models interact with database
   ↓
7. Service processes results
   ↓
8. Router formats and returns response
```

## Dual Versioning Example

The same endpoint functionality can be accessed through two different URL paths:

```
Legacy route:   /api/v1/sitemap/analyzer/scan
                       │
                       │  Same implementation
                       ▼
Truthful route: /api/v2/sitemap_analyzer/scan
```

Both routes:

- Call the same service methods
- Return the same data structures
- Have identical behavior
- But v1 routes include deprecation headers

## Dependency Injection

ScraperSky uses FastAPI's dependency injection system to provide:

- Database sessions
- Authentication context
- Tenant information
- Configuration

```python
@router.get("/items")
async def get_items(
    session: AsyncSession = Depends(get_session_dependency),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
):
    # Implementation using injected dependencies
```

## Conclusion

The modernized ScraperSky architecture:

- Follows industry best practices for API design
- Maintains clean separation of concerns
- Provides backward compatibility with legacy clients
- Ensures consistency through standardized patterns
- Improves maintainability through modular components

This architecture allows for:

- Easier testing through component isolation
- Better error handling through standardized approaches
- Simplified maintenance by localizing changes
- Clear migration path for evolving the API

The Router Factory and API Versioning patterns ensure that these benefits are consistently applied across all endpoints in the system.

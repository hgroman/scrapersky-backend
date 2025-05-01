# Router Factory Implementation

## Overview

The Router Factory is a design pattern implementation that standardizes how FastAPI routes are created and managed throughout the ScraperSky application. This pattern promotes consistent route creation, reduces code duplication, and simplifies testing.

## Purpose

- **Standardization**: Enforces a consistent pattern for creating API endpoints
- **Modularity**: Separates route definition from business logic
- **Maintainability**: Makes route changes easier to implement across the application
- **Testability**: Simplifies testing of route handlers and service methods independently

## Implementation Details

The `RouterFactory` class is designed to create standardized GET and POST routes with consistent:

- Error handling
- Request validation
- Authentication and authorization
- Response formatting
- Background task processing

### Core Components

#### Router Factory

Located at `src/factories/router_factory.py`, the `RouterFactory` class provides methods for creating standardized routes:

```python
class RouterFactory:
    """
    Factory for creating standardized FastAPI routes with consistent error handling,
    request validation, authentication, and response formatting.
    """

    @staticmethod
    def create_get_route(
        router: APIRouter,
        path: str,
        response_model: Type[Any],
        service_method: Callable[..., Awaitable[Any]],
        description: str = "",
        dependencies: List[Depends] = None,
        auth_required: bool = True,
        status_code: int = 200,
        query_params: Dict[str, Type[Any]] = None,
        path_params: Dict[str, Type[Any]] = None,
    ) -> None:
        # Implementation for GET routes

    @staticmethod
    def create_post_route(
        router: APIRouter,
        path: str,
        response_model: Type[Any],
        service_method: Callable[..., Awaitable[Any]],
        request_model: Type[BaseModel] = None,
        description: str = "",
        dependencies: List[Depends] = None,
        auth_required: bool = True,
        status_code: int = 200,
        background_tasks_param: bool = False,
        query_params: Dict[str, Type[Any]] = None,
        path_params: Dict[str, Type[Any]] = None,
    ) -> None:
        # Implementation for POST routes
```

## Usage Examples

### Creating a Basic GET Route

```python
from fastapi import APIRouter
from src.factories.router_factory import RouterFactory
from src.models.response_models import UserResponse
from src.services.user_service import user_service

router = APIRouter()

# Create a GET route for retrieving a user by ID
RouterFactory.create_get_route(
    router=router,
    path="/users/{user_id}",
    response_model=UserResponse,
    service_method=user_service.get_user_by_id,
    description="Get a user by ID",
    path_params={"user_id": int},
)
```

### Creating a POST Route with Background Tasks

```python
from fastapi import APIRouter
from src.factories.router_factory import RouterFactory
from src.models.request_models import CreateUserRequest
from src.models.response_models import UserResponse
from src.services.user_service import user_service

router = APIRouter()

# Create a POST route for creating a user with background tasks
RouterFactory.create_post_route(
    router=router,
    path="/users",
    request_model=CreateUserRequest,
    response_model=UserResponse,
    service_method=user_service.create_user,
    description="Create a new user",
    background_tasks_param=True,
)
```

## OpenAPI Schema Generation

### Challenges with Router Factory and OpenAPI

When implementing the Router Factory pattern, we encountered challenges with FastAPI's automatic OpenAPI schema generation. The factory pattern, while providing excellent standardization and code reuse, can interfere with FastAPI's introspection-based schema generation.

### Solution: Custom OpenAPI Schema

To address these challenges, we implemented a custom OpenAPI schema generation approach:

1. **Static Schema Definition**: We created a static OpenAPI schema in `src/main.py` that defines all endpoints, their parameters, and response models.

2. **Custom Route for Schema**: We added a custom route at `/openapi.json` that serves this static schema.

3. **Custom Swagger UI and ReDoc**: We implemented custom routes for Swagger UI and ReDoc that use our static schema.

4. **OpenAPICompatibleRoute Class**: We created a custom route class that preserves parameter information for OpenAPI schema generation while providing standardized error handling.

```python
class OpenAPICompatibleRoute(APIRoute):
    """
    Custom API route that preserves parameter information for OpenAPI schema generation
    while providing standardized error handling.
    """
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request):
            try:
                return await original_route_handler(request)
            except Exception as e:
                # Use error service to handle exceptions
                error_response = error_service.handle_exception(e, error_code="route_handler_error")
                return error_response

        return custom_route_handler
```

### Documentation Endpoints

The API now provides three documentation endpoints:

1. **Swagger UI**: `/api/docs` - Interactive API documentation with the ability to test endpoints
2. **ReDoc**: `/api/redoc` - Alternative API documentation with a different UI
3. **Custom Documentation**: `/api/documentation` - Comprehensive documentation page with detailed information about the API

## Best Practices

When using the Router Factory, follow these best practices:

1. **Use Service Methods**: Always use service methods for business logic, not direct database operations.

2. **Consistent Error Handling**: Let the factory handle errors consistently rather than implementing custom error handling in each endpoint.

3. **Proper Type Annotations**: Use proper type annotations for request models, response models, and service methods to ensure type safety.

4. **Documentation**: Always provide descriptions for routes and parameters to ensure good API documentation.

5. **Authentication**: Use the `requires_auth` parameter to control authentication requirements for each endpoint.

6. **Background Tasks**: Use the `background_tasks_param` parameter for long-running operations that should be processed asynchronously.

7. **Path and Query Parameters**: Use the `path_params` and `query_params` parameters to extract parameters from the request URL.

## Conclusion

The Router Factory pattern provides a powerful way to standardize route creation in FastAPI applications. By using this pattern, we ensure consistent error handling, request validation, and response formatting across all endpoints.

With the addition of custom OpenAPI schema generation, we've addressed the challenges of combining the factory pattern with FastAPI's automatic documentation generation, providing comprehensive and accurate API documentation.

The pattern has been successfully applied to several key routers in the ScraperSky application, including the Google Maps API and Sitemap Analyzer, and will be extended to all remaining routers as part of the modernization project.

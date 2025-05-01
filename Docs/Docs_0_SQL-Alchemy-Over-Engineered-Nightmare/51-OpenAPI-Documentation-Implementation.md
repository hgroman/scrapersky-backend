# OpenAPI Documentation Implementation

This document details the implementation of custom OpenAPI schema generation in the ScraperSky application, addressing challenges with FastAPI's automatic schema generation when using the Router Factory pattern.

## Overview

FastAPI typically generates OpenAPI documentation automatically based on route definitions, type hints, and docstrings. However, when using custom routing patterns like our Router Factory, this automatic generation can break due to:

1. Custom route handlers that don't follow FastAPI's expected patterns
2. Dynamic route creation that FastAPI's introspection can't properly analyze
3. Missing type information when using factory patterns

To address these challenges, we implemented a custom approach to OpenAPI schema generation that provides comprehensive and accurate API documentation while maintaining the benefits of our Router Factory pattern.

## Implementation Approach

Our solution consists of several components:

1. **Static OpenAPI Schema Definition**: A manually defined OpenAPI schema in `src/main.py`
2. **Custom OpenAPI Route**: A dedicated route at `/openapi.json` that serves the static schema
3. **Documentation UI Routes**: Custom routes for Swagger UI, ReDoc, and a detailed documentation page
4. **OpenAPI Compatible Route Class**: A custom route class that preserves parameter information

### Static OpenAPI Schema

The static schema is defined in `src/main.py` and includes:

- API metadata (title, version, description)
- Authentication schemes
- Tags for grouping endpoints
- Path definitions for all endpoints
- Request and response schemas

Example schema definition:

```python
openapi_schema = {
    "openapi": "3.0.2",
    "info": {
        "title": "ScraperSky API",
        "description": "API for ScraperSky web scraping and analysis",
        "version": "2.0.0"
    },
    "paths": {
        "/api/v2/google_maps_api/search": {
            "get": {
                "tags": ["Google Maps API"],
                "summary": "Search for places using Google Maps API",
                "description": "Search for places using Google Maps API with pagination",
                "operationId": "search_places_v2",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"}
                    },
                    # Additional parameters...
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PlaceSearchResponse"}
                            }
                        }
                    },
                    # Error responses...
                }
            }
        },
        # Additional paths...
    },
    "components": {
        "schemas": {
            "PlaceSearchResponse": {
                "type": "object",
                "properties": {
                    "places": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Place"}
                    },
                    # Additional properties...
                }
            },
            # Additional schemas...
        },
        "securitySchemes": {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
    }
}
```

### Custom OpenAPI Route

A dedicated route at `/openapi.json` serves the static schema:

```python
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return JSONResponse(content=openapi_schema)
```

### Documentation UI Routes

Custom routes for Swagger UI, ReDoc, and a detailed documentation page:

```python
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="ScraperSky API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="ScraperSky API Documentation",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/api/documentation", include_in_schema=False)
async def custom_api_documentation():
    # Custom HTML documentation page with detailed information
    return HTMLResponse(content=html_content)
```

### OpenAPI Compatible Route Class

To ensure compatibility with FastAPI's OpenAPI schema generation, we created a custom route class in `src/factories/openapi_compatible_route.py`:

```python
class OpenAPICompatibleRoute(APIRoute):
    """
    Custom route class that ensures compatibility with FastAPI's OpenAPI schema generation.
    This class handles potential issues with status_code and other parameters that might
    cause problems during schema generation.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                # Handle exceptions using the error service
                return error_service.handle_exception(exc)

        return custom_route_handler

    def get_openapi_path(self, path: str) -> Dict[str, Any]:
        """Override to handle potential status_code issues during OpenAPI generation."""
        try:
            return super().get_openapi_path(path)
        except UnboundLocalError as e:
            if "status_code" in str(e):
                # Handle status_code error by providing a default path
                return self._generate_basic_openapi_path(path)
            raise

    def _generate_basic_openapi_path(self, path: str) -> Dict[str, Any]:
        """Generate a basic OpenAPI path when the standard generation fails."""
        method = self.methods[0].lower()
        return {
            method: {
                "summary": self.summary or "",
                "description": self.description or "",
                "responses": {"200": {"description": "Successful response"}},
                "tags": self.tags or []
            }
        }
```

## Documentation Endpoints

The ScraperSky API provides three documentation endpoints:

1. **Swagger UI**: `/docs` - Interactive API documentation with a modern UI
2. **ReDoc**: `/redoc` - Alternative documentation format with a different layout
3. **Custom Documentation**: `/api/documentation` - Detailed HTML documentation page

## Adding New Endpoints to the Schema

When adding a new endpoint to the API, follow these steps to include it in the documentation:

1. **Add the Path Definition**: Add a new path entry to the `paths` section of the OpenAPI schema in `src/main.py`
2. **Define Request Parameters**: Include all query, path, and body parameters with appropriate schemas
3. **Define Response Schemas**: Document all possible response types, including error responses
4. **Add Component Schemas**: If the endpoint uses custom request or response models, add them to the `components.schemas` section
5. **Include Authentication Requirements**: Specify any authentication requirements using security schemes

Example of adding a new endpoint:

```python
# Add to the paths section
"/api/v2/sitemap_analyzer/analyze": {
    "post": {
        "tags": ["Sitemap Analyzer"],
        "summary": "Analyze a sitemap",
        "description": "Analyze a sitemap URL and extract all URLs",
        "operationId": "analyze_sitemap_v2",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SitemapAnalyzeRequest"}
                }
            }
        },
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/SitemapAnalyzeResponse"}
                    }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            }
        },
        "security": [{"APIKeyHeader": []}]
    }
}

# Add to the components.schemas section
"SitemapAnalyzeRequest": {
    "type": "object",
    "required": ["url"],
    "properties": {
        "url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the sitemap to analyze"
        }
    }
},
"SitemapAnalyzeResponse": {
    "type": "object",
    "properties": {
        "urls": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of URLs found in the sitemap"
        },
        "count": {
            "type": "integer",
            "description": "Number of URLs found"
        }
    }
}
```

## Best Practices

When documenting API endpoints, follow these best practices:

1. **Be Comprehensive**: Include all parameters, responses, and error cases
2. **Use Clear Descriptions**: Provide clear and concise descriptions for all components
3. **Include Examples**: Add examples for request and response bodies
4. **Document Authentication**: Clearly specify authentication requirements
5. **Group Related Endpoints**: Use tags to group related endpoints
6. **Maintain Consistency**: Use consistent naming and formatting across all documentation
7. **Update Documentation with Code**: Keep the documentation in sync with code changes

## Conclusion

Our custom OpenAPI schema generation approach provides comprehensive and accurate API documentation while maintaining the benefits of our Router Factory pattern. By manually defining the schema and providing custom routes for documentation, we ensure that users have access to detailed information about all API endpoints, regardless of how they are implemented internally.

The three documentation endpoints (Swagger UI, ReDoc, and custom documentation) provide different ways to explore and understand the API, catering to different user preferences and needs.

As the API evolves, it is important to keep the documentation up to date by adding new endpoints to the schema and updating existing documentation as needed.

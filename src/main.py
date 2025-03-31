"""
Main FastAPI Application

This module is the entry point for the FastAPI application and handles
the setup of all routes, middleware, and extensions.
"""
import os
import logging
import inspect
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Route
from typing import Any, Dict, Coroutine, List
from contextlib import asynccontextmanager  # Add this import

# Import routers
from .routers import (
    # RBAC routers removed
    google_maps_router,
    modernized_sitemap_router,
    batch_page_scraper_router,
    modernized_page_scraper_router,
    dev_tools_router,
    db_portal_router,
    profile_router
)

from .routers.sqlalchemy import routers as sqlalchemy_routers  # Import SQLAlchemy routers
from .scraper.metadata_extractor import session_manager
from .session.async_session import get_session
from .health.db_health import check_database_connection
from .services.domain_scheduler import setup_domain_scheduler, shutdown_domain_scheduler  # Import the domain scheduler functions

# Standard FastAPI error handling is used instead of custom ErrorService
# from .services.core.error_service import ErrorService

# TENANT ISOLATION COMPLETELY REMOVED
# All tenant isolation code has been removed from the entire application
# Do not re-add any tenant isolation or tenant middleware

# Configure logging with maximum verbosity
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Replace the deprecated event handlers with the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    This replaces the deprecated @app.on_event handlers.
    """
    # Startup logic
    logger.info("Starting up the ScraperSky API")

    # Start the domain processing scheduler
    scheduler = setup_domain_scheduler()
    logger.info("Domain processing scheduler started")

    yield  # This is where FastAPI runs and serves requests

    # Shutdown logic
    await session_manager.close()
    shutdown_domain_scheduler()
    logger.info("Domain processing scheduler shut down")

# Update the FastAPI app initialization to use the lifespan context manager
app = FastAPI(
    title="ScraperSky API",
    description="API for ScraperSky web scraping and data management",
    version="3.0.0",
    debug=True,  # Enable debug mode
    docs_url="/docs",  # Standard docs URL
    redoc_url="/redoc",  # Standard redoc URL
    openapi_url="/openapi.json",  # Standard OpenAPI schema URL
    lifespan=lifespan  # Use the lifespan context manager
)

# TENANT ISOLATION COMPLETELY REMOVED
# Any code for tenant isolation, tenant middleware, RBAC, or feature flags
# has been completely removed from the application.
#
# DO NOT ADD TENANT MIDDLEWARE HERE UNDER ANY CIRCUMSTANCES

# Configure FastAPI for automatic OpenAPI schema generation
# Use FastAPI's native OpenAPI schema generation instead of static schema

# Set up Swagger UI and ReDoc
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_redoc_html,
)

# Explicitly expose OpenAPI schema (this ensures it's always available)
from fastapi.openapi.utils import get_openapi

@app.get("/api/schema.json", include_in_schema=False)
async def get_api_schema():
    """
    Expose the OpenAPI schema directly - never protected by auth.
    """
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return schema

# Custom Swagger and ReDoc routes
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI route using our guaranteed schema endpoint.
    """
    return get_swagger_ui_html(
        openapi_url="/api/schema.json",  # Use our custom schema endpoint
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/api/redoc", include_in_schema=False)
async def redoc_html():
    """
    Custom ReDoc route using our guaranteed schema endpoint.
    """
    return get_redoc_html(
        openapi_url="/api/schema.json",  # Use our custom schema endpoint
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/api/documentation", include_in_schema=False)
async def documentation_page():
    """
    Custom documentation page with detailed information about the API.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ScraperSky API Documentation</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                padding-top: 20px;
            }
            .container { max-width: 1200px; }
            h1 { color: #2c3e50; margin-bottom: 30px; }
            h2 {
                color: #3498db;
                margin-top: 40px;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            h3 { color: #2980b9; margin-top: 25px; }
            pre {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            code { color: #e83e8c; }
            .endpoint {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #3498db;
            }
            .get { border-left-color: #28a745; }
            .post { border-left-color: #007bff; }
            .put { border-left-color: #fd7e14; }
            .delete { border-left-color: #dc3545; }
            .method {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                margin-right: 10px;
            }
            .get-method { background-color: #28a745; }
            .post-method { background-color: #007bff; }
            .put-method { background-color: #fd7e14; }
            .delete-method { background-color: #dc3545; }
            .path { font-family: monospace; font-size: 1.1em; }
            .card { margin-bottom: 20px; }
            .nav-pills .nav-link.active {
                background-color: #3498db;
            }
            .nav-pills .nav-link {
                color: #3498db;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ScraperSky API Documentation</h1>

            <div class="alert alert-info">
                <strong>Note:</strong> This documentation provides a comprehensive overview of the ScraperSky API.
                For interactive API testing, visit the <a href="/api/docs" class="alert-link">Swagger UI</a> or
                <a href="/api/redoc" class="alert-link">ReDoc</a> documentation.
            </div>

            <ul class="nav nav-pills mb-4" id="pills-tab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="pills-overview-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-overview" type="button" role="tab"
                            aria-controls="pills-overview" aria-selected="true">Overview</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="pills-auth-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-auth" type="button" role="tab"
                            aria-controls="pills-auth" aria-selected="false">Authentication</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="pills-endpoints-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-endpoints" type="button" role="tab"
                            aria-controls="pills-endpoints" aria-selected="false">Endpoints</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="pills-models-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-models" type="button" role="tab"
                            aria-controls="pills-models" aria-selected="false">Data Models</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="pills-versioning-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-versioning" type="button" role="tab"
                            aria-controls="pills-versioning" aria-selected="false">API Versioning</button>
                </li>
            </ul>

            <div class="tab-content" id="pills-tabContent">
                <!-- Overview Tab -->
                <div class="tab-pane fade show active" id="pills-overview" role="tabpanel" aria-labelledby="pills-overview-tab">
                    <h2>API Overview</h2>
                    <p>
                        The ScraperSky API provides a comprehensive set of endpoints for web scraping and analysis.
                        It allows you to search for businesses using Google Maps API, analyze website sitemaps,
                        extract email addresses from websites, and more.
                    </p>

                    <h3>Key Features</h3>
                    <ul>
                        <li><strong>Google Maps API Integration</strong> - Search for businesses by type and location</li>
                        <li><strong>Sitemap Analysis</strong> - Discover and analyze XML sitemaps for any domain</li>
                        <li><strong>Batch Processing</strong> - Process multiple domains concurrently</li>
                        <li><strong>Email Scanning</strong> - Extract email addresses from websites</li>
                        <li><strong>Asynchronous Processing</strong> - Long-running tasks are processed asynchronously with status tracking</li>
                    </ul>

                    <h3>API Versioning</h3>
                    <p>
                        The API supports two versions:
                    </p>
                    <ul>
                        <li><strong>v1</strong> - Legacy endpoints with historical naming conventions</li>
                        <li><strong>v2</strong> - Modern endpoints with truthful naming that accurately reflects functionality</li>
                    </ul>
                    <p>
                        We recommend using v2 endpoints for all new integrations as they provide more consistent
                        naming and improved error handling.
                    </p>
                </div>

                <!-- Authentication Tab -->
                <div class="tab-pane fade" id="pills-auth" role="tabpanel" aria-labelledby="pills-auth-tab">
                    <h2>Authentication</h2>
                    <p>
                        Most endpoints in the ScraperSky API require authentication. The API uses JWT (JSON Web Tokens)
                        for authentication.
                    </p>

                    <h3>Obtaining a Token</h3>
                    <p>
                        To obtain a JWT token, send a POST request to the <code>/auth/token</code> endpoint with your
                        credentials:
                    </p>
                    <pre><code>POST /auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}</code></pre>

                    <p>
                        The response will include an access token:
                    </p>
                    <pre><code>{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}</code></pre>

                    <h3>Using the Token</h3>
                    <p>
                        Include the token in the Authorization header of your requests:
                    </p>
                    <pre><code>GET /api/v3/google-maps-api/search/places
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</code></pre>

                    <h3>Token Expiration</h3>
                    <p>
                        Tokens expire after the time specified in the <code>expires_in</code> field (in seconds).
                        When a token expires, you'll need to request a new one.
                    </p>

                    <div class="alert alert-warning">
                        <strong>Note:</strong> In development mode, some endpoints may work without authentication.
                        In production, all protected endpoints require a valid token.
                    </div>
                </div>

                <!-- Endpoints Tab -->
                <div class="tab-pane fade" id="pills-endpoints" role="tabpanel" aria-labelledby="pills-endpoints-tab">
                    <h2>API Endpoints</h2>

                    <h3>Health Checks</h3>
                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/health</span>
                        <p>Check if the API is running properly.</p>
                    </div>

                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/health/database</span>
                        <p>Check if the database connection is working properly.</p>
                    </div>

                    <h3>Google Maps API</h3>
                    <div class="endpoint post">
                        <span class="method post-method">POST</span>
                        <span class="path">/api/v3/google-maps-api/search/places</span>
                        <p>Search for places using Google Places API.</p>
                    </div>

                    <h3>Sitemap Analysis</h3>
                    <div class="endpoint post">
                        <span class="method post-method">POST</span>
                        <span class="path">/sitemap/scan</span>
                        <p>Scan a domain and extract metadata from its sitemap.</p>
                    </div>

                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/sitemap/status/{job_id}</span>
                        <p>Get the status of a sitemap scanning job.</p>
                    </div>

                    <div class="endpoint post">
                        <span class="method post-method">POST</span>
                        <span class="path">/api/v3/sitemap/scan</span>
                        <p>Analyze sitemap for a single domain.</p>
                    </div>

                    <div class="endpoint post">
                        <span class="method post-method">POST</span>
                        <span class="path">/api/v3/batch_page_scraper/scan</span>
                        <p>Analyze sitemaps for multiple domains in batch.</p>
                    </div>

                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/api/v3/batch_page_scraper/status/{job_id}</span>
                        <p>Get the status of a batch job.</p>
                    </div>

                    <h3>Email Scanner</h3>
                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/email-scanner/domains</span>
                        <p>Get a list of domains available for email scanning.</p>
                    </div>

                    <div class="endpoint post">
                        <span class="method post-method">POST</span>
                        <span class="path">/email-scanner/scan/{domain_id}</span>
                        <p>Initiate scanning for email addresses on a given domain.</p>
                    </div>

                    <div class="endpoint get">
                        <span class="method get-method">GET</span>
                        <span class="path">/email-scanner/scan/{domain_id}/status</span>
                        <p>Get the status of an email scanning job.</p>
                    </div>
                </div>

                <!-- Data Models Tab -->
                <div class="tab-pane fade" id="pills-models" role="tabpanel" aria-labelledby="pills-models-tab">
                    <h2>Data Models</h2>

                    <h3>Google Maps API</h3>
                    <div class="card">
                        <div class="card-header">
                            <strong>PlacesSearchRequest</strong>
                        </div>
                        <div class="card-body">
                            <pre><code>{
  "business_type": "string",  // Type of business to search for
  "location": "string",       // Location to search in (city, address, etc.)
  "radius_km": 10,            // Search radius in kilometers
  "tenant_id": "string"       // Optional tenant ID for multi-tenant setups
}</code></pre>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <strong>PlacesSearchResponse</strong>
                        </div>
                        <div class="card-body">
                            <pre><code>{
  "job_id": "string",         // Unique ID for the search job
  "status": "string",         // Status of the job (started, running, completed, failed)
  "status_url": "string"      // URL to check the job status
}</code></pre>
                        </div>
                    </div>

                    <h3>Sitemap Analyzer</h3>
                    <div class="card">
                        <div class="card-header">
                            <strong>SitemapAnalyzerRequest</strong>
                        </div>
                        <div class="card-body">
                            <pre><code>{
  "domain": "string",         // Domain to analyze
  "tenant_id": "string",      // Optional tenant ID
  "user_id": "string",        // Optional user ID
  "user_name": "string",      // Optional user name
  "follow_robots_txt": true,  // Whether to follow robots.txt rules
  "extract_urls": true        // Whether to extract URLs from sitemaps
}</code></pre>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <strong>SitemapAnalyzerResponse</strong>
                        </div>
                        <div class="card-body">
                            <pre><code>{
  "job_id": "string",         // Unique ID for the analysis job
  "status": "string",         // Status of the job
  "status_url": "string",     // URL to check the job status
  "domain": "string"          // Domain being analyzed
}</code></pre>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <strong>SitemapAnalyzerBatchRequest</strong>
                        </div>
                        <div class="card-body">
                            <pre><code>{
  "domains": [                // Array of domains to analyze
    "string"
  ],
  "tenant_id": "string",      // Optional tenant ID
  "user_id": "string",        // Optional user ID
  "user_name": "string",      // Optional user name
  "follow_robots_txt": true,  // Whether to follow robots.txt rules
  "max_concurrent_jobs": 5    // Maximum number of concurrent jobs
}</code></pre>
                        </div>
                    </div>
                </div>

                <!-- API Versioning Tab -->
                <div class="tab-pane fade" id="pills-versioning" role="tabpanel" aria-labelledby="pills-versioning-tab">
                    <h2>API Versioning</h2>
                    <p>
                        The ScraperSky API uses v3 endpoints with consistent naming conventions that accurately reflect their functionality.
                    </p>

                    <h3>Versioning Strategy</h3>
                    <p>
                        Our versioning strategy follows these principles:
                    </p>
                    <ul>
                        <li><strong>Truthful Naming</strong> - v3 endpoints are named according to what they actually do</li>
                        <li><strong>Consistent Format</strong> - All endpoints follow the pattern /api/v3/{resource}</li>
                        <li><strong>RESTful Design</strong> - Resources are named appropriately with clear actions</li>
                    </ul>

                    <h3>Key Endpoints</h3>
                    <p>
                        The following table shows the key endpoints available in the API:
                    </p>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Endpoint</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><code>/api/v3/google-maps-api/search/places</code></td>
                                <td>Search for places using Google Places API</td>
                            </tr>
                            <tr>
                                <td><code>/api/v3/sitemap/scan</code></td>
                                <td>Analyze sitemap for a single domain</td>
                            </tr>
                            <tr>
                                <td><code>/api/v3/batch_page_scraper/scan</code></td>
                                <td>Analyze multiple domains in batch</td>
                            </tr>
                            <tr>
                                <td><code>/api/v3/sitemap/status/{job_id}</code></td>
                                <td>Get the status of a sitemap analysis job</td>
                            </tr>
                            <tr>
                                <td><code>/api/v3/db-portal/tables</code></td>
                                <td>List all database tables</td>
                            </tr>
                            <tr>
                                <td><code>/api/v3/profile/me</code></td>
                                <td>Get current user profile information</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Import settings from central config
from src.config.settings import settings

# CORS Configuration
# Use settings-based CORS configuration
cors_origins = settings.get_cors_origins()

# In development, allow all origins if not specified
if settings.environment == "development" and cors_origins == ["*"]:
    cors_methods = ["*"]
    cors_headers = ["*"]
else:
    # In production, use specific values
    cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers = ["Authorization", "Content-Type", "X-Tenant-Id"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

# AUTH MIDDLEWARE REMOVED: Now using dependencies.py for authentication
# See src/auth/dependencies.py for the new dependency-based authentication
logger.info("Using dependency-based authentication instead of middleware")

# Explicitly log that docs and OpenAPI paths should be public
logger.info("OpenAPI documentation paths should be publicly accessible:")
for path in ["/docs", "/redoc", "/openapi.json", "/api/docs", "/api/redoc"]:
    logger.info(f"  - {path}")

# Debugging middleware to trace all requests (only in development)
if settings.environment.lower() in ["development", "dev"]:
    @app.middleware("http")
    async def debug_request_middleware(request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url.path}")
        try:
            response = await call_next(request)
            logger.debug(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise

# Add SQLAlchemy routers with FastAPI's built-in error handling
for router in sqlalchemy_routers:
    # Use FastAPI's built-in error handling
    app.include_router(router)
    logger.info(f"Added SQLAlchemy router: {router}")

# Add routers with explicit logging and standardized error handling
logger.info("RBAC routers have been removed from the application")

# Legacy router completely removed - using /api/v3/localminer-discoveryscan instead

logger.info("Adding Google Maps router...")
app.include_router(google_maps_router)

logger.info("Adding Sitemap router...")
app.include_router(modernized_sitemap_router)

logger.info("Adding Modernized Page Scraper router...")
app.include_router(modernized_page_scraper_router)

logger.info("Adding Batch Page Scraper router...")
app.include_router(batch_page_scraper_router)

logger.info("Adding Dev Tools router...")
app.include_router(dev_tools_router)

logger.info("Adding DB Portal router...")
app.include_router(db_portal_router)

logger.info("Adding Profile router...")
app.include_router(profile_router)

# Log all registered routes
logger.info("All registered routes:")
for route in app.routes:
    logger.info(f"Route: {str(route)}")

# Serve static files with absolute path
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add custom middleware for cache control
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    """Add cache-control header to responses."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

# Root routes
@app.get("/")
async def root():
    """Redirect root to the main dashboard."""
    return RedirectResponse(url="/static/index.html")

@app.get("/docs")
async def docs_redirect():
    """Redirect /docs to /api/docs for convenience."""
    return RedirectResponse(url="/api/docs")

# Utility view routes
@app.get("/sitemap-viewer")
async def sitemap_viewer():
    """Redirect to sitemap viewer frontend."""
    return RedirectResponse(url="/static/contentmap.html")

@app.get("/static/sitemap-analyzer.html")
async def legacy_sitemap_analyzer():
    """Redirect from old sitemap-analyzer.html path to new contentmap.html path."""
    return RedirectResponse(url="/static/contentmap.html")

@app.get("/sitemap-data-viewer")
async def sitemap_data_viewer():
    """Redirect to sitemap data viewer frontend."""
    return RedirectResponse(url="/static/sitemap-data-viewer.html")

@app.get("/email-scanner")
async def email_scanner_view():
    """Redirect to email scanner frontend."""
    return RedirectResponse(url="/static/email-scanner.html")

# RBAC route removed
# @app.get("/rbac-management")
# async def rbac_management_view():
#     """Redirect to RBAC management frontend."""
#     return RedirectResponse(url="/static/rbac-management.html")

@app.get("/batch-test")
async def batch_test_view():
    """Redirect to batch test frontend."""
    return RedirectResponse(url="/static/batch-test.html")

@app.get("/db-portal")
async def db_portal_view():
    """Redirect to database portal frontend."""
    return RedirectResponse(url="/static/db-portal.html")

@app.get("/api-test")
async def api_test_view():
    """Redirect to API test frontend."""
    return RedirectResponse(url="/static/api-test.html")

# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}

@app.get("/health/database", tags=["health"])
async def database_health():
    """Check database connection health."""
    async with get_session() as session:
        is_healthy = await check_database_connection(session)
        if not is_healthy:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Database connection failed"}
            )
        return {"status": "ok", "message": "Database connection successful"}

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": str(exc.detail), "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors with standardized format."""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errors, "error": True}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with standardized format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with standardized format."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "error_detail": str(exc),
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

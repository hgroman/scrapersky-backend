"""
Main FastAPI Application

This module is the entry point for the FastAPI application and handles
the setup of all routes, middleware, and extensions.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
from pydantic import Field
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- Logging Setup (Must be first) ---
from .config.logging_config import setup_logging

setup_logging()

from src.services.sitemap_import_scheduler import setup_sitemap_import_scheduler
from .health.db_health import check_database_connection
from .routers.batch_page_scraper import router as batch_page_scraper_api_router
from .routers.batch_sitemap import router as batch_sitemap_api_router
from .routers.db_portal import router as db_portal_api_router
from .routers.dev_tools import router as dev_tools_api_router
from .routers.domains import router as domains_api_router
from .routers.email_scanner import router as email_scanner_api_router
from .routers.google_maps_api import router as google_maps_api_router
from .routers.local_businesses import router as local_businesses_api_router
from .routers.modernized_page_scraper import (
    router as modernized_page_scraper_api_router,
)
from .routers.modernized_sitemap import router as modernized_sitemap_api_router
from .routers.places_staging import router as places_staging_api_router
from .routers.profile import router as profile_api_router
from .routers.sitemap_files import router as sitemap_files_router
from .routers.sqlalchemy import routers as sqlalchemy_routers
from .scheduler_instance import shutdown_scheduler, start_scheduler
from .scraper.metadata_extractor import session_manager
from .services.domain_scheduler import setup_domain_scheduler
from .services.domain_sitemap_submission_scheduler import (
    setup_domain_sitemap_submission_scheduler,
)
from .services.sitemap_scheduler import setup_sitemap_scheduler
from .session.async_session import get_session

# Create logger for this module
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with debug mode control."""

    debug_mode: bool = Field(default=False, alias="FASTAPI_DEBUG_MODE")

    model_config = {"env_file": ".env"}


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.

    Initializes shared resources like the scheduler and adds jobs.
    Handles shutdown of shared resources.
    """
    logger.info("Starting up the ScraperSky API - Lifespan Start")

    # Start the shared scheduler instance
    start_scheduler()

    # Add jobs from each module to the shared scheduler
    logger.info("Adding jobs to the shared scheduler...")
    try:
        setup_domain_scheduler()
    except Exception as e:
        logger.error(f"Failed to setup Domain scheduler job: {e}", exc_info=True)

    try:
        setup_sitemap_scheduler()
    except Exception as e:
        logger.error(f"Failed to setup Sitemap scheduler job: {e}", exc_info=True)

    try:
        setup_domain_sitemap_submission_scheduler()
    except Exception as e:
        logger.error(
            f"Failed to setup Domain Sitemap Submission scheduler job: {e}",
            exc_info=True,
        )

    # Setup for the renamed Sitemap Import scheduler
    try:
        setup_sitemap_import_scheduler()
    except Exception as e:
        logger.error(
            f"Failed to setup Sitemap Import scheduler job: {e}", exc_info=True
        )

    logger.info("Finished adding jobs to shared scheduler.")

    yield  # Application runs here

    logger.info("Shutting down the ScraperSky API - Lifespan End")

    # Shutdown the shared scheduler instance
    shutdown_scheduler()

    # Close session manager
    try:
        await session_manager.close()
        logger.info("Session manager closed")
    except Exception as e:
        logger.error(f"Error closing session manager: {e}", exc_info=True)


# Initialize FastAPI app
app = FastAPI(
    title="ScraperSky API",
    description="API for ScraperSky web scraping and data management",
    version="3.0.0",
    debug=settings.debug_mode,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# TENANT ISOLATION COMPLETELY REMOVED
# Any code for tenant isolation, tenant middleware, RBAC, or feature flags
# has been completely removed from the application.
#
# DO NOT ADD TENANT MIDDLEWARE HERE UNDER ANY CIRCUMSTANCES

# Conditionally enable debug tools
if settings.debug_mode:
    from src.debug_tools import enable_debug

    enable_debug(app)
    logger.info("Debug mode enabled - debug tools loaded")
else:
    logger.info("Debug mode disabled - production mode")


@app.get("/api/schema.json", include_in_schema=False)
async def get_api_schema():
    """Expose the OpenAPI schema directly - never protected by auth."""
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return schema


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI route using our guaranteed schema endpoint."""
    return get_swagger_ui_html(
        openapi_url="/api/schema.json",
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/api/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc route using our guaranteed schema endpoint."""
    return get_redoc_html(
        openapi_url="/api/schema.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/api/documentation", include_in_schema=False)
def documentation():
    """Serve the API documentation from static file."""
    return FileResponse(
        Path(__file__).parent.parent / "static/docs.html", media_type="text/html"
    )


# Import settings from central config
from src.config.settings import settings as app_settings

# CORS Configuration
cors_origins = app_settings.get_cors_origins()

# In development, allow all origins if not specified
if app_settings.environment == "development" and cors_origins == ["*"]:
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
logger.info("Using dependency-based authentication instead of middleware")

# Explicitly log that docs and OpenAPI paths should be public
logger.info("OpenAPI documentation paths should be publicly accessible:")
for path in ["/docs", "/redoc", "/openapi.json", "/api/docs", "/api/redoc"]:
    logger.info(f"  - {path}")


# Cache-Control middleware
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


# Add SQLAlchemy routers with FastAPI's built-in error handling
for router in sqlalchemy_routers:
    app.include_router(router)
    logger.info(f"Added SQLAlchemy router: {router}")

# Add routers with explicit logging and standardized error handling
logger.info("RBAC routers have been removed from the application")
logger.info("Including API routers...")

# --- IMPORTANT ROUTER PREFIX CONVENTION --- #
# When including routers below:
# 1. If the router DEFINES its own FULL prefix (including '/api/v3'),
#    include it WITHOUT adding the prefix here.
# 2. If the router only defines the RESOURCE-SPECIFIC part of its prefix
#    (e.g., '/sitemap'), then include it WITH `prefix="/api/v3"` here.
# *** Failure to follow this causes 404 errors. Double-check prefixes! ***
# --- END IMPORTANT ROUTER PREFIX CONVENTION --- #

# Include all routers
app.include_router(google_maps_api_router)
app.include_router(modernized_sitemap_api_router)
app.include_router(
    batch_page_scraper_api_router, prefix="/api/v3", tags=["Batch Page Scraper"]
)
app.include_router(
    modernized_page_scraper_api_router, prefix="/api/v3", tags=["Page Scraper"]
)
app.include_router(dev_tools_api_router)
app.include_router(db_portal_api_router, prefix="/api/v3", tags=["DB Portal"])
app.include_router(profile_api_router, prefix="/api/v3", tags=["Profile"])
app.include_router(batch_sitemap_api_router, prefix="/api/v3", tags=["Batch Sitemap"])
app.include_router(places_staging_api_router, prefix="/api/v3")
app.include_router(local_businesses_api_router)
app.include_router(domains_api_router, tags=["Domains"])
app.include_router(sitemap_files_router)
app.include_router(email_scanner_api_router, prefix="/api/v3", tags=["Email Scanner"])

logger.info("API routers included.")

# Serve static files with absolute path
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"
)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


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
                content={"status": "error", "message": "Database connection failed"},
            )
        return {"status": "ok", "message": "Database connection successful"}


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": str(exc.detail),
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors with standardized format."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            }
        )

    return JSONResponse(status_code=422, content={"detail": errors, "error": True})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with standardized format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail, "status_code": exc.status_code},
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
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=app_settings.host, port=app_settings.port)

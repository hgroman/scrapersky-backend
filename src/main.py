import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict
from src.routers import routers  # Import routers list from __init__.py
from .scraper.metadata_extractor import session_manager

# Configure logging with environment-based levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

app = FastAPI(
    title="ScraperSky",
    description="A FastAPI-based web scraping service for extracting website metadata.",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

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

# Dynamically include all routers from the routers list
for router in routers:
    app.include_router(router)

# Serve static files with absolute path
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def root():
    """Redirect root to static index page."""
    return RedirectResponse(url="/static/index.html")

@app.get("/sitemap-viewer")
async def sitemap_viewer():
    """Serve the sitemap viewer interface."""
    return RedirectResponse(url="/static/sitemap-viewer.html")

@app.get("/sitemap-data-viewer")
async def sitemap_data_viewer():
    """Serve the sitemap data viewer interface."""
    return RedirectResponse(url="/static/sitemap-data-viewer.html")

@app.get("/email-scanner")
async def email_scanner_view():
    """Serve the email scanner interface."""
    return RedirectResponse(url="/static/email-scanner.html")

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with clean error responses."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Customize HTTP exception responses."""
    # Log all 4xx and 5xx errors
    if exc.status_code >= 400:
        logging.error(f"HTTP {exc.status_code} error: {exc.detail} - URL: {request.url}")
    
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions to prevent server crashes."""
    logging.error(f"Unhandled exception: {str(exc)}")
    import traceback
    logging.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.environment != "production" else "An unexpected error occurred"
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await session_manager.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

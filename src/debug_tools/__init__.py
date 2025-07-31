"""
Debug Tools Package

This package contains all debugging utilities that can be conditionally enabled
in the FastAPI application. The tools are designed to help with development
and troubleshooting without impacting production performance.

Usage:
    Set environment variable FASTAPI_DEBUG_MODE=true to enable debug tools.

    from src.debug_tools import enable_debug
    enable_debug(app)
"""

from .middleware import debug_request_middleware
from .routes import router as debug_router
from .runtime_tracer import start_tracing, stop_tracing


def enable_debug(app):
    """
    Inject all debug utilities into a FastAPI app.

    This function adds:
    - Runtime file tracing (startup/shutdown hooks)
    - Debug request middleware for logging
    - Debug routes for introspection

    Args:
        app: FastAPI application instance
    """

    # Add lifespan hooks for tracing
    @app.on_event("startup")
    async def _start_tracing():
        start_tracing()

    @app.on_event("shutdown")
    async def _stop_tracing():
        stop_tracing()

    # Add middleware and routes
    app.middleware("http")(debug_request_middleware)
    app.include_router(debug_router, prefix="/debug", tags=["debug"])

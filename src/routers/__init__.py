"""
Routers Package

This package contains all the FastAPI routers for the application.
"""

from src.config.settings import settings

from .wf7_page_batch_scraper_router import router as batch_page_scraper_router
from .wf5_sitemap_batch_router import router as batch_sitemap_router
from .db_portal import router as db_portal_router
from .google_maps_api import router as google_maps_router
from .wf7_page_modernized_scraper_router import router as modernized_page_scraper_router
from .wf5_sitemap_modernized_router import router as modernized_sitemap_router
from .places_staging import router as places_staging_router
from .profile import router as profile_router

# Export all routers
__all__ = [
    "google_maps_router",
    "modernized_sitemap_router",
    "batch_page_scraper_router",
    "modernized_page_scraper_router",
    "db_portal_router",
    "profile_router",
    "batch_sitemap_router",
    "places_staging_router",
]

# Conditionally import and export dev_tools_router for development environments
if settings.environment.lower() in {"development", "dev"}:
    from .dev_tools import router as dev_tools_router

    __all__.append("dev_tools_router")

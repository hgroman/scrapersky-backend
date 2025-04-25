"""
Routers Package

This package contains all the FastAPI routers for the application.
"""

from .batch_page_scraper import router as batch_page_scraper_router
from .batch_sitemap import router as batch_sitemap_router
from .db_portal import router as db_portal_router
from .dev_tools import router as dev_tools_router
from .google_maps_api import router as google_maps_router
from .modernized_page_scraper import router as modernized_page_scraper_router
from .modernized_sitemap import router as modernized_sitemap_router
from .places_staging import router as places_staging_router
from .profile import router as profile_router

# Export all routers
__all__ = [
    'google_maps_router',
    'modernized_sitemap_router',
    'batch_page_scraper_router',
    'modernized_page_scraper_router',
    'dev_tools_router',
    'db_portal_router',
    'profile_router',
    'batch_sitemap_router',
    'places_staging_router'
]

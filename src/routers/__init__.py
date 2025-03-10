from .chat import router as chat_router
from .email_scanner import router as email_scanner_router
from .sitemap_scraper import router as sitemap_router
from .places_scraper import router as places_router

routers = [
    chat_router,
    email_scanner_router,
    sitemap_router,
    places_router,
]

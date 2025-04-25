"""
API Package

This package contains all API-related modules for the application.
"""

# Import routers to make them available when importing this package
from .router.places_router import router as places_router

# Export available routers
__all__ = [
    'places_router',
]

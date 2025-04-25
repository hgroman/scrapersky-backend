"""
SQLAlchemy-based Routers

This module exports all SQLAlchemy-based routers for FastAPI integration.
These routers are designed to work with the new SQLAlchemy data access layer.
"""

from fastapi import APIRouter

# Create a simple test router for now
test_router = APIRouter(prefix="/api/v3/sqlalchemy-test", tags=["sqlalchemy-test"])

@test_router.get("/health")
async def health_check():
    """Simple health check endpoint to verify SQLAlchemy router is working."""
    return {"status": "ok", "message": "SQLAlchemy router is functioning properly"}

# List of all SQLAlchemy routers - will be extended as we migrate more routers
routers = [
    test_router,
]

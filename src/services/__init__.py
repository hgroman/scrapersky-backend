"""
Services Package

Provides service modules for database and business logic operations.
Note: RBAC-related services have been removed to simplify the authentication system.
"""

from .job_service import job_service  # Modernized SQLAlchemy job_service

# RBAC services removed
# from .rbac.rbac_service import RbacService
# from .rbac.feature_service import FeatureService

# Create service instances for dependency injection
# rbac_service = RbacService()
# feature_service = FeatureService()

# Service instances - ensure these align with active services
#rbac_service = RBACService()  # Removed
# domain_service = DomainService() # Removed

# Explicitly define what gets exported
__all__ = [
    "job_service",
    # Add other active service exports here if any
]

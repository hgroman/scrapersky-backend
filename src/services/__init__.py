"""
Services Package

Provides service modules for database and business logic operations.
Note: RBAC-related services have been removed to simplify the authentication system.
"""

from .domain_service import domain_service
from .job_service import job_service  # Modernized SQLAlchemy job_service

# RBAC services removed
# from .rbac.rbac_service import RbacService
# from .rbac.feature_service import FeatureService

# Create service instances for dependency injection
# rbac_service = RbacService()
# feature_service = FeatureService()

__all__ = [
    'domain_service',
    'job_service',
    # 'rbac_service',      # Removed
    # 'feature_service'    # Removed
]

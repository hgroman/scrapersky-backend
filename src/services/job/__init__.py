"""
Job Services Package (Legacy)

This package has been deprecated in favor of the modernized job_service
at the root level of the services directory.
"""

# Import modernized job_service from parent directory
from ..job_service import job_service

__all__ = ["job_service"]

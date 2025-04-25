"""Utility functions for the scraper module."""

import uuid
from datetime import datetime
from typing import Any, Dict


def generate_job_id(prefix: str = "scan") -> str:
    """
    Generate a unique job ID using UUID.

    Args:
        prefix: Optional prefix for the job ID

    Returns:
        A unique job ID string
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def validate_url(url: str) -> bool:
    """
    Validate that a URL starts with http:// or https://.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    return str(url).startswith(("http://", "https://"))


def format_batch_job_status(
    job_id: str, total: int, processed: int, errors: int
) -> Dict[str, Any]:
    """
    Format batch job status information.

    Args:
        job_id: Unique job identifier
        total: Total number of URLs to process
        processed: Number of URLs processed
        errors: Number of errors encountered

    Returns:
        Dictionary containing job status information
    """
    return {
        "job_id": job_id,
        "total_urls": total,
        "processed_urls": processed,
        "error_count": errors,
        "status": "running" if processed < total else "completed",
        "last_updated": datetime.utcnow().isoformat(),
    }

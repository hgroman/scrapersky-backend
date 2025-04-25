"""
Shared types and interfaces for batch processing.

This module contains shared types, interfaces, and constants used across
batch processing and page scraping services to avoid circular dependencies.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union
from uuid import UUID


class BatchOptions(TypedDict, total=False):
    """Options for batch processing."""
    max_concurrent: int
    max_pages: int  # Added to support page limit per domain
    test_mode: bool
    timeout: int
    retry_count: int

class BatchStatus(TypedDict):
    """Status information for a batch job."""
    batch_id: str
    status: str
    total_domains: int
    completed_domains: int
    failed_domains: int
    progress: float
    created_at: datetime
    updated_at: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    processing_time: Optional[float]
    domain_statuses: Dict[str, Any]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]

class DomainResult(TypedDict):
    """Result of processing a single domain."""
    domain: str
    status: str
    error: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    pages_found: Optional[int]
    pages_processed: Optional[int]

class BatchResult(TypedDict):
    """Result of batch processing operation."""
    batch_id: str
    status: str
    total_domains: int
    completed_domains: int
    failed_domains: int
    results: List[DomainResult]
    error: Optional[str]

# Constants
BATCH_STATUS_PENDING = "pending"
BATCH_STATUS_PROCESSING = "processing"
BATCH_STATUS_COMPLETED = "completed"
BATCH_STATUS_FAILED = "failed"
BATCH_STATUS_CANCELLED = "cancelled"
BATCH_STATUS_ERROR = "error"
BATCH_STATUS_UNKNOWN = "unknown"

DOMAIN_STATUS_PENDING = "pending"
DOMAIN_STATUS_PROCESSING = "processing"
DOMAIN_STATUS_COMPLETED = "completed"
DOMAIN_STATUS_FAILED = "failed"

# Type aliases for better readability
DomainList = List[str]
BatchId = Union[str, UUID]
UserId = Union[str, UUID]
Session = Any  # SQLAlchemy AsyncSession

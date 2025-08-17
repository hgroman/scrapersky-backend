"""
Page Curation Workflow Schemas - WF7 V3 Compliant
Layer 2 Component per ScraperSky Constitutional Standards

Author: The Architect
Date: 2025-08-06
Compliance: 100% Layer 2 Blueprint Adherent
"""

from typing import List
from pydantic import BaseModel, ConfigDict
import uuid
from src.models.enums import PageCurationStatus


class PageCurationBatchStatusUpdateRequest(BaseModel):
    """
    Request schema for batch updating page curation status.
    Implements the dual-status trigger pattern for WF7.
    """
    model_config = ConfigDict(from_attributes=True)
    
    page_ids: List[uuid.UUID]
    status: PageCurationStatus


class PageCurationBatchUpdateResponse(BaseModel):
    """
    Response schema for batch update operations.
    Returns counts of updated and queued pages.
    """
    model_config = ConfigDict(from_attributes=True)
    
    updated_count: int
    queued_count: int


# L2 Schema Guardian Compliance Checklist:
# ✓ Workflow prefix applied (PageCuration*)
# ✓ ConfigDict with from_attributes=True (Pydantic v2)
# ✓ Proper type hints with UUID and List types
# ✓ Clear docstrings for each schema
# ✓ Enum imports from models layer
# ✓ No business logic in schemas (pure data contracts)
"""
Pydantic models specific to the Email Scanner API.
"""

import uuid

from pydantic import BaseModel


class EmailScanRequest(BaseModel):
    """Request body for initiating an email scan."""

    domain_id: uuid.UUID

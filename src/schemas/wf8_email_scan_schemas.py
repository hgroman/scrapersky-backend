# WF8 – The Connector
# Purpose: Contact validation, enrichment, and delivery to external systems
# NEVER put page-scraping logic here – that belongs in WF7

"""
Pydantic models specific to the Email Scanner API.
"""

import uuid

from pydantic import BaseModel


class EmailScanRequest(BaseModel):
    """Request body for initiating an email scan."""

    domain_id: uuid.UUID

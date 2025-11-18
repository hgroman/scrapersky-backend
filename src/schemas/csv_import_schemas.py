"""
Pydantic schemas for CSV import endpoints.

Supports bulk import of domains, pages, and sitemaps via CSV upload.
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class CSVRowResult(BaseModel):
    """Result for a single CSV row."""

    row_number: int
    value: str
    status: str  # "success" or "error"
    id: Optional[UUID] = None
    error: Optional[str] = None


class CSVImportResponse(BaseModel):
    """Response schema for CSV import endpoints."""

    total_rows: int
    successful: int
    failed: int
    skipped: int  # Duplicates or empty rows
    results: List[CSVRowResult]

    class Config:
        json_schema_extra = {
            "example": {
                "total_rows": 100,
                "successful": 95,
                "failed": 3,
                "skipped": 2,
                "results": [
                    {
                        "row_number": 1,
                        "value": "example.com",
                        "status": "success",
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "error": None,
                    },
                    {
                        "row_number": 2,
                        "value": "bad!domain",
                        "status": "error",
                        "id": None,
                        "error": "Invalid domain format: bad!domain",
                    },
                ],
            }
        }

"""
Contact Validation Router (WO-018)

FastAPI endpoints for DeBounce email validation operations.

These endpoints allow the frontend to:
1. Queue contacts for validation
2. Check validation status (for real-time updates)
3. View validation statistics
4. Filter contacts by validation results
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_auth import get_current_user
from src.db.session import get_db_session
from src.schemas.contact_validation_schemas import (
    ValidateContactsRequest,
    ValidateContactsResponse,
    ValidateAllContactsRequest,
    ValidateAllContactsResponse,
    ValidationStatusResponse,
    ValidationSummaryResponse,
)
from src.services.email_validation.validation_api_service import ValidationAPIService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v3/contacts",
    tags=["Email Validation"],
    responses={404: {"description": "Not found"}},
)


@router.post("/validate", response_model=ValidateContactsResponse)
async def validate_contacts(
    request: ValidateContactsRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Queue selected contacts for DeBounce email validation.

    **What This Endpoint Does:**
    - Validates contact IDs and checks they exist
    - Updates `debounce_processing_status` to "Queued"
    - Returns counts of queued/already_processing/already_validated contacts
    - Skips contacts already in "Processing" or "Complete" status

    **What Happens Next:**
    - The background scheduler (runs every 5 minutes) will pick up queued contacts
    - Scheduler calls DeBounce API to validate emails
    - Database is updated with validation results
    - Valid emails are auto-queued for CRM sync (if configured)

    **For Real-time Updates:**
    - Use `GET /api/v3/contacts/validation-status` to poll for results
    - Poll every 2-3 seconds until all contacts are "Complete" or "Error"

    **Request Body:**
    - `contact_ids`: List of 1-100 contact UUIDs to validate

    **Response:**
    - `queued_count`: Number of contacts successfully queued
    - `already_processing`: Number of contacts currently being validated
    - `already_validated`: Number of contacts already validated
    - `invalid_ids`: Contact IDs that were not found

    **Example:**
    ```json
    {
      "contact_ids": [
        "8ef2449f-d3eb-4831-b85e-a385332b6475",
        "f1bae019-a2a4-4caf-aeb6-43c1d8464fd6"
      ]
    }
    ```
    """
    logger.info(
        f"🔍 Validation request from user: {current_user.get('email', 'unknown')} "
        f"for {len(request.contact_ids)} contacts"
    )

    service = ValidationAPIService(session)
    result = await service.queue_contacts_for_validation(request.contact_ids)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/validate/all", response_model=ValidateAllContactsResponse)
async def validate_all_contacts(
    request: ValidateAllContactsRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Queue all contacts matching filters for DeBounce email validation.

    **What This Endpoint Does:**
    - Applies filters to find matching contacts
    - Queues up to `max_contacts` for validation (default 100, max 500)
    - Returns counts of queued/already_processing/already_validated contacts

    **Safety Features:**
    - Maximum 500 contacts per request (prevents accidental mass queueing)
    - Skips contacts already being processed or validated

    **Available Filters:**
    - `curation_status`: Filter by contact curation status (e.g., "Skipped")
    - `validation_status`: Filter by validation result (valid/invalid/disposable/pending/not_validated)
    - `search_email`: Search by email address
    - `search_name`: Search by first or last name
    - `domain_id`: Filter by domain UUID
    - `page_id`: Filter by page UUID

    **Response:**
    - `queued_count`: Number of contacts queued
    - `total_matched`: Total contacts matching filters
    - `filters_applied`: Filters that were used

    **Example:**
    ```json
    {
      "filters": {
        "curation_status": "Skipped",
        "validation_status": "not_validated"
      },
      "max_contacts": 100
    }
    ```
    """
    logger.info(
        f"🔍 Bulk validation request from user: {current_user.get('email', 'unknown')} "
        f"with filters: {request.filters.model_dump(exclude_none=True)}"
    )

    service = ValidationAPIService(session)
    result = await service.queue_filtered_contacts_for_validation(
        request.filters, request.max_contacts
    )

    return result


@router.get("/validation-status", response_model=ValidationStatusResponse)
async def get_validation_status(
    contact_ids: str = Query(
        ...,
        description="Comma-separated list of contact UUIDs",
        example="8ef2449f-d3eb-4831-b85e-a385332b6475,f1bae019-a2a4-4caf-aeb6-43c1d8464fd6",
    ),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get current validation status for specific contacts.

    **What This Endpoint Does:**
    - Returns real-time validation status for requested contacts
    - Includes validation results if validation is complete
    - Includes error messages if validation failed

    **Use Case:**
    - Poll this endpoint every 2-3 seconds after triggering validation
    - Check if all contacts have `processing_status` = "Complete" or "Error"
    - Display results to user once complete

    **Query Parameter:**
    - `contact_ids`: Comma-separated list of contact UUIDs

    **Response Fields:**
    - `validation_status`: "Queued", "Complete", "Error"
    - `processing_status`: "Queued", "Processing", "Complete", "Error"
    - `result`: "valid", "invalid", "disposable", "catch-all", "unknown" (null if pending)
    - `score`: Validation confidence score 0-100 (null if pending)
    - `reason`: Explanation of validation result
    - `validated_at`: Timestamp when validation completed

    **Example Response:**
    ```json
    {
      "success": true,
      "contacts": [
        {
          "id": "8ef2449f-d3eb-4831-b85e-a385332b6475",
          "email": "test@example.com",
          "validation_status": "Complete",
          "processing_status": "Complete",
          "result": "valid",
          "score": 100,
          "reason": "Deliverable"
        }
      ]
    }
    ```

    **Polling Pattern:**
    ```javascript
    const pollValidationStatus = async (contactIds) => {
      const interval = setInterval(async () => {
        const response = await fetch(
          `/api/v3/contacts/validation-status?contact_ids=${contactIds.join(',')}`
        );
        const data = await response.json();

        // Check if all contacts are complete
        const allComplete = data.contacts.every(
          c => c.processing_status === 'Complete' || c.processing_status === 'Error'
        );

        if (allComplete) {
          clearInterval(interval);
          // Update UI with final results
        }
      }, 2000); // Poll every 2 seconds
    };
    ```
    """
    # Parse comma-separated contact IDs
    ids = [id.strip() for id in contact_ids.split(",") if id.strip()]

    if not ids:
        raise HTTPException(
            status_code=400,
            detail="At least one contact ID is required",
        )

    logger.debug(
        f"📊 Validation status check for {len(ids)} contacts by user: {current_user.get('email', 'unknown')}"
    )

    service = ValidationAPIService(session)
    result = await service.get_validation_status(ids)

    return result


@router.get("/validation-summary", response_model=ValidationSummaryResponse)
async def get_validation_summary(
    domain_id: str = Query(
        None, description="Optional: Filter by domain UUID", example=None
    ),
    page_id: str = Query(None, description="Optional: Filter by page UUID", example=None),
    curation_status: str = Query(
        None,
        description="Optional: Filter by curation status",
        example="Skipped",
    ),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get aggregate validation statistics.

    **What This Endpoint Does:**
    - Calculates validation statistics across all contacts (or filtered subset)
    - Returns counts and percentages for dashboard display
    - Supports optional filtering by domain, page, or curation status

    **Use Case:**
    - Display validation summary on Contact Launchpad
    - Show "X of Y contacts validated (Z% valid)"
    - Track validation progress over time

    **Optional Filters:**
    - `domain_id`: Filter by specific domain UUID
    - `page_id`: Filter by specific page UUID
    - `curation_status`: Filter by curation status (e.g., "Skipped")

    **Response Fields:**
    - `total_contacts`: Total number of contacts (after filters)
    - `validated.total`: Number of validated contacts
    - `validated.valid`: Number of valid emails
    - `validated.invalid`: Number of invalid emails
    - `validated.disposable`: Number of disposable emails
    - `not_validated`: Number of contacts not yet validated
    - `pending_validation`: Number of contacts queued or processing
    - `validation_rate`: Percentage of contacts validated
    - `valid_rate`: Percentage of validated contacts that are valid

    **Example Response:**
    ```json
    {
      "success": true,
      "summary": {
        "total_contacts": 500,
        "validated": {
          "total": 300,
          "valid": 250,
          "invalid": 30,
          "disposable": 15,
          "catch_all": 5,
          "unknown": 0
        },
        "not_validated": 150,
        "pending_validation": 50,
        "validation_rate": 60.0,
        "valid_rate": 83.3
      }
    }
    ```
    """
    logger.debug(
        f"📊 Validation summary request from user: {current_user.get('email', 'unknown')}"
    )

    service = ValidationAPIService(session)
    result = await service.get_validation_summary(
        domain_id=domain_id,
        page_id=page_id,
        curation_status=curation_status,
    )

    return result

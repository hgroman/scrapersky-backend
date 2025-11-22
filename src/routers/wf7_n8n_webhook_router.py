"""
WO-021: n8n Enrichment Return Pipeline - Webhook Router

WHAT THIS DOES:
Receives enriched contact data from n8n workflows and stores it in 15 database fields.
This is the INBOUND half of the two-way n8n integration (WO-020 = outbound, WO-021 = inbound).

ENDPOINT:
POST /api/v3/webhooks/n8n/enrichment-complete

AUTHENTICATION:
Bearer token via Authorization header (N8N_WEBHOOK_SECRET environment variable)

THE 15 ENRICHMENT FIELDS (Contact Model):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status Tracking (5 fields):
  • enrichment_status (varchar 20) - pending/complete/partial/failed
  • enrichment_started_at (timestamp) - When enrichment began
  • enrichment_completed_at (timestamp) - When enrichment finished
  • enrichment_error (text) - Error message if failed
  • last_enrichment_id (varchar 255) - For idempotency (prevents duplicates)

Enriched Data (7 fields - JSONB for flexibility):
  • enriched_phone (varchar 50) - Additional phone number
  • enriched_address (jsonb) - {street, city, state, zip, country}
  • enriched_social_profiles (jsonb) - {linkedin, twitter, facebook, etc}
  • enriched_company (jsonb) - {name, website, industry, size}
  • enriched_additional_emails (jsonb array) - ["email1", "email2"]
  • enrichment_confidence_score (int 0-100) - Quality score
  • enrichment_sources (jsonb array) - ["clearbit", "hunter.io"]

Metadata (3 fields):
  • enrichment_duration_seconds (float) - Processing time
  • enrichment_api_calls (int) - Number of API calls made
  • enrichment_cost_estimate (float) - Estimated cost in dollars
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IDEMPOTENCY:
Safe to retry - same enrichment_id won't duplicate data.
Uses last_enrichment_id field to track processed enrichments.

WORKFLOW:
1. n8n workflow completes enrichment
2. n8n POSTs to this endpoint with enriched data
3. Service validates contact exists
4. Service checks idempotency (skip if already processed)
5. Service updates all 15 fields
6. Service returns success with list of updated fields

EXAMPLE REQUEST:
{
  "contact_id": "uuid",
  "enrichment_id": "unique-run-id-123",
  "status": "complete",
  "timestamp": "2025-11-19T10:00:00Z",
  "enriched_data": {
    "phone": "+1-555-0123",
    "address": {"street": "123 Main", "city": "SF", "state": "CA"},
    "social_profiles": {"linkedin": "https://..."},
    "company": {"name": "Acme", "website": "https://acme.com"},
    "additional_emails": ["work@example.com"],
    "confidence_score": 85,
    "sources": ["clearbit", "hunter.io"]
  },
  "metadata": {
    "duration_seconds": 12.5,
    "api_calls": 3,
    "cost_estimate": 0.15
  }
}

RELATED FILES:
• Service: src/services/crm/n8n_enrichment_service.py
• Schemas: src/schemas/n8n_enrichment_schemas.py
• Model: src/models/WF7_V2_L1_1of1_ContactModel.py (lines 122-142)
• Outbound: src/services/crm/n8n_sync_service.py (WO-020)
• Docs: Documentation/Guides/n8n_enrichment_user_guide.md
• Docs: Documentation/Operations/n8n_enrichment_maintenance.md

MAINTENANCE:
• Check logs: docker logs scraper-sky-backend-scrapersky-1 | grep enrichment
• Verify fields: SELECT enrichment_status, enrichment_completed_at FROM contacts WHERE enrichment_status IS NOT NULL
• Test webhook: curl -X POST {url} -H "Authorization: Bearer {secret}" -d @test_payload.json

IMPLEMENTED: 2025-11-19 (Commit b029792)
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.session import get_db_session
from src.schemas.n8n_enrichment_schemas import (
    EnrichmentCompleteRequest,
    EnrichmentCompleteResponse,
    EnrichmentErrorResponse,
)
from src.services.crm.wf7_n8n_enrichment_service import N8nEnrichmentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v3/webhooks/n8n",
    tags=["n8n Webhooks"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing Bearer token"},
        404: {"description": "Contact not found"},
        422: {"description": "Validation error"},
    },
)


def verify_n8n_webhook_secret(authorization: str = Header(None)) -> str:
    """
    Verify n8n webhook authentication via Bearer token.

    Args:
        authorization: Authorization header value (should be "Bearer {token}")

    Returns:
        The verified token

    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    if not authorization:
        logger.warning("⚠️ n8n webhook request missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    if not authorization.startswith("Bearer "):
        logger.warning(f"⚠️ Invalid Authorization format: {authorization[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be 'Bearer {token}'",
        )

    token = authorization.replace("Bearer ", "")

    if not settings.N8N_WEBHOOK_SECRET:
        logger.error("❌ N8N_WEBHOOK_SECRET not configured in settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook authentication not configured",
        )

    if token != settings.N8N_WEBHOOK_SECRET:
        logger.warning("⚠️ Invalid n8n webhook token received")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token",
        )

    logger.debug("✅ n8n webhook authentication successful")
    return token


@router.post(
    "/enrichment-complete",
    response_model=EnrichmentCompleteResponse,
    summary="Receive enriched contact data from n8n",
    description="""
    **Webhook endpoint for n8n to POST enrichment results.**

    This endpoint receives enriched contact data from n8n workflows and updates
    the contact record with the enrichment results.

    **Authentication:**
    - Requires `Authorization: Bearer {N8N_WEBHOOK_SECRET}` header
    - Token must match server's N8N_WEBHOOK_SECRET environment variable

    **Idempotency:**
    - Safe to retry - same `enrichment_id` won't duplicate data
    - Uses `last_enrichment_id` field to track processed enrichments

    **Status Values:**
    - `complete`: Enrichment fully successful, all data available
    - `partial`: Enrichment partially successful, some data available
    - `failed`: Enrichment failed, no data available

    **Request Body:**
    - `contact_id`: UUID of contact to update (required)
    - `enrichment_id`: Unique ID for this enrichment run (required)
    - `status`: Enrichment status (required)
    - `timestamp`: When enrichment completed (required)
    - `enriched_data`: Enriched contact data (optional, required for complete/partial)
    - `metadata`: Enrichment metadata like duration and cost (optional)

    **Response:**
    - `success`: Boolean indicating success
    - `contact_id`: UUID of updated contact
    - `enrichment_id`: Enrichment run ID
    - `message`: Human-readable message
    - `updated_fields`: List of fields that were updated

    **Error Codes:**
    - `401`: Invalid or missing Bearer token
    - `404`: Contact not found
    - `422`: Validation error (invalid payload)
    - `500`: Internal server error
    """,
)
async def receive_enrichment_data(
    request: EnrichmentCompleteRequest,
    session: AsyncSession = Depends(get_db_session),
    _token: str = Depends(verify_n8n_webhook_secret),
) -> EnrichmentCompleteResponse:
    """
    Receive and process enriched contact data from n8n.

    Args:
        request: Enrichment data payload from n8n
        session: Database session (injected)
        _token: Verified webhook token (injected, validates auth)

    Returns:
        EnrichmentCompleteResponse with success status and updated fields

    Raises:
        HTTPException: If contact not found (404) or processing fails (500)
    """
    logger.info(
        f"🎣 Webhook received: contact_id={request.contact_id}, "
        f"enrichment_id={request.enrichment_id}, status={request.status}"
    )

    try:
        # Initialize service and process enrichment
        service = N8nEnrichmentService()
        result = await service.process_enrichment(request, session)

        logger.info(
            f"✅ Webhook processed successfully: {result['updated_fields']}"
        )

        return EnrichmentCompleteResponse(**result)

    except ValueError as e:
        # Contact not found or validation error
        error_msg = str(e)
        logger.error(f"❌ Validation error: {error_msg}")

        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            )

    except Exception as e:
        # Unexpected error
        logger.error(
            f"❌ Unexpected error processing enrichment: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check for n8n webhook endpoint",
    description="Verify the webhook endpoint is available and authentication is configured.",
)
async def webhook_health_check(
    _token: str = Depends(verify_n8n_webhook_secret),
) -> Dict[str, Any]:
    """
    Health check endpoint for n8n webhook.

    Requires authentication to verify N8N_WEBHOOK_SECRET is correctly configured.

    Returns:
        Health status and configuration info
    """
    return {
        "status": "healthy",
        "webhook_url": "/api/v3/webhooks/n8n/enrichment-complete",
        "authentication": "configured",
        "message": "n8n webhook endpoint is ready to receive enrichment data",
    }

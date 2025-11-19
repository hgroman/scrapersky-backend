"""
WO-021: n8n Webhook Router

FastAPI endpoints for receiving enriched contact data from n8n workflows.

This router provides a secure webhook endpoint that n8n can POST to after
completing contact enrichment. Authentication is via Bearer token.
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
from src.services.crm.n8n_enrichment_service import N8nEnrichmentService

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

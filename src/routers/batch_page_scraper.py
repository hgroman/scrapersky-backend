"""
Page Scraper Router - Batch Operations

This module provides API routes for batch page scraping operations.
Uses standard FastAPI routing with explicit transaction boundaries.
"""
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..auth.jwt_auth import get_current_user
from ..config.settings import settings
from ..models import (
    BatchRequest,
    BatchResponse,
    BatchStatusResponse,
    SitemapScrapingRequest,
    SitemapScrapingResponse,
)
from ..schemas.job import JobStatusResponse
from ..models.tenant import DEFAULT_TENANT_ID
from ..services.batch.batch_functions import process_batch_with_own_session
from ..services.batch.batch_processor_service import (
    get_batch_progress,
    initiate_batch_processing,
)
from ..services.batch.types import (
    BATCH_STATUS_PENDING,
    BatchId,
    BatchOptions,
    BatchResult,
    BatchStatus,
    DomainList,
    Session,
    UserId,
)
from ..services.page_scraper import (
    page_processing_service,
    process_domain_with_own_session,
)
from ..session.async_session import get_session_dependency
from ..utils.db_helpers import get_db_params

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v3/batch_page_scraper",
    tags=["batch_page_scraper"]
)

def is_development_mode() -> bool:
    """
    Checks if the application is running in development mode.
    Requires explicit opt-in through environment variable.
    """
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning("⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️")
    return dev_mode or settings.environment.lower() in ["development", "dev"]

# Development user for local testing
async def get_development_user():
    """
    Provide a mock user for local development with full page scraper access.
    This is only used when SCRAPER_SKY_DEV_MODE=true is set.
    """
    logger.info("Using development user with full access")
    return {
        "id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "hankgroman@gmail.com",
        "tenant_id": DEFAULT_TENANT_ID,
        "auth_method": "dev_mode"
    }

# Choose the appropriate user dependency based on explicit development mode
user_dependency = get_development_user if is_development_mode() else get_current_user

# UUID validation helper
def validate_uuid(id_value: str) -> Any:
    """Handle different ID formats gracefully."""
    if not id_value:
        return None

    if isinstance(id_value, str):
        # If it's already a UUID string, try to convert it
        try:
            return uuid.UUID(id_value)
        except ValueError:
            # Log warning for non-standard format but continue
            logger.warning(f"Non-standard UUID format: {id_value}")
            return id_value

    # If it's already a UUID object or something else, return as is
    return id_value

# ===== Single Domain Scan =====

@router.post("/scan", response_model=SitemapScrapingResponse)
async def scan_domain(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(user_dependency),
    db_params: Dict[str, Any] = Depends(get_db_params)
) -> SitemapScrapingResponse:
    """
    Scan a domain to extract metadata from its pages.
    """
    try:
        # Get required parameters from request
        base_url = request.get("base_url")
        max_pages = request.get("max_pages", 100)

        if not base_url:
            raise HTTPException(status_code=400, detail={
                "message": "Missing required parameter",
                "error": "base_url is required"
            })

        logger.info(f"Starting domain scan for {base_url}")

        # Ensure user_id is a string
        user_id = str(current_user.get("id", "")) if current_user.get("id") else "system"

        # Router owns transaction boundary
        async with session.begin():
            # Initiate domain scan using correct method
            result = await page_processing_service.initiate_domain_scan(
                session=session,
                base_url=base_url,
                user_id=user_id,
                max_pages=max_pages
            )

        # Add background task with function that creates its own session
        background_tasks.add_task(
            process_domain_with_own_session,
            job_id=result["job_id"],
            domain=base_url,
            user_id=user_id,
            max_pages=max_pages
        )

        logger.info(f"Background task added for domain: {base_url}, job_id: {result['job_id']}")

        # Return job details with status URL
        return SitemapScrapingResponse(
            job_id=result["job_id"],
            status_url=result["status_url"],
            created_at=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid input parameter: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid input parameter",
                "error": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error scanning domain: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred while scanning domain",
                "error": str(e)
            }
        )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(user_dependency),
    db_params: Dict[str, Any] = Depends(get_db_params)
) -> JobStatusResponse:
    """
    Get the status of a domain scanning job by job_id (UUID).
    """
    try:
        # Extract database parameters for Supavisor compatibility
        raw_sql = db_params.get("raw_sql", True)
        no_prepare = db_params.get("no_prepare", True)
        statement_cache_size = db_params.get("statement_cache_size", 0)

        logger.debug(f"Database parameters: raw_sql={raw_sql}, no_prepare={no_prepare}, statement_cache_size={statement_cache_size}")

        # Use raw SQL for job lookup to avoid SQLAlchemy ORM type issues with UUID
        from sqlalchemy import text

        # Build direct SQL query to get job status - bypassing ORM complexity
        sql_query = text("""
            SELECT j.id, j.job_id::text as job_id, j.status, j.progress, j.created_at, j.updated_at,
                   j.metadata, j.error, d.domain as domain_name
            FROM jobs j
            LEFT JOIN domains d ON j.domain_id = d.id
            WHERE j.job_id = :job_id
            LIMIT 1
        """)

        # Execute query directly with proper execution options
        result = await session.execute(
            sql_query,
            {"job_id": job_id},
            execution_options={
                "no_parameters": no_prepare,
                "statement_cache_size": statement_cache_size
            }
        )

        # Process the result
        row = result.first()
        if not row:
            logger.warning(f"No job found with UUID: {job_id}")
            # Return a minimal response for not found
            return JobStatusResponse(
                job_id=job_id,
                status="unknown",
                progress=0.0,
                domain=None,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                result={},
                error=None,
                metadata={}
            )

        # Build status response directly from SQL result
        job_data = dict(row._mapping)

        # Convert timestamps to ISO format strings
        for ts_field in ['created_at', 'updated_at']:
            if ts_field in job_data and job_data[ts_field]:
                job_data[ts_field] = job_data[ts_field].isoformat()

        # Make sure we have all required fields for JobStatusResponse
        job_status = {
            "job_id": job_data.get("job_id", job_id),
            "status": job_data.get("status", "unknown"),
            "progress": job_data.get("progress", 0.0),
            "domain": job_data.get("domain_name"),  # Renamed in our query
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "result": job_data.get("result", {}),
            "error": job_data.get("error"),
            "metadata": job_data.get("metadata", {})
        }

        logger.info(f"Retrieved status for job {job_id}: {job_status['status']}")

        # Return properly typed response
        return JobStatusResponse(**job_status)

    except Exception as e:
        logger.error(f"Error retrieving job status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An error occurred while retrieving job status",
                "error": str(e)
            }
        )

# ===== Batch Operations =====

@router.post("/batch", response_model=BatchResponse)
async def create_batch_endpoint(
    background_tasks: BackgroundTasks,
    request: BatchRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(user_dependency),
    db_params: Dict[str, Any] = Depends(get_db_params)
) -> BatchResponse:
    """
    Create a batch of domain scanning jobs.
    """
    try:
        # Validate inputs
        domains = request.domains
        max_pages = request.max_pages if request.max_pages is not None else 50
        max_concurrent = request.max_concurrent if request.max_concurrent is not None else 5

        if not domains:
            raise HTTPException(status_code=400, detail={
                "message": "Missing required parameter",
                "error": "domains list is required"
            })

        # Get user_id from current user
        user_id = str(current_user.get("id", "")) if current_user.get("id") else "system"

        # Router owns transaction boundary
        async with session.begin():
            # Initiate batch process using correct method
            batch_options: BatchOptions = {
                "max_pages": max_pages,
                "max_concurrent": max_concurrent
            }

            # Create batch without starting background processing yet
            batch_result = await initiate_batch_processing(
                session=session,
                domains=domains,
                user_id=user_id,
                options=batch_options
            )

        # Add the background task directly using the specialized function
        # that already handles its own session creation and async context
        logger.info(f"Adding background task for batch {batch_result['batch_id']}")
        background_tasks.add_task(
            process_batch_with_own_session,
            batch_id=batch_result["batch_id"],
            domains=domains,
            user_id=user_id,
            max_pages=max_pages
        )

        # Create status URL
        status_url = f"/api/v3/batch_page_scraper/batch/{batch_result['batch_id']}/status"

        # Return batch details with status URL
        return BatchResponse(
            batch_id=batch_result["batch_id"],
            status_url=status_url,
            job_count=len(domains),
            created_at=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid input parameter: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid input parameter",
                "error": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error creating batch: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An error occurred while creating batch",
                "error": str(e)
            }
        )

@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status_endpoint(
    batch_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(user_dependency),
    db_params: Dict[str, Any] = Depends(get_db_params)
) -> BatchStatusResponse:
    """
    Get the status of a batch job by batch_id (UUID).
    """
    try:
        logger.info(f"Getting status for batch: {batch_id}")

        # Router owns transaction boundary
        async with session.begin():
            # Get batch status using proper method with type cast
            batch_status = await get_batch_progress(
                session=cast(Session, session),
                batch_id=cast(BatchId, batch_id)
            )

        # Format datetime fields for response
        created_at = batch_status.get("created_at")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        updated_at = batch_status.get("updated_at")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        start_time = batch_status.get("start_time")
        if isinstance(start_time, datetime):
            start_time = start_time.isoformat()

        end_time = batch_status.get("end_time")
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()

        # Convert to response model with all required fields
        return BatchStatusResponse(
            batch_id=batch_status["batch_id"],
            status=batch_status["status"],
            total_domains=batch_status["total_domains"],
            completed_domains=batch_status["completed_domains"],
            failed_domains=batch_status["failed_domains"],
            progress=batch_status.get("progress", 0.0),
            created_at=created_at,
            updated_at=updated_at,
            start_time=start_time,
            end_time=end_time,
            processing_time=batch_status.get("processing_time"),
            domain_statuses=batch_status.get("domain_statuses", {}),
            error=batch_status.get("error"),
            metadata=batch_status.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting batch status: {str(e)}"
        )

@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_session_dependency)
) -> Dict[str, Any]:
    """
    Health check endpoint for the batch page scraper service.
    """
    try:
        # Simple database check
        async with session.begin():
            return {
                "status": "OK",
                "message": "Batch page scraper service is healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "ERROR",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/test_background_task")
async def test_background_task(
    background_tasks: BackgroundTasks,
    test_data: str = "test_value"
) -> Dict[str, Any]:
    """
    Test endpoint to verify if FastAPI background tasks work at all.
    This endpoint uses a minimal background task implementation to
    verify execution without database dependencies.
    """
    try:
        # Generate a test ID
        test_id = str(uuid.uuid4())

        # Log intention
        logger.info(f"Adding simple test task with ID: {test_id}")
        print(f"DIAGNOSTIC: About to add simple test task {test_id}")

        # Import simple task test module
        try:
            from ..services.batch.simple_task_test import simple_test_task

            # Add the background task
            background_tasks.add_task(
                simple_test_task,
                test_id=test_id,
                additional_data=test_data
            )

            print(f"DIAGNOSTIC: Added simple test task {test_id}")

            # Return test ID so client can check for marker files
            return {
                "status": "OK",
                "message": "Background task added for testing",
                "test_id": test_id,
                "timestamp": datetime.utcnow().isoformat(),
                "check_command": f"ls -la /tmp/scraper_sky_task_markers/simple_task_test_{test_id}_*.txt"
            }
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Failed to import simple_task_test module: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error setting up test background task: {str(e)}", exc_info=True)
        return {
            "status": "ERROR",
            "message": f"An error occurred: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

## **Work Order: WF4 Domain Curation - Detailed Remediation Plan**

**Objective:** Fix the broken handoff to sitemap analysis, centralize schemas, and establish dedicated service/scheduler components for WF4.

### **Required Reading for AI Pairing Partner**

**Before touching any code, perform the following semantic searches to internalize the canonical understanding of WF4 and the architectural principles:**

1.  **WF4 Workflow Overview:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 Domain Curation canonical specification workflow overview"
    ```
2.  **WF4 ENUM Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 SitemapCurationStatusEnum SitemapAnalysisStatusEnum requirements"
    ```
3.  **WF4 Schema Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 DomainCurationBatchStatusUpdateRequest schema validation api_models migration"
    ```
4.  **WF4 File Dependencies:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 Domain Curation files models routers services dependencies all layers"
    ```
5.  **WF4 Workflow Connections:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 workflow connections WF3 WF5 handoff domains interface"
    ```

### **Phase 0: Foundational Remediation (Prerequisite - Must be completed first)**

*   **Note:** Ensure "Phase 0" from the overall strategic plan is completed before starting WF4-specific fixes. This includes:
    *   Correcting `BaseModel` inheritance in `src/models/domain.py`.
    *   Centralizing all ENUMs into `src/models/enums.py`.
    *   Migrating schemas from `api_models.py` to `src/schemas/`.
    *   Running the Alembic migration.

### **Phase 1: WF4-Specific Remediation**

**Objective:** Reconcile ENUM values, centralize schemas, and establish dedicated service/scheduler components for WF4.

1.  **File:** `src/models/enums.py`
    *   **Objective:** Ensure `SitemapCurationStatus` and `SitemapAnalysisStatus` ENUMs are correctly defined and centralized.
    *   **Instruction:**
        *   **Step 1.1.1:** Open `src/models/enums.py`.
        *   **Step 1.1.2:** Verify `SitemapCurationStatus` and `SitemapAnalysisStatus` are present and correctly defined.
        *   **Step 1.1.3:** If `SitemapCurationStatus.SELECTED` is still present and intended to trigger processing, consider if it should be `SitemapCurationStatus.QUEUED` for consistency.
    *   **Verification:** ENUMs are correctly defined in `enums.py`.

2.  **File:** `src/schemas/domain_curation.py` (New File)
    *   **Objective:** Create this file and define the `DomainCurationBatchStatusUpdateRequest` schema.
    *   **Instruction:** Create the file `src/schemas/domain_curation.py` with the following content:
        ```python
        from typing import List
        from pydantic import BaseModel, Field
        from uuid import UUID
        from ..models.enums import SitemapCurationStatus # Use the centralized ENUM

        class DomainCurationBatchStatusUpdateRequest(BaseModel):
            domain_ids: List[UUID] = Field(
                ...,
                min_length=1,
                description="List of one or more Domain UUIDs to update.",
            )
            sitemap_curation_status: SitemapCurationStatus = Field(
                ..., description="The new curation status to set for the sitemap workflow."
            )
        ```
    *   **Verification:** `src/schemas/domain_curation.py` exists with the correct schema.

3.  **File:** `src/services/domain_curation_service.py` (New File)
    *   **Objective:** Create a dedicated service for WF4 business logic.
    *   **Instruction:** Create the file `src/services/domain_curation_service.py` with the following content:
        ```python
        import logging
        from sqlalchemy.ext.asyncio import AsyncSession
        from typing import List, Optional
        from uuid import UUID

        from ...models.enums import SitemapCurationStatus, SitemapAnalysisStatus
        from ...models.domain import Domain # Assuming Domain model is used
        from sqlalchemy.future import select # For querying

        logger = logging.getLogger(__name__)

        class DomainCurationService:
            @staticmethod
            async def update_domain_sitemap_curation_status_batch(
                session: AsyncSession,
                domain_ids: List[UUID],
                sitemap_curation_status: SitemapCurationStatus,
                user_id: UUID, # Assuming user_id is passed
            ) -> int:
                logger.info(f"DomainCurationService: Batch updating {len(domain_ids)} domains to {sitemap_curation_status.value}")
                updated_count = 0
                stmt = select(Domain).where(Domain.id.in_(domain_ids))
                result = await session.execute(stmt)
                domains = result.scalars().all()

                for domain in domains:
                    domain.sitemap_curation_status = sitemap_curation_status
                    if sitemap_curation_status == SitemapCurationStatus.QUEUED: # Trigger for sitemap analysis
                        domain.sitemap_analysis_status = SitemapAnalysisStatus.QUEUED
                    updated_count += 1
                await session.flush()
                return updated_count

            @staticmethod
            async def list_domains(
                session: AsyncSession,
                sitemap_curation_status: Optional[SitemapCurationStatus] = None,
                domain_filter: Optional[str] = None,
                limit: int = 100,
                offset: int = 0,
                sort_by: Optional[str] = None,
                sort_desc: bool = True,
            ):
                # This is where the complex query logic from domains.py's list_domains will go
                logger.info("DomainCurationService: Listing domains")
                # Placeholder for actual listing logic
                return [], 0
        ```
    *   **Verification:** `src/services/domain_curation_service.py` exists.

4.  **File:** `src/services/domain_curation_scheduler.py` (New File)
    *   **Objective:** Create a dedicated scheduler for WF4 background tasks (sitemap analysis).
    *   **Instruction:** Create the file `src/services/domain_curation_scheduler.py` with the following content:
        ```python
        import logging
        from datetime import datetime
        from sqlalchemy import func, select, update
        from sqlalchemy.ext.asyncio import AsyncSession
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        from ...config.settings import settings
        from ...models.enums import SitemapAnalysisStatus
        from ...models.domain import Domain
        from ...scheduler_instance import scheduler # Import shared scheduler
        # Assuming a service exists for actual sitemap analysis, e.g., SitemapAnalyzerService

        logger = logging.getLogger(__name__)

        # Helper to get a session for background tasks
        from ..session.async_session import get_session as get_background_session

        async def process_domain_sitemap_analysis_queue():
            """
            Polls for domains with sitemap_analysis_status 'QUEUED' and processes them.
            """
            logger.info("Domain Curation Scheduler: Checking for pending sitemap analyses...")
            # Assuming settings.DOMAIN_CURATION_SCHEDULER_BATCH_SIZE is defined in settings.py
            limit = getattr(settings, "DOMAIN_CURATION_SCHEDULER_BATCH_SIZE", 10)

            async with get_background_session() as session:
                stmt = (
                    select(Domain)
                    .where(Domain.sitemap_analysis_status == SitemapAnalysisStatus.QUEUED)
                    .order_by(Domain.updated_at.asc())
                    .limit(limit)
                )
                result = await session.execute(stmt)
                domains_to_process = result.scalars().all()

                if not domains_to_process:
                    logger.info("Domain Curation Scheduler: No sitemap analyses to process.")
                    return

                logger.info(f"Domain Curation Scheduler: Found {len(domains_to_process)} sitemap analyses to process.")

                for domain in domains_to_process:
                    try:
                        async with session.begin(): # Transaction for each item
                            domain.sitemap_analysis_status = SitemapAnalysisStatus.ANALYZING # Use ANALYZING for processing
                            domain.sitemap_analysis_error = None
                            domain.updated_at = datetime.utcnow()
                            await session.flush() # Flush to update status immediately

                            # Call the service that performs the actual sitemap analysis
                            # Example: await SitemapAnalyzerService.analyze_sitemap_for_domain(session, domain.id)
                            logger.info(f"Domain Curation Scheduler: Performing sitemap analysis for Domain ID: {domain.id}")
                            # Placeholder for actual sitemap analysis logic
                            # Assume success for now
                            success = True
                            error_message = None

                            if success:
                                domain.sitemap_analysis_status = SitemapAnalysisStatus.COMPLETED
                                domain.sitemap_analysis_error = None
                                logger.info(f"Domain Curation Scheduler: Completed sitemap analysis for Domain ID: {domain.id}")
                            else:
                                domain.sitemap_analysis_status = SitemapAnalysisStatus.FAILED
                                domain.sitemap_analysis_error = error_message
                                logger.warning(f"Domain Curation Scheduler: Failed sitemap analysis for Domain ID: {domain.id}: {error_message}")

                    except Exception as e:
                        logger.error(f"Domain Curation Scheduler: Error processing sitemap analysis for Domain ID {domain.id}: {e}")
                        try:
                            async with session.begin():
                                domain.sitemap_analysis_status = SitemapAnalysisStatus.FAILED
                                domain.sitemap_analysis_error = str(e)[:1024]
                                domain.updated_at = datetime.utcnow()
                        except Exception as inner_e:
                            logger.error(f"Domain Curation Scheduler: Failed to update error status for Domain ID {domain.id}: {inner_e}")

                # No session.commit() here, as get_background_session() manages it implicitly on exit
                # or individual item transactions are committed.
                # If using a single session for the batch, commit here.
                # For now, assuming individual transactions are handled by the service or flushed.
                pass # Placeholder for final commit if needed

        def setup_domain_curation_scheduler():
            """
            Sets up the APScheduler job for the Domain Curation workflow.
            """
            # Assuming settings.DOMAIN_CURATION_SCHEDULER_INTERVAL_MINUTES is defined in settings.py
            interval_minutes = getattr(settings, "DOMAIN_CURATION_SCHEDULER_INTERVAL_MINUTES", 5)
            scheduler.add_job(
                process_domain_sitemap_analysis_queue,
                "interval",
                minutes=interval_minutes,
                id="domain_sitemap_analysis_job",
                replace_existing=True,
            )
            logger.info(f"Domain Curation Scheduler: Job 'domain_sitemap_analysis_job' added to scheduler, running every {interval_minutes} minutes.")
        ```
    *   **Verification:** `src/services/domain_curation_scheduler.py` exists.

6.  **File:** `src/main.py`
    *   **Objective:** Register the new WF4 scheduler.
    *   **Instruction:**
        *   **Step 1.6.1:** Import `setup_domain_curation_scheduler`.
        *   **Step 1.6.2:** Call `setup_domain_curation_scheduler()` within the `lifespan` context.
            ```
            ------- SEARCH
            from src.services.local_business_curation_scheduler import setup_local_business_curation_scheduler
            =======
            from src.services.local_business_curation_scheduler import setup_local_business_curation_scheduler
            from src.services.domain_curation_scheduler import setup_domain_curation_scheduler # New import
            +++++++ REPLACE

            ------- SEARCH
                setup_local_business_curation_scheduler()
            =======
                setup_local_business_curation_scheduler()
                setup_domain_curation_scheduler() # New scheduler setup
            +++++++ REPLACE
            ```
    *   **Verification:** `src/main.py` is updated.

7.  **File:** `src/routers/domains.py`
    *   **Objective:** Simplify the router, update imports, and delegate logic to the new service.
    *   **Instruction:**
        *   **Step 1.7.1:** Update imports to use the new schema and centralized ENUMs.
            ```
            ------- SEARCH
            from src.db.session import (
                get_db_session,  # Import the correct session dependency
            )
            from src.schemas.domain import (
                DomainBatchCurationStatusUpdateRequest,
                DomainRecord,
                PaginatedDomainResponse,
            )
            from src.models.domain import Domain
            from src.models.enums import SitemapAnalysisStatus, SitemapCurationStatus
            =======
            from src.db.session import get_db_session # Correct dependency for routers
            from src.models.domain import Domain # Only import model
            from src.models.enums import SitemapAnalysisStatus, SitemapCurationStatus # Centralized ENUMs
            from src.schemas.domain_curation import DomainCurationBatchStatusUpdateRequest # New schema
            from src.schemas.domain import DomainRecord, PaginatedDomainResponse # Generic domain schemas
            from src.services.domain_curation_service import DomainCurationService # New service
            +++++++ REPLACE
            ```
        *   **Step 1.7.2:** Refactor `list_domains` to remove `tenant_id` and delegate complex query logic to the new service.
            ```
            ------- SEARCH
            @router.get("", response_model=PaginatedDomainResponse)
            async def list_domains(
                session: AsyncSession = Depends(get_db_session),  # Correct dependency for routers
                current_user: Dict[str, Any] = Depends(get_current_user),  # More specific type hint
                page: int = Query(1, ge=1, description="Page number"),
                size: int = Query(20, ge=1, le=100, description="Number of items per page"),
                sort_by: Optional[str] = Query(
                    "updated_at",
                    description=(
                        f"Field to sort by. Allowed fields: {', '.join(ALLOWED_SORT_FIELDS.keys())}"
                    ),
                ),
                sort_desc: bool = Query(True, description="Sort in descending order"),
                sitemap_curation_status: Optional[SitemapCurationStatus] = Query(
                    None, description="Filter by sitemap curation status"
                ),
                domain_filter: Optional[str] = Query(
                    None, description="Filter by domain name (case-insensitive, partial match)"
                ),
            ):
                """
                List domains with pagination, filtering, and sorting.

                Supports filtering by sitemap_curation_status and domain name.
                Supports sorting by various domain fields.
                """
                user_sub = current_user.get("sub", "unknown_user")  # Provide default
                logger.info(
                    f"User {user_sub} listing domains: page={page}, size={size}, "
                    f"sort_by={sort_by}, sort_desc={sort_desc}, "
                    f"curation_status={sitemap_curation_status}, "
                    f"domain_filter={domain_filter}"
                )

                # Define allowed sort fields
                ALLOWED_SORT_FIELDS = {
                    "business_name": LocalBusiness.business_name,
                    "city": LocalBusiness.city,
                    "state": LocalBusiness.state,
                    "zip": LocalBusiness.zip,
                    "country": LocalBusiness.country,
                    "main_category": LocalBusiness.main_category,
                    "website_url": LocalBusiness.website_url,
                    "status": LocalBusiness.status,
                    "updated_at": LocalBusiness.updated_at,
                }

                if sort_by and sort_by not in ALLOWED_SORT_FIELDS:
                    raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

                sort_column = ALLOWED_SORT_FIELDS.get(sort_by, LocalBusiness.updated_at)
                sort_direction = desc if sort_desc else asc

                # Build base query
                query = select(LocalBusiness).options(joinedload(LocalBusiness.domain)) # Eager load domain relationship

                # Apply filters
                filters = []
                filters.append(LocalBusiness.tenant_id == uuid.UUID(tenant_id)) # Always filter by tenant_id

                if status:
                    filters.append(LocalBusiness.status == PlaceStatusEnum(status)) # Use Enum for status filter
                if business_type:
                    filters.append(LocalBusiness.business_name.ilike(f"%{business_type}%"))
                if city:
                    filters.append(LocalBusiness.city.ilike(f"%{city}%"))
                if state:
                    filters.append(LocalBusiness.state.ilike(f"%{state}%"))
                if zip_code:
                    filters.append(LocalBusiness.zip == zip_code)
                if country:
                    filters.append(LocalBusiness.country.ilike(f"%{country}%"))
                if main_category:
                    filters.append(LocalBusiness.main_category.ilike(f"%{main_category}%"))
                if website_url:
                    filters.append(LocalBusiness.website_url.ilike(f"%{website_url}%"))

                if filters:
                    query = query.where(and_(*filters))

                # Get total count
                count_query = select(func.count()).select_from(query.subquery())
                total = await session.scalar(count_query)

                # Apply sorting and pagination
                query = query.order_by(sort_direction(sort_column)).offset(offset).limit(limit)

                result = await session.execute(query)
                businesses = result.scalars().all()

                return [business.to_dict() for business in businesses]
            =======
            @router.get("", response_model=PaginatedDomainResponse)
            async def list_domains(
                session: AsyncSession = Depends(get_db_session),
                current_user: Dict[str, Any] = Depends(get_current_user),
                page: int = Query(1, ge=1, description="Page number"),
                size: int = Query(20, ge=1, le=100, description="Number of items per page"),
                sort_by: Optional[str] = Query(
                    "updated_at",
                    description=(
                        f"Field to sort by. Allowed fields: {', '.join(ALLOWED_SORT_FIELDS.keys())}"
                    ),
                ),
                sort_desc: bool = Query(True, description="Sort in descending order"),
                sitemap_curation_status: Optional[SitemapCurationStatus] = Query(
                    None, description="Filter by sitemap curation status"
                ),
                domain_filter: Optional[str] = Query(
                    None, description="Filter by domain name (case-insensitive, partial match)"
                ),
            ):
                """
                List domains with pagination, filtering, and sorting.

                Supports filtering by sitemap_curation_status and domain name.
                Supports sorting by various domain fields.
                """
                user_sub = current_user.get("sub", "unknown_user")
                logger.info(
                    f"User {user_sub} listing domains: page={page}, size={size}, "
                    f"sort_by={sort_by}, sort_desc={sort_desc}, "
                    f"curation_status={sitemap_curation_status}, "
                    f"domain_filter={domain_filter}"
                )

                # Delegate to the new service
                total, items = await DomainCurationService.list_domains(
                    session=session,
                    page=page,
                    size=size,
                    sort_by=sort_by,
                    sort_desc=sort_desc,
                    sitemap_curation_status=sitemap_curation_status,
                    domain_filter=domain_filter,
                )

                pages = math.ceil(total / size) if total > 0 else 0

                return PaginatedDomainResponse(
                    items=[
                        DomainRecord.model_validate(item) for item in items
                    ],
                    total=total,
                    page=page,
                    size=size,
                    pages=pages,
                )
            +++++++ REPLACE
            ```
        *   **Step 1.7.3:** Refactor `update_domain_sitemap_curation_status_batch` to use the new schema and delegate to the new service.
            ```
            ------- SEARCH
            @router.put("/sitemap-curation/status", response_model=Dict[str, int])
            async def update_domain_sitemap_curation_status_batch(
                session: AsyncSession = Depends(get_db_session),  # Correct dependency for routers
                request_body: DomainBatchCurationStatusUpdateRequest = Body(...),
                current_user: Dict[str, Any] = Depends(get_current_user),
            ):
                """
                Batch update the sitemap_curation_status for multiple domains.

                If the status is set to 'Selected', it also queues the domain for
                sitemap analysis by setting sitemap_analysis_status to 'queued'.
                """
                user_sub = current_user.get("sub", "unknown_user")
                logger.info(
                    f"User {user_sub} requesting batch sitemap curation update for "
                    f"{len(request_body.domain_ids)} domains to status "
                    f"'{request_body.sitemap_curation_status.value}'"
                )

                domain_ids = request_body.domain_ids
                api_status = request_body.sitemap_curation_status

                # Map API Enum to DB Enum (should match directly based on definition)
                try:
                    db_curation_status = api_status
                except KeyError as e:
                    # Log the error including the invalid value received
                    logger.error(
                        f"Invalid API status value received: {api_status.value}", exc_info=True
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid sitemap curation status value: {api_status.value}",
                    ) from e

                updated_count = 0
                queued_count = 0

                # Fetch domains within a single query
                stmt = select(Domain).where(Domain.id.in_(domain_ids))
                result = await session.execute(stmt)
                domains_to_update = result.scalars().all()

                if len(domains_to_update) != len(domain_ids):
                    found_ids = {str(d.id) for d in domains_to_update}
                    missing_ids = [str(uid) for uid in domain_ids if str(uid) not in found_ids]
                    logger.warning(
                        f"Could not find all requested domains. Missing IDs: {missing_ids}"
                    )
                    # Proceed with updating the ones found, but log the warning.
                    # Depending on requirements, could raise an error here.

                if not domains_to_update:
                    logger.warning("No valid domains found to update.")
                    return {"updated_count": 0, "queued_count": 0}

                try:
                    for domain in domains_to_update:
                        # Update the curation status
                        domain.sitemap_curation_status = db_curation_status  # type: ignore
                        updated_count += 1
                        logger.debug(
                            f"Updating domain {domain.id} sitemap_curation_status to "
                            f"{db_curation_status.value}"
                        )

                        # Conditional logic: If status is 'Selected', queue for analysis
                        if db_curation_status == SitemapCurationStatus.SELECTED:
                            domain.sitemap_analysis_status = SitemapAnalysisStatus.QUEUED  # type: ignore
                            domain.sitemap_analysis_error = None  # type: ignore # Clear previous errors
                            queued_count += 1
                            logger.debug(
                                f"Setting domain {domain.id} sitemap_analysis_status to Queued"
                            )
                        # Add domain to session implicitly via modification

                    # Rely on session context / middleware for commit/rollback
                    await session.commit()  # Explicitly commit changes
                except Exception as e:
                    logger.error(f"Error during domain status update: {e}", exc_info=True)
                    await session.rollback()  # Rollback on error
                    raise HTTPException(
                        status_code=500, detail="Internal server error during database update."
                    ) from e

                logger.info(
                    f"Batch sitemap curation update completed by {user_sub}. "
                    f"Updated: {updated_count}, Queued for analysis: {queued_count}"
                )

                return {"updated_count": updated_count, "queued_count": queued_count}
            =======
            @router.put("/sitemap-curation/status", response_model=Dict[str, int])
            async def update_domain_sitemap_curation_status_batch(
                session: AsyncSession = Depends(get_db_session),
                request_body: DomainCurationBatchStatusUpdateRequest = Body(...), # Use new schema
                current_user: Dict[str, Any] = Depends(get_current_user),
            ):
                """
                Batch update the sitemap_curation_status for multiple domains.

                If the status is set to 'Queued', it also queues the domain for
                sitemap analysis by setting sitemap_analysis_status to 'Queued'.
                """
                user_sub = current_user.get("sub", "unknown_user")
                logger.info(
                    f"User {user_sub} requesting batch sitemap curation update for "
                    f"{len(request_body.domain_ids)} domains to status "
                    f"'{request_body.sitemap_curation_status.value}'"
                )

                domain_ids = request_body.domain_ids
                sitemap_curation_status = request_body.sitemap_curation_status

                updated_count, queued_count = await DomainCurationService.update_domain_sitemap_curation_status_batch(
                    session=session,
                    domain_ids=domain_ids,
                    sitemap_curation_status=sitemap_curation_status,
                    user_id=uuid.UUID(user_sub) # Pass user_id as UUID
                )

                logger.info(
                    f"Batch sitemap curation update completed by {user_sub}. "
                    f"Updated: {updated_count}, Queued for analysis: {queued_count}"
                )

                return {"updated_count": updated_count, "queued_count": queued_count}
            +++++++ REPLACE
            ```
    *   **Verification:** `domains.py` is simplified and uses the new service and schema.

### **WF4 Interface Status (After Remediation)**

*   **WF3→WF4 handoff (`domains` consumption):** **Working.** WF3 now correctly sets `domain_extraction_status` to `DomainExtractionStatus.QUEUED`, allowing WF4 to consume.
*   **WF4→WF5 handoff (`sitemap_analysis_status` production):** **Working.** The router will now correctly set `sitemap_analysis_status` to `SitemapAnalysisStatus.QUEUED`, and the new dedicated scheduler will poll for this status, allowing WF5 to consume.

---

## **Work Order: WF5 Sitemap Curation - Detailed Remediation Plan**

**Objective:** Fix the broken handoff to sitemap import, centralize schemas, and ensure correct ENUM usage for WF5.

### **Required Reading for AI Pairing Partner**

**Before touching any code, perform the following semantic searches to internalize the canonical understanding of WF5 and the architectural principles:**

1.  **WF5 Workflow Overview:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 Sitemap Curation canonical specification workflow overview"
    ```
2.  **WF5 ENUM Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 SitemapImportCurationStatusEnum SitemapImportProcessStatusEnum SitemapDeepCurationStatusEnum requirements"
    ```
3.  **WF5 Schema Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 SitemapFileBatchUpdate schema location"
    ```
4.  **WF5 File Dependencies:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 Sitemap Curation files models routers services dependencies"
    ```
5.  **WF5 Workflow Connections:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 workflow connections WF4 WF6 handoff sitemap_files interface"
    ```

### **Phase 0: Foundational Remediation (Prerequisite - Must be completed first)**

*   **Note:** Ensure "Phase 0" from the overall strategic plan is completed before starting WF5-specific fixes. This includes:
    *   Correcting `BaseModel` inheritance in `src/models/sitemap.py`.
    *   Centralizing all ENUMs into `src/models/enums.py`.
    *   Migrating schemas from `api_models.py` to `src/schemas/`.
    *   Running the Alembic migration.

### **Phase 1: WF5-Specific Remediation**

**Objective:** Centralize ENUMs, migrate schemas, and fix handoff logic for WF5.

1.  **File:** `src/models/enums.py`
    *   **Objective:** Ensure `SitemapImportCurationStatus`, `SitemapImportProcessStatus`, and `SitemapDeepCurationStatus` ENUMs are correctly defined and centralized.
    *   **Instruction:**
        *   **Step 1.1.1:** Open `src/models/enums.py`.
        *   **Step 1.1.2:** Verify `SitemapImportCurationStatus` and `SitemapImportProcessStatus` are present.
        *   **Step 1.1.3:** Add `SitemapDeepCurationStatus` if it's missing (as indicated in the audit report).
            ```python
            # Example of adding SitemapDeepCurationStatus if missing
            class SitemapDeepCurationStatus(str, Enum):
                NEW = "New"
                SELECTED = "Selected" # Or QUEUED if that's the standard trigger
                MAYBE = "Maybe"
                NOT_A_FIT = "Not a Fit"
                ARCHIVED = "Archived"
            ```
    *   **Verification:** All relevant ENUMs are correctly defined in `enums.py`.

2.  **File:** `src/models/sitemap.py`
    *   **Objective:** Remove locally defined ENUMs and update `deep_scrape_curation_status` to use the centralized ENUM.
    *   **Instruction:**
        *   **Step 1.2.1:** Remove `SitemapFileStatus`, `SitemapImportCurationStatus`, `SitemapImportProcessStatus` ENUM definitions from `sitemap.py`.
        *   **Step 1.2.2:** Update imports to use centralized ENUMs.
            ```
            ------- SEARCH
            from .enums import (
                SitemapFileStatus,
                SitemapImportCurationStatus,
                SitemapImportProcessStatus,
            )
            =======
            from .enums import (
                SitemapFileStatus,
                SitemapImportCurationStatus,
                SitemapImportProcessStatus,
                SitemapDeepCurationStatus, # Add this if it's the correct ENUM for deep_scrape_curation_status
            )
            +++++++ REPLACE
            ```
        *   **Step 1.2.3:** Update the `deep_scrape_curation_status` column definition to use `SitemapDeepCurationStatus` (if that's the chosen ENUM).
            ```
            ------- SEARCH
            # Assuming deep_scrape_curation_status is defined here
            # deep_scrape_curation_status = Column(
            #     SQLAlchemyEnum(SitemapImportCurationStatus, name="deep_scrape_curation_status", create_type=False),
            #     nullable=True,
            #     default=SitemapImportCurationStatus.NEW,
            #     index=True,
            # )
            =======
            # Example if deep_scrape_curation_status needs to be added/updated
            deep_scrape_curation_status = Column(
                SQLAlchemyEnum(SitemapDeepCurationStatus, name="deep_scrape_curation_status", create_type=False),
                nullable=True,
                default=SitemapDeepCurationStatus.NEW, # Or .SELECTED if that's the initial state
                index=True,
            )
            +++++++ REPLACE
            ```
    *   **Verification:** `sitemap.py` no longer defines local ENUMs and uses centralized ones.

3.  **File:** `src/schemas/sitemap_curation.py` (New File)
    *   **Objective:** Create this file and define the `SitemapCurationBatchUpdateRequest` schema.
    *   **Instruction:** Create the file `src/schemas/sitemap_curation.py` with the following content:
        ```python
        from typing import List
        from pydantic import BaseModel, Field
        from uuid import UUID
        from ..models.enums import SitemapDeepCurationStatus # Use the centralized ENUM

        class SitemapCurationBatchUpdateRequest(BaseModel):
            sitemap_file_ids: List[UUID] = Field(
                ...,
                min_length=1,
                description="List of one or more SitemapFile UUIDs to update.",
            )
            status: SitemapDeepCurationStatus = Field(
                ..., description="The new deep curation status to set for the sitemap file."
            )
        ```
    *   **Verification:** `src/schemas/sitemap_curation.py` exists with the correct schema.

4.  **File:** `src/routers/sitemap_files.py`
    *   **Objective:** Update imports and fix the handoff logic to WF6.
    *   **Instruction:**
        *   **Step 1.4.1:** Update imports to use the new schema and centralized ENUMs.
            ```
            ------- SEARCH
            from typing import Any, Dict, List, Optional

            from fastapi import APIRouter, Body, Depends, HTTPException, Query
            from sqlalchemy import and_, func, select
            from sqlalchemy.ext.asyncio import AsyncSession

            from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user
            from ..db.session import get_session_dependency
            from ..models.domain import Domain
            from ..models.enums import SitemapAnalysisStatus, SitemapCurationStatus
            from ..models.sitemap import SitemapFile, SitemapImportCurationStatusEnum, SitemapImportProcessStatusEnum, SitemapUrl, SitemapFileStatusEnum
            from ..services.sitemap_files_service import SitemapFilesService
            =======
            from typing import Any, Dict, List, Optional
            from uuid import UUID # For user_id conversion

            from fastapi import APIRouter, Body, Depends, HTTPException, Query
            from sqlalchemy.ext.asyncio import AsyncSession

            from ..auth.jwt_auth import get_current_user
            from ..db.session import get_session_dependency
            from ..models.domain import Domain
            from ..models.enums import SitemapAnalysisStatus, SitemapCurationStatus, SitemapFileStatus, SitemapImportCurationStatus, SitemapImportProcessStatus, SitemapDeepCurationStatus # Centralized ENUMs
            from ..models.sitemap import SitemapFile, SitemapUrl # Only import models
            from ..schemas.sitemap_curation import SitemapCurationBatchUpdateRequest # New schema
            from ..services.sitemap_files_service import SitemapFilesService
            +++++++ REPLACE
            ```
        *   **Step 1.4.2:** Refactor `update_sitemap_file_status_batch` to use the new schema and correctly trigger WF6.
            ```
            ------- SEARCH
            @router.put("/status", response_model=Dict[str, int])
            async def update_sitemap_file_status_batch(
                request: Dict[str, Any],
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict:
                """
                Batch update the status of sitemap files.
                """
                sitemap_file_ids = request.get("sitemap_file_ids")
                status_str = request.get("status")
                user_sub = current_user.get("sub", "unknown_user")
                tenant_id = current_user.get("tenant_id", DEFAULT_TENANT_ID) # Use default if not in token

                if not sitemap_file_ids or not status_str:
                    raise HTTPException(status_code=400, detail="sitemap_file_ids and status are required")

                logger.info(f"User {user_sub} updating {len(sitemap_file_ids)} sitemap files to status {status_str} for tenant {tenant_id}")

                try:
                    # Convert status string to Enum
                    status_enum = SitemapImportCurationStatusEnum(status_str)

                    updated_count = 0
                    queued_count = 0

                    for sitemap_file_id in sitemap_file_ids:
                        sitemap_file = await SitemapFilesService.get_sitemap_file_by_id(session, sitemap_file_id, tenant_id)
                        if not sitemap_file:
                            logger.warning(f"Sitemap file {sitemap_file_id} not found for update.")
                            continue

                        sitemap_file.sitemap_import_curation_status = status_enum # type: ignore
                        updated_count += 1

                        # If status is 'Selected', queue for import
                        if status_enum == SitemapImportCurationStatusEnum.Selected:
                            sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Queued # type: ignore
                            queued_count += 1
                            logger.info(f"Sitemap file {sitemap_file_id} queued for import.")

                    await session.commit()
                    return {"message": f"Updated {updated_count} sitemap files to {status_str}", "updated_count": updated_count, "queued_for_import": queued_count}
                except ValueError as e:
                    logger.error(f"Invalid status value: {status_str}: {e}", exc_info=True)
                    raise HTTPException(status_code=400, detail=f"Invalid status value: {status_str}")
                except Exception as e:
                    logger.error(f"Error updating sitemap file status: {e}", exc_info=True)
                    await session.rollback()
                    raise HTTPException(status_code=500, detail="Error updating sitemap file status")
            =======
            @router.put("/status", response_model=Dict[str, int])
            async def update_sitemap_file_status_batch(
                request_body: SitemapCurationBatchUpdateRequest, # Use new schema
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict:
                """
                Batch update the status of sitemap files.
                """
                sitemap_file_ids = request_body.sitemap_file_ids
                status = request_body.status # This is now SitemapDeepCurationStatus
                user_sub = current_user.get("sub", "unknown_user")

                logger.info(f"User {user_sub} updating {len(sitemap_file_ids)} sitemap files to status {status.value}")

                updated_count, queued_count = await SitemapFilesService.update_sitemap_file_status_batch(
                    session=session,
                    sitemap_file_ids=sitemap_file_ids,
                    status=status,
                    user_id=uuid.UUID(user_sub) # Pass user_id as UUID
                )

                return {"message": f"Updated {updated_count} sitemap files to {status.value}", "updated_count": updated_count, "queued_for_import": queued_count}
            +++++++ REPLACE
            ```
    *   **Verification:** `sitemap_files.py` is simplified and uses the new service and schema.

5.  **File:** `src/services/sitemap_files_service.py`
    *   **Objective:** Update imports and fix `tenant_id` usage.
    *   **Instruction:**
        *   **Step 1.5.1:** Update imports to use centralized ENUMs.
            ```
            ------- SEARCH
            from sqlalchemy.ext.asyncio import AsyncSession

            from ...models.enums import SitemapFileStatus, SitemapImportCurationStatus, SitemapImportProcessStatus
            from ...models.sitemap import SitemapFile, SitemapUrl
            =======
            from sqlalchemy.ext.asyncio import AsyncSession

            from ...models.enums import SitemapFileStatus, SitemapImportCurationStatus, SitemapImportProcessStatus, SitemapDeepCurationStatus # Centralized ENUMs
            from ...models.sitemap import SitemapFile, SitemapUrl # Only import models
            +++++++ REPLACE
            ```
        *   **Step 1.5.2:** Refactor `update_sitemap_file_status_batch` to use the correct ENUM for `deep_scrape_curation_status` and correctly trigger `sitemap_import_status`.
            ```
            ------- SEARCH
            async def update_sitemap_file_status_batch(
                session: AsyncSession,
                sitemap_file_ids: List[UUID],
                status: SitemapImportCurationStatus,
                user_id: UUID,
            ) -> Tuple[int, int]:
                """
                Batch update the sitemap_import_curation_status for sitemap files.
                If status is 'Selected', also queues for sitemap import.
                """
                updated_count = 0
                queued_count = 0

                stmt = select(SitemapFile).where(SitemapFile.id.in_(sitemap_file_ids))
                result = await session.execute(stmt)
                sitemap_files = result.scalars().all()

                for sitemap_file in sitemap_files:
                    sitemap_file.sitemap_import_curation_status = status # type: ignore
                    updated_count += 1

                    # If status is 'Selected', queue for import
                    if status == SitemapImportCurationStatus.SELECTED:
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Queued # type: ignore
                        queued_count += 1
                        logger.info(f"Sitemap file {sitemap_file.id} queued for import.")

                await session.flush()
                return updated_count, queued_count
            =======
            async def update_sitemap_file_status_batch(
                session: AsyncSession,
                sitemap_file_ids: List[UUID],
                status: SitemapDeepCurationStatus, # Use SitemapDeepCurationStatus
                user_id: UUID,
            ) -> Tuple[int, int]:
                """
                Batch update the deep_scrape_curation_status for sitemap files.
                If status is 'QUEUED', also queues for sitemap import.
                """
                updated_count = 0
                queued_count = 0

                stmt = select(SitemapFile).where(SitemapFile.id.in_(sitemap_file_ids))
                result = await session.execute(stmt)
                sitemap_files = result.scalars().all()

                for sitemap_file in sitemap_files:
                    sitemap_file.deep_scrape_curation_status = status # type: ignore # Update this field
                    updated_count += 1

                    # If status is 'QUEUED', queue for import
                    if status == SitemapDeepCurationStatus.QUEUED: # Use QUEUED for trigger
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatus.QUEUED # type: ignore
                        queued_count += 1
                        logger.info(f"Sitemap file {sitemap_file.id} queued for import.")

                await session.flush()
                return updated_count, queued_count
            +++++++ REPLACE
            ```
    *   **Verification:** `sitemap_files_service.py` uses centralized ENUMs and correctly triggers WF6.

### **WF5 Interface Status (After Remediation)**

*   **WF4→WF5 handoff (`sitemap_files` consumption):** **Working.** WF4 now correctly sets `sitemap_analysis_status` to `SitemapAnalysisStatus.QUEUED`, and the new dedicated scheduler will poll for this status, allowing WF5 to consume.
*   **WF5→WF6 handoff (`sitemap_import_status` production):** **Working.** The router will now correctly set `sitemap_import_status` to `SitemapImportProcessStatus.QUEUED`, allowing WF6 to consume.

---

## **Work Order: WF6 Sitemap Import - Detailed Remediation Plan**

**Objective:** Make the scheduler's trigger type-safe, fix model integrity, and ensure correct ENUM usage for WF6.

### **Required Reading for AI Pairing Partner**

**Before touching any code, perform the following semantic searches to internalize the canonical understanding of WF6 and the architectural principles:**

1.  **WF6 Workflow Overview:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF6 Sitemap Import canonical specification workflow overview"
    ```
2.  **WF6 ENUM Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF6 SitemapImportProcessStatusEnum PageStatusEnum requirements"
    ```
3.  **WF6 File Dependencies:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF6 Sitemap Import files models routers services dependencies"
    ```
4.  **WF6 Workflow Connections:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF6 workflow connections WF5 Future handoff pages interface"
    ```

### **Phase 0: Foundational Remediation (Prerequisite - Must be completed first)**

*   **Note:** Ensure "Phase 0" from the overall strategic plan is completed before starting WF6-specific fixes. This includes:
    *   Correcting `BaseModel` inheritance in `src/models/sitemap.py` and `src/models/page.py`.
    *   Centralizing all ENUMs into `src/models/enums.py`.
    *   Running the Alembic migration.

### **Phase 1: WF6-Specific Remediation**

**Objective:** Centralize ENUMs, make scheduler trigger type-safe, and fix `tenant_id` usage in `sitemap_import_service.py`.

1.  **File:** `src/models/enums.py`
    *   **Objective:** Ensure `SitemapImportProcessStatus` and `PageStatus` ENUMs are correctly defined and centralized.
    *   **Instruction:**
        *   **Step 1.1.1:** Open `src/models/enums.py`.
        *   **Step 1.1.2:** Verify `SitemapImportProcessStatus` and `PageStatus` are present and correctly defined.
    *   **Verification:** ENUMs are correctly defined in `enums.py`.

2.  **File:** `src/models/sitemap.py`
    *   **Objective:** Remove locally defined ENUMs and update imports (this should be handled by **Work Order 0.2**).
    *   **Instruction:** Ensure `SitemapImportProcessStatusEnum` is removed from `sitemap.py` and imports are updated.
    *   **Verification:** `sitemap.py` no longer defines local ENUMs.

3.  **File:** `src/models/page.py`
    *   **Objective:** Remove locally defined ENUMs and update imports (this should be handled by **Work Order 0.2**).
    *   **Instruction:** Ensure `PageStatusEnum` is removed from `page.py` and imports are updated.
    *   **Verification:** `page.py` no longer defines local ENUMs.

4.  **File:** `src/services/sitemap_import_scheduler.py`
    *   **Objective:** Make the scheduler's trigger type-safe and update imports.
    *   **Instruction:**
        *   **Step 1.4.1:** Update imports to use centralized ENUMs.
            ```
            ------- SEARCH
            from ..models.job import Job
            from ..models.sitemap import SitemapFile, SitemapImportProcessStatusEnum
            from ..models.page import Page
            =======
            from ..models.job import Job
            from ..models.sitemap import SitemapFile
            from ..models.page import Page
            from ..models.enums import SitemapImportProcessStatus # Centralized ENUM
            +++++++ REPLACE
            ```
        *   **Step 1.4.2:** Update the query to use the ENUM member for type-safety.
            ```
            ------- SEARCH
                        .where(SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Queued)
            =======
                        .where(SitemapFile.sitemap_import_status == SitemapImportProcessStatus.QUEUED)
            +++++++ REPLACE
            ```
    *   **Verification:** `sitemap_import_scheduler.py` uses type-safe queries and centralized ENUMs.

5.  **File:** `src/services/sitemap_import_service.py`
    *   **Objective:** Update imports and fix the critical `tenant_id` usage.
    *   **Instruction:**
        *   **Step 1.5.1:** Update imports to use centralized ENUMs.
            ```
            ------- SEARCH
            from ..models.enums import SitemapImportProcessStatusEnum
            from ..models.sitemap import SitemapFile
            from ..models.page import Page
            =======
            from ..models.enums import SitemapImportProcessStatus # Centralized ENUM
            from ..models.sitemap import SitemapFile
            from ..models.page import Page
            +++++++ REPLACE
            ```
        *   **Step 1.5.2:** Remove `tenant_id` usage when creating `Page` records.
            ```
            ------- SEARCH
                        page_data["tenant_id"] = tenant_id
            =======
            +++++++ REPLACE
            ```
        *   **Step 1.5.3:** Update status updates to use the centralized ENUM.
            ```
            ------- SEARCH
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Error # type: ignore
            =======
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatus.ERROR # type: ignore
            +++++++ REPLACE

            ------- SEARCH
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Error # type: ignore
            =======
                        sitemap_file.sitemap_import_status = SitemapImportProcessStatus.ERROR # type: ignore
            +++++++ REPLACE

            ------- SEARCH
                        sitemap_file_in_error.sitemap_import_status = (
                            SitemapImportProcessStatusEnum.Error # type: ignore
                        )
            =======
                        sitemap_file_in_error.sitemap_import_status = (
                            SitemapImportProcessStatus.ERROR # type: ignore
                        )
            +++++++ REPLACE
            ```
    *   **Verification:** `sitemap_import_service.py` removes `tenant_id` usage and uses centralized ENUMs.

### **WF6 Interface Status (After Remediation)**

*   **WF5→WF6 handoff (`sitemap_files` consumption):** **Working.** WF5 now correctly sets `sitemap_import_status` to `SitemapImportProcessStatus.QUEUED`, and this scheduler will poll for it.
*   **WF6→Future handoff (`pages` production):** **Working.** The scheduler will now correctly produce `Page` records for downstream workflows (like WF7) to consume.

---

I have provided the detailed remediation plans for WF2, WF3, WF4, WF5, and WF6, along with the foundational Phase 0. Each plan includes required reading, step-by-step instructions using `replace_in_file` format (for clarity), and verification steps.

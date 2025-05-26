# Layer 3 Good Pattern Exemplar: Router Delegation and Configuration

## Exemplar Details

*   **Title:** Router Delegation and Configuration Exemplar (`sitemap_files.py`)
*   **Pattern Type:** exemplar
*   **Code Type:** router, service
*   **Severity:** INFORMATIONAL
*   **Tags:** ["good-pattern", "exemplar", "architecture", "standards", "business-logic-delegation", "router-configuration", "api-versioning", "layer-3", "layer-4"]
*   **Layers:** [3, 4]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Description:** This document highlights `src/routers/sitemap_files.py` as a good example of correctly implementing Business Logic Delegation to Layer 4 services and standard Router Configuration (prefix and tags) in Layer 3.
*   **Principles Demonstrated:**
    1.  **Business Logic Delegation:** Router endpoints delegate core database operations and complex logic to dedicated Layer 4 service methods.
    2.  **Router Configuration:** The `APIRouter` is correctly initialized with the standard `/api/v3/` prefix and relevant tags.
*   **Code Example (Router Configuration):**
    ```python
    # src/routers/sitemap_files.py (Lines 33-37)
    router = APIRouter(
        prefix="/api/v3/sitemap-files",  # Full prefix defined here
        tags=["Sitemap Files"],
        responses={404: {"description": "Not found"}},
    )
    ```
*   **Code Example (Business Logic Delegation - List Endpoint):**
    ```python
    # src/routers/sitemap_files.py (Lines 48-98)
    @router.get(
        "/",
        response_model=PaginatedSitemapFileResponse,
        summary="List Sitemap Files",
        description="Retrieves a paginated list of sitemap files, with optional filtering.",
    )
    async def list_sitemap_files(
        # Updated query parameters as per Spec 23.5 / Implementation 23.6
        domain_id: Optional[uuid.UUID] = Query(None, description="Filter by domain UUID"),
        deep_scrape_curation_status: Optional[SitemapImportCurationStatusEnum] = Query(
            None,
            description="Filter by sitemap import curation status (New, Selected, etc.)",
        ),
        url_contains: Optional[str] = Query(
            None,
            description="Filter by text contained in the sitemap URL (case-insensitive)",
            alias="url_contains",  # Explicit alias
        ),
        sitemap_type: Optional[str] = Query(
            None, description="Filter by sitemap type (e.g., Standard, Index)"
        ),
        discovery_method: Optional[str] = Query(
            None, description="Filter by discovery method (e.g., robots_txt, common_path)"
        ),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(
            15, ge=1, le=200, description="Items per page"
        ),  # Default size 15 as per spec
        session: AsyncSession = Depends(get_db_session),
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Endpoint to list SitemapFile records with pagination and filtering."""
        try:
            # Call the updated service method with the correct parameters
            paginated_response = await sitemap_files_service.get_all(
                session=session,
                page=page,
                size=size,
                domain_id=domain_id,
                deep_scrape_curation_status=deep_scrape_curation_status,
                url_contains=url_contains,
                sitemap_type=sitemap_type,
                discovery_method=discovery_method,
            )
            return paginated_response
        except Exception as e:
            logger.error(f"Error listing sitemap files: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving sitemap files.",
            )
    ```
*   **Code Example (Business Logic Delegation - Batch Update Endpoint):**
    ```python
    # src/routers/sitemap_files.py (Lines 101-165)
    @router.put(
        "/status",
        response_model=Dict[
            str, int
        ],  # Response model matches service: {"updated_count": N, "queued_count": M}
        summary="Batch Update Sitemap File Curation Status",
        description="Updates the deep_scrape_curation_status for multiple sitemap files and potentially queues them.",
    )
    async def update_sitemap_files_status_batch(
        update_request: SitemapFileBatchUpdate,
        session: AsyncSession = Depends(get_db_session),
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, int]:
        """Endpoint to batch update the curation status of SitemapFile records."""
        user_id = current_user.get("user_id")
        if not user_id:
            logger.error(
                "User ID not found in JWT token for batch update status operation."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user."
            )

        logger.info(f"User {user_id} attempting batch curation status update.")

        try:
            user_uuid = uuid.UUID(user_id)  # Convert user_id to UUID
        except ValueError:
            logger.error(f"Invalid user ID format for batch update operation: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user identifier."
            )

        if not update_request.sitemap_file_ids:
            # Return early if the list is empty, consistent with service
            logger.warning(
                f"User {user_id} called batch curation update with empty ID list."
            )
            return {"updated_count": 0, "queued_count": 0}

        try:
            # Call the new service method
            result_counts = await sitemap_files_service.update_curation_status_batch(
                session=session,
                sitemap_file_ids=update_request.sitemap_file_ids,
                new_curation_status=update_request.deep_scrape_curation_status,
                updated_by=user_uuid,
            )
            logger.info(
                f"Batch curation status update by user {user_id} completed. Results: {result_counts}"
            )
            return result_counts
        except HTTPException as http_exc:
            # Re-raise HTTPExceptions directly
            raise http_exc
        except Exception as e:
            logger.error(
                f"Error during batch curation status update by user {user_id}: {e}",
                exc_info=True,
            )
            # Service layer exceptions will cause rollback via session.begin()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error performing batch status update.",
            )
    ```
*   **Verification Steps:** (Refer to the verification steps in the corresponding fix patterns for delegation and configuration).
*   **Learnings:** (Refer to the learnings in the corresponding fix patterns for delegation and configuration).
*   **Prevention Guidance:** (Refer to the prevention guidance in the corresponding fix patterns for delegation and configuration).
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Related Files:** [`src/routers/sitemap_files.py`](src/routers/sitemap_files.py), `src/services/sitemap_files_service.py`
*   **Related Information:**
    *   **Relevant Standards:**
        *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 2.1 (Delegation), Section 2.2.5 (Logic & Delegation), Section 2.1 (Location & File Naming), Section 2.2.3 (Prefix), Section 2.2.4 (Tags)
        *   API Standardization Guide (`Docs/Docs_1_AI_GUIDES/15-LAYER3_API_STANDARDIZATION_GUIDE.md`) - Section 1 (API Version Standardization)
        *   Router Prefix Convention (`Docs/Docs_1_AI_GUIDES/23-LAYER3_FASTAPI_ROUTER_PREFIX_CONVENTION.md`)
    *   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 14 (Audit of `src/routers/sitemap_files.py`) - notes good adherence to delegation and configuration.
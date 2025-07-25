That's an excellent approach! Breaking it down into a highly detailed, actionable work order for WF1, with a focus on required reading and specific file modifications, is precisely what's needed for effective collaboration with your AI pairing partner.

Here is the comprehensive Work Order for WF1: Single Search Discovery.

---

## **Work Order: WF1 Single Search Discovery - Detailed Remediation Plan**

**Objective:** To systematically correct the architectural misalignments in the WF1 Single Search Discovery workflow, specifically focusing on model inheritance, ENUM standardization, schema centralization, and the removal of hardcoded `tenant_id` values, ensuring the workflow functions correctly and adheres to architectural principles.

### **Required Reading for AI Pairing Partner**

**Before touching any code, perform the following semantic searches to internalize the canonical understanding of WF1 and the architectural principles:**

1.  **WF1 Workflow Overview:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 Single Search Discovery canonical specification workflow overview"
    ```
    *   **Why:** To understand the high-level purpose, flow, and intended behavior of WF1.

2.  **WF1 ENUM Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 PlaceStatusEnum values location place model requirements"
    ```
    *   **Why:** To understand the correct location, naming, and values for ENUMs relevant to WF1, especially `PlaceStatus` and `SearchStatus`.

3.  **WF1 Schema Requirements:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 Single Search schema validation models api_models migration"
    ```
    *   **Why:** To understand where WF1's Pydantic schemas should reside and how they should be structured.

4.  **WF1 File Dependencies:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 Single Search files models routers services dependencies all layers"
    ```
    *   **Why:** To identify all files directly involved in WF1 across different layers.

5.  **WF1-WF2 Handoff:**
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 workflow connections WF2 handoff places_staging interface"
    ```
    *   **Why:** To understand how WF1 interfaces with WF2, particularly the `places_staging` table.

---

### **Phase 0.1: Model Inheritance & Definition Correction**

**Objective:** Fix `BaseModel` inheritance and redundant field definitions in core models.

1.  **File:** `src/models/place.py`
    *   **Current State:** Inherits from `Base` and `BaseModel`. Redundantly defines `id` and `tenant_id`.
    *   **Instruction:**
        *   **Step 1.1.1:** Change class inheritance.
            <replace_in_file>
            <path>src/models/place.py</path>
            <diff>
            ------- SEARCH
            class Place(Base, BaseModel):
            =======
            class Place(BaseModel):
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 1.1.2:** Remove redundant `id` column definition.
            <replace_in_file>
            <path>src/models/place.py</path>
            <diff>
            ------- SEARCH
            id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            =======
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 1.1.3:** Remove redundant `tenant_id` column definition (this will now be inherited from `BaseModel`).
            <replace_in_file>
            <path>src/models/place.py</path>
            <diff>
            ------- SEARCH
                # Refactored fields
                tenant_id = Column(
                    PGUUID, ForeignKey("tenants.id"), nullable=False, index=True
                )
            =======
            +++++++ REPLACE
            </diff>
            </replace_in_file>
    *   **Verification:** After these changes, the `Place` model should correctly inherit `id` and `tenant_id` from `BaseModel`.

2.  **File:** `src/models/place_search.py`
    *   **Current State:** Inherits from `Base` and `BaseModel`. Redundantly defines `id` and `tenant_id`. Uses `DEFAULT_TENANT_ID`.
    *   **Instruction:**
        *   **Step 1.2.1:** Change class inheritance.
            <replace_in_file>
            <path>src/models/place_search.py</path>
            <diff>
            ------- SEARCH
            class PlaceSearch(Base, BaseModel):
            =======
            class PlaceSearch(BaseModel):
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 1.2.2:** Remove redundant `id` column definition.
            <replace_in_file>
            <path>src/models/place_search.py</path>
            <diff>
            ------- SEARCH
                id = Column(PGUUID, primary_key=True, default=uuid.uuid4)
            =======
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 1.2.3:** Remove redundant `tenant_id` column definition (this will now be inherited from `BaseModel`).
            <replace_in_file>
            <path>src/models/place_search.py</path>
            <diff>
            ------- SEARCH
                tenant_id = Column(
                    PGUUID, ForeignKey("tenants.id"), nullable=False, index=True, default=DEFAULT_TENANT_ID
                )
            =======
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 1.2.4:** Remove import of `DEFAULT_TENANT_ID` as it's no longer needed here.
            <replace_in_file>
            <path>src/models/place_search.py</path>
            <diff>
            ------- SEARCH
            from .enums import SearchStatus
            from .tenant import DEFAULT_TENANT_ID
            =======
            from .enums import SearchStatus
            +++++++ REPLACE
            </diff>
            </replace_in_file>
    *   **Verification:** After these changes, the `PlaceSearch` model should correctly inherit `id` and `tenant_id` from `BaseModel`.

### **Phase 0.2: Schema Centralization**

**Objective:** Create `src/schemas/single_search.py` and move WF1-related schemas from `src/routers/google_maps_api.py` into it.

1.  **File:** `src/schemas/single_search.py` (New File)
    *   **Objective:** Create a new schema file for WF1.
    *   **Instruction:** Create the file with the following content.
        <write_to_file>
        <path>src/schemas/single_search.py</path>
        <content>
        from typing import Dict, Optional
        from datetime import datetime
        from pydantic import BaseModel, Field

        # Request model for WF1 search endpoint
        class SingleSearchRequest(BaseModel):
            business_type: str = Field(..., description="Type of business to search (e.g., 'dentist')")
            location: str = Field(..., description="Location to search (e.g., 'New York, NY')")
            radius_km: int = Field(10, description="Search radius in kilometers")

        # Response model for WF1 search status
        class SingleSearchStatusResponse(BaseModel):
            job_id: str = Field(..., description="Unique job ID for tracking the search")
            status: str = Field(..., description="Current status of the search job")
            progress: float = Field(0.0, description="Progress of the search job (0.0-1.0)")
            created_at: Optional[datetime] = Field(None, description="Timestamp when the job was created")
            updated_at: Optional[datetime] = Field(None, description="Timestamp when the job was last updated")
        </content>
        </write_to_file>
    *   **Verification:** Confirm the file `src/schemas/single_search.py` is created with the specified content.

2.  **File:** `src/routers/google_maps_api.py`
    *   **Objective:** Remove the locally defined schemas as they have been moved.
    *   **Instruction:** Remove the `PlacesSearchRequest` and `PlacesStatusResponse` classes.
        <replace_in_file>
        <path>src/routers/google_maps_api.py</path>
        <diff>
        ------- SEARCH
        # Create API models
        class PlacesSearchRequest(BaseModel):
            business_type: str
            location: str
            radius_km: int = 10
            tenant_id: Optional[str] = None


        class PlacesStatusResponse(BaseModel):
            job_id: str
            status: str
            progress: float = 0.0
            created_at: Optional[datetime] = None
            updated_at: Optional[datetime] = None
        =======
        +++++++ REPLACE
        </diff>
        </replace_in_file>
    *   **Verification:** Confirm these classes are removed from the file.

### **Phase 1: Workflow-Specific Fixes**

**Objective:** Standardize status ENUM usage and remove hardcoded `tenant_id` values.

1.  **File:** `src/routers/google_maps_api.py`
    *   **Objective:** Update imports and use the new schema and ENUM. Remove hardcoded `tenant_id` usage.
    *   **Current State:** Imports `DEFAULT_TENANT_ID`. Uses hardcoded `status="pending"`. Uses local schemas.
    *   **Instruction:**
        *   **Step 2.1.1:** Update imports for schema and `SearchStatus` ENUM.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            from pydantic import BaseModel
            from sqlalchemy.ext.asyncio import AsyncSession

            from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user

            # RBAC imports removed
            # from ..utils.permissions import (
            #     require_permission,
            #     require_feature_enabled,
            #     require_role_level
            # )
            from ..config.settings import settings
            from ..models import PlaceSearch
            from ..services.places.places_search_service import PlacesSearchService
            from ..services.places.places_service import PlacesService
            from ..services.places.places_storage_service import PlacesStorageService
            from ..session.async_session import get_session, get_session_dependency
            =======
            from sqlalchemy.ext.asyncio import AsyncSession

            from ..auth.jwt_auth import get_current_user
            from ..config.settings import settings
            from ..models import PlaceSearch
            from ..models.enums import SearchStatus # Import SearchStatus ENUM
            from ..schemas.single_search import SingleSearchRequest, SingleSearchStatusResponse # Import new schemas
            from ..services.places.places_search_service import PlacesSearchService
            from ..services.places.places_service import PlacesService
            from ..services.places.places_storage_service import PlacesStorageService
            from ..session.async_session import get_session, get_session_dependency
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.2:** Update `search_places` endpoint to use the new `SingleSearchRequest` schema and `SearchStatus.PENDING`. Remove `request.tenant_id` from `PlaceSearch` creation.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.post("/search/places", response_model=Dict)
            async def search_places(
                request: PlacesSearchRequest,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict[str, Any]:
                """
                Search for places using Google Maps API.

                Uses the Google Places API to search for business locations based on type and location.
                Results are stored in the database for later retrieval.

                Args:
                    request: Search parameters
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Dictionary with job ID and status URL
                """
                # Extract user information
                user_info = current_user
                logger.info(
                    f"🔍 User details: user_id={user_info.get('user_id')}, tenant_id={request.tenant_id}"
                )

                # Generate job ID
                job_id = str(uuid.uuid4())

                try:
                    # Router owns the transaction boundary
                    async with session.begin():
                        # Create search record - store radius_km in params JSON field
                        search_record = PlaceSearch(
                            id=job_id,
                            tenant_id=request.tenant_id,
                            business_type=request.business_type,
                            location=request.location,
                            params={"radius_km": request.radius_km},
                            status="pending",
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            user_id=user_info.get("user_id", "unknown"),
                        )
            =======
            @router.post("/search/places", response_model=Dict) # Keep Dict for now, will refactor response_model later
            async def search_places(
                request: SingleSearchRequest, # Use new schema
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict[str, Any]:
                """
                Search for places using Google Maps API.

                Uses the Google Places API to search for business locations based on type and location.
                Results are stored in the database for later retrieval.

                Args:
                    request: Search parameters
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Dictionary with job ID and status URL
                """
                # Extract user information
                user_info = current_user
                logger.info(
                    f"🔍 User details: user_id={user_info.get('user_id')}" # Removed tenant_id from log
                )

                # Generate job ID
                job_id = str(uuid.uuid4())

                try:
                    # Router owns the transaction boundary
                    async with session.begin():
                        # Create search record - store radius_km in params JSON field
                        search_record = PlaceSearch(
                            # id is now automatically generated by BaseModel
                            # tenant_id is now automatically handled by BaseModel
                            business_type=request.business_type,
                            location=request.location,
                            params={"radius_km": request.radius_km},
                            status=SearchStatus.PENDING, # Use ENUM
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            user_id=user_info.get("user_id", "unknown"),
                        )
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.3:** Update `get_search_status` endpoint to use `SingleSearchStatusResponse` and remove hardcoded `DEFAULT_TENANT_ID`.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.get("/search/status/{job_id}", response_model=PlacesStatusResponse)
            async def get_search_status(
                job_id: str,
                request: Request,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> PlacesStatusResponse:
                """
                Get the status of a places search job.

                Args:
                    job_id: Job ID to check
                    request: FastAPI request object
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Job status response
                """
                # Validate input
                if not job_id:
                    raise HTTPException(status_code=400, detail="Job ID is required")

                # Get tenant ID with proper fallbacks
                tenant_id = current_user.get("tenant_id", "")
                if not tenant_id:
                    tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

                logger.info(f"Using JWT validation only (RBAC removed) for tenant: {tenant_id}")

                try:
                    # Check database for status (primary source of truth)
                    async with session.begin():
                        search_record = await places_search_service.get_search_by_id(
                            session=session, job_id=job_id, tenant_id=tenant_id
                        )

                        if not search_record:
                            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                        # Calculate progress based on status
                        progress = 0.0
                        if search_record.status == "processing":
                            progress = 0.5
                        elif search_record.status == "complete":
                            progress = 1.0

                        # Use database status information
                        return PlacesStatusResponse(
                            job_id=job_id,
                            status=search_record.status or "unknown",
                            progress=progress,
                            created_at=search_record.created_at,
                            updated_at=search_record.updated_at,
                        )
            =======
            @router.get("/search/status/{job_id}", response_model=SingleSearchStatusResponse) # Use new schema
            async def get_search_status(
                job_id: str,
                request: Request,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> SingleSearchStatusResponse: # Use new schema
                """
                Get the status of a places search job.

                Args:
                    job_id: Job ID to check
                    request: FastAPI request object
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Job status response
                """
                # Validate input
                if not job_id:
                    raise HTTPException(status_code=400, detail="Job ID is required")

                # Tenant ID is now handled by BaseModel and session context. No explicit tenant_id filtering needed.
                logger.info(f"Using JWT validation only (RBAC removed) for job_id: {job_id}")

                try:
                    # Check database for status (primary source of truth)
                    async with session.begin():
                        # The get_search_by_id method in places_search_service.py needs to be updated to remove tenant_id
                        search_record = await places_search_service.get_search_by_id(
                            session=session, job_id=job_id # Removed tenant_id
                        )

                        if not search_record:
                            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                        # Calculate progress based on status (using ENUM values)
                        progress = 0.0
                        if search_record.status == SearchStatus.RUNNING: # Use ENUM
                            progress = 0.5
                        elif search_record.status == SearchStatus.COMPLETED: # Use ENUM
                            progress = 1.0

                        # Use database status information
                        return SingleSearchStatusResponse( # Use new schema
                            job_id=job_id,
                            status=search_record.status.value, # Use .value for string representation
                            progress=progress,
                            created_at=search_record.created_at,
                            updated_at=search_record.updated_at,
                        )
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.4:** Remove `DEFAULT_TENANT_ID` import.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user
            =======
            from ..auth.jwt_auth import get_current_user
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.5:** Update `process_places_search_background` to remove `tenant_id` and use `SearchStatus` ENUM.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
                    # Set up background task arguments
                    task_args = {
                        "job_id": job_id,
                        "business_type": request.business_type,
                        "location": request.location,
                        "radius_km": request.radius_km,
                        "user_info": user_info,
                        "tenant_id": request.tenant_id,
                    }

                # Start background processing task outside transaction
                async def process_places_search_background(args: Dict[str, Any]):
                    """Background task to process places search."""
                    try:
                        # Create a new session for background task using the ONE AND ONLY ONE acceptable method
                        async with get_session() as bg_session:
                            # Extract task arguments
                            job_id = args["job_id"]
                            business_type = args["business_type"]
                            location = args["location"]
                            radius_km = args["radius_km"]
                            user_info = args["user_info"]

                            # As per architectural mandate: JWT authentication happens ONLY at API gateway endpoints,
                            # while database operations NEVER handle JWT or tenant authentication
                            # We'll still log the tenant_id for tracking purposes
                            logger.info(f"🔍 Processing job {job_id} from API gateway")

                            # Log user info for audit purposes only
                            user_id = user_info.get("user_id", "dev-admin-id")
                            logger.info(f"🔍 Request initiated by user_id {user_id}")

                            # Perform search via the search service inside a transaction
                            async with bg_session.begin():
                                # As per architectural mandate: database operations NEVER handle JWT or tenant authentication
                                result = await places_search_service.search_and_store(
                                    session=bg_session,
                                    job_id=job_id,
                                    business_type=business_type,
                                    location=location,
                                    radius_km=radius_km,
                                    api_key=GOOGLE_MAPS_API_KEY or None,
                                    user_id=user_id,
                                )

                                logger.info(
                                    f"🔍 Completed places search job {job_id}: {result}"
                                )
                    except Exception as e:
                        logger.error(f"Error in background places search task: {str(e)}")
                        # Create a new session for error handling
                        try:
                            async with get_session() as error_session:
                                async with error_session.begin():
                                    # Update status to failed in database
                                    from sqlalchemy import update

                                    from ..models.place_search import PlaceSearch

                                    stmt = (
                                        update(PlaceSearch)
                                        .where(PlaceSearch.id == uuid.UUID(job_id))
                                        .values(status="failed", updated_at=datetime.utcnow())
                                    )
                                    await error_session.execute(stmt)
            =======
                    # Set up background task arguments
                    task_args = {
                        "job_id": job_id,
                        "business_type": request.business_type,
                        "location": request.location,
                        "radius_km": request.radius_km,
                        "user_info": user_info,
                        # Removed tenant_id from task_args
                    }

                # Start background processing task outside transaction
                async def process_places_search_background(args: Dict[str, Any]):
                    """Background task to process places search."""
                    try:
                        # Create a new session for background task using the ONE AND ONLY ONE acceptable method
                        async with get_session() as bg_session:
                            # Extract task arguments
                            job_id = args["job_id"]
                            business_type = args["business_type"]
                            location = args["location"]
                            radius_km = args["radius_km"]
                            user_info = args["user_info"]

                            logger.info(f"🔍 Processing job {job_id} from API gateway")

                            # Log user info for audit purposes only
                            user_id = user_info.get("user_id", "dev-admin-id")
                            logger.info(f"🔍 Request initiated by user_id {user_id}")

                            # Perform search via the search service inside a transaction
                            async with bg_session.begin():
                                result = await places_search_service.search_and_store(
                                    session=bg_session,
                                    job_id=job_id,
                                    business_type=business_type,
                                    location=location,
                                    radius_km=radius_km,
                                    api_key=GOOGLE_MAPS_API_KEY or None,
                                    user_id=user_id,
                                )

                                logger.info(
                                    f"🔍 Completed places search job {job_id}: {result}"
                                )
                    except Exception as e:
                        logger.error(f"Error in background places search task: {str(e)}")
                        # Create a new session for error handling
                        try:
                            async with get_session() as error_session:
                                async with error_session.begin():
                                    # Update status to failed in database
                                    from sqlalchemy import update

                                    from ..models.place_search import PlaceSearch

                                    stmt = (
                                        update(PlaceSearch)
                                        .where(PlaceSearch.id == uuid.UUID(job_id))
                                        .values(status=SearchStatus.FAILED, updated_at=datetime.utcnow()) # Use ENUM
                                    )
                                    await error_session.execute(stmt)
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.6:** Update `get_staging_places` to remove `tenant_id` and `DEFAULT_TENANT_ID` usage.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.get("/places/staging", response_model=List[Dict])
            async def get_staging_places(
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                job_id: Optional[str] = None,
                tenant_id: Optional[str] = None,
                limit: int = Query(100, ge=1, le=1000),
                offset: int = Query(0, ge=0),
            ) -> List[Dict]:
                """
                Get places from the staging area.

                Args:
                    session: Database session
                    current_user: Authenticated user information
                    job_id: Optional job ID filter
                    tenant_id: Optional tenant ID filter
                    limit: Maximum number of places to return
                    offset: Number of places to skip

                Returns:
                    List of place records
                """
                # RBAC permission check removed
                # require_permission(current_user, "places:view")

                # Validate tenant ID
                tenant_id = tenant_id or current_user.get("tenant_id", "")

                # Ensure tenant_id is never None
                if not tenant_id:
                    logger.warning("No tenant ID found in request or user token, using default")
                    tenant_id = DEFAULT_TENANT_ID

                # RBAC feature checks removed
                # await require_feature_enabled(
                #     tenant_id=tenant_id,
                #     feature_name="google_maps_api",
                #     session=session,
                #     user_permissions=current_user.get("permissions", [])
                # )

                logger.info(
                    f"Using JWT validation only (RBAC removed) for staging places, tenant: {tenant_id}"
                )

                try:
                    # Get places from staging
                    async with session.begin():
                        places, total_count = await places_storage_service.get_places_for_job(
                            session=session,
                            tenant_id=tenant_id or DEFAULT_TENANT_ID,
                            job_id=job_id or "",  # Ensure job_id is never None
                            limit=limit,
                            offset=offset,
                        )

                        # Convert to serializable dictionaries
                        result = []
                        for place in places:
                            place_dict = {
                                "id": str(place.id) if place.id is not None else None,
                                "name": place.name,
                                "address": place.address,
                                "website": place.website,
                                "phone": place.phone,
                                "latitude": place.latitude,
                                "longitude": place.longitude,
                                "place_id": place.place_id,
                                "tenant_id": str(place.tenant_id)
                                if place.tenant_id is not None
                                else None,
                                "business_type": place.business_type,
                                "source": place.source,
                                "created_at": place.created_at.isoformat()
                                if place.created_at is not None
                                else None,
                                "updated_at": place.updated_at.isoformat()
                                if place.updated_at is not None
                                else None,
                                "job_id": place.job_id,
                            }
                            result.append(place_dict)

                        return result
            =======
            @router.get("/places/staging", response_model=List[Dict])
            async def get_staging_places(
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                job_id: Optional[str] = None,
                limit: int = Query(100, ge=1, le=1000),
                offset: int = Query(0, ge=0),
            ) -> List[Dict]:
                """
                Get places from the staging area.

                Args:
                    session: Database session
                    current_user: Authenticated user information
                    job_id: Optional job ID filter
                    limit: Maximum number of places to return
                    offset: Number of places to skip

                Returns:
                    List of place records
                """
                logger.info(
                    f"Using JWT validation only (RBAC removed) for staging places."
                )

                try:
                    # Get places from staging
                    async with session.begin():
                        places, total_count = await places_storage_service.get_places_for_job(
                            session=session,
                            job_id=job_id or "",  # Ensure job_id is never None
                            limit=limit,
                            offset=offset,
                        )

                        # Convert to serializable dictionaries
                        result = []
                        for place in places:
                            place_dict = {
                                "id": str(place.id) if place.id is not None else None,
                                "name": place.name,
                                "address": place.address,
                                "website": place.website,
                                "phone": place.phone,
                                "latitude": place.latitude,
                                "longitude": place.longitude,
                                "place_id": place.place_id,
                                # Removed tenant_id from response as it's handled by BaseModel
                                "business_type": place.business_type,
                                "source": place.source,
                                "created_at": place.created_at.isoformat()
                                if place.created_at is not None
                                else None,
                                "updated_at": place.updated_at.isoformat()
                                if place.updated_at is not None
                                else None,
                                "job_id": place.job_id,
                            }
                            result.append(place_dict)

                        return result
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.7:** Update `update_place_status` to remove hardcoded status validation and `tenant_id` usage.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.post("/places/staging/status", response_model=Dict)
            async def update_place_status(
                place_ids: List[str],
                status: str,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                tenant_id: Optional[str] = None,
            ) -> Dict:
                """
                Update the status of places in the staging area.

                Args:
                    place_ids: List of place IDs to update
                    status: New status value
                    session: Database session
                    current_user: Authenticated user information
                    tenant_id: Optional tenant ID

                Returns:
                    Result with count of updated places
                """
                # Validate input
                if not place_ids:
                    raise HTTPException(status_code=400, detail="Place IDs are required")

                if status not in ["approved", "rejected", "pending"]:
                    raise HTTPException(
                        status_code=400, detail="Status must be one of: approved, rejected, pending"
                    )

                # Validate tenant ID
                tenant_id = tenant_id or current_user.get("tenant_id", "")

                # Ensure tenant_id is never None
                if not tenant_id:
                    logger.warning("No tenant ID found in request or user token, using default")
                    tenant_id = DEFAULT_TENANT_ID

                # RBAC feature checks removed
                # await require_feature_enabled(
                #     tenant_id=tenant_id,
                #     feature_name="google_maps_api",
                #     session=session,
                #     user_permissions=current_user.get("permissions", [])
                # )

                logger.info(
                    f"Using JWT validation only (RBAC removed) for update status, tenant: {tenant_id}"
                )

                try:
                    # Update place status
                    async with session.begin():
                        # Use PlacesService for status updates instead of missing PlacesStorageService method
                        count = 0
                        for place_id in place_ids:
                            success = await PlacesService.update_status(
                                session=session,
                                place_id=place_id,
                                status=status,
                                tenant_id=tenant_id,
                                user_id=current_user.get("user_id", "system"),
                            )
                            if success:
                                count += 1

                        return {"success": True, "updated_count": count, "status": status}
            =======
            @router.post("/places/staging/status", response_model=Dict)
            async def update_place_status(
                place_ids: List[str],
                status: str, # Status will be validated by the service
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict:
                """
                Update the status of places in the staging area.

                Args:
                    place_ids: List of place IDs to update
                    status: New status value
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Result with count of updated places
                """
                # Validate input
                if not place_ids:
                    raise HTTPException(status_code=400, detail="Place IDs are required")

                logger.info(
                    f"Using JWT validation only (RBAC removed) for update status."
                )

                try:
                    # Update place status
                    async with session.begin():
                        # Use PlacesService for status updates instead of missing PlacesStorageService method
                        count = 0
                        for place_id in place_ids:
                            success = await PlacesService.update_status(
                                session=session,
                                place_id=place_id,
                                status=status,
                                user_id=current_user.get("user_id", "system"),
                            )
                            if success:
                                count += 1

                        return {"success": True, "updated_count": count, "status": status}
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.8:** Update `batch_update_places` to remove `tenant_id` usage.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.post("/places/staging/batch", response_model=Dict)
            async def batch_update_places(
                places: List[Dict],
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                tenant_id: Optional[str] = None,
            ) -> Dict:
                """
                Batch update places in the staging area.

                Args:
                    places: List of place records to update
                    session: Database session
                    current_user: Authenticated user information
                    tenant_id: Optional tenant ID

                Returns:
                    Result with count of updated places
                """
                # Validate input
                if not places:
                    raise HTTPException(status_code=400, detail="Places are required")

                # Validate tenant ID
                tenant_id = tenant_id or current_user.get("tenant_id", "")

                # Ensure tenant_id is never None
                if not tenant_id:
                    logger.warning("No tenant ID found in request or user token, using default")
                    tenant_id = DEFAULT_TENANT_ID

                # RBAC feature checks removed
                # await require_feature_enabled(
                #     tenant_id=tenant_id,
                #     feature_name="google_maps_api",
                #     session=session,
                #     user_permissions=current_user.get("permissions", [])
                # )

                logger.info(
                    f"Using JWT validation only (RBAC removed) for batch update, tenant: {tenant_id}"
                )

                try:
                    # Convert dict records to Place model instances
                    place_ids = []
                    for place_dict in places:
                        # We need to ensure each place has an ID
                        if not place_dict.get("id"):
                            raise HTTPException(
                                status_code=400, detail="Each place must have an ID"
                            )

                        # Collect place IDs for batch update
                        place_ids.append(place_dict.get("id"))

                    # Update the places using PlacesService
                    async with session.begin():
                        # Use batch_update_status
                        updated_count = await PlacesService.batch_update_status(
                            session=session,
                            place_ids=place_ids,
                            status="updated",  # Default status
                            tenant_id=tenant_id,
                        )

                        return {"success": True, "updated_count": updated_count}
            =======
            @router.post("/places/staging/batch", response_model=Dict)
            async def batch_update_places(
                places: List[Dict],
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
            ) -> Dict:
                """
                Batch update places in the staging area.

                Args:
                    places: List of place records to update
                    session: Database session
                    current_user: Authenticated user information

                Returns:
                    Result with count of updated places
                """
                # Validate input
                if not places:
                    raise HTTPException(status_code=400, detail="Places are required")

                logger.info(
                    f"Using JWT validation only (RBAC removed) for batch update."
                )

                try:
                    # Convert dict records to Place model instances
                    place_ids = []
                    for place_dict in places:
                        # We need to ensure each place has an ID
                        if not place_dict.get("id"):
                            raise HTTPException(
                                status_code=400, detail="Each place must have an ID"
                            )

                        # Collect place IDs for batch update
                        place_ids.append(place_dict.get("id"))

                    # Update the places using PlacesService
                    async with session.begin():
                        # Use batch_update_status
                        updated_count = await PlacesService.batch_update_status(
                            session=session,
                            place_ids=place_ids,
                            status="updated",  # Default status
                        )

                        return {"success": True, "updated_count": updated_count}
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.9:** Update `get_job_results` to remove `tenant_id` and `DEFAULT_TENANT_ID` usage.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.get("/results/{job_id}", response_model=Dict)
            async def get_job_results(
                job_id: str,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                limit: int = Query(100, ge=1, le=1000),
                offset: int = Query(0, ge=0),
            ) -> Dict:
                """
                Get places discovered for a specific job ID.

                This endpoint retrieves all places found during a discovery scan for a given job.

                Args:
                    job_id: The ID of the search job
                    session: Database session
                    current_user: Authenticated user information
                    limit: Maximum number of results to return
                    offset: Pagination offset

                Returns:
                    Dictionary with places data, total count, and job information
                """
                # Validate tenant ID with proper fallbacks
                tenant_id = current_user.get("tenant_id", "")
                if not tenant_id:
                    tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

                logger.info(f"Retrieving job results for job_id={job_id}, tenant_id={tenant_id}")

                try:
                    # Get search job details first to include in response
                    from sqlalchemy import select

                    from ..models.place_search import PlaceSearch

                    # Get job details
                    stmt = select(PlaceSearch).where(PlaceSearch.id == uuid.UUID(job_id))
                    result = await session.execute(stmt)
                    job = result.scalars().first()

                    if not job:
                        logger.warning(f"Job {job_id} not found")
                        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                    # Use the get_places_for_job method from the storage service
                    places_list, total_count = await places_storage_service.get_places_for_job(
                        session=session,
                        job_id=job_id,
                        tenant_id=tenant_id,
                        limit=limit,
                        offset=offset,
                    )

                    # Convert to serializable dictionaries
                    places = []
                    for place in places_list:
                        # Create base dictionary with required fields
                        place_dict = {
                            "id": str(place.id) if place.id is not None else None,
                            "name": place.name,
                            "place_id": place.place_id,
                            "business_type": place.business_type,
                            "latitude": place.latitude,
                            "longitude": place.longitude,
                            "status": getattr(place, "status", "new"),
                        }

                        # Add optional fields if they exist
                        if (
                            hasattr(place, "formatted_address")
                            and place.formatted_address is not None
                        ):
                            place_dict["formatted_address"] = place.formatted_address

                        if hasattr(place, "vicinity") and place.vicinity is not None:
                            place_dict["vicinity"] = place.vicinity

                        if hasattr(place, "rating") and place.rating is not None:
                            place_dict["rating"] = place.rating

                        if (
                            hasattr(place, "user_ratings_total")
                            and place.user_ratings_total is not None
                        ):
                            place_dict["user_ratings_total"] = place.user_ratings_total

                        # Add timestamps
                        if hasattr(place, "search_time") and place.search_time is not None:
                            place_dict["search_time"] = place.search_time.isoformat()

                        # Add reference to job
                        if place.search_job_id is not None:
                            place_dict["search_job_id"] = str(place.search_job_id)

                        places.append(place_dict)

                    # Return formatted response
                    return {
                        "places": places,
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "job_info": {
                            "job_id": str(job.id),
                            "business_type": job.business_type,
                            "location": job.location,
                            "status": job.status,
                            "created_at": job.created_at.isoformat()
                            if job.created_at is not None
                            else None,
                            "completed_at": job.updated_at.isoformat()
                            if job.updated_at is not None
                            else None,
                        },
                        "filters": {},
                    }
            =======
            @router.get("/results/{job_id}", response_model=Dict)
            async def get_job_results(
                job_id: str,
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                limit: int = Query(100, ge=1, le=1000),
                offset: int = Query(0, ge=0),
            ) -> Dict:
                """
                Get places discovered for a specific job ID.

                This endpoint retrieves all places found during a discovery scan for a given job.

                Args:
                    job_id: The ID of the search job
                    session: Database session
                    current_user: Authenticated user information
                    limit: Maximum number of results to return
                    offset: Pagination offset

                Returns:
                    Dictionary with places data, total count, and job information
                """
                logger.info(f"Retrieving job results for job_id={job_id}")

                try:
                    # Get search job details first to include in response
                    from sqlalchemy import select

                    from ..models.place_search import PlaceSearch

                    # Get job details
                    stmt = select(PlaceSearch).where(PlaceSearch.id == uuid.UUID(job_id))
                    result = await session.execute(stmt)
                    job = result.scalars().first()

                    if not job:
                        logger.warning(f"Job {job_id} not found")
                        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

                    # Use the get_places_for_job method from the storage service
                    places_list, total_count = await places_storage_service.get_places_for_job(
                        session=session,
                        job_id=job_id,
                        limit=limit,
                        offset=offset,
                    )

                    # Convert to serializable dictionaries
                    places = []
                    for place in places_list:
                        # Create base dictionary with required fields
                        place_dict = {
                            "id": str(place.id) if place.id is not None else None,
                            "name": place.name,
                            "place_id": place.place_id,
                            "business_type": place.business_type,
                            "latitude": place.latitude,
                            "longitude": place.longitude,
                            "status": getattr(place, "status", "new"),
                        }

                        # Add optional fields if they exist
                        if (
                            hasattr(place, "formatted_address")
                            and place.formatted_address is not None
                        ):
                            place_dict["formatted_address"] = place.formatted_address

                        if hasattr(place, "vicinity") and place.vicinity is not None:
                            place_dict["vicinity"] = place.vicinity

                        if hasattr(place, "rating") and place.rating is not None:
                            place_dict["rating"] = place.rating

                        if (
                            hasattr(place, "user_ratings_total")
                            and place.user_ratings_total is not None
                        ):
                            place_dict["user_ratings_total"] = place.user_ratings_total

                        # Add timestamps
                        if hasattr(place, "search_time") and place.search_time is not None:
                            place_dict["search_time"] = place.search_time.isoformat()

                        # Add reference to job
                        if place.search_job_id is not None:
                            place_dict["search_job_id"] = str(place.search_job_id)

                        places.append(place_dict)

                    # Return formatted response
                    return {
                        "places": places,
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "job_info": {
                            "job_id": str(job.id),
                            "business_type": job.business_type,
                            "location": job.location,
                            "status": job.status.value, # Use .value for ENUM
                            "created_at": job.created_at.isoformat()
                            if job.created_at is not None
                            else None,
                            "completed_at": job.updated_at.isoformat()
                            if job.updated_at is not None
                            else None,
                        },
                        "filters": {},
                    }
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.1.10:** Update `get_search_history` to remove `tenant_id` and `DEFAULT_TENANT_ID` usage.
            <replace_in_file>
            <path>src/routers/google_maps_api.py</path>
            <diff>
            ------- SEARCH
            @router.get("/search/history", response_model=List[Dict])
            async def get_search_history(
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                limit: int = Query(20, ge=1, le=100),
                offset: int = Query(0, ge=0),
                status: Optional[str] = None,
                tenant_id: Optional[str] = None,
            ) -> List[Dict]:
                """
                Get search history for the tenant.

                This endpoint retrieves the history of search jobs for a tenant,
                which can be used to avoid duplicate searches and view past results.

                Args:
                    session: Database session
                    current_user: Authenticated user information
                    limit: Maximum number of records to return
                    offset: Offset for pagination
                    status: Optional filter by status
                    tenant_id: Optional tenant ID override

                Returns:
                    List of search job records
                """
                # Validate tenant ID with proper fallbacks
                tenant_id = tenant_id or current_user.get("tenant_id", "")
                if not tenant_id:
                    tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

                logger.info(f"Retrieving search history for tenant_id={tenant_id}")

                try:
                    from sqlalchemy import desc, select

                    from ..models.place_search import PlaceSearch

                    # Build base query
                    query = (
                        select(PlaceSearch)
                        .where(PlaceSearch.tenant_id == uuid.UUID(tenant_id))
                        .order_by(desc(PlaceSearch.created_at))
                    )

                    # Add status filter if provided
                    if status:
                        query = query.where(PlaceSearch.status == status)

                    # Add pagination
                    query = query.limit(limit).offset(offset)

                    # Execute query
                    result = await session.execute(query)
                    searches = result.scalars().all()

                    # Convert to serializable dictionaries
                    search_history = []
                    for search in searches:
                        # Create search dictionary with essential fields
                        search_dict = {
                            "id": str(search.id),
                            "business_type": search.business_type,
                            "location": search.location,
                            "status": search.status,
                            "created_at": search.created_at.isoformat()
                            if search.created_at is not None
                            else None,
                            "updated_at": search.updated_at.isoformat()
                            if search.updated_at is not None
                            else None,
                        }

                        # Add user ID if available
                        if search.user_id is not None:
                            search_dict["user_id"] = search.user_id

                        # Add parameters if available
                        if search.params is not None:
                            search_dict["params"] = search.params

                        search_history.append(search_dict)

                    return search_history
            =======
            @router.get("/search/history", response_model=List[Dict])
            async def get_search_history(
                session: AsyncSession = Depends(get_session_dependency),
                current_user: Dict = Depends(get_current_user),
                limit: int = Query(20, ge=1, le=100),
                offset: int = Query(0, ge=0),
                status: Optional[SearchStatus] = Query(None, description="Filter by search status"), # Use ENUM
            ) -> List[Dict]:
                """
                Get search history for the tenant.

                This endpoint retrieves the history of search jobs,
                which can be used to avoid duplicate searches and view past results.

                Args:
                    session: Database session
                    current_user: Authenticated user information
                    limit: Maximum number of records to return
                    offset: Offset for pagination
                    status: Optional filter by status
                    tenant_id: Optional tenant ID override

                Returns:
                    List of search job records
                """
                logger.info(f"Retrieving search history.")

                try:
                    from sqlalchemy import desc, select

                    from ..models.place_search import PlaceSearch

                    # Build base query (tenant_id is handled by BaseModel)
                    query = (
                        select(PlaceSearch)
                        .order_by(desc(PlaceSearch.created_at))
                    )

                    # Add status filter if provided
                    if status:
                        query = query.where(PlaceSearch.status == status) # Use ENUM

                    # Add pagination
                    query = query.limit(limit).offset(offset)

                    # Execute query
                    result = await session.execute(query)
                    searches = result.scalars().all()

                    # Convert to serializable dictionaries
                    search_history = []
                    for search in searches:
                        # Create search dictionary with essential fields
                        search_dict = {
                            "id": str(search.id),
                            "business_type": search.business_type,
                            "location": search.location,
                            "status": search.status.value, # Use .value for ENUM
                            "created_at": search.created_at.isoformat()
                            if search.created_at is not None
                            else None,
                            "updated_at": search.updated_at.isoformat()
                            if search.updated_at is not None
                            else None,
                        }

                        # Add user ID if available
                        if search.user_id is not None:
                            search_dict["user_id"] = search.user_id

                        # Add parameters if available
                        if search.params is not None:
                            search_dict["params"] = search.params

                        search_history.append(search_dict)

                    return search_history
            +++++++ REPLACE
            </diff>
            </replace_in_file>
    *   **Verification:** Confirm changes are applied in `google_maps_api.py`.

2.  **File:** `src/services/places/places_search_service.py`
    *   **Objective:** Standardize status updates to use `SearchStatus` ENUM. Remove hardcoded `tenant_id`.
    *   **Current State:** Uses hardcoded strings for status. Contains hardcoded `tenant_id`.
    *   **Instruction:**
        *   **Step 2.2.1:** Update imports to include `SearchStatus`.
            <replace_in_file>
            <path>src/services/places/places_search_service.py</path>
            <diff>
            ------- SEARCH
            from sqlalchemy.ext.asyncio import AsyncSession

            # Removed custom error service import in favor of FastAPI's built-in error handling

            logger = logging.getLogger(__name__)
            =======
            from sqlalchemy.ext.asyncio import AsyncSession

            from ...models.enums import SearchStatus # Import SearchStatus

            logger = logging.getLogger(__name__)
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.2.2:** Update `search_and_store` to use `SearchStatus` ENUM and remove hardcoded `tenant_id`.
            <replace_in_file>
            <path>src/services/places/places_search_service.py</path>
            <diff>
            ------- SEARCH
            async def search_and_store(
                session: Any,
                job_id: str,
                business_type: str,
                location: str,
                radius_km: int = 10,
                api_key: Optional[str] = None,
                user_id: Optional[str] = None,
            ) -> Dict[str, Any]:
                """
                Search for places and store them in the database.

                Args:
                    session: Database session
                    job_id: Unique job identifier
                    business_type: Type of business to search
                    location: Location to search
                    radius_km: Search radius in kilometers
                    api_key: Google Maps API key (optional)
                    user_id: User ID for attribution

                Returns:
                    Dictionary with search results and status
                """
                from sqlalchemy import update

                from ...models.place_search import PlaceSearch
                from .places_storage_service import PlacesStorageService

                try:
                    # Update the search record to mark it as processing
                    stmt = (
                        update(PlaceSearch)
                        .where(PlaceSearch.id == uuid.UUID(job_id))
                        .values(status="processing", updated_at=datetime.utcnow())
                    )
                    await session.execute(stmt)
                    # Note: We don't commit here as the router owns the transaction

                    # Perform the search
                    places = await PlacesSearchService.search_places(
                        location=location,
                        business_type=business_type,
                        radius_km=radius_km,
                        max_results=20,
                    )

                    # Get storage service to store places
                    storage_service = PlacesStorageService()

                    # Store the places in the database
                    tenant_id = "550e8400-e29b-41d4-a716-446655440000"  # Default tenant ID
                    success_count, failed_places = await storage_service.store_places(
                        session=session,
                        places=places,
                        search_id=job_id,
                        tenant_id=tenant_id,
                        user_id=user_id or "00000000-0000-0000-0000-000000000000",
                    )

                    # Update the status in the database
                    stmt = (
                        update(PlaceSearch)
                        .where(PlaceSearch.id == uuid.UUID(job_id))
                        .values(status="complete", updated_at=datetime.utcnow())
                    )
                    await session.execute(stmt)
                    # Note: We don't commit here as the router owns the transaction

                    return {"success": True, "places_count": success_count, "job_id": job_id}

                except Exception as e:
                    logger.error(f"Error in search and store: {str(e)}")

                    # Update the status to failed in the database
                    try:
                        stmt = (
                            update(PlaceSearch)
                            .where(PlaceSearch.id == uuid.UUID(job_id))
                            .values(status="failed", updated_at=datetime.utcnow())
                        )
                        await session.execute(stmt)
            =======
            async def search_and_store(
                session: AsyncSession, # Use AsyncSession type hint
                job_id: str,
                business_type: str,
                location: str,
                radius_km: int = 10,
                api_key: Optional[str] = None,
                user_id: Optional[str] = None,
            ) -> Dict[str, Any]:
                """
                Search for places and store them in the database.

                Args:
                    session: Database session
                    job_id: Unique job identifier
                    business_type: Type of business to search
                    location: Location to search
                    radius_km: Search radius in kilometers
                    api_key: Google Maps API key (optional)
                    user_id: User ID for attribution

                Returns:
                    Dictionary with search results and status
                """
                from sqlalchemy import update

                from ...models.place_search import PlaceSearch
                from .places_storage_service import PlacesStorageService

                try:
                    # Update the search record to mark it as processing
                    stmt = (
                        update(PlaceSearch)
                        .where(PlaceSearch.id == uuid.UUID(job_id))
                        .values(status=SearchStatus.RUNNING, updated_at=datetime.utcnow()) # Use ENUM
                    )
                    await session.execute(stmt)
                    # Note: We don't commit here as the router owns the transaction

                    # Perform the search
                    places = await PlacesSearchService.search_places(
                        location=location,
                        business_type=business_type,
                        radius_km=radius_km,
                        max_results=20,
                    )

                    # Get storage service to store places
                    storage_service = PlacesStorageService()

                    # Store the places in the database
                    # Tenant ID is now handled by BaseModel
                    success_count, failed_places = await storage_service.store_places(
                        session=session,
                        places=places,
                        search_id=job_id,
                        user_id=user_id or "00000000-0000-0000-0000-000000000000",
                    )

                    # Update the status in the database
                    stmt = (
                        update(PlaceSearch)
                        .where(PlaceSearch.id == uuid.UUID(job_id))
                        .values(status=SearchStatus.COMPLETED, updated_at=datetime.utcnow()) # Use ENUM
                    )
                    await session.execute(stmt)
                    # Note: We don't commit here as the router owns the transaction

                    return {"success": True, "places_count": success_count, "job_id": job_id}

                except Exception as e:
                    logger.error(f"Error in search and store: {str(e)}")

                    # Update the status to failed in the database
                    try:
                        stmt = (
                            update(PlaceSearch)
                            .where(PlaceSearch.id == uuid.UUID(job_id))
                            .values(status=SearchStatus.FAILED, updated_at=datetime.utcnow()) # Use ENUM
                        )
                        await session.execute(stmt)
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.2.3:** Update `get_search_by_id` to remove `tenant_id` parameter.
            <replace_in_file>
            <path>src/services/places/places_search_service.py</path>
            <diff>
            ------- SEARCH
            async def get_search_by_id(
                session: Any, job_id: str, tenant_id: str
            ) -> Optional[Any]:
            =======
            async def get_search_by_id(
                session: AsyncSession, job_id: str # Removed tenant_id
            ) -> Optional[Any]:
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.2.4:** Remove `process_places_search_background` function, as it's a duplicate and uses an anti-pattern for session management.
            <replace_in_file>
            <path>src/services/places/places_search_service.py</path>
            <diff>
            ------- SEARCH
            async def process_places_search_background(session: AsyncSession,
                job_id: str,
                business_type: str,
                location: str,
                radius_km: int = 10,
                api_key: Optional[str] = None,
                user_id: Optional[str] = None,
            ):
                """
                Process a places search in the background.

                Args:
                    job_id (str): The ID of the job.
                    business_type (str): The type of business to search for.
                    location (str): The location to search in.
                    radius_km (int, optional): The radius in kilometers to search. Defaults to 10.
                    api_key (Optional[str], optional): The Google Maps API key. Defaults to None.
                    user_id (Optional[str], optional): The ID of the user performing the search. Defaults to None.
                """
                print(f"DEBUGGING: Starting background task for job_id {job_id}")

                import uuid

                from sqlalchemy import select

                from ...models import Place, SearchJob
                from ...services.job_service import job_service

                # Create job_uuid from job_id
                try:
                    job_uuid = uuid.UUID(job_id)
                except ValueError:
                    print(f"DEBUGGING ERROR: Invalid job_id format: {job_id}")
                    return

                # Create a dedicated session for background task
                async with get_session() as session:
                    # Add these options to disable prepared statements for Supavisor compatibility
                    session.bind.engine.update_execution_options(
                        no_parameters=True,  # Disable prepared statements
                        statement_cache_size=0,  # Disable statement caching
                    )
                    print("DEBUGGING: Created session with Supavisor compatibility options")

                    try:
                        # Update job status to processing
                        async with session.begin():
                            await job_service.update_status(
                                session=session, job_id=job_uuid, status="processing", progress=0.1
                            )

                        # Perform the search
                        print(
                            f"DEBUGGING: Performing search for {business_type} in {location} with radius {radius_km}km"
                        )

                        search_results = []
                        try:
                            # Execute Google Maps API search
                            places_service = PlacesSearchService()
                            search_results = await places_service.search_places(
                                location=location,
                                business_type=business_type,
                                radius_km=radius_km,
                                max_results=50,  # Reasonable limit for testing
                            )

                            print(f"DEBUGGING: Found {len(search_results)} places")

                            # Store results
                            async with session.begin():
                                # Find job by id to get tenant_id
                                job_query = select(SearchJob).where(SearchJob.job_id == job_uuid)
                                job_result = await session.execute(
                                    job_query,
                                    execution_options={
                                        "no_parameters": True,
                                        "statement_cache_size": 0,
                                    },
                                )
                                job = job_result.scalars().first()

                                if not job:
                                    raise ValueError(f"Job {job_id} not found")

                                # Get tenant_id from job
                                tenant_id = job.tenant_id

                                # Store each place
                                for place in search_results:
                                    # Check if place already exists
                                    place_id = place.get("place_id")
                                    if not place_id:
                                        continue

                                    existing_query = select(Place).where(
                                        Place.place_id == place_id, Place.tenant_id == tenant_id
                                    )
                                    existing_result = await session.execute(
                                        existing_query,
                                        execution_options={
                                            "no_parameters": True,
                                            "statement_cache_size": 0,
                                        },
                                    )
                                    existing_place = existing_result.scalars().first()

                                    if existing_place:
                                        # Update existing place
                                        for key, value in place.items():
                                            if hasattr(existing_place, key) and key != "id":
                                                setattr(existing_place, key, value)
                                        session.add(existing_place)
                                    else:
                                        # Create new place
                                        new_place = Place(
                                            id=uuid.uuid4(),
                                            tenant_id=tenant_id,
                                            job_id=job_uuid,
                                            place_id=place_id,
                                            name=place.get("name", ""),
                                            address=place.get("address", ""),
                                            phone=place.get("phone", ""),
                                            website=place.get("website", ""),
                                            location_lat=place.get("location_lat"),
                                            location_lng=place.get("location_lng"),
                                            rating=place.get("rating"),
                                            place_types=place.get("place_types", []),
                                            business_status=place.get("business_status", ""),
                                            raw_data=place,
                                        )
                                        session.add(new_place)

                                await session.flush()

                            # Update job status to complete
                            async with session.begin():
                                await job_service.update_status(
                                    session=session,
                                    job_id=job_uuid,
                                    status="completed",
                                    progress=1.0,
                                    result_data={
                                        "places_found": len(search_results),
                                        "location": location,
                                        "business_type": business_type,
                                        "radius_km": radius_km,
                                    },
                                )

                            print(f"DEBUGGING: Successfully completed search job {job_id}")

                        except Exception as search_error:
                            print(f"DEBUGGING ERROR in search: {str(search_error)}")
                            # Update job status to failed
                            async with session.begin():
                                await job_service.update_status(
                                    session=session,
                                    job_id=job_uuid,
                                    status="failed",
                                    error=str(search_error),
                                    progress=0,
                                )

                    except Exception as e:
                        print(f"DEBUGGING CRITICAL ERROR: {str(e)}")
                        # Try to update status one last time
                        try:
                            async with session.begin():
                                await job_service.update_status(
                                    session=session,
                                    job_id=job_uuid,
                                    status="failed",
                                    error=f"Critical error: {str(e)}",
                                    progress=0,
                                )
                            except Exception as final_error:
                                print(f"DEBUGGING: Failed to update job status: {str(final_error)}")
            =======
            +++++++ REPLACE
            </diff>
            </replace_in_file>
    *   **Verification:** Confirm changes are applied in `places_search_service.py`.

3.  **File:** `src/services/places/places_storage_service.py`
    *   **Objective:** Remove hardcoded `tenant_id` and `DEFAULT_TENANT_ID` usage.
    *   **Current State:** Uses hardcoded `tenant_id` and `DEFAULT_TENANT_ID`.
    *   **Instruction:**
        *   **Step 2.3.1:** Update `store_places` to remove `tenant_id` parameter and related hardcoded logic.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
            async def store_places(
                session: AsyncSession,
                places: List[Dict[str, Any]],
                search_id: str,
                tenant_id: str,
                user_id: str,
            ) -> Tuple[int, List[Dict[str, Any]]]:
                """
                Store places from Google Maps API.

                Args:
                    session: SQLAlchemy session
                    places: List of places to store
                    search_id: Search job ID
                    tenant_id: Tenant ID for isolation
                    user_id: User ID for attribution

                Returns:
                    Tuple of (success_count, failed_places)
                """
                if not places:
                    logger.info("No places to store")
                    return 0, []

                # Convert string UUIDs to UUID objects with better error handling
                tenant_uuid = None
                user_uuid = None
                search_uuid = None
                user_name = "Unknown User"

                try:
                    # Try to convert tenant_id to UUID
                    if tenant_id and tenant_id != "default":
                        try:
                            tenant_uuid = (
                                uuid.UUID(tenant_id)
                                if isinstance(tenant_id, str)
                                else tenant_id
                            )
                        except ValueError:
                            logger.warning(
                                f"Invalid UUID format for tenant_id: {tenant_id}, using default UUID"
                            )
                            tenant_uuid = uuid.UUID(
                                "550e8400-e29b-41d4-a716-446655440000"
                            )  # Default UUID
                        else:
                            # Use default tenant ID if not provided or is "default"
                            tenant_uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
                            logger.info("Using default tenant UUID")
            =======
            async def store_places(
                session: AsyncSession,
                places: List[Dict[str, Any]],
                search_id: str,
                user_id: str,
            ) -> Tuple[int, List[Dict[str, Any]]]:
                """
                Store places from Google Maps API.

                Args:
                    session: SQLAlchemy session
                    places: List of places to store
                    search_id: Search job ID
                    user_id: User ID for attribution

                Returns:
                    Tuple of (success_count, failed_places)
                """
                if not places:
                    logger.info("No places to store")
                    return 0, []

                # Convert string UUIDs to UUID objects with better error handling
                user_uuid = None
                search_uuid = None
                user_name = "Unknown User"

                try:
                    # Tenant ID is handled by BaseModel. No explicit tenant_id handling needed here.
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.3.2:** Remove `tenant_uuid` from log and `new_place_data`.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
                logger.info(
                    f"Using tenant_uuid: {tenant_uuid}, user_uuid: {user_uuid}, search_uuid: {search_uuid}"
                )
            =======
                logger.info(
                    f"Using user_uuid: {user_uuid}, search_uuid: {search_uuid}"
                )
            +++++++ REPLACE
            </diff>
            </replace_in_file>
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
                        # Ensure tenant_id is a valid UUID
                        new_place_data["tenant_id"] = tenant_uuid

                        # IMPORTANT: Always provide default UUIDs for created_by and user_id
                        # The database has a NOT NULL constraint on these columns
                        new_place_data["created_by"] = user_uuid
                        new_place_data["user_id"] = user_uuid
            =======
                        # Tenant ID is handled by BaseModel. No explicit tenant_id handling needed here.
                        # IMPORTANT: Always provide default UUIDs for created_by and user_id
                        # The database has a NOT NULL constraint on these columns
                        new_place_data["created_by"] = user_uuid
                        new_place_data["user_id"] = user_uuid
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.3.3:** Update `get_places_for_job` to remove `tenant_id` parameter and filtering.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
            async def get_places_for_job(
                session: AsyncSession,
                job_id: str,
                tenant_id: str,
                limit: int = 100,
                offset: int = 0,
            ) -> Tuple[List[Place], int]:
                """
                Get places associated with a specific job.

                Args:
                    session: SQLAlchemy session
                    job_id: Job ID
                    tenant_id: Tenant ID for isolation
                    limit: Maximum number of records
                    offset: Offset for pagination

                Returns:
                    Tuple of (places, total_count)
                """
                try:
                    job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
                    tenant_uuid = (
                        uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
                    )
                except ValueError as e:
                    logger.error(f"Invalid UUID format: {e}")
                    return [], 0

                # Build query
                query = (
                    select(Place)
                    .where(
                        and_(Place.search_job_id == job_uuid, Place.tenant_id == tenant_uuid)
                    )
                    .limit(limit)
                    .offset(offset)
                )

                # Get total count
                count_query = select(func.count()).select_from(
                    select(Place)
                    .where(
                        and_(Place.search_job_id == job_uuid, Place.tenant_id == tenant_uuid)
                    )
                    .subquery()
                )
            =======
            async def get_places_for_job(
                session: AsyncSession,
                job_id: str,
                limit: int = 100,
                offset: int = 0,
            ) -> Tuple[List[Place], int]:
                """
                Get places associated with a specific job.

                Args:
                    session: SQLAlchemy session
                    job_id: Job ID
                    limit: Maximum number of records
                    offset: Offset for pagination

                Returns:
                    Tuple of (places, total_count)
                """
                try:
                    job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
                except ValueError as e:
                    logger.error(f"Invalid UUID format: {e}")
                    return [], 0

                # Build query (tenant_id is handled by BaseModel)
                query = (
                    select(Place)
                    .where(Place.search_job_id == job_uuid)
                    .limit(limit)
                    .offset(offset)
                )

                # Get total count
                count_query = select(func.count()).select_from(
                    select(Place)
                    .where(Place.search_job_id == job_uuid)
                    .subquery()
                )
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.3.4:** Update `get_places_from_staging` to remove `tenant_id` parameter and filtering.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
            async def get_places_from_staging(
                session: AsyncSession,
                tenant_id: str,
                job_id: Optional[str] = None,
                status: Optional[str] = None,
                business_type: Optional[str] = None,
                location: Optional[str] = None,
                limit: int = 100,
                offset: int = 0,
            ) -> Tuple[List[Place], int]:
                """
                Get places from the staging table with filtering capabilities.

                Args:
                    session: SQLAlchemy session
                    tenant_id: Tenant ID for isolation
                    job_id: Optional job ID to filter by
                    status: Optional status to filter by (New, Selected, Maybe, Not a Fit, Archived)
                    business_type: Optional business type to filter by
                    location: Optional location to filter by
                    limit: Maximum number of records to return
                    offset: Offset for pagination

                Returns:
                    Tuple of (places, total_count)
                """
                try:
                    # Convert tenant_id to UUID
                    tenant_uuid = (
                        uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
                    )

                    # Build base query for places
                    query = select(Place).where(Place.tenant_id == tenant_uuid)

                    # Apply optional filters
                    if job_id:
                        try:
                            job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
                            query = query.where(Place.search_job_id == job_uuid)
                        except ValueError:
                            logger.warning(f"Invalid UUID format for job_id: {job_id}")

                    if status:
                        # Filter by status - using the enum type from database
                        query = query.where(Place.status == status)

                    if business_type:
                        # Add ILIKE for case-insensitive partial matching
                        query = query.where(Place.business_type.ilike(f"%{business_type}%"))

                    if location:
                        # Search in both search_location and formatted_address fields
                        location_filter = or_(
                            Place.search_location.ilike(f"%{location}%"),
                            Place.formatted_address.ilike(f"%{location}%"),
                        )
                        query = query.where(location_filter)

                    # Add order by most recent search_time
                    query = query.order_by(Place.search_time.desc())

                    # Get total count for pagination
                    count_query = select(func.count()).select_from(query.subquery())
                    count_result = await session.scalar(count_query)
                    total_count = 0 if count_result is None else count_result

                    # Apply pagination
                    paginated_query = query.limit(limit).offset(offset)

                    # Execute query
                    result = await session.execute(paginated_query)
                    places = result.scalars().all()

                    return list(places), total_count
            =======
            async def get_places_from_staging(
                session: AsyncSession,
                job_id: Optional[str] = None,
                status: Optional[str] = None,
                business_type: Optional[str] = None,
                location: Optional[str] = None,
                limit: int = 100,
                offset: int = 0,
            ) -> Tuple[List[Place], int]:
                """
                Get places from the staging table with filtering capabilities.

                Args:
                    session: SQLAlchemy session
                    job_id: Optional job ID to filter by
                    status: Optional status to filter by (New, Selected, Maybe, Not a Fit, Archived)
                    business_type: Optional business type to filter by
                    location: Optional location to filter by
                    limit: Maximum number of records to return
                    offset: Offset for pagination

                Returns:
                    Tuple of (places, total_count)
                """
                try:
                    # Build base query for places (tenant_id is handled by BaseModel)
                    query = select(Place)

                    # Apply optional filters
                    if job_id:
                        try:
                            job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
                            query = query.where(Place.search_job_id == job_uuid)
                        except ValueError:
                            logger.warning(f"Invalid UUID format for job_id: {job_id}")

                    if status:
                        # Filter by status - using the enum type from database
                        query = query.where(Place.status == status)

                    if business_type:
                        # Add ILIKE for case-insensitive partial matching
                        query = query.where(Place.business_type.ilike(f"%{business_type}%"))

                    if location:
                        # Search in both search_location and formatted_address fields
                        location_filter = or_(
                            Place.search_location.ilike(f"%{location}%"),
                            Place.formatted_address.ilike(f"%{location}%"),
                        )
                        query = query.where(location_filter)

                    # Add order by most recent search_time
                    query = query.order_by(Place.search_time.desc())

                    # Get total count for pagination
                    count_query = select(func.count()).select_from(query.subquery())
                    count_result = await session.scalar(count_query)
                    total_count = 0 if count_result is None else count_result

                    # Apply pagination
                    paginated_query = query.limit(limit).offset(offset)

                    # Execute query
                    result = await session.execute(paginated_query)
                    places = result.scalars().all()

                    return list(places), total_count
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.3.5:** Update `update_places_status` to remove `tenant_id` parameter and filtering.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
            async def update_places_status(
                session: AsyncSession,
                place_id: str,
                status: str,
                tenant_id: Optional[str] = None,
                user_id: Optional[str] = None,
            ) -> bool:
                """
                Update the status of a place in the staging table.

                Args:
                    session: SQLAlchemy session
                    place_id: Google Place ID
                    status: New status (New, Selected, Maybe, Not a Fit, Archived)
                    tenant_id: Optional tenant ID for isolation
                    user_id: Optional user ID for attribution

                Returns:
                    Boolean indicating success
                """
                try:
                    # Validate status value
                    valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
                    if status not in valid_statuses:
                        logger.warning(
                            f"Invalid status value: {status}. Must be one of {valid_statuses}"
                        )
                        return False

                    # First check if the place exists
                    query = select(Place).where(Place.place_id == place_id)

                    # Add tenant filter if provided
                    if tenant_id:
                        try:
                            tenant_uuid = (
                                uuid.UUID(tenant_id)
                                if isinstance(tenant_id, str)
                                else tenant_id
                            )
                            query = query.where(Place.tenant_id == tenant_uuid)
                        except ValueError:
                            logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
            =======
            async def update_places_status(
                session: AsyncSession,
                place_id: str,
                status: str,
                user_id: Optional[str] = None,
            ) -> bool:
                """
                Update the status of a place in the staging table.

                Args:
                    session: SQLAlchemy session
                    place_id: Google Place ID
                    status: New status (New, Selected, Maybe, Not a Fit, Archived)
                    user_id: Optional user ID for attribution

                Returns:
                    Boolean indicating success
                """
                try:
                    # Validate status value (This should ideally be handled by the calling router/service using ENUMs)
                    # For now, keep basic validation if status is a string
                    valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
                    if status not in valid_statuses:
                        logger.warning(
                            f"Invalid status value: {status}. Must be one of {valid_statuses}"
                        )
                        return False

                    # First check if the place exists (tenant_id is handled by BaseModel)
                    query = select(Place).where(Place.place_id == place_id)
            +++++++ REPLACE
            </diff>
            </replace_in_file>
        *   **Step 2.3.6:** Update `batch_update_places` to remove `tenant_id` parameter and filtering.
            <replace_in_file>
            <path>src/services/places/places_storage_service.py</path>
            <diff>
            ------- SEARCH
            async def batch_update_places(
                session: AsyncSession,
                place_ids: List[str],
                status: str,
                tenant_id: Optional[str] = None,
                user_id: Optional[str] = None,
            ) -> int:
                """
                Update the status of multiple places in batch.

                Args:
                    session: SQLAlchemy session
                    place_ids: List of Google Place IDs
                    status: New status (New, Selected, Maybe, Not a Fit, Archived)
                    tenant_id: Optional tenant ID for isolation
                    user_id: Optional user ID for attribution

                Returns:
                    Number of records updated
                """
                try:
                    # Validate input
                    if not place_ids:
                        logger.warning("No place_ids provided for batch update")
                        return 0

                    # Validate status value
                    valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
                    if status not in valid_statuses:
                        logger.warning(
                            f"Invalid status value: {status}. Must be one of {valid_statuses}"
                        )
                        return 0

                    # For batch updates, we'll query for all matching places and update them individually
                    # This ensures proper enum handling
                    query = select(Place).where(Place.place_id.in_(place_ids))

                    # Add tenant filter if provided
                    if tenant_id:
                        try:
                            tenant_uuid = (
                                uuid.UUID(tenant_id)
                                if isinstance(tenant_id, str)
                                else tenant_id
                            )
                            query = query.where(Place.tenant_id == tenant_uuid)
                        except ValueError:
                            logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
            =======
            async def batch_update_places(
                session: AsyncSession,
                place_ids: List[str],
                status: str,
                user_id: Optional[str] = None,
            ) -> int:
                """
                Update the status of multiple places in batch.

                Args:
                    session: SQLAlchemy session
                    place_ids: List of Google Place IDs
                    status: New status (New, Selected, Maybe, Not a Fit, Archived)
                    user_id: Optional user ID for attribution

                Returns:
                    Number of records updated
                """
                try:
                    # Validate input
                    if not place_ids:
                        logger.warning("No place_ids provided for batch update")
                        return 0

                    # Validate status value (This should ideally be handled by the calling router/service using ENUMs)
                    # For now, keep basic validation if status is a string
                    valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
                    if status not in valid_statuses:
                        logger.warning(
                            f"Invalid status value: {status}. Must be one of {valid_statuses}"
                        )
                        return 0

                    # For batch updates, we'll query for all matching places and update them individually
                    # This ensures proper enum handling (tenant_id is handled by BaseModel)
                    query = select(Place).where(Place.place_id.in_(place_ids))
            +++++++ REPLACE
            </diff>
            </replace_in_file>
    *   **Verification:** Confirm changes are applied in `places_storage_service.py`.

### **Final Verification for WF1**

1.  **Manual Code Review:** Visually inspect `src/models/place.py`, `src/models/place_search.py`, `src/schemas/single_search.py`, `src/routers/google_maps_api.py`, `src/services/places/places_search_service.py`, and `src/services/places/places_storage_service.py` to ensure all changes are correctly applied and imports are resolved.
2.  **Test Execution (if possible):** If you have a local test suite, run tests related to WF1 to ensure functionality.
3.  **Alembic Migration Check:** Remember that **Phase 0.3 (Database Migration)** is a critical follow-up step after all models are corrected across all workflows. It requires human review of the generated migration script.

Upon successful completion of these steps, WF1 should be significantly closer to its canonical specification, with its core issues addressed. You can then provide feedback on this process, and we can proceed to the next workflow.
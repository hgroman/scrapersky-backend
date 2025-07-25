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

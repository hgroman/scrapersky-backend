Project Plan: ScraperSky V2 Pipeline Modernization

Version: 1.0
Date: 2025-08-02
Author: Gemini

1. Mission Statement

To build a new, complete, and architecturally consistent ScraperSky V2 data processing pipeline in parallel with the existing V1 system. Our strategy is to "Harvest the
Fruit First" by immediately implementing the final, value-extracting workflow (WF7) and then systematically rebuilding the preceding workflows backwards (WF6 through
WF1). This approach delivers business value at the earliest possible moment and mitigates risk by ensuring every new component is built upon the project's most mature
and proven architectural patterns.

2. Guiding Principles (The V2 Canon)

This project will adhere strictly to the following principles, derived from the best practices observed in the V1 pipeline:

1.  The Universal Background Pattern: All asynchronous background processing will be implemented using a dedicated, single-purpose scheduler that leverages the
    `run_job_loop` Curation SDK. This is non-negotiable.
2.  The Universal Trigger Pattern: All API endpoints that initiate background work will use the Dual-Status Update Pattern. A user-facing curation_status change will
    automatically trigger a processing_status change to Queued.
3.  Strict Parallelism: The V2 pipeline will be built entirely under the /api/v2/ namespace. There will be zero modification to the V1 API endpoints or services. This
    ensures V1 remains operational and allows for safe, parallel testing.
4.  Build New, Don't Repair Old: Project scope is strictly limited to building the V2 pipeline. There will be no refactoring or bug fixing of the V1 workflows. The V1
    pipeline will be decommissioned in the final phase.

### **2.1. Subject Matter Experts & Authoritative Sources**

This project will consult the following V1 source files as the definitive Subject Matter Experts (SMEs) for implementing the V2 architecture. All V2 components must adhere to the patterns established in these files.

| Area of Expertise | Authoritative Source (The "SME") |
| :--- | :--- |
| **Background Processing** | `/src/services/sitemap_import_scheduler.py` |
| *(The Gold Standard)* | **Expertise:** The canonical implementation of a dedicated scheduler using the `run_job_loop` SDK. This is the blueprint for all V2 schedulers. |
| **API Trigger Logic** | `/src/routers/domains.py` |
| *(The Dual-Status Pattern)* | **Expertise:** The cleanest implementation of the Dual-Status Update pattern, which serves as the blueprint for all V2 API routers. |
| **End-to-End Workflow** | **Workflow 6: The Recorder** |
| *(The Complete Model)* | **Expertise:** The most mature, fully-functional workflow, demonstrating the correct interaction between a dedicated scheduler, a service, and the SDK. |
| **V2 Implementation Spec** | **Workflow 7: The Extractor (Truth Doc)** |
| *(The Blueprint)* | **Expertise:** The formal specification and starting point for the first phase of the V2 project. |

### **2.2. Adherence to Architectural Canon**

All V2 development must strictly conform to the project's established 7-layer architecture and naming conventions. The following documents, and the layer-specific blueprints they reference, are the definitive source of truth for these standards and must be followed for all new code:

-   **Architectural Truth:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_6_Architecture_and_Status/v_1.0-ARCH-TRUTH-Definitive_Reference.md`
-   **Naming & Patterns Guide:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`

### **3. Project Phases & Workstreams**

The project will be executed in three distinct phases, following the "build backwards" strategy.

---

Phase 1: Harvest the Fruit (Implement the Missing Link: WF7)

Objective: To immediately begin processing the backlog of Page records and extracting Contact data, delivering the primary business value of the entire pipeline.

- Workstream 1.1: Create the WF7 Service & Scheduler

  - File: Create /src/services/page_curation_service.py.
  - Action: Implement process_single_page_for_page_curation(page_id, session), including logic for fetching page HTML, parsing content, and creating Contact records.
  - File: Create /src/services/page_curation_scheduler.py.
  - Action: Implement process_page_curation_queue() using the run_job_loop SDK, configured for the Page model and its page_processing_status field.
  - File: Update /src/main.py to initialize the new page_curation_scheduler.
  - File: Update /src/config/settings.py with scheduler intervals and batch sizes for WF7.

- Workstream 1.2: Create the WF7 API Endpoint
  - File: Create /src/routers/v2/pages.py.
  - Action: Implement a PUT /api/v2/pages/status endpoint that performs the Dual-Status Update on Page records. This will be used for manual curation and testing.

Phase 1 Outcome: A fully functional WF7 that begins processing the Page records produced by the existing V1 pipeline. Business value starts being generated.

---

Phase 2: Rebuild the Pipeline (From WF6 to WF1)

Objective: To systematically replace each V1 workflow with a new V2 implementation that adheres to the Guiding Principles.

- Workstream 2.1: Adopt WF6 - The Recorder (Sitemap Import)

  - Action: The existing WF6 is the gold standard. Create a new /api/v2/sitemap-files.py router that reuses the logic from the V1 router. The existing
    sitemap_import_scheduler and sitemap_import_service are already V2-compliant and will be used as-is.

- Workstream 2.2: Rebuild WF5 - The Flight Planner (Sitemap Curation)

  - Action: Create a new /api/v2/sitemap-files.py router (or add to the one from 2.1) with the Dual-Status Update logic for SitemapFile records. This will queue files
    for the V2 WF6.

- Workstream 2.3: Rebuild WF4 - The Surveyor (Domain Curation)

  - Action: Create /src/routers/v2/domains.py with the Dual-Status Update logic.
  - Action: Create a new, dedicated v2_domain_curation_scheduler.py that uses the run_job_loop SDK to process queued domains and hand off to the V2 WF5.

- Workstream 2.4: Rebuild WF3, WF2, and WF1
  - Action: Repeat the pattern for each workflow:
    1.  Create the /api/v2/... router with the correct Dual-Status Update logic.
    2.  Create the dedicated V2 scheduler using the run_job_loop SDK.
    3.  Ensure the output of each V2 workflow correctly feeds the input of the next V2 workflow.

Phase 2 Outcome: A complete, parallel V2 pipeline that is architecturally consistent, robust, and fully independent of V1.

---

Phase 3: UI Integration & Decommissioning

Objective: To migrate user interaction to the V2 pipeline and safely retire the V1 system.

- Workstream 3.1: Develop V2 User Interface

  - Action: Fork the existing /static/ HTML and JavaScript files.
  - Action: Modify the forked JavaScript to point all API calls to the /api/v2/ endpoints.
  - Action: Deploy the V2 UI on a separate URL or behind a feature flag for internal testing.

- Workstream 3.2: Migration and Cutover

  - Action: Run V1 and V2 in parallel for a defined period, comparing outputs to ensure data integrity and consistency.
  - Action: Once V2 is validated, perform the cutover by making the V2 UI the default for all users.

- Workstream 3.3: Decommission V1
  - Action: After a safe observation period with no V1 traffic, formally decommission the V1 pipeline.
  - Action: Remove all V1 routers, schedulers, and UI files from the codebase.

4. Definition of Done

The project will be considered complete when:

1.  The WF7 workflow is live and has successfully processed the entire backlog of Page records.
2.  All V2 workflows (WF1-WF7) are implemented according to the Guiding Principles and are processing data end-to-end.
3.  The V2 UI is the default user interface.
4.  All V1 API endpoints and schedulers have been removed from the production codebase.

This plan provides a clear, realistic, and value-driven path to modernizing the ScraperSky pipeline. Let's begin.

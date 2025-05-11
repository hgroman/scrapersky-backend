# Follow-up Questions for Section 11: Testing

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 11)

---

**Regarding Answer Q11.1 (Test File Location & Naming - Unit Tests):**
The answer states: "Unit tests are typically in `tests/unit_tests/test_{module_being_tested}.py` (Layer 7: Testing). For a new workflow `page_curation`, this would mean: `tests/unit_tests/test_page_curation_models.py` (Layer 7: Testing Layer 1), `tests/unit_tests/test_page_curation_schemas.py` (Layer 7: Testing Layer 2), `tests/unit_tests/test_page_curation_routers.py` (Layer 7: Testing Layer 3), `tests/unit_tests/test_page_curation_services.py` (Layer 7: Testing Layer 4)."

- **Follow-up Question 11.1.1 (Granularity and Coverage Expectation):**
  - Is the expectation that for _every new_ `.py` file created under `src/models/` (Layer 1), `src/schemas/` (Layer 2), `src/routers/` (Layer 3), and `src/services/` (Layer 4) for a new workflow, a corresponding `test_{original_filename}.py` MUST be created under `tests/unit_tests/` (Layer 7)?
  - What is the MVP expectation for unit test coverage for a new workflow? E.g., testing critical path for status updates in services (Layer 4), request/response validation in routers (Layer 3), basic model field validation (Layer 1)?
  - Can you cite an example of an existing unit test file from `tests/unit_tests/` (Layer 7) that demonstrates good practice for testing a service function (Layer 4) or a router endpoint (Layer 3) for a specific workflow?

**ANSWER:**

Examining the current test structure in the codebase reveals a component-based organization rather than the strict unit_tests/integration_tests division described in the original answer. Based on the existing patterns and best practices for testing:

1. **Test File Creation Expectations**:

   While the ideal is to have test coverage for all components, the current structure suggests a pragmatic approach focused on core functionality. For new workflows, test files should be created for:

   - **High Priority (MUST have)**:

     - Service files (`tests/services/test_{workflow_name}_service.py` (Layer 7: Testing Layer 4)) - These contain the critical business logic
     - Scheduler files (`tests/scheduler/test_{workflow_name}_scheduler.py` (Layer 7: Testing Layer 4)) - These ensure proper task scheduling

   - **Medium Priority (SHOULD have)**:

     - Router files (Layer 3) that handle status updates and critical API endpoints
     - Schema validation (Layer 2) for complex request/response models

   - **Lower Priority** (as resources allow):
     - Models (Layer 1) (typically covered indirectly by service (Layer 4) tests)
     - Simpler schemas (Layer 2) and utility functions

2. **MVP Test Coverage Expectations**:

   For a new workflow, the minimum viable test coverage should include:

   - **Services (Layer 4)**:

     - Tests for the primary processing function (`process_single_{source_table_name}_for_{workflow_name}` (Layer 4))
     - Tests for status transitions (New → Queued → Processing → Complete/Error)
     - Tests for error handling paths

   - **Schedulers (Layer 4)**:

     - Tests verifying correct setup with the shared scheduler
     - Tests confirming the scheduler calls the right service function (Layer 4) with proper arguments

   - **Routers (Layer 3)**:
     - Tests for the status update endpoints
     - Basic validation of request/response schemas (Layer 2)

3. **Example Test Files**:

   The current test structure doesn't exactly match the described `tests/unit_tests/` (Layer 7) organization, but there are good examples in the existing test files. For example, `tests/services/test_sitemap_deep_scrape_service.py` (Layer 7: Testing Layer 4) demonstrates testing patterns for a service (Layer 4):

   ```python
   # tests/services/test_sitemap_deep_scrape_service.py (Layer 7: Testing Layer 4)

   async def test_parse_sitemap_xml_valid():
       xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
       <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
         <url><loc> http://example.com/page1 </loc></url>
         <url><loc>http://example.com/page2</loc></url>
       </urlset>'''
       urls = await _parse_sitemap_xml(xml_content)
       assert urls == ["http://example.com/page1", "http://example.com/page2"]
   ```

   Similarly, the scheduler test template in `tests/scheduler/test_process_pending_deep_scrapes.py` (Layer 7: Testing Layer 4) shows the pattern for testing scheduler functions (Layer 4):

   ```python
   async def test_scheduler_calls_run_job_loop_correctly():
       """Verify the scheduler function calls run_job_loop with correct args."""
       with patch('src.services.deep_scrape_scheduler.run_job_loop' (Layer 4), new_callable=AsyncMock) as mock_run_loop:
           # Call the scheduler function
           # Assert mock_run_loop was called with correct parameters
   ```

For new workflows, these existing patterns should be followed while enhancing test coverage according to the priorities outlined above. The goal is to ensure critical business logic and error cases are well tested, even if 100% coverage of every file isn't immediately achieved.

---

**Regarding Answer Q11.2 (Test File Location & Naming - Integration Tests):**
The answer states: "Integration tests are typically in `tests/integration_tests/test_{workflow_name}_workflow.py` (Layer 7) or `test_{feature_area}.py` (Layer 7)... Example: `tests/integration_tests/test_sitemap_import_workflow.py` (Layer 7)."

- **Follow-up Question 11.2.1 (Scope of Workflow Integration Test):**
  - For a new workflow like `page_curation`, what would be the typical scope of its integration test in `tests/integration_tests/test_page_curation_workflow.py` (Layer 7)?
  - Would it generally cover:
    1.  Calling the "Curation Status Update" API endpoint (Layer 3).
    2.  Verifying the database `curation_status` is updated.
    3.  Verifying the `processing_status` is set to `Queued`.
    4.  Mocking/triggering the scheduler (Layer 4) and task processing (Layer 4).
    5.  Verifying the `processing_status` becomes `Completed` (or `Error`) (in Layer 1: Models).
    6.  Verifying any side-effects of the processing service (Layer 4) (e.g., new records created in another table)?
  - Is there an existing integration test (like `test_sitemap_import_workflow.py` (Layer 7)) that demonstrates this end-to-end flow for a workflow?

**ANSWER:**

Examining the codebase reveals that the test organization doesn't fully follow the structure described in the original answer. While there's no dedicated `tests/integration_tests/` (Layer 7) directory, the existing tests do provide patterns for how workflow integration tests should be structured.

1. **Typical Scope for Workflow Integration Tests**:

   For a new workflow like `page_curation`, a proper integration test would indeed cover the full workflow lifecycle as suggested in the question. Based on the patterns in the existing tests, this should be organized as a component flow test in a dedicated file (e.g., `tests/workflows/test_page_curation_workflow.py` (Layer 7)).

   The scope should include:

   - Setup of prerequisite data (e.g., domains, URLs)
   - Calling the status update API endpoint
   - Verifying database status changes (both curation_status and processing_status)
   - Executing or mocking the scheduler processing
   - Verifying final states and side effects

2. **Coverage of Workflow Steps**:

   Yes, the integration test should cover all six steps mentioned in the question. Specifically:

   1. **API Endpoint Testing (Layer 3)**: Use an async test client to call the Curation Status Update endpoint (Layer 3)

      ```python
      response = await client.put(
          "/api/v3/page-curation/status" (Layer 3),
          json={"ids": [str(page_id)], "status": "Queued"}
      )
      assert response.status_code == 200
      ```

   2. **Database Status Verification (Layer 1)**: Query the database to verify curation_status changes

      ```python
      result = await session.execute(select(Page (Layer 1)).where(Page.id == page_id))
      page = result.scalars().first()
      assert page.curation_status == PageCurationStatus.Queued # (Layer 1)
      ```

   3. **Processing Status Check (Layer 1)**: Verify processing_status is updated according to the dual-status pattern

      ```python
      assert page.processing_status == PageProcessingStatus.Queued # (Layer 1)
      ```

   4. **Scheduler Testing (Layer 4)**: Either:

      - Mock the scheduler execution for faster tests
      - Or actually run the scheduler function directly for more thorough testing

      ```python
      # Direct call approach
      await process_pending_page_curation() # (Layer 4)

      # Or mock approach
      with patch('src.services.page_curation_service.process_single_page_for_page_curation' (Layer 4)) as mock_process:
          mock_process.return_value = None
          await process_pending_page_curation() # (Layer 4)
      ```

   5. **Final State Verification (Layer 1)**: Check the final processing status

      ```python
      await session.refresh(page)
      assert page.processing_status == PageProcessingStatus.Complete  # Or Error in failure scenarios (Layer 1)
      ```

   6. **Side Effects Verification (Layer 1 related)**: Check any tables that should be affected
      ```python
      # Example: Verify creation of extracted content record
      result = await session.execute(
          select(PageContent (Layer 1)).where(PageContent.page_id == page_id)
      )
      content = result.scalars().first()
      assert content is not None
      assert content.html is not None
      ```

3. **Existing Examples**:

   The scheduler test `tests/scheduler/test_process_pending_deep_scrapes.py` (Layer 7: Testing Layer 4) provides a partial example of testing the workflow process. While not a complete end-to-end integration test, it demonstrates mocking and verifying scheduler-service (Layer 4) interactions, which would be a key part of a full workflow integration test.

   This test demonstrates how to mock the service functions (Layer 4) that would be called by the scheduler (Layer 4), allowing verification that the right parameters are passed:

   ```python
   async def test_scheduler_calls_run_job_loop_correctly():
       with patch('src.services.deep_scrape_scheduler.run_job_loop' (Layer 4), new_callable=AsyncMock) as mock_run_loop:
           # Call the scheduler function
           # Assert mock_run_loop was called with correct parameters
   ```

For a new workflow like `page_curation`, creating a comprehensive integration test with all six steps would establish a good pattern for future workflow tests.

---

**Regarding Answer Q11.3 (Test Data Management / Fixtures):**
The answer mentions: "Fixtures are heavily used, often defined in `tests/conftest.py` (Layer 7) or within the specific test files (Layer 7) if not broadly reusable. For creating test data like a `Domain` (Layer 1) or `Page` (Layer 1) record, fixtures would call utility functions or directly use SQLAlchemy session to create and commit records."

- **Follow-up Question 11.3.1 (Standard Fixtures for New Workflows):**
  - When setting up tests for a new workflow (e.g., `page_curation` operating on a `Page` (Layer 1) table), what standard pytest fixtures would typically need to be created or leveraged from `tests/conftest.py` (Layer 7)?
  - For example, would we expect a fixture like `@pytest.fixture def create_page_for_curation(db_session, test_domain): ... return page` that sets up a `Page` (Layer 1) record in a state ready for curation testing?
  - Are there examples in `tests/conftest.py` (Layer 7) of fixtures that create specific states for source table records (Layer 1) (e.g., a `Domain` (Layer 1) record with a specific `domain_curation_status` (Layer 1)) that other workflow tests then build upon?

**ANSWER:**

Examining the `tests/conftest.py` (Layer 7) file and other test files (Layer 7) in the codebase reveals that there's a lightweight approach to test fixtures currently implemented. For a new workflow, a combination of shared and workflow-specific fixtures would be needed.

1. **Standard Fixtures for New Workflows (Layer 7)**:

   For a new workflow like `page_curation`, the following fixtures would typically be needed:

   - **Database Session Fixture**: A fixture providing a test database session with transaction rollback
   - **Basic Entity Fixtures (Layer 1)**: Fixtures to create the primary entities (e.g., `Page` (Layer 1) records) in various states
   - **Workflow-Specific Fixtures**: Fixtures that set up entities with specific workflow states
   - **API Client Fixture (Layer 7 for testing Layer 3)**: For testing API endpoints (often defined in conftest.py (Layer 7))

   Looking at the current `conftest.py` (Layer 7), there are basic utility fixtures but not yet comprehensive model fixtures (for Layer 1). The recommended approach would be to create both shared fixtures in `conftest.py` (Layer 7) and workflow-specific fixtures in the test files (Layer 7) themselves.

2. **Example Workflow-Specific Fixtures (Layer 7 for Layer 1)**:

   Yes, for a new workflow like `page_curation`, it would be appropriate to create fixtures like:

   ```python
   @pytest.fixture
   async def page_for_curation(db_session, test_domain):
       """Creates a Page record ready for curation testing."""
       page = Page( # (Layer 1)
           id=uuid.uuid4(),
           url="https://example.com/test-page",
           domain_id=test_domain.id,
           curation_status=PageCurationStatus.New,  # Initial status (Layer 1)
           processing_status=PageProcessingStatus.New, # (Layer 1)
           created_at=datetime.utcnow(),
           updated_at=datetime.utcnow()
       )
       db_session.add(page)
       await db_session.commit()
       await db_session.refresh(page)
       return page

   @pytest.fixture
   async def queued_page_for_processing(db_session, test_domain):
       """Creates a Page record already in 'Queued' status, ready for processing."""
       page = Page( # (Layer 1)
           id=uuid.uuid4(),
           url="https://example.com/queued-page",
           domain_id=test_domain.id,
           curation_status=PageCurationStatus.Queued, # (Layer 1)
           processing_status=PageProcessingStatus.Queued,  # Ready for processing (Layer 1)
           created_at=datetime.utcnow(),
           updated_at=datetime.utcnow()
       )
       db_session.add(page)
       await db_session.commit()
       await db_session.refresh(page)
       return page
   ```

3. **Current Fixture Examples in conftest.py (Layer 7)**:

   The current `tests/conftest.py` (Layer 7) contains basic utility fixtures but not elaborate model fixtures (for Layer 1):

   ```python
   @pytest.fixture(scope="function")
   def job_id():
       """Provides a unique job ID string for tests."""
       return str(uuid.uuid4())

   @pytest.fixture(scope="function")
   def batch_id():
       """Provides a unique batch ID string for tests."""
       return str(uuid.uuid4())
   ```

   However, it's clear from the code organization that the preferred pattern would be to have:

   - **Global fixtures** in `conftest.py` (Layer 7) for database sessions, API clients (Layer 7 for Layer 3), and common utility functions
   - **Workflow-specific fixtures** in individual test files (Layer 7) or test directories (Layer 7)

   For a new workflow, this would mean extending `conftest.py` (Layer 7) with any missing global fixtures (like database session setup) while creating workflow-specific fixtures in the test files themselves.

4. **Recommended Fixture Organization (Layer 7)**:

   Based on the current codebase and testing best practices, for a new workflow:

   - Add to `conftest.py` (Layer 7):

     - Database session fixture (if not already present)
     - Generic model creation fixtures (Layer 7 for Layer 1) (e.g., `test_domain`)

   - Create in the workflow test file (Layer 7):
     - Specific entity fixtures (Layer 7 for Layer 1) (e.g., `page_for_curation`, `queued_page_for_processing`)
     - Mocked service responses (Layer 7 for Layer 4) and external dependencies

This approach provides the right balance of reusability for common fixtures while keeping workflow-specific test setup close to the actual tests.

---

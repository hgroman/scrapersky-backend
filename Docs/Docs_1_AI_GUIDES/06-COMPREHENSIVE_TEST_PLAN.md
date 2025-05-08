# COMPREHENSIVE TEST PLAN

This document outlines a structured approach to testing the ScraperSky backend, with a focus on verifying critical functionality and ensuring proper transaction management.

## 1. DATABASE TRANSACTION TESTS

### Transaction Boundary Tests

These tests verify that transactions are properly managed by routers and background tasks.

```python
async def test_router_transaction_management():
    """
    Test that router correctly manages transaction boundaries.

    This test verifies:
    1. Transaction commits on success
    2. Transaction rolls back on error
    3. Background tasks are added after transaction commit
    """
    # Mock service and background tasks
    mock_service = create_mock_service()
    mock_bg_tasks = create_mock_background_tasks()

    # Test case 1: Successful transaction
    test_data = {"id": str(uuid.uuid4()), "name": "test"}
    response = await client.post(
        "/api/v3/resource",
        json=test_data,
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201

    # Verify data was committed
    async with get_test_session() as session:
        result = await session.execute(
            select(TestModel).where(TestModel.id == test_data["id"])
        )
        model = result.scalars().first()
        assert model is not None
        assert model.name == test_data["name"]

    # Verify background task was added after commit
    assert mock_bg_tasks.add_task.called
    assert mock_bg_tasks.add_task.call_args[0][0] == mock_service.background_process

    # Test case 2: Failed transaction
    error_data = {"id": str(uuid.uuid4()), "name": "error_trigger"}
    mock_service.create_resource.side_effect = ValueError("Test error")

    response = await client.post(
        "/api/v3/resource",
        json=error_data,
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 400

    # Verify data was NOT committed
    async with get_test_session() as session:
        result = await session.execute(
            select(TestModel).where(TestModel.id == error_data["id"])
        )
        model = result.scalars().first()
        assert model is None
```

### Service Transaction Awareness Tests

These tests verify that services are properly transaction-aware without managing transactions.

```python
async def test_service_transaction_awareness():
    """
    Test that services are properly transaction-aware.

    This test verifies:
    1. Services use the provided session
    2. Services don't create their own transactions
    3. Services propagate errors for transaction handling
    """
    # Create test service
    test_service = RealService()

    # Create mock session with transaction tracking
    mock_session = create_mock_session()

    # Test case 1: Service uses provided session
    await test_service.create_resource(mock_session, {"name": "test"})

    # Verify session was used correctly
    assert mock_session.add.called
    assert mock_session.begin.not_called  # Service should not call begin()

    # Test case 2: Service propagates errors
    mock_session.reset_mock()
    mock_session.add.side_effect = ValueError("Test error")

    with pytest.raises(ValueError):
        await test_service.create_resource(mock_session, {"name": "error"})
```

### Background Task Transaction Tests

These tests verify that background tasks properly manage their own transactions.

```python
async def test_background_task_transactions():
    """
    Test that background tasks properly manage their own transactions.

    This test verifies:
    1. Background tasks create their own sessions
    2. They manage transaction boundaries
    3. They handle errors properly
    4. They ensure session cleanup
    """
    # Setup test tracking
    session_created = False
    transaction_begun = False
    session_closed = False

    # Mock session factory
    original_factory = async_session_factory

    def mock_factory():
        nonlocal session_created
        session_created = True
        session = original_factory()

        # Wrap session methods to track calls
        original_begin = session.begin
        original_close = session.close

        async def tracked_begin(*args, **kwargs):
            nonlocal transaction_begun
            transaction_begun = True
            return await original_begin(*args, **kwargs)

        async def tracked_close(*args, **kwargs):
            nonlocal session_closed
            session_closed = True
            return await original_close(*args, **kwargs)

        session.begin = tracked_begin
        session.close = tracked_close
        return session

    # Replace factory temporarily
    import src.db.session
    src.db.session.async_session_factory = mock_factory

    try:
        # Execute background task
        task_id = str(uuid.uuid4())
        await process_domain_with_own_session(
            job_id=task_id,
            domain="example.com",
            tenant_id="550e8400-e29b-41d4-a716-446655440000"
        )

        # Verify session management
        assert session_created, "Background task did not create session"
        assert transaction_begun, "Background task did not begin transaction"
        assert session_closed, "Background task did not close session"

        # Verify database state
        async with get_test_session() as session:
            result = await session.execute(
                select(JobStatus).where(JobStatus.job_id == task_id)
            )
            status = result.scalars().first()
            assert status is not None
            assert status.status == "complete"
    finally:
        # Restore original factory
        src.db.session.async_session_factory = original_factory
```

## 2. API ENDPOINT TESTS

### Core Endpoint Tests

These tests verify that API endpoints function correctly and follow established patterns.

```python
async def test_sitemap_scan_endpoint():
    """
    Test the sitemap scan endpoint.

    This test verifies:
    1. Authentication works correctly
    2. Request validation works
    3. Response format is correct
    4. Background task is started
    """
    # Setup authentication
    headers = {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"
    }

    # Test case 1: Successful request
    request_data = {
        "base_url": "example.com",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "max_pages": 100
    }

    response = await client.post(
        "/api/v3/sitemap/scan",
        json=request_data,
        headers=headers
    )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "status_url" in data
    assert data["status_url"].startswith("/api/v3/sitemap/status/")

    # Test case 2: Invalid request
    invalid_data = {
        "base_url": "",  # Empty URL
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
    }

    response = await client.post(
        "/api/v3/sitemap/scan",
        json=invalid_data,
        headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

    # Test case 3: Authentication failure
    response = await client.post(
        "/api/v3/sitemap/scan",
        json=request_data,
        # No headers
    )

    assert response.status_code == 401
```

### Background Task Status Tests

These tests verify that background task status can be correctly retrieved.

```python
async def test_job_status_endpoint():
    """
    Test the job status endpoint.

    This test verifies:
    1. Status retrieval works for in-memory jobs
    2. Status retrieval works for database jobs
    3. Not found response for invalid jobs
    """
    # Setup test job
    job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

    # Add job to in-memory tracking
    from src.services.sitemap.processing_service import _job_statuses
    _job_statuses[job_id] = {
        "status": "running",
        "created_at": datetime.utcnow().isoformat(),
        "domain": "example.com",
        "progress": 0.5
    }

    # Setup authentication
    headers = {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"
    }

    # Test case 1: Retrieve in-memory status
    response = await client.get(
        f"/api/v3/sitemap/status/{job_id}",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["progress"] == 0.5

    # Test case 2: Create database job and retrieve status
    async with get_test_session() as session:
        async with session.begin():
            job = Job(
                job_id=f"sitemap_db_{uuid.uuid4().hex[:32]}",
                status="complete",
                tenant_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
                progress=1.0,
                metadata={"domain": "database-example.com"}
            )
            session.add(job)

    response = await client.get(
        f"/api/v3/sitemap/status/{job.job_id}",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["progress"] == 1.0
    assert data["domain"] == "database-example.com"

    # Test case 3: Not found job
    non_existent_job_id = f"sitemap_{uuid.uuid4().hex[:32]}"
    response = await client.get(
        f"/api/v3/sitemap/status/{non_existent_job_id}",
        headers=headers
    )

    assert response.status_code == 200  # Note: returns 200 with not_found status
    data = response.json()
    assert data["status"] == "not_found"
```

## 3. AUTHENTICATION AND AUTHORIZATION TESTS

### Authentication Tests

These tests verify that authentication works correctly.

```python
async def test_authentication():
    """
    Test authentication functionality.

    This test verifies:
    1. Valid tokens are accepted
    2. Invalid tokens are rejected
    3. Expired tokens are rejected
    4. User information is correctly retrieved
    """
    # Create test endpoints
    @app.get("/test/auth")
    async def test_auth_endpoint(current_user: dict = Depends(get_current_user)):
        return {"user_id": current_user["id"]}

    # Test case 1: Valid token
    valid_token = create_test_token("test_user")
    response = await client.get(
        "/test/auth",
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"

    # Test case 2: Invalid token
    invalid_token = "invalid.token.here"
    response = await client.get(
        "/test/auth",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 401

    # Test case 3: Expired token
    expired_token = create_test_token("test_user", expires_in=-3600)  # Expired 1 hour ago
    response = await client.get(
        "/test/auth",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
```

### Authorization Tests

These tests verify that authorization and permission checking works correctly.

```python
async def test_permission_checking():
    """
    Test permission checking functionality.

    This test verifies:
    1. Users with required permissions can access endpoints
    2. Users without required permissions are denied
    3. Feature flag checks work correctly
    """
    # Create test endpoints
    @app.get("/test/protected")
    async def test_protected_endpoint(
        current_user: dict = Depends(get_current_user)
    ):
        require_permission(current_user, "access_test")
        return {"access": "granted"}

    @app.get("/test/feature")
    async def test_feature_endpoint(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session)
    ):
        await require_feature_enabled(
            tenant_id=current_user["tenant_id"],
            feature_name="test_feature",
            session=session,
            permissions=current_user.get("permissions", [])
        )
        return {"feature": "enabled"}

    # Test case 1: User with permission
    user_with_perm = {
        "id": "user1",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "permissions": ["access_test"]
    }
    token_with_perm = create_test_token_for_user(user_with_perm)

    response = await client.get(
        "/test/protected",
        headers={"Authorization": f"Bearer {token_with_perm}"}
    )

    assert response.status_code == 200

    # Test case 2: User without permission
    user_without_perm = {
        "id": "user2",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "permissions": ["other_permission"]
    }
    token_without_perm = create_test_token_for_user(user_without_perm)

    response = await client.get(
        "/test/protected",
        headers={"Authorization": f"Bearer {token_without_perm}"}
    )

    assert response.status_code == 403

    # Test case 3: Feature flag check
    # Setup test data in database
    async with get_test_session() as session:
        async with session.begin():
            tenant_feature = TenantFeature(
                tenant_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
                feature_name="test_feature",
                is_enabled=True
            )
            session.add(tenant_feature)

    response = await client.get(
        "/test/feature",
        headers={
            "Authorization": f"Bearer {token_with_perm}",
            "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"
        }
    )

    assert response.status_code == 200
```

## 4. INTEGRATION TESTS

### Sitemap Scanning Integration Tests

These tests verify that the sitemap scanning functionality works end-to-end.

```python
async def test_sitemap_scanning_integration():
    """
    Test sitemap scanning integration.

    This test verifies the end-to-end flow:
    1. Scan request is accepted
    2. Background task processes the domain
    3. Sitemap data is stored in the database
    4. Status can be retrieved
    """
    # Setup mocks for external services
    mock_sitemap_analyzer(
        sitemaps=[
            {
                "url": "https://example.com/sitemap.xml",
                "sitemap_type": "standard",
                "discovery_method": "common_path",
                "url_count": 10,
                "size_bytes": 1024,
                "urls": [
                    {"url": "https://example.com/page1", "lastmod": "2023-01-01"},
                    {"url": "https://example.com/page2", "lastmod": "2023-01-02"}
                ]
            }
        ]
    )

    # Setup authentication
    headers = {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"
    }

    # Step 1: Initiate scan
    response = await client.post(
        "/api/v3/sitemap/scan",
        json={
            "base_url": "example.com",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "max_pages": 100
        },
        headers=headers
    )

    assert response.status_code == 202
    data = response.json()
    job_id = data["job_id"]

    # Step 2: Process the job (in tests we can't wait for background task)
    await process_domain_now(
        job_id=job_id,
        domain="example.com",
        tenant_id="550e8400-e29b-41d4-a716-446655440000"
    )

    # Step 3: Verify database state
    async with get_test_session() as session:
        # Check sitemap_files table
        sitemap_query = select(SitemapFile).where(SitemapFile.job_id == job_id)
        sitemap_result = await session.execute(sitemap_query)
        sitemaps = sitemap_result.scalars().all()

        assert len(sitemaps) == 1
        sitemap = sitemaps[0]
        assert sitemap.url == "https://example.com/sitemap.xml"
        assert sitemap.sitemap_type == "standard"

        # Check sitemap_urls table
        urls_query = select(SitemapUrl).where(SitemapUrl.sitemap_id == sitemap.id)
        urls_result = await session.execute(urls_query)
        urls = urls_result.scalars().all()

        assert len(urls) == 2
        assert any(url.url == "https://example.com/page1" for url in urls)
        assert any(url.url == "https://example.com/page2" for url in urls)

    # Step 4: Check status endpoint
    response = await client.get(
        f"/api/v3/sitemap/status/{job_id}",
        headers=headers
    )

    assert response.status_code == 200
    status_data = response.json()
    assert status_data["status"] == "complete"
    assert status_data["progress"] == 1.0
```

### Batch Processing Integration Tests

These tests verify that the batch processing functionality works end-to-end.

```python
async def test_batch_processing_integration():
    """
    Test batch processing integration.

    This test verifies the end-to-end flow:
    1. Batch job is created
    2. URLs are processed
    3. Results are stored in the database
    4. Status can be retrieved
    """
    # Setup code similar to sitemap integration test
    # ...
```

## 5. TEST IMPLEMENTATION PLAN

1. **Create Test Infrastructure**
   - Mock session factory for testing
   - Test database setup and teardown
   - Mock external services

2. **Implement Transaction Tests**
   - Router transaction tests
   - Service transaction awareness tests
   - Background task transaction tests

3. **Implement API Tests**
   - Core endpoint tests
   - Background task status tests

4. **Implement Auth Tests**
   - Authentication tests
   - Authorization tests

5. **Implement Integration Tests**
   - Sitemap scanning tests
   - Batch processing tests

6. **Create Test Fixtures**
   - Authentication fixtures
   - Database fixtures
   - External service mocks

7. **Implement Test Runner**
   - Enable parallel test execution
   - Configure test reporting
   - Set up CI integration

## 6. TEST EXECUTION GUIDE

1. **Running Transaction Tests**
   ```bash
   pytest tests/transaction/ -v
   ```

2. **Running API Tests**
   ```bash
   pytest tests/api/ -v
   ```

3. **Running Auth Tests**
   ```bash
   pytest tests/auth/ -v
   ```

4. **Running Integration Tests**
   ```bash
   pytest tests/integration/ -v
   ```

5. **Running All Tests**
   ```bash
   pytest
   ```

6. **Test Reporting**
   ```bash
   pytest --html=test_report.html
   ```

## 7. TEST MAINTENANCE GUIDE

1. **Adding New Tests**
   - Create test files in the appropriate directory
   - Use existing fixtures where applicable
   - Follow the established patterns

2. **Updating Existing Tests**
   - Maintain test isolation
   - Ensure proper cleanup
   - Document any changes

3. **Managing Test Data**
   - Use fixtures for test data
   - Clean up after tests
   - Use transaction rollbacks for database tests

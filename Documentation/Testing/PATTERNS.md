# Test Patterns

**Purpose:** Copy-paste complete test implementations

---

## SQLAlchemy Model Testing

### ENUM Column - Complete Pattern

```python
def test_enum_column_complete(session):
    """
    Complete ENUM column test including filtering.
    
    CRITICAL: Must test WHERE clauses, not just INSERT/SELECT.
    Based on: 2025-11-20 Incomplete ENUM Migration incident
    """
    # Test INSERT
    obj = LocalBusiness(
        tenant_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        business_name="Test Business",
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(obj)
    session.commit()
    obj_id = obj.id
    
    # Test SELECT by ID
    retrieved = session.get(LocalBusiness, obj_id)
    assert retrieved.domain_extraction_status == DomainExtractionStatusEnum.Queued
    
    # Test FILTER (CRITICAL - this is what schedulers do)
    queued = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    ).all()
    assert len(queued) > 0, "Filter by enum failed - missing native_enum=True?"
    assert any(b.id == obj_id for b in queued)
    
    # Test UPDATE
    obj.domain_extraction_status = DomainExtractionStatusEnum.Processing
    session.commit()
    session.refresh(obj)
    assert obj.domain_extraction_status == DomainExtractionStatusEnum.Processing
    
    # Test comparison in query
    processing = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Processing
    ).all()
    assert any(b.id == obj_id for b in processing)
    
    # Cleanup
    session.delete(obj)
    session.commit()
```

### Foreign Key Constraint Testing

```python
def test_foreign_key_constraint(session):
    """Test FK constraint enforcement"""
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    invalid_tenant_id = uuid.uuid4()
    
    # Test valid FK works
    obj = Place(
        tenant_id=valid_tenant_id,
        place_id="test_place_123",
        status=PlaceStatusEnum.New
    )
    session.add(obj)
    session.commit()
    obj_id = obj.id
    
    # Test invalid FK fails
    with pytest.raises(IntegrityError):
        invalid_obj = Place(
            tenant_id=invalid_tenant_id,  # Doesn't exist
            place_id="test_place_456",
            status=PlaceStatusEnum.New
        )
        session.add(invalid_obj)
        session.commit()
    
    session.rollback()
    
    # Cleanup
    session.delete(session.get(Place, obj_id))
    session.commit()
```

### NOT NULL Constraint Testing

```python
def test_not_null_constraint(session):
    """Test NOT NULL constraint enforcement"""
    # Test NULL value fails
    with pytest.raises(IntegrityError):
        obj = Domain(
            domain="test.com",
            tenant_id=None,  # NOT NULL constraint
        )
        session.add(obj)
        session.commit()
    
    session.rollback()
```

---

## Scheduler Testing

### Scheduler with Queued Work

```python
async def test_scheduler_processes_work(session):
    """
    Test scheduler with actual queued work.
    
    CRITICAL: Don't trust "0 items found" as success.
    Based on: 2025-11-20 Scheduler Silent Failure pattern
    """
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Create queued work
    business = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Test Business",
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(business)
    session.commit()
    business_id = business.id
    
    # Run scheduler
    from src.services.domain_extraction_scheduler import process_domain_extraction_queue
    await process_domain_extraction_queue()
    
    # Verify work was processed
    session.refresh(business)
    assert business.domain_extraction_status != DomainExtractionStatusEnum.Queued
    
    # Cleanup
    session.delete(business)
    session.commit()
```

### Scheduler Query Pattern Test

```python
def test_scheduler_query_pattern(session):
    """Test the actual query pattern schedulers use"""
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Create test data
    queued = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Queued Business",
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    processing = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Processing Business",
        domain_extraction_status=DomainExtractionStatusEnum.Processing
    )
    session.add_all([queued, processing])
    session.commit()
    
    # Test scheduler query pattern
    stmt = (
        select(LocalBusiness.id)
        .where(LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued)
        .order_by(LocalBusiness.updated_at.asc())
        .limit(20)
        .with_for_update(skip_locked=True)
    )
    
    result = session.execute(stmt)
    ids = [row[0] for row in result]
    
    assert queued.id in ids
    assert processing.id not in ids
    
    # Cleanup
    session.delete(queued)
    session.delete(processing)
    session.commit()
```

---

## Router Testing

### Endpoint with Status Filter

```python
async def test_router_status_filter(client):
    """Test router filtering by enum status"""
    # Create test data with different statuses
    # ... setup code ...
    
    # Test filter by single status
    response = await client.get(
        "/api/v3/domains?sitemap_curation_status=Selected"
    )
    assert response.status_code == 200
    data = response.json()
    assert all(d["sitemap_curation_status"] == "Selected" for d in data["items"])
    
    # Test filter by multiple statuses
    response = await client.get(
        "/api/v3/domains?sitemap_curation_status=Selected,New"
    )
    assert response.status_code == 200
    data = response.json()
    assert all(d["sitemap_curation_status"] in ["Selected", "New"] for d in data["items"])
```

---

## Database Migration Testing

### Pre-Migration Data Audit

```python
def test_pre_migration_data_audit(session):
    """Audit data before migration that adds constraints"""
    # Check for NULL values before adding NOT NULL constraint
    null_count = session.query(LocalBusiness).filter(
        LocalBusiness.tenant_id.is_(None)
    ).count()
    assert null_count == 0, f"Found {null_count} NULL tenant_ids - must fix before migration"
    
    # Check for invalid FK references
    invalid_fk = session.query(LocalBusiness).filter(
        ~LocalBusiness.tenant_id.in_(
            session.query(Tenant.id)
        )
    ).count()
    assert invalid_fk == 0, f"Found {invalid_fk} invalid tenant_ids - must fix before migration"
```

### Post-Migration Verification

```python
def test_post_migration_verification(session):
    """Verify migration completed successfully"""
    # Verify constraint exists
    inspector = inspect(session.bind)
    constraints = inspector.get_foreign_keys("local_businesses")
    tenant_fk = [c for c in constraints if "tenant_id" in c["constrained_columns"]]
    assert len(tenant_fk) > 0, "tenant_id FK constraint not found"
    
    # Verify data integrity
    total_before = 647  # Known count before migration
    total_after = session.query(LocalBusiness).count()
    assert total_after == total_before, f"Data loss: {total_before} -> {total_after}"
```

---

## How to Use These Patterns

1. **Find relevant pattern** for your change
2. **Copy the entire pattern** - don't modify
3. **Adapt** only the model/field names
4. **Run the test** before declaring work complete

**Don't write tests from scratch - copy these patterns.**

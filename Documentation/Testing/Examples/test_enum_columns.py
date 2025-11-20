"""
Example: Complete ENUM column testing

Based on: 2025-11-20 Incomplete ENUM Migration incident
Demonstrates: Why filtering tests are critical, not just INSERT/SELECT
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.models.local_business import LocalBusiness, DomainExtractionStatusEnum
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.place import PlaceStatusEnum


def test_enum_insert_and_select_only_incomplete(session):
    """
    ❌ INCOMPLETE TEST - This passed but production broke
    
    This test only verifies INSERT and SELECT by ID.
    It does NOT test filtering (WHERE clauses) which is what schedulers do.
    """
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Create record
    business = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Test Business",
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(business)
    session.commit()
    business_id = business.id
    
    # Retrieve by ID
    retrieved = session.get(LocalBusiness, business_id)
    assert retrieved.domain_extraction_status == DomainExtractionStatusEnum.Queued
    
    # ❌ TEST PASSED but production broke because we never tested filtering
    
    # Cleanup
    session.delete(retrieved)
    session.commit()


def test_enum_complete_with_filtering(session):
    """
    ✅ COMPLETE TEST - Tests filtering which is what broke in production
    
    This test verifies:
    1. INSERT works
    2. SELECT by ID works
    3. Filtering by enum value works (CRITICAL)
    4. Comparison in WHERE clause works
    5. UPDATE works
    """
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Test INSERT
    business = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Test Business",
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(business)
    session.commit()
    business_id = business.id
    
    # Test SELECT by ID
    retrieved = session.get(LocalBusiness, business_id)
    assert retrieved.domain_extraction_status == DomainExtractionStatusEnum.Queued
    
    # Test FILTER (CRITICAL - this is what schedulers do)
    # This would have caught the missing native_enum=True
    queued = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    ).all()
    assert len(queued) > 0, "Filter by enum failed - missing native_enum=True?"
    assert any(b.id == business_id for b in queued)
    
    # Test comparison in WHERE clause (what broke in production)
    stmt = select(LocalBusiness).where(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    )
    result = session.execute(stmt).scalars().all()
    assert any(b.id == business_id for b in result)
    
    # Test UPDATE
    business.domain_extraction_status = DomainExtractionStatusEnum.Processing
    session.commit()
    session.refresh(business)
    assert business.domain_extraction_status == DomainExtractionStatusEnum.Processing
    
    # Test filtering after update
    processing = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Processing
    ).all()
    assert any(b.id == business_id for b in processing)
    
    # Cleanup
    session.delete(business)
    session.commit()


def test_enum_all_values(session):
    """Test all enum values work correctly"""
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Test each enum value
    for status in DomainExtractionStatusEnum:
        business = LocalBusiness(
            tenant_id=valid_tenant_id,
            business_name=f"Test {status.value}",
            domain_extraction_status=status
        )
        session.add(business)
        session.commit()
        
        # Verify filtering works for this value
        results = session.query(LocalBusiness).filter(
            LocalBusiness.domain_extraction_status == status
        ).all()
        assert any(b.id == business.id for b in results)
        
        session.delete(business)
        session.commit()


def test_enum_default_value(session):
    """Test enum default value works"""
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # Create without specifying enum value
    business = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Test Default",
        # domain_extraction_status not specified - should use default
    )
    session.add(business)
    session.commit()
    
    # Verify default is None (as configured)
    assert business.domain_extraction_status is None
    
    # Cleanup
    session.delete(business)
    session.commit()


def test_multiple_enum_columns(session):
    """Test model with multiple enum columns"""
    valid_tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    # LocalBusiness has two enum columns: status and domain_extraction_status
    business = LocalBusiness(
        tenant_id=valid_tenant_id,
        business_name="Test Multiple Enums",
        status=PlaceStatusEnum.Maybe,
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(business)
    session.commit()
    business_id = business.id
    
    # Test filtering by first enum
    by_status = session.query(LocalBusiness).filter(
        LocalBusiness.status == PlaceStatusEnum.Maybe
    ).all()
    assert any(b.id == business_id for b in by_status)
    
    # Test filtering by second enum
    by_extraction = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    ).all()
    assert any(b.id == business_id for b in by_extraction)
    
    # Test filtering by both
    by_both = session.query(LocalBusiness).filter(
        LocalBusiness.status == PlaceStatusEnum.Maybe,
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    ).all()
    assert any(b.id == business_id for b in by_both)
    
    # Cleanup
    session.delete(business)
    session.commit()


# Pytest fixture example
@pytest.fixture
def session():
    """Database session fixture"""
    # Setup: Create session
    from src.db.session import get_db_session
    session = next(get_db_session())
    
    yield session
    
    # Teardown: Rollback any uncommitted changes
    session.rollback()
    session.close()

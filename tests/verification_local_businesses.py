import os
from uuid import uuid4
from datetime import datetime

# Mock environment variables BEFORE importing any project modules
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/db"
os.environ["SUPABASE_POOLER_HOST"] = "localhost"
os.environ["SUPABASE_POOLER_PORT"] = "6543"
os.environ["SUPABASE_POOLER_USER"] = "postgres"
os.environ["SUPABASE_DB_PASSWORD"] = "postgres"

from src.models.place import PlaceStatusEnum
from src.models.local_business import DomainExtractionStatusEnum

# We will try to import the models. 
# Initially they are in the router. 
# After refactor, they should be importable from the router (re-exported) or we check the new location.
# For now, let's just check if we can instantiate them to ensure structure is preserved.

def test_local_business_record_structure():
    try:
        from src.routers.local_businesses import LocalBusinessRecord
    except ImportError:
        # Fallback to new location if router import fails (though router should probably import them)
        from src.schemas.local_business_schemas import LocalBusinessRecord

    record = LocalBusinessRecord(
        id=uuid4(),
        business_name="Test Business",
        full_address="123 Test St",
        phone="555-1234",
        website_url="http://example.com",
        status=PlaceStatusEnum.New,
        domain_extraction_status=DomainExtractionStatusEnum.Queued,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tenant_id=uuid4()
    )
    assert record.business_name == "Test Business"
    assert record.status == PlaceStatusEnum.New

def test_paginated_response_structure():
    try:
        from src.routers.local_businesses import PaginatedLocalBusinessResponse, LocalBusinessRecord
    except ImportError:
        from src.schemas.local_business_schemas import PaginatedLocalBusinessResponse, LocalBusinessRecord

    record = LocalBusinessRecord(
        id=uuid4(),
        business_name="Test Business",
        full_address="123 Test St",
        phone="555-1234",
        website_url="http://example.com",
        status=PlaceStatusEnum.New,
        domain_extraction_status=DomainExtractionStatusEnum.Queued,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tenant_id=uuid4()
    )
    
    response = PaginatedLocalBusinessResponse(
        items=[record],
        total=1,
        page=1,
        size=50,
        pages=1
    )
    assert len(response.items) == 1
    assert response.total == 1

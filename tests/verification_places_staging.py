import os
import pytest
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

from src.models.place import PlaceStatusEnum, GcpApiDeepScanStatusEnum

# We will try to import the models. 
# Initially they are in the router. 
# After refactor, they should be importable from the router (re-exported) or we check the new location.

def test_places_staging_record_structure():
    try:
        from src.routers.places_staging import PlaceStagingRecord
    except ImportError:
        from src.schemas.places_staging_schemas import PlaceStagingRecord

    record = PlaceStagingRecord(
        place_id="test_place_id",
        business_name="Test Business",
        address="123 Test St",
        category="Restaurant",
        search_location="New York",
        latitude=40.7128,
        longitude=-74.0060,
        rating=4.5,
        reviews_count=100,
        price_level=2,
        status=PlaceStatusEnum.New.value,
        updated_at=datetime.now(),
        last_deep_scanned_at=datetime.now(),
        search_job_id=uuid4(),
        tenant_id=uuid4()
    )
    assert record.business_name == "Test Business"
    assert record.status == PlaceStatusEnum.New.value

def test_paginated_response_structure():
    try:
        from src.routers.places_staging import PaginatedPlaceStagingResponse, PlaceStagingRecord
    except ImportError:
        from src.schemas.places_staging_schemas import PaginatedPlaceStagingResponse, PlaceStagingRecord

    record = PlaceStagingRecord(
        place_id="test_place_id",
        business_name="Test Business",
        address="123 Test St",
        category="Restaurant",
        search_location="New York",
        latitude=40.7128,
        longitude=-74.0060,
        rating=4.5,
        reviews_count=100,
        price_level=2,
        status=PlaceStatusEnum.New.value,
        updated_at=datetime.now(),
        last_deep_scanned_at=datetime.now(),
        search_job_id=uuid4(),
        tenant_id=uuid4()
    )
    
    response = PaginatedPlaceStagingResponse(
        items=[record],
        total=1,
        page=1,
        size=50,
        pages=1
    )
    assert len(response.items) == 1
    assert response.total == 1

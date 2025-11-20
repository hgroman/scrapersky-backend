import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.places.places_deep_service import PlacesDeepService

# Mock logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_process_single_deep_scan_uses_passed_session():
    """
    Verify that process_single_deep_scan uses the passed session
    and does NOT call get_session().
    """
    print("Testing process_single_deep_scan refactor...")

    # Mock session
    mock_session = AsyncMock()
    mock_session.begin.return_value.__aenter__.return_value = mock_session

    # Mock Google Maps client to avoid API calls
    with patch("src.services.places.places_deep_service.googlemaps.Client") as MockGmaps:
        mock_gmaps_instance = MockGmaps.return_value
        # Mock place details response
        mock_gmaps_instance.place.return_value = {
            "status": "OK",
            "result": {
                "name": "Test Place",
                "formatted_address": "123 Test St",
                "place_id": "test_place_id"
            }
        }

        # Mock SQLAlchemy result
        mock_result = MagicMock()
        mock_business = MagicMock()
        mock_business.id = "test_uuid"
        mock_result.scalar_one_or_none.return_value = mock_business
        mock_session.execute.return_value = mock_result

        # Mock get_session to ensure it's NOT called
        with patch("src.services.places.places_deep_service.get_session", side_effect=Exception("get_session() should not be called!")) as mock_get_session:
            
            service = PlacesDeepService()
            # Mock JobService to avoid complexity
            service.job_service = AsyncMock()

            try:
                # Call method with passed session
                await service.process_single_deep_scan(
                    place_id="test_place_id",
                    tenant_id="00000000-0000-0000-0000-000000000000",
                    session=mock_session
                )
                print("✅ Method executed without calling get_session()")
            except Exception as e:
                print(f"❌ Method failed: {e}")
                if "get_session() should not be called!" in str(e):
                    print("❌ FAILURE: The method attempted to call get_session()!")
                raise e

            # Verify session usage (e.g., execute was called)
            # The method calls session.execute for the upsert
            assert mock_session.execute.called, "Session.execute should have been called"
            print("✅ Session.execute was called on the passed session")

if __name__ == "__main__":
    try:
        asyncio.run(test_process_single_deep_scan_uses_passed_session())
        print("✅ Verification Passed")
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)

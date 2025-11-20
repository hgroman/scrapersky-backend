import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
from uuid import uuid4

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.deep_scan_scheduler import process_single_deep_scan_wrapper
from src.models.place import GcpApiDeepScanStatusEnum

# Mock logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scheduler_wrapper_integration():
    """
    Verify that process_single_deep_scan_wrapper correctly passes the session
    to PlacesDeepService.process_single_deep_scan.
    """
    print("Testing scheduler wrapper integration...")

    # Mock session
    mock_session = AsyncMock()
    # session.begin() is synchronous, returns an async context manager
    mock_session.begin = MagicMock()
    mock_transaction = AsyncMock()
    mock_session.begin.return_value = mock_transaction
    mock_transaction.__aenter__.return_value = mock_session

    # Mock Place record
    mock_place = MagicMock()
    mock_place.id = uuid4()
    mock_place.place_id = "test_place_id"
    mock_place.tenant_id = uuid4()
    mock_place.deep_scan_status = GcpApiDeepScanStatusEnum.Queued

    # Mock DB result for fetching place
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_place
    mock_session.execute.return_value = mock_result

    # Mock PlacesDeepService
    with patch("src.services.deep_scan_scheduler.PlacesDeepService") as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.process_single_deep_scan = AsyncMock(return_value={"some": "data"})

        try:
            # Call the wrapper
            await process_single_deep_scan_wrapper(mock_place.id, mock_session)
            print("✅ Wrapper executed successfully")
        except Exception as e:
            print(f"❌ Wrapper failed: {e}")
            raise e

        # Verify the service was called with the session
        mock_service_instance.process_single_deep_scan.assert_called_once()
        call_args = mock_service_instance.process_single_deep_scan.call_args
        
        # Check arguments: place_id, tenant_id, session
        _, kwargs = call_args
        
        # Check positional args if any (likely kwargs based on my refactor)
        # My refactor used kwargs: place_id=..., tenant_id=..., session=...
        
        assert kwargs.get("place_id") == str(mock_place.place_id), "place_id mismatch"
        assert kwargs.get("tenant_id") == str(mock_place.tenant_id), "tenant_id mismatch"
        assert kwargs.get("session") == mock_session, "Session was NOT passed to service!"
        
        print("✅ Service was called with the correct session")

if __name__ == "__main__":
    try:
        asyncio.run(test_scheduler_wrapper_integration())
        print("✅ Integration Verification Passed")
    except Exception as e:
        print(f"❌ Integration Verification Failed: {e}")
        sys.exit(1)

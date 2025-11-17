"""
Unit tests for WF2 Deep Scan Scheduler

Tests the deep_scan_scheduler.py module including:
- Adapter wrapper function
- Queue processing function
- Scheduler setup function
- Edge cases and error handling
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.place import GcpApiDeepScanStatusEnum, Place
from src.models.local_business import LocalBusiness
from src.services.deep_scan_scheduler import (
    process_deep_scan_queue,
    process_single_deep_scan_wrapper,
    setup_deep_scan_scheduler,
)


class TestDeepScanAdapter:
    """Tests for process_single_deep_scan_wrapper adapter function."""

    @pytest.mark.asyncio
    async def test_adapter_processes_place_successfully(self, db_session: AsyncSession):
        """Test adapter successfully processes a valid Place record."""

        # Setup: Create test place
        place = Place(
            id=uuid4(),
            place_id="test_place_123",
            tenant_id=uuid4(),
            name="Test Business",
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock the service to return a LocalBusiness
        mock_local_business = LocalBusiness(
            id=uuid4(),
            name="Test Business",
            place_id=place.id
        )

        with patch(
            "src.services.deep_scan_scheduler.PlacesDeepService.process_single_deep_scan",
            return_value=mock_local_business
        ) as mock_service:
            # Execute: Call adapter
            await process_single_deep_scan_wrapper(place.id, db_session)

            # Verify: Service called with correct params
            mock_service.assert_called_once()
            call_args = mock_service.call_args
            assert call_args[1]["place_id"] == str(place.place_id)
            assert call_args[1]["tenant_id"] == str(place.tenant_id)

        # Verify: Place status updated to Completed
        await db_session.refresh(place)
        assert place.deep_scan_status == GcpApiDeepScanStatusEnum.Completed
        assert place.deep_scan_error is None

    @pytest.mark.asyncio
    async def test_adapter_handles_service_failure(self, db_session: AsyncSession):
        """Test adapter handles service returning None (failure case)."""

        # Setup: Create test place
        place = Place(
            id=uuid4(),
            place_id="test_place_456",
            tenant_id=uuid4(),
            name="Test Business",
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock service to return None (failure)
        with patch(
            "src.services.deep_scan_scheduler.PlacesDeepService.process_single_deep_scan",
            return_value=None
        ):
            # Execute: Call adapter
            await process_single_deep_scan_wrapper(place.id, db_session)

        # Verify: Place status updated to Error
        await db_session.refresh(place)
        assert place.deep_scan_status == GcpApiDeepScanStatusEnum.Error
        assert "Deep scan returned None" in place.deep_scan_error

    @pytest.mark.asyncio
    async def test_adapter_raises_error_when_place_not_found(self, db_session: AsyncSession):
        """Test adapter raises ValueError when Place record doesn't exist."""

        # Setup: Use non-existent UUID
        fake_id = uuid4()

        # Execute & Verify: Should raise ValueError
        with pytest.raises(ValueError, match=f"Place {fake_id} not found"):
            await process_single_deep_scan_wrapper(fake_id, db_session)

    @pytest.mark.asyncio
    async def test_adapter_updates_timestamp(self, db_session: AsyncSession):
        """Test adapter updates the updated_at timestamp."""

        # Setup: Create test place
        initial_time = datetime.utcnow()
        place = Place(
            id=uuid4(),
            place_id="test_place_789",
            tenant_id=uuid4(),
            name="Test Business",
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=initial_time,
            updated_at=initial_time
        )
        db_session.add(place)
        await db_session.commit()

        # Mock service
        mock_local_business = LocalBusiness(id=uuid4(), name="Test")
        with patch(
            "src.services.deep_scan_scheduler.PlacesDeepService.process_single_deep_scan",
            return_value=mock_local_business
        ):
            # Execute: Call adapter
            await process_single_deep_scan_wrapper(place.id, db_session)

        # Verify: Timestamp updated
        await db_session.refresh(place)
        assert place.updated_at > initial_time


class TestDeepScanQueue:
    """Tests for process_deep_scan_queue function."""

    @pytest.mark.asyncio
    async def test_queue_processes_queued_places(self, db_session: AsyncSession):
        """Test queue processor handles Queued places."""

        # Setup: Create queued place
        place = Place(
            id=uuid4(),
            place_id="queued_place",
            tenant_id=uuid4(),
            deep_scan_status=GcpApiDeepScanStatusEnum.Queued,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock the SDK run_job_loop to verify it's called correctly
        with patch("src.services.deep_scan_scheduler.run_job_loop") as mock_loop:
            # Execute: Run queue processor
            await process_deep_scan_queue()

            # Verify: SDK loop called with correct parameters
            mock_loop.assert_called_once()
            call_kwargs = mock_loop.call_args[1]
            assert call_kwargs["model"] == Place
            assert call_kwargs["queued_status"] == GcpApiDeepScanStatusEnum.Queued
            assert call_kwargs["processing_status"] == GcpApiDeepScanStatusEnum.Processing
            assert call_kwargs["completed_status"] == GcpApiDeepScanStatusEnum.Completed
            assert call_kwargs["failed_status"] == GcpApiDeepScanStatusEnum.Error
            assert call_kwargs["status_field_name"] == "deep_scan_status"
            assert call_kwargs["error_field_name"] == "deep_scan_error"

    @pytest.mark.asyncio
    async def test_queue_skips_non_queued_places(self, db_session: AsyncSession):
        """Test queue processor ignores non-Queued places."""

        # Setup: Create place with Completed status
        place = Place(
            id=uuid4(),
            place_id="completed_place",
            tenant_id=uuid4(),
            deep_scan_status=GcpApiDeepScanStatusEnum.Completed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock the SDK to track what gets processed
        processed_ids = []

        async def mock_processing_function(item_id, session):
            processed_ids.append(item_id)

        with patch(
            "src.services.deep_scan_scheduler.run_job_loop",
            side_effect=lambda **kwargs: kwargs["processing_function"]
        ):
            # Execute: Run queue processor
            await process_deep_scan_queue()

        # Verify: Completed place was not processed
        assert place.id not in processed_ids

    @pytest.mark.asyncio
    async def test_queue_handles_empty_queue(self, db_session: AsyncSession):
        """Test queue processor handles empty queue gracefully."""

        # Setup: Ensure no queued places exist
        stmt = select(Place).where(Place.deep_scan_status == GcpApiDeepScanStatusEnum.Queued)
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

        # Execute: Should not raise exception
        try:
            await process_deep_scan_queue()
        except Exception as e:
            pytest.fail(f"Queue processor should handle empty queue, but raised: {e}")


class TestDeepScanSetup:
    """Tests for setup_deep_scan_scheduler function."""

    def test_setup_registers_job_with_scheduler(self):
        """Test setup function registers job with correct configuration."""

        # Setup: Mock scheduler
        mock_scheduler = MagicMock()

        with patch("src.services.deep_scan_scheduler.scheduler", mock_scheduler):
            # Execute: Setup scheduler
            setup_deep_scan_scheduler()

            # Verify: Job registered
            mock_scheduler.add_job.assert_called_once()

            # Verify: Job configuration
            call_kwargs = mock_scheduler.add_job.call_args[1]
            assert call_kwargs["id"] == "process_deep_scan_queue"
            assert call_kwargs["name"] == "WF2 - Deep Scan Queue Processor"
            assert call_kwargs["trigger"] == "interval"
            assert call_kwargs["replace_existing"] is True
            assert call_kwargs["coalesce"] is True
            assert call_kwargs["misfire_grace_time"] == 60

    def test_setup_uses_settings_configuration(self):
        """Test setup function uses settings for interval, batch size, max instances."""

        mock_scheduler = MagicMock()

        with patch("src.services.deep_scan_scheduler.scheduler", mock_scheduler):
            with patch("src.services.deep_scan_scheduler.settings") as mock_settings:
                mock_settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES = 5
                mock_settings.DEEP_SCAN_SCHEDULER_BATCH_SIZE = 10
                mock_settings.DEEP_SCAN_SCHEDULER_MAX_INSTANCES = 1

                # Execute: Setup scheduler
                setup_deep_scan_scheduler()

                # Verify: Settings used
                call_kwargs = mock_scheduler.add_job.call_args[1]
                assert call_kwargs["minutes"] == 5
                assert call_kwargs["max_instances"] == 1


class TestDeepScanEdgeCases:
    """Tests for edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_handles_place_deleted_during_processing(self, db_session: AsyncSession):
        """Test handling when Place is deleted between fetch and process."""

        # Setup: Create and then delete place
        place_id = uuid4()
        place = Place(
            id=place_id,
            place_id="deleted_place",
            tenant_id=uuid4(),
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Delete the place
        await db_session.delete(place)
        await db_session.commit()

        # Execute & Verify: Should raise ValueError (handled by SDK)
        with pytest.raises(ValueError, match=f"Place {place_id} not found"):
            await process_single_deep_scan_wrapper(place_id, db_session)

    @pytest.mark.asyncio
    async def test_handles_service_exception(self, db_session: AsyncSession):
        """Test handling when service raises an exception."""

        # Setup: Create test place
        place = Place(
            id=uuid4(),
            place_id="error_place",
            tenant_id=uuid4(),
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock service to raise exception
        with patch(
            "src.services.deep_scan_scheduler.PlacesDeepService.process_single_deep_scan",
            side_effect=Exception("Service Error")
        ):
            # Execute & Verify: Exception propagates (SDK will catch it)
            with pytest.raises(Exception, match="Service Error"):
                await process_single_deep_scan_wrapper(place.id, db_session)

    @pytest.mark.asyncio
    async def test_handles_null_place_id(self, db_session: AsyncSession):
        """Test handling when place_id is null."""

        # Setup: Create place with null place_id
        place = Place(
            id=uuid4(),
            place_id=None,  # Null place_id
            tenant_id=uuid4(),
            deep_scan_status=GcpApiDeepScanStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(place)
        await db_session.commit()

        # Mock service (should handle null gracefully)
        with patch(
            "src.services.deep_scan_scheduler.PlacesDeepService.process_single_deep_scan",
            return_value=None
        ):
            # Execute: Should not crash
            await process_single_deep_scan_wrapper(place.id, db_session)

        # Verify: Error status set
        await db_session.refresh(place)
        assert place.deep_scan_status == GcpApiDeepScanStatusEnum.Error

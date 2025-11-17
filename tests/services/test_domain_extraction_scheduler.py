"""
Unit tests for WF3 Domain Extraction Scheduler

Tests the domain_extraction_scheduler.py module including:
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

from src.models.local_business import DomainExtractionStatusEnum, LocalBusiness
from src.models.domain import Domain
from src.services.domain_extraction_scheduler import (
    process_domain_extraction_queue,
    process_domain_extraction_wrapper,
    setup_domain_extraction_scheduler,
)


class TestDomainExtractionAdapter:
    """Tests for process_domain_extraction_wrapper adapter function."""

    @pytest.mark.asyncio
    async def test_adapter_processes_business_successfully(self, db_session: AsyncSession):
        """Test adapter successfully processes a valid LocalBusiness record."""

        # Setup: Create test local business
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Test Business",
            website="https://example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock the service to return True (success)
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=True
        ) as mock_service:
            # Execute: Call adapter
            await process_domain_extraction_wrapper(business.id, db_session)

            # Verify: Service called with correct params
            mock_service.assert_called_once()
            call_args = mock_service.call_args
            assert call_args[1]["local_business_id"] == business.id
            assert call_args[1]["session"] == db_session

        # Verify: LocalBusiness status updated to Completed
        await db_session.refresh(business)
        assert business.domain_extraction_status == DomainExtractionStatusEnum.Completed
        assert business.domain_extraction_error is None

    @pytest.mark.asyncio
    async def test_adapter_handles_service_failure(self, db_session: AsyncSession):
        """Test adapter handles service returning False (failure case)."""

        # Setup: Create test local business
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Test Business",
            website="https://invalid-domain.test",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock service to return False (failure)
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=False
        ):
            # Execute: Call adapter
            await process_domain_extraction_wrapper(business.id, db_session)

        # Verify: LocalBusiness status updated to Error
        await db_session.refresh(business)
        assert business.domain_extraction_status == DomainExtractionStatusEnum.Error
        assert "Failed to create Domain record" in business.domain_extraction_error

    @pytest.mark.asyncio
    async def test_adapter_raises_error_when_business_not_found(self, db_session: AsyncSession):
        """Test adapter raises ValueError when LocalBusiness record doesn't exist."""

        # Setup: Use non-existent UUID
        fake_id = uuid4()

        # Execute & Verify: Should raise ValueError
        with pytest.raises(ValueError, match=f"LocalBusiness {fake_id} not found"):
            await process_domain_extraction_wrapper(fake_id, db_session)

    @pytest.mark.asyncio
    async def test_adapter_updates_timestamp(self, db_session: AsyncSession):
        """Test adapter updates the updated_at timestamp."""

        # Setup: Create test local business
        initial_time = datetime.utcnow()
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Test Business",
            website="https://example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=initial_time,
            updated_at=initial_time
        )
        db_session.add(business)
        await db_session.commit()

        # Mock service
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=True
        ):
            # Execute: Call adapter
            await process_domain_extraction_wrapper(business.id, db_session)

        # Verify: Timestamp updated
        await db_session.refresh(business)
        assert business.updated_at > initial_time


class TestDomainExtractionQueue:
    """Tests for process_domain_extraction_queue function."""

    @pytest.mark.asyncio
    async def test_queue_processes_queued_businesses(self, db_session: AsyncSession):
        """Test queue processor handles Queued businesses."""

        # Setup: Create queued business
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Queued Business",
            website="https://queued.example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Queued,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock the SDK run_job_loop to verify it's called correctly
        with patch("src.services.domain_extraction_scheduler.run_job_loop") as mock_loop:
            # Execute: Run queue processor
            await process_domain_extraction_queue()

            # Verify: SDK loop called with correct parameters
            mock_loop.assert_called_once()
            call_kwargs = mock_loop.call_args[1]
            assert call_kwargs["model"] == LocalBusiness
            assert call_kwargs["queued_status"] == DomainExtractionStatusEnum.Queued
            assert call_kwargs["processing_status"] == DomainExtractionStatusEnum.Processing
            assert call_kwargs["completed_status"] == DomainExtractionStatusEnum.Completed
            assert call_kwargs["failed_status"] == DomainExtractionStatusEnum.Error
            assert call_kwargs["status_field_name"] == "domain_extraction_status"
            assert call_kwargs["error_field_name"] == "domain_extraction_error"

    @pytest.mark.asyncio
    async def test_queue_skips_non_queued_businesses(self, db_session: AsyncSession):
        """Test queue processor ignores non-Queued businesses."""

        # Setup: Create business with Completed status
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Completed Business",
            website="https://completed.example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Completed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock the SDK to track what gets processed
        processed_ids = []

        async def mock_processing_function(item_id, session):
            processed_ids.append(item_id)

        with patch(
            "src.services.domain_extraction_scheduler.run_job_loop",
            side_effect=lambda **kwargs: kwargs["processing_function"]
        ):
            # Execute: Run queue processor
            await process_domain_extraction_queue()

        # Verify: Completed business was not processed
        assert business.id not in processed_ids

    @pytest.mark.asyncio
    async def test_queue_handles_empty_queue(self, db_session: AsyncSession):
        """Test queue processor handles empty queue gracefully."""

        # Setup: Ensure no queued businesses exist
        stmt = select(LocalBusiness).where(
            LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

        # Execute: Should not raise exception
        try:
            await process_domain_extraction_queue()
        except Exception as e:
            pytest.fail(f"Queue processor should handle empty queue, but raised: {e}")


class TestDomainExtractionSetup:
    """Tests for setup_domain_extraction_scheduler function."""

    def test_setup_registers_job_with_scheduler(self):
        """Test setup function registers job with correct configuration."""

        # Setup: Mock scheduler
        mock_scheduler = MagicMock()

        with patch("src.services.domain_extraction_scheduler.scheduler", mock_scheduler):
            # Execute: Setup scheduler
            setup_domain_extraction_scheduler()

            # Verify: Job registered
            mock_scheduler.add_job.assert_called_once()

            # Verify: Job configuration
            call_kwargs = mock_scheduler.add_job.call_args[1]
            assert call_kwargs["id"] == "process_domain_extraction_queue"
            assert call_kwargs["name"] == "WF3 - Domain Extraction Queue Processor"
            assert call_kwargs["trigger"] == "interval"
            assert call_kwargs["replace_existing"] is True
            assert call_kwargs["coalesce"] is True
            assert call_kwargs["misfire_grace_time"] == 60

    def test_setup_uses_settings_configuration(self):
        """Test setup function uses settings for interval, batch size, max instances."""

        mock_scheduler = MagicMock()

        with patch("src.services.domain_extraction_scheduler.scheduler", mock_scheduler):
            with patch("src.services.domain_extraction_scheduler.settings") as mock_settings:
                mock_settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES = 2
                mock_settings.DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE = 20
                mock_settings.DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES = 1

                # Execute: Setup scheduler
                setup_domain_extraction_scheduler()

                # Verify: Settings used
                call_kwargs = mock_scheduler.add_job.call_args[1]
                assert call_kwargs["minutes"] == 2
                assert call_kwargs["max_instances"] == 1


class TestDomainExtractionEdgeCases:
    """Tests for edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_handles_business_deleted_during_processing(self, db_session: AsyncSession):
        """Test handling when LocalBusiness is deleted between fetch and process."""

        # Setup: Create and then delete business
        business_id = uuid4()
        business = LocalBusiness(
            id=business_id,
            tenant_id=uuid4(),
            name="Deleted Business",
            website="https://deleted.example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Delete the business
        await db_session.delete(business)
        await db_session.commit()

        # Execute & Verify: Should raise ValueError (handled by SDK)
        with pytest.raises(ValueError, match=f"LocalBusiness {business_id} not found"):
            await process_domain_extraction_wrapper(business_id, db_session)

    @pytest.mark.asyncio
    async def test_handles_service_exception(self, db_session: AsyncSession):
        """Test handling when service raises an exception."""

        # Setup: Create test business
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Error Business",
            website="https://error.example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock service to raise exception
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            side_effect=Exception("Service Error")
        ):
            # Execute & Verify: Exception propagates (SDK will catch it)
            with pytest.raises(Exception, match="Service Error"):
                await process_domain_extraction_wrapper(business.id, db_session)

    @pytest.mark.asyncio
    async def test_handles_null_website(self, db_session: AsyncSession):
        """Test handling when business website is null."""

        # Setup: Create business with null website
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="No Website Business",
            website=None,  # Null website
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock service (should handle null gracefully)
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=False
        ):
            # Execute: Should not crash
            await process_domain_extraction_wrapper(business.id, db_session)

        # Verify: Error status set
        await db_session.refresh(business)
        assert business.domain_extraction_status == DomainExtractionStatusEnum.Error

    @pytest.mark.asyncio
    async def test_handles_invalid_website_url(self, db_session: AsyncSession):
        """Test handling when business has invalid website URL."""

        # Setup: Create business with invalid URL
        business = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Invalid URL Business",
            website="not-a-valid-url",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business)
        await db_session.commit()

        # Mock service to return False for invalid URL
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=False
        ):
            # Execute: Should not crash
            await process_domain_extraction_wrapper(business.id, db_session)

        # Verify: Error status set
        await db_session.refresh(business)
        assert business.domain_extraction_status == DomainExtractionStatusEnum.Error


class TestDomainExtractionConcurrency:
    """Tests for concurrent execution scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_extraction_same_domain(self, db_session: AsyncSession):
        """Test handling when multiple businesses extract the same domain concurrently."""

        # Setup: Create two businesses with same domain
        business1 = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Business 1",
            website="https://example.com",
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        business2 = LocalBusiness(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Business 2",
            website="https://example.com",  # Same domain
            domain_extraction_status=DomainExtractionStatusEnum.Processing,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(business1)
        db_session.add(business2)
        await db_session.commit()

        # Mock service to return True for both
        with patch(
            "src.services.domain_extraction_scheduler.LocalBusinessToDomainService.create_pending_domain_from_local_business",
            return_value=True
        ):
            # Execute: Process both (simulating concurrent extraction)
            await process_domain_extraction_wrapper(business1.id, db_session)
            await process_domain_extraction_wrapper(business2.id, db_session)

        # Verify: Both completed successfully
        await db_session.refresh(business1)
        await db_session.refresh(business2)
        assert business1.domain_extraction_status == DomainExtractionStatusEnum.Completed
        assert business2.domain_extraction_status == DomainExtractionStatusEnum.Completed

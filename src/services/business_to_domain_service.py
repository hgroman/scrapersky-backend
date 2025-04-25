"""
Service to handle the process of creating a pending Domain entry
from a selected LocalBusiness record.
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.domain import Domain
from src.models.local_business import LocalBusiness

# Assuming a utility for domain extraction exists or will be created
# from src.utils.domain_extractor import extract_domain_from_url

logger = logging.getLogger(__name__)


class LocalBusinessToDomainService:
    """
    Handles the logic for extracting a domain from a LocalBusiness website URL
    and creating a corresponding 'pending' Domain record.
    """

    async def create_pending_domain_from_local_business(
        self, local_business_id: UUID, session: AsyncSession
    ) -> bool:
        """
        Fetches a LocalBusiness, extracts its domain, and creates a new Domain record
        with 'pending' status.

        Args:
            local_business_id: The UUID of the LocalBusiness record.
            session: The SQLAlchemy AsyncSession to use.

        Returns:
            True if a new pending Domain was successfully created or if the domain
            already existed, False if an error occurred (e.g., business not found,
            no URL, extraction error, DB error).
        """
        logger.info(
            f"Starting domain extraction for local_business_id: {local_business_id}"
        )

        try:
            # 1. Fetch the LocalBusiness record
            stmt = select(LocalBusiness).where(LocalBusiness.id == local_business_id)
            result = await session.execute(stmt)
            business = result.scalar_one_or_none()

            if not business:
                logger.warning(f"LocalBusiness not found for id: {local_business_id}")
                return False  # Indicate failure, business not found

            # 2. Check for website URL
            website_url = business.website_url
            # Explicit check for None or empty string
            if website_url is None or website_url == "":
                logger.info(
                    f"No website_url found for local_business_id: {local_business_id}. Skipping domain creation."
                )
                # This is not necessarily an error, just nothing to process. Return True as the step completed.
                return True

            # 3. Extract the domain (Placeholder for actual extraction logic)
            # TODO: Implement robust domain extraction (e.g., using tldextract or similar)
            try:
                # extracted_domain = extract_domain_from_url(website_url) # Replace with actual call
                # Simplified placeholder:
                if website_url.startswith("http://"):
                    extracted_domain = website_url.split("/")[2]
                elif website_url.startswith("https://"):
                    extracted_domain = website_url.split("/")[2]
                else:
                    # Basic attempt if no scheme, might need refinement
                    extracted_domain = website_url.split("/")[0]

                if not extracted_domain:
                    raise ValueError("Could not extract domain from URL")

                # Remove www. if present for consistency
                extracted_domain = extracted_domain.replace("www.", "")

                logger.info(
                    f"Extracted domain '{extracted_domain}' from URL '{website_url}' for business {local_business_id}"
                )

            except Exception as extraction_error:
                logger.error(
                    f"Error extracting domain from URL '{website_url}' for business {local_business_id}: {extraction_error}",
                    exc_info=True,
                )
                # Consider this a failure of the process
                return False

            # 4. Check if domain already exists
            stmt_domain_check = select(Domain).where(Domain.domain == extracted_domain)
            result_domain_check = await session.execute(stmt_domain_check)
            existing_domain = result_domain_check.scalar_one_or_none()

            if existing_domain:
                logger.info(
                    f"Domain '{extracted_domain}' already exists (ID: {existing_domain.id}). Skipping creation."
                )
                # Domain already exists, maybe link it? For now, just consider it success.
                # Optionally, update existing_domain.local_business_id if null? TBD based on product reqs.
                return True

            # 5. Create new Domain record
            new_domain = Domain(
                domain=extracted_domain,
                status="pending",  # Explicitly set status for the next processing stage
                local_business_id=local_business_id,
                # tenant_id will be set by default in the model
            )
            session.add(new_domain)
            # Flush to ensure the domain is added before the scheduler potentially updates the business status to completed
            await session.flush()
            logger.info(
                f"Successfully created new pending Domain record (ID: {new_domain.id}) for domain '{extracted_domain}' from business {local_business_id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Unexpected error processing local_business_id {local_business_id}: {e}",
                exc_info=True,
            )
            # Consider rolling back? The outer scheduler function should handle final status update.
            # Here, indicate failure.
            return False

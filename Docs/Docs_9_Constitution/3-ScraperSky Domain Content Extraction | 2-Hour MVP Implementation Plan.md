> ⚠️ **SOURCE OF TRUTH**
> This document overrides any conflicting information in summaries.
> Code is final authority; update THIS doc if it diverges.

# ScraperSky Domain Content Extraction: 2-Hour MVP Implementation Plan

## Overview

This document outlines a rapid implementation plan for the ScraperSky Domain Content Extraction service. The goal is to build a functional MVP within 2 hours that extracts valuable information from websites and stores it in structured database tables, while adhering to the existing ScraperSky architecture patterns.

## Core Architecture Principles

- **Follow existing producer-consumer pattern**
- **Use SQLAlchemy ORM exclusively** (no raw SQL) - See [ABSOLUTE ORM REQUIREMENT](../../../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)
- **Connect via Supavisor** for proper connection pooling
- **Implement as a standard workflow** within the ScraperSky ecosystem

## Implementation Phases

### Phase 0: Quick Prototype (30 min)

#### 0.1 Basic Crawler Setup

```python
# src/services/domain_content_service.py

import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import re
import json
import logging

class DomainContentExtractor:
    def __init__(self):
        self.crawler = AsyncWebCrawler(max_concurrent_tasks=5)
        self.config = CrawlerRunConfig(
            stream=True,
            check_robots_txt=True,
            user_agent="ScraperSkyBot/1.0"
        )

    async def crawl_domain(self, url):
        """Crawl a single domain homepage and return the results."""
        try:
            results = []
            async for result in self.crawler.arun(url, self.config):
                results.append(result)

            return results[0] if results else None
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            return None
```

#### 0.2 Data Extraction Functions

```python
# src/services/extraction_utils.py

import re
from bs4 import BeautifulSoup
import json

def extract_emails(html_content):
    """Extract email addresses from HTML content."""
    if not html_content:
        return []

    # Basic email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, html_content))

    # Filter out common false positives
    filtered_emails = [
        email for email in emails
        if not any(exclude in email for exclude in ['@example', '@domain'])
    ]

    # Categorize emails
    categorized = []
    for email in filtered_emails:
        email_type = "general"
        if any(prefix in email.lower().split('@')[0] for prefix in ['info', 'contact', 'hello']):
            email_type = "general"
        elif any(prefix in email.lower().split('@')[0] for prefix in ['sales', 'billing']):
            email_type = "sales"
        elif any(prefix in email.lower().split('@')[0] for prefix in ['support', 'help']):
            email_type = "support"

        categorized.append({
            "email": email,
            "type": email_type
        })

    return categorized

def extract_social_media(html_content, domain_url):
    """Extract social media links from HTML content."""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    social_platforms = {
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'instagram': ['instagram.com'],
        'linkedin': ['linkedin.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'pinterest': ['pinterest.com'],
        'tiktok': ['tiktok.com'],
        'github': ['github.com']
    }

    social_links = []

    # Find all links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href'].lower()

        # Skip empty, javascript, and mailto links
        if not href or href.startswith(('javascript:', 'mailto:', '#')):
            continue

        # Normalize URL
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = domain_url.rstrip('/') + href

        # Check if link matches any social platform
        for platform, domains in social_platforms.items():
            if any(domain in href for domain in domains):
                # Extract handle from URL if possible
                handle = None
                path_parts = href.split('/')
                if len(path_parts) > 3 and path_parts[3]:
                    handle = path_parts[3].split('?')[0]

                social_links.append({
                    "platform": platform,
                    "url": href,
                    "handle": handle
                })
                break

    return social_links

def extract_metadata(html_content, url):
    """Extract basic metadata from HTML content."""
    if not html_content:
        return {}

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title
    title = None
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        title = title_tag.string.strip()

    # Extract description
    description = None
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content'].strip()

    # Count images
    image_count = len(soup.find_all('img'))

    # Estimate word count
    text = soup.get_text()
    word_count = len(text.split())

    metadata = {
        "title": title,
        "description": description,
        "url": url,
        "stats": {
            "image_count": image_count,
            "word_count": word_count
        },
        "raw_html_length": len(html_content) if html_content else 0
    }

    return metadata
```

#### 0.3 Quick Test Script

```python
# scripts/test_extraction.py

import asyncio
import json
from services.domain_content_service import DomainContentExtractor
from services.extraction_utils import extract_emails, extract_social_media, extract_metadata

async def test_extraction(urls):
    extractor = DomainContentExtractor()
    results = []

    for url in urls:
        print(f"Crawling {url}...")
        crawl_result = await extractor.crawl_domain(url)

        if not crawl_result or not crawl_result.html:
            print(f"Failed to crawl {url}")
            continue

        html_content = crawl_result.html

        result = {
            "url": url,
            "metadata": extract_metadata(html_content, url),
            "emails": extract_emails(html_content),
            "social_media": extract_social_media(html_content, url)
        }

        results.append(result)
        print(f"Extracted data from {url}")

    # Save results to file for review
    with open('extraction_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Processed {len(results)} domains. Results saved to extraction_results.json")

if __name__ == "__main__":
    test_urls = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com"
    ]

    asyncio.run(test_extraction(test_urls))
```

<!--
  The full SQLAlchemy model definitions are now in appendix A.
  Developers must NOT create migrations until Phase 0 produces approved fields.
-->
### Phase 1: Database Schema Implementation (20 min)

#### 1.1 Schema Requirements

Implement the database schema following the Constitution specifications:

1. **Domains Table Extensions**:

   - `content_extraction_status` (ENUM)
   - `content_extraction_error` (TEXT)
   - `last_crawled` (TIMESTAMP)
   - `metadata` (JSONB)

2. **New Contacts Table**: For storing extracted email contacts

3. **New SocialMedia Table**: For storing social media links and handles

4. **Required Enum Values**: Follow standard status naming conventions

Refer to Appendix A for complete schema implementation details.

### Phase 2: Core Service Implementation (40 min)

#### 2.1 Main Service Class

```python
# src/services/domain_content_service.py

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from sqlalchemy.orm import selectinload
import uuid

from models.domain_content import Domain, Contact, SocialMedia
from schemas.domain_content import DomainContentProcessingStatus
from services.extraction_utils import extract_emails, extract_social_media, extract_metadata
from services.domain_content_extractor import DomainContentExtractor

logger = logging.getLogger(__name__)

class DomainContentService:
    def __init__(self):
        self.extractor = DomainContentExtractor()

    async def process_domain(self, domain_id: uuid.UUID, session: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Process a domain by crawling it and extracting content.

        Args:
            domain_id: UUID of the domain to process
            session: SQLAlchemy async session

        Returns:
            Dictionary with extraction results or None if failure
        """
        try:
            # Get domain from database
            stmt = select(Domain).where(Domain.id == domain_id).options(
                selectinload(Domain.contacts),
                selectinload(Domain.social_media_accounts)
            )
            result = await session.execute(stmt)
            domain = result.scalar_one_or_none()

            if not domain:
                logger.error(f"Domain with ID {domain_id} not found")
                return None

            # Crawl domain
            crawl_result = await self.extractor.crawl_domain(domain.url)

            if not crawl_result or not crawl_result.html:
                error_msg = f"Failed to crawl domain: {domain.url}"
                await self._update_domain_status(
                    domain_id,
                    DomainContentProcessingStatus.ERROR,
                    error_msg,
                    session
                )
                return None

            html_content = crawl_result.html

            # Extract data
            emails = extract_emails(html_content)
            social_links = extract_social_media(html_content, domain.url)
            metadata = extract_metadata(html_content, domain.url)

            # Update domain metadata
            domain.title = metadata.get("title") or domain.title
            domain.description = metadata.get("description") or domain.description
            domain.metadata = metadata

            # Store contacts (with deduplication)
            existing_emails = {contact.email for contact in domain.contacts}
            for email_data in emails:
                if email_data["email"] not in existing_emails:
                    contact = Contact(
                        domain_id=domain_id,
                        email=email_data["email"],
                        type=email_data["type"]
                    )
                    session.add(contact)
                    existing_emails.add(email_data["email"])

            # Store social media accounts (with deduplication)
            existing_social = {(account.platform, account.url) for account in domain.social_media_accounts}
            for social_data in social_links:
                key = (social_data["platform"], social_data["url"])
                if key not in existing_social:
                    social = SocialMedia(
                        domain_id=domain_id,
                        platform=social_data["platform"],
                        handle=social_data.get("handle"),
                        url=social_data["url"]
                    )
                    session.add(social)
                    existing_social.add(key)

            # Update domain status
            await self._update_domain_status(
                domain_id,
                DomainContentProcessingStatus.COMPLETE,
                None,
                session
            )

            # Return extraction results
            return {
                "domain_id": domain_id,
                "metadata": metadata,
                "emails_extracted": len(emails),
                "social_accounts_extracted": len(social_links)
            }

        except Exception as e:
            logger.exception(f"Error processing domain {domain_id}: {e}")
            await self._update_domain_status(
                domain_id,
                DomainContentProcessingStatus.ERROR,
                str(e),
                session
            )
            return None

    async def _update_domain_status(
        self,
        domain_id: uuid.UUID,
        status: DomainContentProcessingStatus,
        error: Optional[str],
        session: AsyncSession
    ):
        """Update the processing status of a domain."""
        stmt = (
            update(Domain)
            .where(Domain.id == domain_id)
            .values(
                domain_content_processing_status=status.value,
                domain_content_processing_error=error
            )
        )
        await session.execute(stmt)
```

#### 2.2 Scheduler Implementation

```python
# src/schedulers/domain_content_scheduler.py

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from datetime import datetime, timedelta

from db.session import get_db
from models.domain_content import Domain
from schemas.domain_content import DomainContentProcessingStatus
from services.domain_content_service import DomainContentService

logger = logging.getLogger(__name__)

class DomainContentScheduler:
    def __init__(self):
        self.service = DomainContentService()
        self.max_concurrent = 5  # Process up to 5 domains concurrently
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent)

    async def process_pending_domains(self):
        """
        Find domains with QUEUED status and process them.
        """
        async with get_db() as session:
            # Find domains with QUEUED status
            stmt = select(Domain).where(
                Domain.domain_content_processing_status == DomainContentProcessingStatus.QUEUED.value
            ).limit(20)  # Process max 20 domains per run

            result = await session.execute(stmt)
            domains = result.scalars().all()

            if not domains:
                logger.info("No domains queued for processing")
                return

            logger.info(f"Found {len(domains)} domains to process")

            # Process domains concurrently
            tasks = []
            for domain in domains:
                task = asyncio.create_task(self._process_domain(domain.id, session))
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

    async def _process_domain(self, domain_id, session_factory):
        """Process a single domain with concurrency control."""
        async with self.processing_semaphore:
            async with session_factory() as session:
                async with session.begin():
                    # Update status to PROCESSING
                    stmt = (
                        update(Domain)
                        .where(Domain.id == domain_id)
                        .values(
                            domain_content_processing_status=DomainContentProcessingStatus.PROCESSING.value
                        )
                    )
                    await session.execute(stmt)

            # Start new session for actual processing
            async with session_factory() as session:
                async with session.begin():
                    await self.service.process_domain(domain_id, session)

    async def cleanup_stale_jobs(self):
        """Reset jobs stuck in PROCESSING state for too long (e.g., 30 minutes)."""
        async with get_db() as session:
            async with session.begin():
                thirty_mins_ago = datetime.utcnow() - timedelta(minutes=30)

                stmt = (
                    update(Domain)
                    .where(
                        and_(
                            Domain.domain_content_processing_status == DomainContentProcessingStatus.PROCESSING.value,
                            Domain.updated_at < thirty_mins_ago
                        )
                    )
                    .values(
                        domain_content_processing_status=DomainContentProcessingStatus.ERROR.value,
                        domain_content_processing_error="Processing timed out after 30 minutes"
                    )
                )

                result = await session.execute(stmt)
                logger.info(f"Reset {result.rowcount} stale processing jobs")
```

### Phase 3: API Router Implementation (20 min)

```python
# src/routers/domain_content.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Optional
import uuid

from db.session import get_db
from models.domain_content import Domain
from schemas.domain_content import (
    Domain as DomainSchema,
    DomainCreate,
    DomainUpdate,
    DomainContentCurationStatus,
    DomainContentProcessingStatus,
    DomainContentExtraction
)
from services.domain_content_service import DomainContentService

router = APIRouter(prefix="/api/v3/domain-content", tags=["domain-content"])

@router.post("/process/{domain_id}", response_model=DomainSchema)
async def process_domain(
    domain_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """
    Queue a domain for content extraction.
    This follows the ScraperSky producer-consumer pattern:
    1. Update curation_status to QUEUED
    2. Update processing_status to QUEUED
    """
    async with session.begin():
        # Check if domain exists
        stmt = select(Domain).where(Domain.id == domain_id)
        result = await session.execute(stmt)
        domain = result.scalar_one_or_none()

        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")

        # Update statuses
        stmt = (
            update(Domain)
            .where(Domain.id == domain_id)
            .values(
                domain_content_curation_status=DomainContentCurationStatus.QUEUED.value,
                domain_content_processing_status=DomainContentProcessingStatus.QUEUED.value,
                domain_content_processing_error=None
            )
            .returning(Domain)
        )

        result = await session.execute(stmt)
        updated_domain = result.scalar_one()

        return updated_domain

@router.get("/domains/{domain_id}", response_model=DomainSchema)
async def get_domain(
    domain_id: uuid.UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get a domain with its extracted content."""
    stmt = select(Domain).where(Domain.id == domain_id)
    result = await session.execute(stmt)
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    return domain

@router.get("/domains", response_model=List[DomainSchema])
async def list_domains(
    status: Optional[DomainContentProcessingStatus] = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db)
):
    """List domains with optional status filtering."""
    query = select(Domain)

    if status:
        query = query.where(Domain.domain_content_processing_status == status.value)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    domains = result.scalars().all()

    return domains
```

### Phase 4: Integration with Main App (10 min)

#### 4.1 Register Router and Scheduler

```python
# src/main.py

# Import existing modules
# ...

# Import new modules
from routers import domain_content
from schedulers.domain_content_scheduler import DomainContentScheduler

# Initialize scheduler
domain_content_scheduler = DomainContentScheduler()

# Register router
app.include_router(domain_content.router)

# Register scheduler jobs
@app.on_event("startup")
async def start_schedulers():
    # Register existing schedulers
    # ...

    # Register domain content scheduler
    scheduler.add_job(
        domain_content_scheduler.process_pending_domains,
        "interval",
        minutes=1,
        id="domain_content_processing"
    )

    scheduler.add_job(
        domain_content_scheduler.cleanup_stale_jobs,
        "interval",
        minutes=5,
        id="domain_content_cleanup"
    )
```

## Testing and Verification

### Test Script

```python
# scripts/test_domain_content.py

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.domain_content import Domain
from schemas.domain_content import DomainContentCurationStatus, DomainContentProcessingStatus
from services.domain_content_service import DomainContentService

async def test_domain_processing():
    """
    Test the domain content extraction process on a sample domain.
    """
    # Sample domain data
    test_domain_url = "https://example.com"

    async with get_db() as session:
        async with session.begin():
            # Create test domain
            domain = Domain(
                url=test_domain_url,
                domain_content_curation_status=DomainContentCurationStatus.NEW.value,
                domain_content_processing_status=DomainContentProcessingStatus.NEW.value
            )
            session.add(domain)
            await session.flush()
            domain_id = domain.id

    print(f"Created test domain with ID: {domain_id}")

    # Process domain
    service = DomainContentService()
    async with get_db() as session:
        async with session.begin():
            # Update status to PROCESSING
            domain = await session.get(Domain, domain_id)
            domain.domain_content_processing_status = DomainContentProcessingStatus.PROCESSING.value

    print("Processing domain...")
    async with get_db() as session:
        async with session.begin():
            result = await service.process_domain(domain_id, session)

    print(f"Processing result: {result}")

    # Verify results
    async with get_db() as session:
        domain = await session.get(Domain, domain_id)
        print(f"Domain status: {domain.domain_content_processing_status}")
        print(f"Domain title: {domain.title}")
        print(f"Domain description: {domain.description}")
        print(f"Contacts found: {len(domain.contacts)}")
        print(f"Social media accounts found: {len(domain.social_media_accounts)}")

        # Print contacts
        print("\nContacts:")
        for contact in domain.contacts:
            print(f"  - {contact.email} ({contact.type})")

        # Print social media
        print("\nSocial Media:")
        for social in domain.social_media_accounts:
            print(f"  - {social.platform}: {social.handle or 'N/A'} - {social.url}")

if __name__ == "__main__":
    asyncio.run(test_domain_processing())
```

## Strategic Considerations

1. **Deduplication Strategy**:

   - Contacts are deduplicated by email address per domain
   - Social media accounts are deduplicated by platform+URL per domain
   - Database constraints ensure uniqueness

2. **JSON "Miscellaneous" Bucket**:

   - The `metadata` JSON field in the `domains` table stores all additional extracted data
   - This provides flexibility to store any additional information without schema changes

3. **Phased Implementation**:

   - This MVP focuses on basic extraction without vector database integration
   - The metadata extraction provides a foundation for future vector embedding

4. **Integration with Existing Workflow**:
   - The implementation follows the ScraperSky producer-consumer pattern
   - Uses standard naming conventions for status fields
   - Integrates with the existing scheduler infrastructure

## Future Expansion

1. **Vector Database Integration**:

   - Add chunking and embedding of page content
   - Implement HNSW indexing for similarity search
   - Add vector search endpoints

2. **Advanced Crawling**:

   - Extend to crawl multiple pages per domain
   - Add depth and breadth control parameters
   - Implement more sophisticated URL normalization

3. **Enhanced Metadata Extraction**:

   - Implement schema.org structured data extraction
   - Add sentiment analysis for page content
   - Extract pricing information and product details

4. **UI Integration**:
   - Create domain-curation-tab.js for frontend integration
   - Implement CRUD operations in the UI
   - Add visualization for extracted data

## Appendix A – Deferred Schema Code

### Database Models

```python
# src/models/domain_content.py

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from db.base import Base

class Domain(Base):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Status fields following ScraperSky conventions
    domain_content_curation_status = Column(String, nullable=False, default="New")
    domain_content_processing_status = Column(String, nullable=False, default="New")
    domain_content_processing_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", back_populates="domain", cascade="all, delete-orphan")
    social_media_accounts = relationship("SocialMedia", back_populates="domain", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, default="general")  # general, sales, support, etc.

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    domain = relationship("Domain", back_populates="contacts")

    # Composite unique constraint to prevent duplicates per domain
    __table_args__ = (
        {'schema': 'public'},
        UniqueConstraint('domain_id', 'email', name='uq_domain_email'),
    )

class SocialMedia(Base):
    __tablename__ = "social_media_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    platform = Column(String, nullable=False)  # facebook, twitter, instagram, etc.
    handle = Column(String, nullable=True)
    url = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    domain = relationship("Domain", back_populates="social_media_accounts")

    # Composite unique constraint to prevent duplicates per domain
    __table_args__ = (
        {'schema': 'public'},
        UniqueConstraint('domain_id', 'platform', 'url', name='uq_domain_platform_url'),
    )
```

### Pydantic Schemas

```python
# src/schemas/domain_content.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

class DomainContentCurationStatus(str, Enum):
    NEW = "New"
    QUEUED = "Queued"
    SELECTED = "Selected"
    NOT_A_FIT = "Not a Fit"
    ARCHIVED = "Archived"

class DomainContentProcessingStatus(str, Enum):
    NEW = "New"
    QUEUED = "Queued"
    PROCESSING = "Processing"
    COMPLETE = "Complete"
    ERROR = "Error"

class ContactBase(BaseModel):
    email: str
    type: str = "general"

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: UUID
    domain_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class SocialMediaBase(BaseModel):
    platform: str
    handle: Optional[str] = None
    url: str

class SocialMediaCreate(SocialMediaBase):
    pass

class SocialMedia(SocialMediaBase):
    id: UUID
    domain_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class DomainBase(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    domain_content_curation_status: Optional[DomainContentCurationStatus] = None
    domain_content_processing_status: Optional[DomainContentProcessingStatus] = None

class Domain(DomainBase):
    id: UUID
    domain_content_curation_status: DomainContentCurationStatus
    domain_content_processing_status: DomainContentProcessingStatus
    domain_content_processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contacts: List[Contact] = []
    social_media_accounts: List[SocialMedia] = []

    class Config:
        orm_mode = True

class DomainContentExtraction(BaseModel):
    domain_id: UUID
    extract_emails: bool = True
    extract_social_media: bool = True
    extract_metadata: bool = True
```

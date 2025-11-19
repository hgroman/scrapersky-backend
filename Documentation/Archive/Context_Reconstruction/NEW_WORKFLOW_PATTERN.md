# ScraperSky New Workflow Creation Pattern
**Purpose:** How to add completely new workflows to the system
**Last Updated:** November 17, 2025
**Audience:** Developers adding major features, workflow architects

---

## Overview

This guide documents how to create **entirely new workflows** in the ScraperSky system, following established architectural patterns and ensuring consistency with existing WF1-7.

### When to Create a New Workflow

**Create a new workflow when:**
- Adding a major new data processing pipeline
- Introducing a new data source (beyond Google Maps)
- Adding complex multi-step processing
- Need user curation + automated processing

**Don't create a workflow when:**
- Adding a simple endpoint (use direct submission instead)
- One-off data processing (use script or service)
- Minor feature addition to existing workflow

---

## Workflow Anatomy

Every ScraperSky workflow follows the **4-Layer Constitutional Architecture**:

```
Layer 1: Models (Database Schema)
   ↓
Layer 2: Schemas (API Contracts)
   ↓
Layer 3: Routers (API Endpoints, Transaction Boundaries)
   ↓
Layer 4: Services (Business Logic)
   ↓
Optional: Scheduler (Background Processing)
```

---

## Step-by-Step: Create WF8 (Example)

Let's create **WF8: Email Validation** as an example:
- **Input:** Domain records with emails
- **Output:** Validated emails with deliverability scores
- **Process:** Background validation + user curation

### Step 1: Design the Data Model (Layer 1)

**File:** `src/models/email_validation.py`

```python
"""
WF8 Email Validation Model
Layer 1 Component per ScraperSky Constitutional Standards
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base import Base


# Status Enums (Follow dual-status pattern if user curation needed)
class EmailCurationStatusEnum(enum.Enum):
    """User decision on email validity"""
    New = "New"
    Selected = "Selected"      # User approved
    Rejected = "Rejected"      # User rejected
    Maybe = "Maybe"            # Needs review


class EmailValidationStatusEnum(enum.Enum):
    """System processing status"""
    Queued = "Queued"          # Waiting for validation
    Processing = "Processing"  # Validation in progress
    Complete = "Complete"      # Validation finished
    Error = "Error"            # Validation failed


class EmailValidation(Base):
    """
    WF8 Email Validation Model

    Stores email addresses extracted from domains with validation results.
    """
    __tablename__ = "email_validations"

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    domain_id = Column(PGUUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)

    # Email Data
    email = Column(String(255), nullable=False, index=True)
    source = Column(String(100))  # Where email was found

    # Validation Results
    is_deliverable = Column(Boolean)
    deliverability_score = Column(Float)  # 0.0-1.0
    validation_metadata = Column(JSONB)   # Additional validation data

    # Dual-Status Pattern (User + System)
    email_curation_status = Column(
        String(50),
        nullable=False,
        default=EmailCurationStatusEnum.New.value,
        index=True
    )
    email_validation_status = Column(
        String(50),
        nullable=True,  # NULL until queued
        index=True
    )

    # Error Tracking
    validation_error = Column(Text)

    # Audit Fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String(255))
    tenant_id = Column(PGUUID(as_uuid=True))

    # Relationships
    domain = relationship("Domain", back_populates="email_validations")
```

**Key Decisions:**
- **Dual-status pattern:** User curation + system processing
- **JSONB for flexibility:** Validation metadata can vary
- **Index strategy:** Status fields + email for fast queries
- **Foreign key:** Link to Domain (source of email)

### Migration:
```python
# alembic/versions/xxx_create_email_validations.py
def upgrade():
    op.create_table(
        'email_validations',
        # ... columns ...
    )
    op.create_index('idx_email_curation_status', 'email_validations', ['email_curation_status'])
    op.create_index('idx_email_validation_status', 'email_validations', ['email_validation_status'])
```

---

### Step 2: Create API Schemas (Layer 2)

**File:** `src/schemas/WF8_L2_EmailValidationSchemas.py`

```python
"""
WF8 Email Validation Schemas
Layer 2 Component per ScraperSky Constitutional Standards
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class EmailValidationResponse(BaseModel):
    """Response schema for email validation record"""
    id: UUID
    email: EmailStr
    domain_id: UUID
    is_deliverable: Optional[bool]
    deliverability_score: Optional[float]
    email_curation_status: str
    email_validation_status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailCurationBatchUpdateRequest(BaseModel):
    """Request to batch update email curation status"""
    email_ids: List[UUID]
    status: str  # New/Selected/Rejected/Maybe


class EmailCurationBatchUpdateResponse(BaseModel):
    """Response after batch status update"""
    updated_count: int
    queued_count: int  # How many were queued for validation
```

---

### Step 3: Create Router (Layer 3)

**File:** `src/routers/v3/WF8_V3_L3_EmailValidationRouter.py`

```python
"""
WF8 Email Validation Router
Layer 3 Component per ScraperSky Constitutional Standards

Author: The Architect
Date: 2025-11-17
Compliance: 100% Layer 3 Blueprint Adherent
"""

from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.schemas.WF8_L2_EmailValidationSchemas import (
    EmailValidationResponse,
    EmailCurationBatchUpdateRequest,
    EmailCurationBatchUpdateResponse
)
from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
from src.models.email_validation import (
    EmailValidation,
    EmailCurationStatusEnum,
    EmailValidationStatusEnum
)

router = APIRouter(prefix="/api/v3/email-validations", tags=["V3 - Email Validation"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_email_validations(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
    curation_status: Optional[EmailCurationStatusEnum] = None,
    validation_status: Optional[EmailValidationStatusEnum] = None,
):
    """
    Get email validations with filtering.

    Returns paginated list of email validation records.
    """
    filters = []
    if curation_status:
        filters.append(EmailValidation.email_curation_status == curation_status.value)
    if validation_status:
        filters.append(EmailValidation.email_validation_status == validation_status.value)

    # Get total count
    count_stmt = select(EmailValidation)
    if filters:
        count_stmt = count_stmt.where(*filters)
    count_result = await session.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    # Get paginated results
    stmt = select(EmailValidation).offset(offset).limit(limit)
    if filters:
        stmt = stmt.where(*filters)
    result = await session.execute(stmt)
    emails = result.scalars().all()

    return {
        "emails": [EmailValidationResponse.from_orm(e) for e in emails],
        "total": total_count,
        "offset": offset,
        "limit": limit
    }


@router.put("/status", response_model=EmailCurationBatchUpdateResponse)
async def update_email_curation_status_batch(
    request: EmailCurationBatchUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Batch update email curation status.

    Implements dual-status pattern:
    - Updates email_curation_status to requested value
    - If status='Selected', triggers validation by setting email_validation_status='Queued'
    """
    updated_count = 0
    queued_count = 0

    # Router owns transaction boundary
    async with session.begin():
        stmt = select(EmailValidation).where(EmailValidation.id.in_(request.email_ids))
        result = await session.execute(stmt)
        emails_to_update = result.scalars().all()

        if not emails_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No emails found with provided IDs"
            )

        for email in emails_to_update:
            email.email_curation_status = request.status
            updated_count += 1

            # Dual-Status Pattern - trigger validation when Selected
            if request.status == EmailCurationStatusEnum.Selected.value:
                email.email_validation_status = EmailValidationStatusEnum.Queued.value
                email.validation_error = None
                queued_count += 1

    return EmailCurationBatchUpdateResponse(
        updated_count=updated_count,
        queued_count=queued_count
    )
```

**Critical Patterns:**
- **Transaction boundary:** Router owns `async with session.begin()`
- **Dual-status update:** When Selected → Queued
- **Authentication:** `Depends(get_current_user)`
- **V3 prefix:** `/api/v3/email-validations`

---

### Step 4: Create Service (Layer 4)

**File:** `src/services/WF8_L4_EmailValidationService.py`

```python
"""
WF8 Email Validation Service
Layer 4 Component per ScraperSky Constitutional Standards
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.email_validation import (
    EmailValidation,
    EmailValidationStatusEnum
)

logger = logging.getLogger(__name__)


class EmailValidationService:
    """
    Service for validating email addresses.

    This service handles:
    - Email format validation
    - Deliverability checks
    - Domain verification
    - Result storage
    """

    async def validate_single_email(
        self,
        email_id: UUID,
        session: AsyncSession
    ) -> bool:
        """
        Validate a single email address.

        Args:
            email_id: UUID of EmailValidation record
            session: Database session (no active transaction)

        Returns:
            True if validation successful, False otherwise
        """
        # Service manages its own transaction
        async with session.begin():
            # Fetch email record
            email = await session.get(EmailValidation, email_id)
            if not email:
                logger.error(f"Email {email_id} not found")
                return False

            logger.info(f"Validating email: {email.email}")

            try:
                # Call external validation API (e.g., ZeroBounce, Hunter.io)
                result = await self._call_validation_api(email.email)

                # Update record with results
                email.is_deliverable = result["is_deliverable"]
                email.deliverability_score = result["score"]
                email.validation_metadata = result["metadata"]
                email.email_validation_status = EmailValidationStatusEnum.Complete.value
                email.validation_error = None

                logger.info(f"Email {email.email} validated: {result['is_deliverable']}")
                return True

            except Exception as e:
                logger.error(f"Email validation failed for {email.email}: {e}")
                email.email_validation_status = EmailValidationStatusEnum.Error.value
                email.validation_error = str(e)
                return False

    async def _call_validation_api(self, email: str) -> dict:
        """
        Call external email validation API.

        In production, integrate with service like:
        - ZeroBounce
        - Hunter.io
        - Kickbox
        - NeverBounce
        """
        # Placeholder - implement actual API call
        import asyncio
        await asyncio.sleep(0.5)  # Simulate API call

        return {
            "is_deliverable": True,
            "score": 0.95,
            "metadata": {
                "provider": "gmail",
                "catch_all": False,
                "disposable": False
            }
        }
```

**Service Patterns:**
- **Async session management:** Service owns transaction
- **Error handling:** Try/except with status updates
- **Logging:** Info + error levels
- **External API calls:** Abstracted to private method

---

### Step 5: Create Scheduler (Background Processing)

**File:** `src/schedulers/WF8_EmailValidationScheduler.py`

```python
"""
WF8 Email Validation Scheduler
Processes email records queued for validation
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.email_validation import (
    EmailValidation,
    EmailValidationStatusEnum
)
from src.scheduler_instance import scheduler
from src.services.WF8_L4_EmailValidationService import EmailValidationService

logger = logging.getLogger(__name__)


async def process_email_validation_wrapper(item_id: UUID, session: AsyncSession) -> None:
    """
    Adapter wrapper for EmailValidationService to work with SDK.
    """
    service = EmailValidationService()
    success = await service.validate_single_email(item_id, session)

    # SDK handles status updates, but we can add custom logic
    if not success:
        logger.warning(f"Email validation failed for {item_id}")


async def process_email_validation_queue():
    """
    Process emails queued for validation using SDK job loop.
    """
    try:
        await run_job_loop(
            model=EmailValidation,
            status_enum=EmailValidationStatusEnum,
            queued_status=EmailValidationStatusEnum.Queued,
            processing_status=EmailValidationStatusEnum.Processing,
            completed_status=EmailValidationStatusEnum.Complete,
            failed_status=EmailValidationStatusEnum.Error,
            processing_function=process_email_validation_wrapper,
            batch_size=settings.EMAIL_VALIDATION_SCHEDULER_BATCH_SIZE or 10,
            order_by_column=asc(EmailValidation.updated_at),
            status_field_name="email_validation_status",
            error_field_name="validation_error",
        )
    except Exception as e:
        logger.exception(f"Critical error in email validation scheduler: {e}")


# Register with scheduler
scheduler.add_job(
    process_email_validation_queue,
    "interval",
    seconds=settings.EMAIL_VALIDATION_SCHEDULER_INTERVAL_SECONDS or 300,
    id="wf8_email_validation_processor",
    max_instances=settings.EMAIL_VALIDATION_SCHEDULER_MAX_INSTANCES or 1,
    replace_existing=True,
)

logger.info("WF8 Email Validation Scheduler registered")
```

**Scheduler Configuration:**
```bash
# Add to .env
EMAIL_VALIDATION_SCHEDULER_INTERVAL_SECONDS=300  # 5 minutes
EMAIL_VALIDATION_SCHEDULER_BATCH_SIZE=10
EMAIL_VALIDATION_SCHEDULER_MAX_INSTANCES=1
```

---

### Step 6: Register Router in main.py

**File:** `src/main.py`

```python
from src.routers.v3 import WF8_V3_L3_EmailValidationRouter

# Register WF8 router
app.include_router(WF8_V3_L3_EmailValidationRouter.router)
```

---

### Step 7: Testing

#### Unit Tests

**File:** `tests/services/test_email_validation_service.py`

```python
import pytest
from uuid import uuid4
from src.services.WF8_L4_EmailValidationService import EmailValidationService
from src.models.email_validation import EmailValidation, EmailValidationStatusEnum


@pytest.mark.asyncio
async def test_validate_email_success(test_session):
    """Test successful email validation"""
    # Create test email record
    email = EmailValidation(
        id=uuid4(),
        email="test@example.com",
        domain_id=uuid4(),
        email_validation_status=EmailValidationStatusEnum.Queued.value
    )
    test_session.add(email)
    await test_session.commit()

    # Validate
    service = EmailValidationService()
    result = await service.validate_single_email(email.id, test_session)

    # Assert
    assert result is True
    await test_session.refresh(email)
    assert email.email_validation_status == EmailValidationStatusEnum.Complete.value
    assert email.is_deliverable is not None
```

#### Integration Tests

```bash
# Create test email record
psql -c "INSERT INTO email_validations (id, email, domain_id, email_curation_status, email_validation_status) VALUES (gen_random_uuid(), 'test@example.com', (SELECT id FROM domains LIMIT 1), 'Selected', 'Queued');"

# Wait for scheduler
sleep 10

# Check result
psql -c "SELECT email, email_validation_status, is_deliverable FROM email_validations WHERE email = 'test@example.com';"
```

---

## Workflow Integration Checklist

### Required Components
- [ ] Layer 1: Model with status enums
- [ ] Layer 2: Request/response schemas
- [ ] Layer 3: Router with transaction boundaries
- [ ] Layer 4: Service with business logic
- [ ] Scheduler (if background processing needed)
- [ ] Migration scripts (Alembic)
- [ ] Configuration (.env variables)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation

### Optional Components
- [ ] GUI interface (React components)
- [ ] Health check queries
- [ ] Monitoring alerts
- [ ] Cost tracking
- [ ] Rate limiting

### Cross-Workflow Integration
- [ ] Update SYSTEM_MAP.md
- [ ] Update QUICK_START.md
- [ ] Create WF8 documentation file
- [ ] Update DEPENDENCY_MAP.md (if external APIs)
- [ ] Add to HEALTH_CHECKS.md

---

## Common Mistakes to Avoid

### ❌ Inconsistent Naming
```python
# WRONG - Inconsistent naming
class EmailCheck(Base):  # Should be EmailValidation
    __tablename__ = "validations"  # Should be email_validations
```

### ✅ Consistent Naming Convention
```python
# CORRECT
class EmailValidation(Base):
    __tablename__ = "email_validations"
    email_validation_status = Column(...)  # Matches workflow name
```

### ❌ Missing Status Fields
```python
# WRONG - Can't track processing
class EmailValidation(Base):
    email = Column(String)
    # Missing status fields!
```

### ✅ Dual-Status Pattern
```python
# CORRECT - Full status tracking
class EmailValidation(Base):
    email_curation_status = Column(...)    # User decision
    email_validation_status = Column(...)  # System processing
    validation_error = Column(...)         # Error tracking
```

### ❌ Router Owns Business Logic
```python
# WRONG - Business logic in router
@router.post("/validate")
async def validate_email(...):
    # Complex validation logic here  # ❌ Should be in service!
```

### ✅ Service Owns Business Logic
```python
# CORRECT - Router delegates to service
@router.post("/validate")
async def validate_email(...):
    service = EmailValidationService()
    result = await service.validate_single_email(...)
    return result
```

---

## Summary

Creating a new workflow requires:
1. **Design:** Data model with dual-status pattern
2. **Implement:** All 4 layers (Model → Schema → Router → Service)
3. **Background:** Scheduler using SDK if needed
4. **Test:** Unit + integration tests
5. **Document:** Update system documentation
6. **Deploy:** Migration + configuration

**Follow established patterns to ensure:**
- Consistency with existing workflows
- Easy maintenance and debugging
- Clear separation of concerns
- Scalable architecture

---

## Related Documentation

- **Patterns:** [PATTERNS.md](./PATTERNS.md)
- **Extensibility:** [EXTENSIBILITY_PATTERNS.md](./EXTENSIBILITY_PATTERNS.md)
- **System Map:** [SYSTEM_MAP.md](./SYSTEM_MAP.md)
- **WF4-7 Example:** [WF4_WF5_WF7_COMPLETE_INDEX.md](../Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)

---

**Last Updated:** November 17, 2025
**Status:** Complete workflow creation guide
**Usage:** Reference when creating new major workflows

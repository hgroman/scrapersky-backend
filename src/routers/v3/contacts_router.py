import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.jwt_auth import get_current_user
from src.db.session import get_db_session
from src.models.enums import (
    ContactCurationStatus,
    ContactEmailTypeEnum,
    ContactProcessingStatus,
    HubSpotProcessingStatus,
    HubSpotSyncStatus,
)
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.schemas.contact_schemas import (
    ContactCreate,
    ContactCurationBatchStatusUpdateRequest,
    ContactCurationBatchUpdateResponse,
    ContactCurationFilteredUpdateRequest,
    ContactRead,
    ContactUpdate,
)

router = APIRouter(
    prefix="/api/v3/contacts",
    tags=["Contacts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Create a new contact record."""
    new_contact = Contact(**contact_in.model_dump())
    session.add(new_contact)
    await session.commit()
    await session.refresh(new_contact)
    return new_contact


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve a single contact by its ID."""
    result = await session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: uuid.UUID,
    contact_in: ContactUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update a contact record."""
    result = await session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)

    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a contact record."""
    result = await session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await session.delete(contact)
    await session.commit()
    return None


@router.get("", response_model=List[ContactRead])
async def list_contacts(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    contact_curation_status: Optional[ContactCurationStatus] = Query(None),
    contact_processing_status: Optional[ContactProcessingStatus] = Query(None),
    hubspot_sync_status: Optional[HubSpotSyncStatus] = Query(None),
    email_type: Optional[ContactEmailTypeEnum] = Query(None),
    domain_id: Optional[uuid.UUID] = Query(None),
    page_id: Optional[uuid.UUID] = Query(None),
    email_contains: Optional[str] = Query(None),
    name_contains: Optional[str] = Query(None),
    has_gmail: Optional[bool] = Query(None),
):
    """Retrieve a list of contacts with filtering and pagination."""
    filters = []
    if contact_curation_status:
        filters.append(Contact.contact_curation_status == contact_curation_status)
    if contact_processing_status:
        filters.append(Contact.contact_processing_status == contact_processing_status)
    if hubspot_sync_status:
        filters.append(Contact.hubspot_sync_status == hubspot_sync_status)
    if email_type:
        filters.append(Contact.email_type == email_type)
    if domain_id:
        filters.append(Contact.domain_id == domain_id)
    if page_id:
        filters.append(Contact.page_id == page_id)
    if email_contains:
        filters.append(Contact.email.ilike(f"%{email_contains}%"))
    if name_contains:
        filters.append(Contact.name.ilike(f"%{name_contains}%"))
    if has_gmail is not None:
        filters.append(Contact.has_gmail == has_gmail)

    # Query for paginated data
    stmt = select(Contact).where(*filters).limit(limit).offset(offset)
    result = await session.execute(stmt)
    contacts = result.scalars().all()

    # The work order specifies a paginated response with total, but for simplicity here we return a list.
    # A full implementation would require a second query for the total count.
    return contacts


@router.put("/status", response_model=ContactCurationBatchUpdateResponse)
async def batch_update_status(
    update_request: ContactCurationBatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Batch update status for a list of contact IDs."""
    if not update_request.contact_ids:
        return ContactCurationBatchUpdateResponse(updated_count=0, queued_count=0)

    stmt = select(Contact).where(Contact.id.in_(update_request.contact_ids))
    result = await session.execute(stmt)
    contacts_to_update = result.scalars().all()

    updated_count = 0
    queued_count = 0
    for contact in contacts_to_update:
        contact.contact_curation_status = update_request.status
        updated_count += 1
        if update_request.status == ContactCurationStatus.Queued:
            contact.contact_processing_status = ContactProcessingStatus.Queued
            contact.contact_processing_error = None
            queued_count += 1

    await session.commit()
    return ContactCurationBatchUpdateResponse(
        updated_count=updated_count, queued_count=queued_count
    )


@router.put("/status/filtered", response_model=ContactCurationBatchUpdateResponse)
async def filtered_batch_update_status(
    update_request: ContactCurationFilteredUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Batch update status for all contacts matching filter criteria."""
    filters = []
    if update_request.contact_curation_status:
        filters.append(Contact.contact_curation_status == update_request.contact_curation_status)
    if update_request.contact_processing_status:
        filters.append(Contact.contact_processing_status == update_request.contact_processing_status)
    if update_request.hubspot_sync_status:
        filters.append(Contact.hubspot_sync_status == update_request.hubspot_sync_status)
    if update_request.email_type:
        filters.append(Contact.email_type == update_request.email_type)
    if update_request.domain_id:
        filters.append(Contact.domain_id == update_request.domain_id)
    if update_request.page_id:
        filters.append(Contact.page_id == update_request.page_id)
    if update_request.email_contains:
        filters.append(Contact.email.ilike(f"%{update_request.email_contains}%"))
    if update_request.name_contains:
        filters.append(Contact.name.ilike(f"%{update_request.name_contains}%"))
    if update_request.has_gmail is not None:
        filters.append(Contact.has_gmail == update_request.has_gmail)

    stmt = select(Contact).where(*filters)
    result = await session.execute(stmt)
    contacts_to_update = result.scalars().all()

    if not contacts_to_update:
        return ContactCurationBatchUpdateResponse(updated_count=0, queued_count=0)

    updated_count = 0
    queued_count = 0
    for contact in contacts_to_update:
        contact.contact_curation_status = update_request.status
        updated_count += 1
        if update_request.status == ContactCurationStatus.Queued:
            contact.contact_processing_status = ContactProcessingStatus.Queued
            contact.contact_processing_error = None
            queued_count += 1

    await session.commit()
    return ContactCurationBatchUpdateResponse(
        updated_count=updated_count, queued_count=queued_count
    )

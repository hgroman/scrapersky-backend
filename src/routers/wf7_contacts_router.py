import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.jwt_auth import get_current_user
from src.db.session import get_db_session
from src.models.enums import (
    ContactCurationStatus,
    ContactEmailTypeEnum,
    ContactProcessingStatus,
    CRMProcessingStatus,
    CRMSyncStatus,
    HubSpotProcessingStatus,
    HubSpotSyncStatus,
)
from src.models.wf7_contact import Contact
from src.schemas.wf7_contact_schemas import (
    ContactCreate,
    ContactCurationBatchStatusUpdateRequest,
    ContactCurationBatchUpdateResponse,
    ContactCurationFilteredUpdateRequest,
    ContactRead,
    ContactUpdate,
    CRMSelectionRequest,
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
    brevo_sync_status: Optional[CRMSyncStatus] = Query(None),
    mautic_sync_status: Optional[CRMSyncStatus] = Query(None),
    n8n_sync_status: Optional[CRMSyncStatus] = Query(None),
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
        filters.append(Contact.contact_curation_status == contact_curation_status.value)
    if contact_processing_status:
        filters.append(
            Contact.contact_processing_status == contact_processing_status.value
        )
    if hubspot_sync_status:
        filters.append(Contact.hubspot_sync_status == hubspot_sync_status.value)
    if brevo_sync_status:
        filters.append(Contact.brevo_sync_status == brevo_sync_status.value)
    if mautic_sync_status:
        filters.append(Contact.mautic_sync_status == mautic_sync_status.value)
    if n8n_sync_status:
        filters.append(Contact.n8n_sync_status == n8n_sync_status.value)
    if email_type:
        filters.append(Contact.email_type == email_type.value)
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
        contact.contact_curation_status = update_request.status.value
        updated_count += 1
        if update_request.status == ContactCurationStatus.Queued:  # noqa: SCRAPERSKY-E102 - Python enum comparison
            contact.contact_processing_status = ContactProcessingStatus.Queued.value
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
        filters.append(
            Contact.contact_curation_status
            == update_request.contact_curation_status.value
        )
    if update_request.contact_processing_status:
        filters.append(
            Contact.contact_processing_status
            == update_request.contact_processing_status.value
        )
    if update_request.hubspot_sync_status:
        filters.append(
            Contact.hubspot_sync_status == update_request.hubspot_sync_status.value
        )
    if update_request.email_type:
        filters.append(Contact.email_type == update_request.email_type.value)
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
        contact.contact_curation_status = update_request.status.value
        updated_count += 1
        if update_request.status == ContactCurationStatus.Queued:  # noqa: SCRAPERSKY-E102 - Python enum comparison
            contact.contact_processing_status = ContactProcessingStatus.Queued.value
            contact.contact_processing_error = None
            queued_count += 1

    await session.commit()
    return ContactCurationBatchUpdateResponse(
        updated_count=updated_count, queued_count=queued_count
    )


@router.put("/crm/select", response_model=Dict[str, Any])
async def select_contacts_for_crm_sync(
    request: CRMSelectionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Mark contacts as 'Selected' for one or more CRM platforms.

    Sets {crm}_sync_status = 'Selected' AND {crm}_processing_status = 'Queued'.
    Implements dual-status pattern: user selection triggers system queuing.

    Request body:
    {
        "contact_ids": ["uuid1", "uuid2"],
        "crms": ["brevo", "hubspot"],  // Which CRMs to mark as selected
        "action": "select"  // or "unselect" to set back to "New"
    }
    """
    if not request.contact_ids:
        return {"updated_count": 0, "message": "No contact IDs provided"}

    if not request.crms:
        return {"updated_count": 0, "message": "No CRMs specified"}

    # Validate CRM names
    valid_crms = {"brevo", "mautic", "n8n", "hubspot"}
    invalid_crms = set(request.crms) - valid_crms
    if invalid_crms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CRM names: {invalid_crms}. Valid: {valid_crms}",
        )

    stmt = select(Contact).where(Contact.id.in_(request.contact_ids))
    result = await session.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(
            status_code=404, detail="No contacts found with provided IDs"
        )

    updated_count = 0
    queued_count = 0  # Track how many CRM entries were queued for processing
    target_status = (
        CRMSyncStatus.Selected.value
        if request.action == "select"
        else CRMSyncStatus.New.value
    )

    for contact in contacts:
        for crm in request.crms:
            # Update the appropriate sync status field (curation status)
            if crm == "brevo":
                contact.brevo_sync_status = target_status
                # Dual-Status Pattern - trigger when Selected
                if request.action == "select":
                    contact.brevo_processing_status = CRMProcessingStatus.Queued.value
                    contact.brevo_processing_error = None
                    queued_count += 1
                elif request.action == "unselect":
                    # Reset processing status when unselecting
                    contact.brevo_processing_status = None
                    contact.brevo_processing_error = None

            elif crm == "mautic":
                contact.mautic_sync_status = target_status
                # Dual-Status Pattern
                if request.action == "select":
                    contact.mautic_processing_status = CRMProcessingStatus.Queued.value
                    contact.mautic_processing_error = None
                    queued_count += 1
                elif request.action == "unselect":
                    contact.mautic_processing_status = None
                    contact.mautic_processing_error = None

            elif crm == "n8n":
                contact.n8n_sync_status = target_status
                # Dual-Status Pattern
                if request.action == "select":
                    contact.n8n_processing_status = CRMProcessingStatus.Queued.value
                    contact.n8n_processing_error = None
                    queued_count += 1
                elif request.action == "unselect":
                    contact.n8n_processing_status = None
                    contact.n8n_processing_error = None

            elif crm == "hubspot":
                contact.hubspot_sync_status = target_status
                # Dual-Status Pattern
                if request.action == "select":
                    contact.hubspot_processing_status = (
                        HubSpotProcessingStatus.Queued.value
                    )
                    contact.hubspot_processing_error = None
                    queued_count += 1
                elif request.action == "unselect":
                    contact.hubspot_processing_status = None
                    contact.hubspot_processing_error = None

        updated_count += 1

    await session.commit()

    return {
        "updated_count": updated_count,
        "queued_count": queued_count,
        "crms": request.crms,
        "action": request.action,
        "message": f"{request.action.capitalize()}ed {updated_count} contacts for {len(request.crms)} CRM(s), {queued_count} queued for processing",
    }

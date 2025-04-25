from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    email: EmailStr
    email_type: Optional[str] = None
    has_gmail: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    phone_office: Optional[str] = None
    phone_mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    context: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ContactCreate(ContactBase):
    website_id: int
    page_id: int


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    website_id: int
    page_id: int
    first_seen: datetime
    last_seen: datetime
    times_seen: int
    found_at_url: Optional[str] = None

    class Config:
        orm_mode = True

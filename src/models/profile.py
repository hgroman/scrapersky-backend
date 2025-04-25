"""
Profile Models

This module defines both SQLAlchemy and Pydantic models for profile-related operations.
Tenant relationships have been removed.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from .base import Base
from .base import BaseModel as BaseORMModel
from .tenant import DEFAULT_TENANT_ID


class Profile(Base, BaseORMModel):
    """SQLAlchemy model for profiles table."""
    __tablename__ = 'profiles'

    # Keep tenant_id column for compatibility but no foreign key or relationship
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, default=DEFAULT_TENANT_ID)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(Text, nullable=True)
    active = Column(Boolean, nullable=True, default=True)

class ProfileBase(BaseModel):
    """Base model for profile data."""
    # Always use default tenant ID
    tenant_id: str = DEFAULT_TENANT_ID  
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = True

class ProfileCreate(ProfileBase):
    """Model for creating a new profile."""
    pass

class ProfileUpdate(BaseModel):
    """Model for updating an existing profile."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None

class ProfileResponse(ProfileBase):
    """Model for profile responses."""
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
#!/usr/bin/env python3
"""
Debug Contact Creation Issue
Test script to identify exactly why contact creation is failing
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.WF7_V2_L1_1of1_ContactModel import Contact
from db.session import get_session_context
from models.enums import ContactCurationStatus, ContactEmailTypeEnum

async def test_contact_creation():
    """Test contact creation with both old and new enum approaches"""
    print("🔍 Testing Contact Creation - Enum Debug")
    print("=" * 50)
    
    async with get_session_context() as session:
        try:
            # Test 1: Try creating contact with Python enum (old way)
            print("\n1️⃣ Testing with Python Enum (OLD WAY)")
            try:
                contact_old = Contact(
                    domain_id="123e4567-e89b-12d3-a456-426614174000",  # Dummy UUID
                    page_id="123e4567-e89b-12d3-a456-426614174001",   # Dummy UUID
                    email="test_old@example.com",
                    name="Test Contact Old",
                    contact_curation_status=ContactCurationStatus.New,  # Python enum
                    email_type=ContactEmailTypeEnum.SERVICE  # Python enum
                )
                print(f"✅ Contact object created with Python enums")
                print(f"   contact_curation_status: {contact_old.contact_curation_status} (type: {type(contact_old.contact_curation_status)})")
                print(f"   email_type: {contact_old.email_type} (type: {type(contact_old.email_type)})")
            except Exception as e:
                print(f"❌ Failed to create contact with Python enums: {e}")
                
            # Test 2: Try creating contact with string values (new way)
            print("\n2️⃣ Testing with String Values (NEW WAY)")
            try:
                contact_new = Contact(
                    domain_id="123e4567-e89b-12d3-a456-426614174000",  # Dummy UUID
                    page_id="123e4567-e89b-12d3-a456-426614174001",   # Dummy UUID
                    email="test_new@example.com",
                    name="Test Contact New",
                    contact_curation_status="New",  # String value
                    email_type="SERVICE"  # String value
                )
                print(f"✅ Contact object created with string values")
                print(f"   contact_curation_status: {contact_new.contact_curation_status} (type: {type(contact_new.contact_curation_status)})")
                print(f"   email_type: {contact_new.email_type} (type: {type(contact_new.email_type)})")
            except Exception as e:
                print(f"❌ Failed to create contact with string values: {e}")
                
            # Test 3: Check what the database schema expects
            print("\n3️⃣ Checking Database Schema Expectations")
            
            # Get existing contact to see what values are stored
            stmt = select(Contact).limit(1)
            result = await session.execute(stmt)
            existing_contact = result.scalar_one_or_none()
            
            if existing_contact:
                print(f"✅ Found existing contact:")
                print(f"   Email: {existing_contact.email}")
                print(f"   contact_curation_status: '{existing_contact.contact_curation_status}' (type: {type(existing_contact.contact_curation_status)})")
                print(f"   email_type: '{existing_contact.email_type}' (type: {type(existing_contact.email_type)})")
            else:
                print("❌ No existing contacts found in database")
                
        except Exception as e:
            print(f"❌ Database session error: {e}")
            import traceback
            traceback.print_exc()

async def test_enum_values():
    """Test what enum values are available"""
    print("\n🔍 Testing Enum Values")
    print("=" * 30)
    
    print("ContactCurationStatus values:")
    for status in ContactCurationStatus:
        print(f"  - {status.name} = '{status.value}' (type: {type(status.value)})")
        
    print("\nContactEmailTypeEnum values:")
    for email_type in ContactEmailTypeEnum:
        print(f"  - {email_type.name} = '{email_type.value}' (type: {type(email_type.value)})")

async def main():
    """Run all tests"""
    print("🛡️ Contact Creation Debug - Deep Investigation")
    print("=" * 60)
    
    await test_enum_values()
    await test_contact_creation()
    
    print("\n" + "=" * 60)
    print("🛡️ Debug Complete - Check output above for issues")

if __name__ == "__main__":
    asyncio.run(main())

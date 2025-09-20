#!/usr/bin/env python3
"""
Direct BaseModel Contact Creation Test
Test that Contact() instantiation works with the BaseModel fix
"""

import sys
import os
import asyncio
import uuid

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test just the Contact model instantiation first
from models.WF7_V2_L1_1of1_ContactModel import Contact

def test_contact_creation():
    """Test Contact instantiation (the critical part that was failing)"""
    print("🔍 Testing BaseModel Contact Creation")
    print("=" * 50)
    
    # Generate valid UUIDs
    domain_id = str(uuid.uuid4())
    page_id = str(uuid.uuid4())
    
    try:
        # Test Contact instantiation (this is where the BaseModel bug was)
        print("1️⃣ Creating Contact object...")
        new_contact = Contact(
            domain_id=domain_id,
            page_id=page_id,
            email="test.basemodel@example.com",
            name="BaseModel Test Contact",
            phone_number="555-TEST-123",
            source_url="https://test-basemodel.com"
        )
        print(f"✅ Contact object created successfully")
        print(f"   ID: {new_contact.id}")
        print(f"   ID type: {type(new_contact.id)}")
        print(f"   Email: {new_contact.email}")
        print(f"   Contact curation status: {new_contact.contact_curation_status}")
        print(f"   HubSpot sync status: {new_contact.hubspot_sync_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"   Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("🛡️ BaseModel Contact Creation Test")
    print("=" * 60)
    
    success = await test_contact_creation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 RESULT: BaseModel fix is WORKING")
        print("   Contact creation succeeds with new UUID generation")
    else:
        print("🎯 RESULT: BaseModel fix is BROKEN")
        print("   Contact creation fails - need to investigate further")

if __name__ == "__main__":
    asyncio.run(main())

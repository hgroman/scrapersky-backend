#!/usr/bin/env python3
"""
Verify contact exists in database 
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from sqlalchemy.future import select
from src.session.async_session import get_session
from src.models.WF7_V2_L1_1of1_ContactModel import Contact

# Load environment variables
load_dotenv()

async def verify_contact():
    """Verify the contact exists in database"""
    
    contact_id = '6c81a40b-ba11-4a12-8e3c-662151d2b1ce'
    
    try:
        async with get_session() as session:
            stmt = select(Contact).where(Contact.id == contact_id)
            result = await session.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact:
                print(f'✅ VERIFIED! Contact exists in Supabase:')
                print(f'   ID: {contact.id}')
                print(f'   Name: {contact.name}')
                print(f'   Email: {contact.email}')
                print(f'   Phone: {contact.phone_number}')
                print(f'   Domain ID: {contact.domain_id}')
                print(f'   Page ID: {contact.page_id}')
                print(f'   Created: {contact.created_at}')
                return True
            else:
                print(f'❌ Contact {contact_id} not found in database')
                return False
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_contact())
    print(f"\n{'✅ VERIFICATION PASSED' if success else '❌ VERIFICATION FAILED'}")
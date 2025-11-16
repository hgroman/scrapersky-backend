#!/usr/bin/env python3
"""
Check if new contacts are being created by WF7 service
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from sqlalchemy.future import select
from sqlalchemy import func
from src.session.async_session import get_session
from src.models.WF7_V2_L1_1of1_ContactModel import Contact

# Load environment variables
load_dotenv()

async def check_new_contacts():
    """Check if new contacts are being created by WF7"""
    
    try:
        async with get_session() as session:
            # Count total contacts
            stmt = select(func.count(Contact.id))
            result = await session.execute(stmt)
            total = result.scalar()
            print(f"📊 Total contacts: {total}")
            
            # Get latest contacts
            stmt2 = select(Contact).order_by(Contact.created_at.desc()).limit(10)
            result2 = await session.execute(stmt2)
            latest = result2.scalars().all()
            
            print("\n🕐 Latest contacts:")
            for i, contact in enumerate(latest):
                print(f"   {i+1}. {contact.email}")
                print(f"      Phone: {contact.phone_number}")
                print(f"      Created: {contact.created_at}")
                print(f"      Domain ID: {contact.domain_id}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_new_contacts())
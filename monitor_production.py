#!/usr/bin/env python3
"""
Monitor production WF7 processing (with local stopped)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from sqlalchemy.future import select
from sqlalchemy import func
from src.session.async_session import get_session
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.page import Page
from src.models.enums import PageProcessingStatus

load_dotenv()

async def monitor_production():
    print("🔍 Monitoring PRODUCTION WF7 Processing (local Docker stopped)")
    print("="*60)
    
    async with get_session() as session:
        # Get contacts from last 5 minutes
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        
        stmt = select(Contact).where(
            Contact.created_at > five_min_ago
        ).order_by(Contact.created_at.desc())
        result = await session.execute(stmt)
        recent_contacts = result.scalars().all()
        
        print(f"📊 Contacts created in last 5 minutes: {len(recent_contacts)}")
        for contact in recent_contacts[:5]:
            print(f"  - {contact.email} at {contact.created_at}")
        
        # Count pages in different statuses
        for status in [PageProcessingStatus.Queued, PageProcessingStatus.Processing, 
                      PageProcessingStatus.Complete, PageProcessingStatus.Error]:
            stmt2 = select(func.count(Page.id)).where(Page.page_processing_status == status)
            result2 = await session.execute(stmt2)
            count = result2.scalar()
            print(f"\n📋 Pages in {status.name}: {count}")

if __name__ == "__main__":
    asyncio.run(monitor_production())

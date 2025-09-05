#!/usr/bin/env python3
"""
Check page statuses to understand WF7 scheduler issue
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from sqlalchemy.future import select
from src.session.async_session import get_session
from src.models.page import Page
from src.models.enums import PageProcessingStatus

# Load environment variables
load_dotenv()

async def check_page_statuses():
    """Check current page statuses to understand WF7 scheduler issue"""
    
    try:
        async with get_session() as session:
            # Check Selected pages (curation status)
            stmt = select(Page).where(Page.page_curation_status == 'Selected').limit(5)
            result = await session.execute(stmt)
            selected_pages = result.scalars().all()
            
            print(f"📊 Pages with curation_status='Selected': {len(selected_pages)}")
            if selected_pages:
                for i, page in enumerate(selected_pages[:3]):
                    print(f"   Page {i+1}: {page.id}")
                    print(f"     URL: {str(page.url)[:60]}...")
                    print(f"     Curation Status: {page.page_curation_status}")
                    print(f"     Processing Status: {page.page_processing_status}")
                    print()
            
            # Check Queued pages (processing status)
            stmt2 = select(Page).where(Page.page_processing_status == PageProcessingStatus.Queued)
            result2 = await session.execute(stmt2)
            queued_pages = result2.scalars().all()
            
            print(f"📊 Pages with processing_status='Queued': {len(queued_pages)}")
            
            # Count all processing statuses
            for status in PageProcessingStatus:
                stmt3 = select(Page).where(Page.page_processing_status == status)
                result3 = await session.execute(stmt3)
                count = len(result3.scalars().all())
                print(f"   {status.name}: {count} pages")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_page_statuses())
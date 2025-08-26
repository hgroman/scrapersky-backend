#!/usr/bin/env python3
"""
Reset Selected pages from Error to Queued status for WF7 processing
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
from src.models.enums import PageCurationStatus, PageProcessingStatus

# Load environment variables
load_dotenv()

async def reset_selected_pages_to_queued():
    """Reset Selected pages from Error status back to Queued for processing"""
    
    try:
        async with get_session() as session:
            # Find Selected pages that are in Error status
            stmt = select(Page).where(
                Page.page_curation_status == PageCurationStatus.Selected
            ).where(
                Page.page_processing_status == PageProcessingStatus.Error
            )
            result = await session.execute(stmt)
            error_pages = result.scalars().all()
            
            print(f"🔍 Found {len(error_pages)} Selected pages in Error status")
            
            if len(error_pages) == 0:
                print("✅ No pages need to be reset")
                return
            
            # Show first few pages
            for i, page in enumerate(error_pages[:5]):
                print(f"   Page {i+1}: {page.id}")
                print(f"     URL: {str(page.url)[:60]}...")
                print(f"     Error: {page.page_processing_error}")
                print()
            
            # Reset them to Queued status
            reset_count = 0
            for page in error_pages:
                page.page_processing_status = PageProcessingStatus.Queued
                page.page_processing_error = None
                reset_count += 1
            
            await session.commit()
            print(f"🔄 Reset {reset_count} pages from Error → Queued")
            
            print(f"✅ Successfully reset {reset_count} pages to Queued status")
            print("📋 WF7 scheduler should now pick up these pages for processing")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_selected_pages_to_queued())
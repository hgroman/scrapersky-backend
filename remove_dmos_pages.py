#!/usr/bin/env python3
"""
Remove all dmos.com pages that are clogging up the system
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

# Load environment variables
load_dotenv()

async def remove_dmos_pages():
    """Remove all dmos.com pages"""
    
    try:
        async with get_session() as session:
            # Find all dmos pages
            stmt = select(Page).where(Page.url.like('%dmos.com%'))
            result = await session.execute(stmt)
            dmos_pages = result.scalars().all()
            
            print(f"🔍 Found {len(dmos_pages)} dmos.com pages to remove")
            
            if len(dmos_pages) == 0:
                print("✅ No dmos.com pages found")
                return
            
            # Show first few pages
            for i, page in enumerate(dmos_pages[:5]):
                print(f"   Page {i+1}: {page.id}")
                print(f"     URL: {str(page.url)}")
                print(f"     Curation: {page.page_curation_status}")
                print(f"     Processing: {page.page_processing_status}")
                print()
            
            # Delete them all
            for page in dmos_pages:
                await session.delete(page)
            
            await session.commit()
            print(f"🗑️  Successfully deleted {len(dmos_pages)} dmos.com pages")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(remove_dmos_pages())
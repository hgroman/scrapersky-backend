import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import async_session_factory

async def run_health_checks():
    print("Running Health Checks...")
    
    async with async_session_factory() as session:
        # 1. Check Queue Depths
        print("\n=== 1. Queue Depths ===")
        
        # Domains waiting for sitemap discovery
        result = await session.execute(text("SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued'"))
        domains_queued = result.scalar()
        print(f"Domains queued for sitemap discovery: {domains_queued} (Expected: 0-50)")
        
        # Sitemaps waiting for URL extraction
        result = await session.execute(text("SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued'"))
        sitemaps_queued = result.scalar()
        print(f"Sitemaps queued for URL extraction: {sitemaps_queued} (Expected: 0-100)")
        
        # Pages waiting for scraping
        result = await session.execute(text("SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued'"))
        pages_queued = result.scalar()
        print(f"Pages queued for scraping: {pages_queued} (Expected: 0-500)")
        
        # 2. Check for Stuck Jobs
        print("\n=== 2. Stuck Jobs ===")
        result = await session.execute(text("SELECT COUNT(*) FROM jobs WHERE status = 'pending' AND created_at < NOW() - INTERVAL '5 minutes'"))
        stuck_jobs = result.scalar()
        print(f"Jobs stuck in pending > 5 minutes: {stuck_jobs} (Expected: 0)")
        
        # 3. Check Recent Processing
        print("\n=== 3. Recent Processing ===")
        result = await session.execute(text("SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Complete' AND updated_at > NOW() - INTERVAL '1 hour'"))
        pages_processed = result.scalar()
        print(f"Pages processed in last hour: {pages_processed} (Expected: > 0 if active)")
        
    print("\nHealth Checks Complete.")

if __name__ == "__main__":
    asyncio.run(run_health_checks())

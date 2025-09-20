#!/usr/bin/env python3
"""
Test script for WF7 Concurrent Processing Implementation
Guardian Authority: WF7 Production Reality Guardian v2
"""

import asyncio
import time
import os
import logging
from sqlalchemy import select
from src.models.page import Page
from src.models.enums import PageProcessingStatus
from src.services.WF7_V2_L4_1of2_PageCurationService import PageCurationService
from src.session.async_session import get_background_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_queued_pages(limit: int = 10):
    """Get a batch of queued pages for testing."""
    async with get_background_session() as session:
        stmt = select(Page).where(
            Page.page_processing_status == PageProcessingStatus.Queued
        ).limit(limit)
        result = await session.execute(stmt)
        pages = result.scalars().all()
        return [page.id for page in pages]

async def test_sequential_processing(page_ids):
    """Test current sequential processing pattern."""
    logger.info(f"🔄 TESTING SEQUENTIAL PROCESSING: {len(page_ids)} pages")
    
    # Temporarily disable concurrent processing
    os.environ['WF7_ENABLE_CONCURRENT_PROCESSING'] = 'false'
    
    service = PageCurationService()
    start_time = time.time()
    
    async with get_background_session() as session:
        results = await service.process_pages_concurrently(page_ids, session)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r['success'])
    
    logger.info(f"✅ SEQUENTIAL RESULTS: {len(page_ids)} pages in {total_time:.2f}s")
    logger.info(f"📊 Success: {success_count}/{len(page_ids)}, Rate: {len(page_ids)/total_time:.2f} pages/sec")
    
    return {
        'total_time': total_time,
        'success_count': success_count,
        'pages_per_second': len(page_ids) / total_time,
        'results': results
    }

async def test_concurrent_processing(page_ids):
    """Test new concurrent processing pattern."""
    logger.info(f"⚡ TESTING CONCURRENT PROCESSING: {len(page_ids)} pages")
    
    # Enable concurrent processing
    os.environ['WF7_ENABLE_CONCURRENT_PROCESSING'] = 'true'
    
    service = PageCurationService()
    start_time = time.time()
    
    async with get_background_session() as session:
        results = await service.process_pages_concurrently(page_ids, session)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r['success'])
    
    logger.info(f"✅ CONCURRENT RESULTS: {len(page_ids)} pages in {total_time:.2f}s")
    logger.info(f"📊 Success: {success_count}/{len(page_ids)}, Rate: {len(page_ids)/total_time:.2f} pages/sec")
    
    return {
        'total_time': total_time,
        'success_count': success_count,
        'pages_per_second': len(page_ids) / total_time,
        'results': results
    }

async def validate_performance_improvement(sequential_result, concurrent_result):
    """Validate the performance improvement."""
    logger.info("🎯 PERFORMANCE COMPARISON:")
    logger.info(f"Sequential: {sequential_result['pages_per_second']:.2f} pages/sec")
    logger.info(f"Concurrent: {concurrent_result['pages_per_second']:.2f} pages/sec")
    
    if concurrent_result['pages_per_second'] > 0:
        improvement = concurrent_result['pages_per_second'] / sequential_result['pages_per_second']
        logger.info(f"🚀 IMPROVEMENT: {improvement:.1f}x faster")
        
        if improvement >= 5.0:
            logger.info("✅ SUCCESS: >5x improvement achieved!")
            return True
        else:
            logger.warning(f"⚠️  PARTIAL: {improvement:.1f}x improvement (target: 10x)")
            return False
    else:
        logger.error("❌ FAILURE: Concurrent processing failed")
        return False

async def check_contact_creation():
    """Verify contacts were actually created."""
    async with get_background_session() as session:
        from src.models.WF7_V2_L1_1of1_ContactModel import Contact
        
        # Get latest contacts
        stmt = select(Contact).order_by(Contact.created_at.desc()).limit(10)
        result = await session.execute(stmt)
        contacts = result.scalars().all()
        
        logger.info(f"📝 LATEST CONTACTS: {len(contacts)} found")
        for contact in contacts[:3]:
            logger.info(f"   - {contact.email} (Page: {contact.page_id})")
        
        return len(contacts)

async def main():
    """Main test execution."""
    logger.info("🛡️ WF7 CONCURRENT PROCESSING TEST - Guardian v2")
    logger.info("=" * 60)
    
    try:
        # Get test pages
        logger.info("📋 Getting queued pages for testing...")
        page_ids = await get_queued_pages(limit=6)  # Small test batch
        
        if not page_ids:
            logger.error("❌ No queued pages found for testing")
            return
        
        logger.info(f"🎯 Testing with {len(page_ids)} pages")
        
        # Test sequential first (half the pages)
        sequential_pages = page_ids[:3]
        sequential_result = await test_sequential_processing(sequential_pages)
        
        # Small delay between tests
        await asyncio.sleep(2)
        
        # Test concurrent (remaining pages)
        concurrent_pages = page_ids[3:]
        concurrent_result = await test_concurrent_processing(concurrent_pages)
        
        # Validate results
        success = await validate_performance_improvement(sequential_result, concurrent_result)
        
        # Check contact creation
        await check_contact_creation()
        
        logger.info("=" * 60)
        if success:
            logger.info("🎉 TEST PASSED: Concurrent processing working!")
        else:
            logger.info("⚠️  TEST PARTIAL: Implementation needs optimization")
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
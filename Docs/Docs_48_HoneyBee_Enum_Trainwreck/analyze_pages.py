#!/usr/bin/env python3
"""
Quick analysis script to understand current page_type distribution
and URL patterns in the pages table.
"""
import asyncio
from collections import Counter, defaultdict
from sqlalchemy import select, func
from src.session.async_session import get_session
from src.models.page import Page
from src.utils.honeybee_categorizer import HoneybeeCategorizer


async def analyze_current_data():
    """Analyze current page_type distribution and URL patterns."""
    session = await get_session()
    if session is None:
        print("Failed to get database session")
        return
        
    print("🔍 ANALYZING PAGES TABLE DATA...")
    print("=" * 60)
    
    try:
        async with session.begin():
            # 1. Page type distribution
            print("\n📊 CURRENT PAGE_TYPE DISTRIBUTION:")
            result = await session.execute(
                select(Page.page_type, func.count().label('count'))
                .group_by(Page.page_type)
                .order_by(func.count().desc())
            )
            page_types = result.fetchall()
            
            total_pages = sum(count for _, count in page_types)
            print(f"Total pages: {total_pages:,}")
            
            for page_type, count in page_types:
                percentage = (count / total_pages) * 100 if total_pages > 0 else 0
                print(f"  {page_type or 'NULL'}: {count:,} ({percentage:.1f}%)")
            
            # 2. Sample URLs for each category
            print("\n🔗 SAMPLE URLs BY CATEGORY:")
            for page_type, _ in page_types[:5]:  # Top 5 categories
                if page_type is None:
                    page_type_condition = Page.page_type.is_(None)
                    display_type = "NULL"
                else:
                    page_type_condition = Page.page_type == page_type
                    display_type = page_type
                    
                result = await session.execute(
                    select(Page.url)
                    .where(page_type_condition)
                    .limit(3)
                )
                urls = [row[0] for row in result.fetchall()]
                
                print(f"\n{display_type} examples:")
                for url in urls:
                    print(f"  {url}")
            
            # 3. Curation status breakdown
            print("\n📋 CURATION STATUS BREAKDOWN:")
            result = await session.execute(
                select(Page.page_curation_status, func.count().label('count'))
                .group_by(Page.page_curation_status)
                .order_by(func.count().desc())
            )
            curation_status = result.fetchall()
            
            for status, count in curation_status:
                percentage = (count / total_pages) * 100 if total_pages > 0 else 0
                print(f"  {status or 'NULL'}: {count:,} ({percentage:.1f}%)")
            
            # 4. Processing status breakdown  
            print("\n⚙️  PROCESSING STATUS BREAKDOWN:")
            result = await session.execute(
                select(Page.page_processing_status, func.count().label('count'))
                .group_by(Page.page_processing_status)
                .order_by(func.count().desc())
            )
            processing_status = result.fetchall()
            
            for status, count in processing_status:
                percentage = (count / total_pages) * 100 if total_pages > 0 else 0
                print(f"  {status or 'NULL'}: {count:,} ({percentage:.1f}%)")

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return
    
    finally:
        await session.close()


async def test_categorizer_patterns():
    """Test the categorizer against some sample URLs to understand patterns."""
    print("\n" + "=" * 60)
    print("🧪 TESTING CURRENT CATEGORIZER PATTERNS...")
    print("=" * 60)
    
    hb = HoneybeeCategorizer()
    
    # Test URLs that should match different patterns
    test_urls = [
        # Contact pages
        "https://example.com/contact",
        "https://example.com/contact-us",  
        "https://example.com/contact/",
        "https://example.com/careers/contact",
        "https://example.com/jobs/apply/contact",
        
        # Excluded pages
        "https://example.com/blog/some-post",
        "https://example.com/about-us/team",
        "https://example.com/services/consulting",
        "https://example.com/document.pdf",
        
        # Ambiguous pages
        "https://example.com/",
        "https://example.com/pricing",
        "https://example.com/about",
        "https://example.com/services",
        "https://example.com/team",
    ]
    
    print("\nCategorization Results:")
    for url in test_urls:
        result = hb.categorize(url)
        decision = result["decision"]
        category = result["category"]
        confidence = result["confidence"]
        exclusions = result["exclusions"]
        
        status = "✅ INCLUDE" if decision == "include" else "❌ SKIP"
        exclusion_note = f" [EXCLUDED: {exclusions}]" if exclusions else ""
        
        print(f"  {status} | {category:15} | {confidence:.1f} | {url}{exclusion_note}")


if __name__ == "__main__":
    asyncio.run(analyze_current_data())
    asyncio.run(test_categorizer_patterns())
import asyncio
from sqlalchemy import select
from src.session.async_session import get_session
from src.models.page import Page
from src.models.enums import PageCurationStatus, PageTypeEnum
from src.utils.honeybee_categorizer import HoneybeeCategorizer


async def run():
    """
    Backfill existing pages with Honeybee categorization.
    Processes existing pages in batches and applies the same categorization
    and selection rules as the import service.
    """
    hb = HoneybeeCategorizer()
    
    session = await get_session()
    if session is None:
        print("Failed to get database session")
        return
        
    try:
        offset, size = 0, 500
        total_processed = 0
        total_skipped = 0
        total_selected = 0
        
        while True:
            async with session.begin():
                rows = (await session.execute(
                    select(Page).order_by(Page.created_at).offset(offset).limit(size)
                )).scalars().all()
                
                if not rows:
                    break
                    
                for pg in rows:
                    r = hb.categorize(pg.url)
                    
                    if r["decision"] == "skip":
                        # Still store decision for audit
                        pg.honeybee_json = {
                            "v": 1,
                            "decision": {
                                "category": "unknown",  # String literal for skipped pages
                                "confidence": 0.0,
                                "matched_regex": None
                            },
                            "exclusions": r["exclusions"]
                        }
                        pg.page_type = PageTypeEnum.UNKNOWN.value  # Store as string value
                        pg.path_depth = r["depth"]
                        pg.priority_level = 3
                        total_skipped += 1
                        continue
                    
                    # Update page with categorization results
                    pg.page_type = r["category"].value  # Store as string value
                    pg.path_depth = r["depth"]
                    pg.priority_level = 1 if r["confidence"] >= 0.6 else 3
                    pg.honeybee_json = {
                        "v": 1,
                        "decision": {
                            "category": r["category"].value,  # Store enum value, not enum object
                            "confidence": r["confidence"],
                            "matched_regex": r["matched"]
                        },
                        "exclusions": r["exclusions"]
                    }
                    
                    # Apply auto-selection rules
                    if r["category"] in {PageTypeEnum.CONTACT_ROOT, PageTypeEnum.CAREER_CONTACT, PageTypeEnum.LEGAL_ROOT} and r["confidence"] >= 0.6 and r["depth"] <= 2:
                        pg.page_curation_status = PageCurationStatus.Selected
                        total_selected += 1
                        
                    total_processed += 1
                
                print(f"Processed batch: offset={offset}, processed={len(rows)}")
                
            offset += size
            
        print(f"""
Backfill Complete!
Total pages processed: {total_processed}
Total pages skipped: {total_skipped}
Total pages auto-selected: {total_selected}
""")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(run())

────────────────────────────────────────
### File 2: `WF_RENAMING_MASTER_PLAN_2025-11-20.md`

```markdown
# WORKFLOW INTUITIVE RENAMING MASTER PLAN – November 20, 2025

## Why
After years of organic growth the file names no longer reflect the actual 7 workflows. This has caused countless outages, confusion, and weeks of debugging.

## Principles
- Database is ground truth — we never change it again
- One atomic, scripted rename — no incremental pain
- No WF6 (intentional skip)
- Direct-submission “fast lanes” are named by the workflow they inject into

## Final Mapping

| Workflow | Current Model(s)                              | New Model File                              | New Scheduler(s)                                           | New Router Prefix (if exists)         |
|----------|-----------------------------------------------|---------------------------------------------|------------------------------------------------------------|---------------------------------------|
| WF1      | place.py                                      | src/models/wf1_place_staging.py             | –                                                          | wf1_places_                           |
| WF2      | deep_scan_scheduler.py                        | src/services/background/wf2_deep_scan_scheduler.py | wf2_deep_scan_scheduler.py                                 | –                                     |
| WF3      | local_business.py                             | src/models/wf3_local_business.py            | wf3_domain_extraction_scheduler.py                         | wf3_local_business_                   |
| WF4      | domain.py                                     | src/models/wf4_domain.py                    | wf4_domain_monitor_scheduler.py <br> wf4_sitemap_discovery_scheduler.py | wf4_domain_                           |
| WF5      | sitemap.py                                    | src/models/wf5_sitemap_file.py              | wf5_sitemap_import_scheduler.py                            | wf5_sitemap_                          |
| WF7      | page.py + WF7_V2_L1_1of1_ContactModel.py      | src/models/wf7_page.py <br> src/models/wf7_contact.py | wf7_page_curation_scheduler.py <br> wf7_crm_*_scheduler.py | wf7_page_ / wf7_contact_             |

## Direct-submission fast lanes (rename only)
| Current router                                        | New name                                              |
|-------------------------------------------------------|-------------------------------------------------------|
| v3/sitemaps_direct_submission_router.py               | wf5_sitemap_direct_submission_router.py               |
| v3/sitemaps_csv_import_router.py                      | wf5_sitemap_csv_import_router.py                      |
| v3/pages_direct_submission_router.py                  | wf7_page_direct_submission_router.py                  |
| v3/pages_csv_import_router.py                         | wf7_page_csv_import_router.py                         |

## Final directory layout
# Python File Status Map ([NOVEL] / [SHARED])

This document is the master source of truth for Python file usage status in the ScraperSky backend. Every file is mapped as either:

- `[NOVEL]`: Unique to a specific workflow
- `[SHARED]`: Used across multiple workflows
- `[ORPHANED]`: Not referenced in any workflow or documentation (flagged for review)

| #   | File Path                                                         | Status | Referenced In (Docs/Workflows)                      |
| --- | ----------------------------------------------------------------- | ------ | --------------------------------------------------- | ------------------------------------------------ |
| 1   | src/routers/batch_page_scraper.py (Layer 3: Routers)              | NOVEL  | 1-main_routers.md, WF1, ...                         |
| 2   | src/routers/batch_sitemap.py (Layer 3: Routers)                   | NOVEL  | 1-main_routers.md, ...                              |
| 3   | src/routers/db_portal.py (Layer 3: Routers)                       | NOVEL  | 1-main_routers.md, ...                              |
| 4   | src/routers/dev_tools.py (Layer 3: Routers)                       | NOVEL  | 1-main_routers.md, ...                              |
| 5   | src/routers/domains.py (Layer 3: Routers)                         | NOVEL  | 1-main_routers.md, ...                              |
| 6   | src/routers/email_scanner.py (Layer 3: Routers)                   | NOVEL  | 1-main_routers.md, ...                              |
| 7   | src/routers/google_maps_api.py (Layer 3: Routers)                 | NOVEL  | 1-main_routers.md, WF1, ...                         |
| 8   | src/routers/local_businesses.py (Layer 3: Routers)                | NOVEL  | 1-main_routers.md, ...                              |
| 9   | src/routers/modernized_page_scraper.py (Layer 3: Routers)         | NOVEL  | 1-main_routers.md, ...                              |
| 10  | src/routers/modernized_sitemap.py (Layer 3: Routers)              | NOVEL  | 1-main_routers.md, WF1, ...                         |
| 11  | src/routers/places_staging.py (Layer 3: Routers)                  | NOVEL  | 1-main_routers.md, WF2, ...                         |
| 12  | src/routers/profile.py (Layer 3: Routers)                         | NOVEL  | 1-main_routers.md, ...                              |
| 13  | src/routers/sitemap_files.py (Layer 3: Routers)                   | NOVEL  | 1-main_routers.md, ...                              |
| 14  | src/routers/sqlalchemy/**init**.py (Layer 3: Routers)             | SHARED | 1-main_routers.md, ...                              |
| 15  | src/services/sitemap_scheduler.py (Layer 4: Services)             | SHARED | WF2, ...                                            |
| 16  | src/services/places/places_deep_service.py (Layer 4: Services)    | SHARED | WF2, ...                                            |
| 17  | src/scheduler_instance.py                                         | SHARED | WF2, ...                                            | <!-- Added during WF2 audit for traceability --> |
| 18  | src/models/place.py (Layer 1: Models & ENUMs)                     | SHARED | WF1, WF2, ...                                       |
| 19  | src/models/place_search.py (Layer 1: Models & ENUMs)              | SHARED | WF1, ...                                            |
| 20  | src/services/places/places_search_service.py (Layer 4: Services)  | SHARED | WF1, ...                                            |
| 21  | src/services/places/places_storage_service.py (Layer 4: Services) | SHARED | WF1, ...                                            |
| 22  | src/services/sitemap_import_scheduler.py (Layer 4: Services)      | NOVEL  | WF6, 1.1-background-services.md                     |
| 23  | src/services/sitemap_import_service.py (Layer 4: Services)        | NOVEL  | WF6, 1.1-background-services.md                     |
| 24  | src/common/sitemap_parser.py                                      | SHARED | WF5, WF6                                            |
| 25  | src/common/curation_sdk/scheduler_loop.py                         | SHARED | WF3, WF4, WF5, WF6                                  |
| 26  | src/models/page.py (Layer 1: Models & ENUMs)                      | SHARED | WF6, future page processing workflows               |
| 27  | src/models/sitemap.py (Layer 1: Models & ENUMs)                   | SHARED | WF5, WF6                                            |
| 28  | src/models/local_business.py (Layer 1: Models & ENUMs)            | SHARED | WF2, WF3, WF4                                       |
| 29  | src/models/domain.py (Layer 1: Models & ENUMs)                    | SHARED | WF3, WF4, WF5, WF6                                  |
| 30  | src/models/base.py (Layer 1: Models & ENUMs)                      | SHARED | WF1, WF2, WF3, WF4, WF5, WF6                        |
| 31  | src/models/api_models.py (Layer 1: Models & ENUMs)                | SHARED | WF2, WF3, WF4, WF5                                  |
| 32  | src/models/place.py (Layer 1: Models & ENUMs)                     | SHARED | WF1, WF2, WF3 (includes PlaceStatusEnum)            |
| 33  | src/models/local_business.py (Layer 1: Models & ENUMs)            | SHARED | WF2, WF3, WF4 (includes DomainExtractionStatusEnum) |
| 34  | src/models/domain.py (Layer 1: Models & ENUMs)                    | SHARED | WF3, WF4, WF5 (includes SitemapCurationStatusEnum)  |
| 35  | src/models/sitemap.py (Layer 1: Models & ENUMs)                   | SHARED | WF5, WF6 (includes SitemapImportProcessStatusEnum)  |
| 36  | src/models/page.py (Layer 1: Models & ENUMs)                      | SHARED | WF6, future workflows (includes PageStatusEnum)     |
| 37  | src/models/enums.py (Layer 1: Models & ENUMs)                     | SHARED | Multiple workflows, contains shared enums           |
| ... | ...                                                               | ...    |

> **Note:** This table is a starting point. As docs are updated, every Python file in the project should be added and referenced here. Orphaned files will be flagged for review/removal.

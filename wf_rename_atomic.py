#!/usr/bin/env python3
import shutil
from pathlib import Path

root = Path(__file__).parent.resolve()
moves = [
    # models
    ("src/models/place.py", "src/models/wf1_place_staging.py"),
    ("src/models/local_business.py", "src/models/wf3_local_business.py"),
    ("src/models/domain.py", "src/models/wf4_domain.py"),
    ("src/models/sitemap.py", "src/models/wf5_sitemap_file.py"),
    ("src/models/page.py", "src/models/wf7_page.py"),
    ("src/models/WF7_V2_L1_1of1_ContactModel.py", "src/models/wf7_contact.py"),

    # schedulers → background directory
    ("src/services/deep_scan_scheduler.py", "src/services/background/wf2_deep_scan_scheduler.py"),
    ("src/services/domain_extraction_scheduler.py", "src/services/background/wf3_domain_extraction_scheduler.py"),
    ("src/services/domain_scheduler.py", "src/services/background/wf4_domain_monitor_scheduler.py"),
    ("src/services/domain_sitemap_submission_scheduler_fixed.py", "src/services/background/wf4_sitemap_discovery_scheduler.py"),
    ("src/services/sitemap_import_scheduler.py", "src/services/background/wf5_sitemap_import_scheduler.py"),
    ("src/services/WF7_V2_L4_2of2_PageCurationScheduler.py", "src/services/background/wf7_page_curation_scheduler.py"),

    # CRM schedulers
    ("src/services/crm/brevo_sync_scheduler.py", "src/services/background/wf7_crm_brevo_sync_scheduler.py"),
    ("src/services/crm/hubspot_sync_scheduler.py", "src/services/background/wf7_crm_hubspot_sync_scheduler.py"),
    ("src/services/crm/n8n_sync_scheduler.py", "src/services/background/wf7_crm_n8n_sync_scheduler.py"),
    ("src/services/email_validation/debounce_scheduler.py", "src/services/background/wf7_crm_debounce_scheduler.py"),

    # fast-lane routers
    ("src/routers/v3/sitemaps_direct_submission_router.py", "src/routers/wf5_sitemap_direct_submission_router.py"),
    ("src/routers/v3/sitemaps_csv_import_router.py", "src/routers/wf5_sitemap_csv_import_router.py"),
    ("src/routers/v3/pages_direct_submission_router.py", "src/routers/wf7_page_direct_submission_router.py"),
    ("src/routers/v3/pages_csv_import_router.py", "src/routers/wf7_page_csv_import_router.py"),
]

print(f"Executing rename from root: {root}")

for src, dst in moves:
    s = root / src
    d = root / dst
    if s.exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        print(f"✓ {src} → {dst}")
    else:
        print(f"Missing {src}")

print("\nRenaming complete. Now run import fixes.")

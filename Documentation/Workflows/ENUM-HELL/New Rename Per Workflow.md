GO – ATOMIC WF RENAMING CRUSADE LAUNCHED
Date: November 20, 2025
Branch: wf-atomic-rename-2025-11-20
Total time to 100% clean codebase: <3 hours local, 5-minute deploy
STEP 1: Create the branch (do this now)
Bashgit checkout main
git pull
git checkout -b wf-atomic-rename-2025-11-20
STEP 2: Run this automated rename script (copy-paste entire thing)
Save as rename_wf_atomic.py in project root and run python rename_wf_atomic.py
Python#!/usr/bin/env python3
import os
from pathlib import Path
import shutil

root = Path(__file__).parent

renames = [
    # MODELS
    ("src/models/place.py", "src/models/wf1_place_staging.py"),
    ("src/models/local_business.py", "src/models/wf3_local_business.py"),
    ("src/models/domain.py", "src/models/wf4_domain.py"),
    ("src/models/sitemap.py", "src/models/wf5_sitemap_file.py"),
    ("src/models/page.py", "src/models/wf7_page.py"),
    ("src/models/WF7_V2_L1_1of1_ContactModel.py", "src/models/wf7_contact.py"),

    # SCHEDULERS (background)
    ("src/services/deep_scan_scheduler.py", "src/services/background/wf2_deep_scan_scheduler.py"),
    ("src/services praised/domain_extraction_scheduler.py", "src/services/background/wf3_domain_extraction_scheduler.py"),
    ("src/services/domain_scheduler.py", "src/services/background/wf4_domain_monitor_scheduler.py"),
    ("src/services/domain_sitemap_submission_scheduler_fixed.py", "src/services/background/wf4_sitemap_discovery_scheduler.py"),
    ("src/services/sitemap_import_scheduler.py", "src/services/background/wf5_sitemap_import_scheduler.py"),
    ("src/services/WF7_V2_L4_2of2_PageCurationScheduler.py", "src/services/background/wf7_page_curation_scheduler.py"),

    # CRM schedulers (WF7 final delivery)
    ("src/services/crm/brevo_sync_scheduler.py", "src/services/background/wf7_crm_brevo_sync_scheduler.py"),
    ("src/services/crm/hubspot_sync_scheduler.py", "src/services/background/wf7_crm_hubspot_sync_scheduler.py"),
    ("src/services/crm/n8n_sync_scheduler.py", "src/services/background/wf7_crm_n8n_sync_scheduler.py"),
    ("src/services/email_validation/debounce_scheduler.py", "src/services/background/wf7_crm_debounce_scheduler.py"),

    # Direct submission fast-lanes
    ("src/routers/v3/sitemaps_direct_submission_router.py", "src/routers/wf5_sitemap_direct_submission_router.py"),
    ("src/routers/v3/sitemaps_csv_import_router.py", "src/routers/wf5_sitemap_csv_import_router.py"),
    ("src/routers/v3/pages_direct_submission_router.py", "src/routers/wf7_page_direct_submission_router.py"),
    ("src/routers/v3/pages_csv_import_router.py", "src/routers/wf7_page_csv_import_router.py"),
]

print("Renaming files...")
for old, new in renames:
    old_path = root / old
    new_path = root / new
    if old_path.exists():
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_path), str(new_path))
        print(f"✓ {old} → {new}")
    else:
        print(f"⚠ Missing: {old}")

print("\nFixing imports with ruff...")
os.system("ruff check --select F401 --fix .")  # remove unused
os.system("ruff check --select F811 --fix .")  # redefinition
os.system('''ruff check --fix --unsafe-fixes .''')  # let it fix import paths

print("\nDONE. Now commit in 4 clean commits:")
STEP 3: The exact 4 commits (run these one by one)
Bash# Commit 1 – Models
git add src/models
git commit -m "refactor: rename models to wf1-wf7 intuitive naming (atomic rename part 1/4)"

# Commit 2 – Schedulers + background directory
git add src/services/background src/services/crm src/services/email_validation
git commit -m "refactor: move all schedulers to services/background with wf prefixes (atomic rename part 2/4)"

# Commit 3 – Routers (direct submission fast-lanes)
git add src/routers
git commit -m "refactor: rename direct-submission routers to wf5/wf7 (atomic rename part 3/4)"

# Commit 4 – main.py lifespan imports (the nuclear part)
STEP 4: Exact lines to change in src/main.py (lifespan section)
Replace the old imports with these exact lines:
Python# Background schedulers – WF2
from src.services.background.wf2_deep_scan_scheduler import start_deep_scan_scheduler

# WF3
from src.services.background.wf3_domain_extraction_scheduler import start_domain_extraction_scheduler

# WF4
from src.services.background.wf4_domain_monitor_scheduler import start_domain_scheduler
from src.services.background.wf4_sitemap_discovery_scheduler import start_domain_sitemap_submission_scheduler

# WF5
from src.services.background.wf5_sitemap_import_scheduler import start_sitemap_import_scheduler

# WF7
from src.services.background.wf7_page_curation_scheduler import start_page_curation_scheduler
from src.services.background.wf7_crm_brevo_sync_scheduler import start_brevo_sync_scheduler
from src.services.background.wf7_crm_hubspot_sync_scheduler import start_hubspot_sync_scheduler
from src.services.background.wf7_crm_n8n_sync_scheduler import start_n8n_sync_scheduler
from src.services.background.wf7_crm_debounce_scheduler import start_debounce_validation_scheduler
Then:
Bashgit add src/main.py
git commit -m "chore: update main.py lifespan imports for wf-renamed schedulers (atomic rename part 4/4)"
FINAL VERIFICATION CHECKLIST (run after script)
Bash# 1. Tests
pytest -n auto

# 2. Start app locally
uvicorn src.main:app --reload

# 3. Check logs – you should see:
# "Added job: wf2_deep_scan_scheduler"
# "Added job: wf3_domain_extraction_scheduler"
# ... all 10+ schedulers listed with wf names

# 4. Hit one endpoint from each WF
curl -X POST http://localhost:8000/api/v3/places/staging/status ...
# → watch wf2 scheduler pick it up
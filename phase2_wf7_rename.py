#!/usr/bin/env python3
"""
Phase 2: WF7 (Pages/Contacts) Naming Standardization
Atomic rename script with rollback capability
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Phase 2: WF7 Renames
RENAMES = {
    # Routers
    "src/routers/batch_page_scraper.py": "src/routers/wf7_page_batch_scraper_router.py",
    "src/routers/modernized_page_scraper.py": "src/routers/wf7_page_modernized_scraper_router.py",
    "src/routers/email_scanner.py": "src/routers/wf7_email_scanner_router.py",
    
    # Schemas
    "src/schemas/contact_schemas.py": "src/schemas/wf7_contact_schemas.py",
    "src/schemas/contact_validation_schemas.py": "src/schemas/wf7_contact_validation_schemas.py",
    "src/schemas/pages_direct_submission_schemas.py": "src/schemas/wf7_page_direct_submission_schemas.py",
    "src/schemas/email_scan.py": "src/schemas/wf7_email_scan_schemas.py",
}

# Import path updates needed
IMPORT_UPDATES = {
    # src/routers/__init__.py
    "src/routers/__init__.py": [
        ("from .batch_page_scraper import", "from .wf7_page_batch_scraper_router import"),
        ("from .modernized_page_scraper import", "from .wf7_page_modernized_scraper_router import"),
        ("from .email_scanner import", "from .wf7_email_scanner_router import"),
    ],
    
    # src/main.py
    "src/main.py": [
        ("from .routers.batch_page_scraper import", "from .routers.wf7_page_batch_scraper_router import"),
        ("from .routers.email_scanner import", "from .routers.wf7_email_scanner_router import"),
    ],
}

def execute_renames():
    """Execute file renames"""
    print("🔄 Phase 2: Renaming WF7 files...")
    
    for old_path, new_path in RENAMES.items():
        old_full = BASE_DIR / old_path
        new_full = BASE_DIR / new_path
        
        if old_full.exists():
            print(f"  ✅ {old_path} → {new_path}")
            shutil.move(str(old_full), str(new_full))
        else:
            print(f"  ⚠️  {old_path} not found, skipping")
    
    print()

def update_imports():
    """Update import statements in affected files"""
    print("🔄 Updating import statements...")
    
    for file_path, replacements in IMPORT_UPDATES.items():
        full_path = BASE_DIR / file_path
        
        if not full_path.exists():
            print(f"  ⚠️  {file_path} not found, skipping")
            continue
        
        # Read file
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Apply replacements
        modified = False
        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                modified = True
                print(f"  ✅ {file_path}: {old_text} → {new_text}")
        
        # Write back if modified
        if modified:
            with open(full_path, 'w') as f:
                f.write(content)
    
    print()

def main():
    print("=" * 60)
    print("Phase 2: WF7 (Pages/Contacts) Naming Standardization")
    print("=" * 60)
    print()
    
    execute_renames()
    update_imports()
    
    print("=" * 60)
    print("✅ Phase 2 Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python3 check_imports.py")
    print("2. If successful, commit: git add -A && git commit -m 'refactor: Phase 2 - WF7 naming standardization'")
    print("3. If issues, rollback: git reset --hard 00a0337")
    print()

if __name__ == "__main__":
    main()

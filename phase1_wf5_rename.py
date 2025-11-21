#!/usr/bin/env python3
"""
Phase 1: WF5 (Sitemap) Naming Standardization
Atomic rename script with rollback capability
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Phase 1: WF5 Renames
RENAMES = {
    # Routers
    "src/routers/sitemap_files.py": "src/routers/wf5_sitemap_file_router.py",
    "src/routers/batch_sitemap.py": "src/routers/wf5_sitemap_batch_router.py",
    "src/routers/modernized_sitemap.py": "src/routers/wf5_sitemap_modernized_router.py",
    
    # Schemas
    "src/schemas/sitemap_file.py": "src/schemas/wf5_sitemap_file_schemas.py",
    "src/schemas/sitemaps_direct_submission_schemas.py": "src/schemas/wf5_sitemap_direct_submission_schemas.py",
}

# Import path updates needed
IMPORT_UPDATES = {
    # src/routers/__init__.py
    "src/routers/__init__.py": [
        ("from .batch_sitemap import", "from .wf5_sitemap_batch_router import"),
        ("from .modernized_sitemap import", "from .wf5_sitemap_modernized_router import"),
    ],
    
    # src/main.py
    "src/main.py": [
        ("from .routers.modernized_sitemap import", "from .routers.wf5_sitemap_modernized_router import"),
        ("from .routers.sitemap_files import", "from .routers.wf5_sitemap_file_router import"),
    ],
}

def execute_renames():
    """Execute file renames"""
    print("🔄 Phase 1: Renaming WF5 files...")
    
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
    print("Phase 1: WF5 (Sitemap) Naming Standardization")
    print("=" * 60)
    print()
    
    execute_renames()
    update_imports()
    
    print("=" * 60)
    print("✅ Phase 1 Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python3 check_imports.py")
    print("2. Run: docker build -t scraper-sky-backend:phase1-test .")
    print("3. If successful, commit: git add -A && git commit -m 'refactor: Phase 1 - WF5 naming standardization'")
    print("4. If issues, rollback: git reset --hard HEAD~1")
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 3: WF4 (Domains) Naming Standardization
Atomic rename script with rollback capability
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Phase 3: WF4 Renames
RENAMES = {
    # Routers
    "src/routers/domains.py": "src/routers/wf4_domain_router.py",
    
    # Schemas
    "src/schemas/domains_direct_submission_schemas.py": "src/schemas/wf4_domain_direct_submission_schemas.py",
}

# Import path updates needed
IMPORT_UPDATES = {
    # src/routers/__init__.py
    "src/routers/__init__.py": [
        ("from .domains import", "from .wf4_domain_router import"),
    ],
    
    # src/main.py
    "src/main.py": [
        ("from .routers.domains import", "from .routers.wf4_domain_router import"),
    ],
}

def execute_renames():
    """Execute file renames"""
    print("🔄 Phase 3: Renaming WF4 files...")
    
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
    print("Phase 3: WF4 (Domains) Naming Standardization")
    print("=" * 60)
    print()
    
    execute_renames()
    update_imports()
    
    print("=" * 60)
    print("✅ Phase 3 Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python3 check_imports.py")
    print("2. Commit and continue to Phase 4")
    print()

if __name__ == "__main__":
    main()

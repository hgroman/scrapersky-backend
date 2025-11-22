#!/usr/bin/env python3
"""
Phase 5: WF1 (Places) Atomic Rename Script
Renames files for Places workflow standardization
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "src"

# Define renames: (old_path, new_path)
RENAMES = [
    # Routers
    ("routers/places_staging.py", "routers/wf1_place_staging_router.py"),
    ("routers/google_maps_api.py", "routers/wf1_google_maps_api_router.py"),
    
    # Schemas
    ("schemas/places_staging_schemas.py", "schemas/wf1_place_staging_schemas.py"),
    
    # Models
    ("models/place_search.py", "models/wf1_place_search.py"),
]

def main():
    print("=" * 80)
    print("Phase 5: WF1 (Places) - Atomic File Rename")
    print("=" * 80)
    
    # Verify all source files exist
    print("\n[1/3] Verifying source files exist...")
    for old_path, new_path in RENAMES:
        old_full = BASE_DIR / old_path
        if not old_full.exists():
            print(f"  ❌ ERROR: Source file not found: {old_path}")
            return False
        print(f"  ✓ Found: {old_path}")
    
    # Check for conflicts
    print("\n[2/3] Checking for naming conflicts...")
    for old_path, new_path in RENAMES:
        new_full = BASE_DIR / new_path
        if new_full.exists():
            print(f"  ❌ ERROR: Target file already exists: {new_path}")
            return False
        print(f"  ✓ No conflict: {new_path}")
    
    # Execute renames
    print("\n[3/3] Executing renames...")
    for old_path, new_path in RENAMES:
        old_full = BASE_DIR / old_path
        new_full = BASE_DIR / new_path
        
        try:
            shutil.move(str(old_full), str(new_full))
            print(f"  ✓ Renamed: {old_path} → {new_path}")
        except Exception as e:
            print(f"  ❌ ERROR renaming {old_path}: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✅ Phase 5 file renames completed successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update import statements in src/main.py")
    print("2. Run check_imports.py to verify")
    print("3. Docker build test")
    print("4. Commit changes")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

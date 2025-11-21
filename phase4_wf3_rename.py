#!/usr/bin/env python3
"""
Phase 4: WF3 (Local Business) Naming Standardization
Atomic rename script with rollback capability
"""

import os
import sys
from pathlib import Path

# Define base paths
BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
ROUTERS_DIR = SRC_DIR / "routers"
SCHEMAS_DIR = SRC_DIR / "schemas"

# Define renames: (old_path, new_path)
RENAMES = [
    # Routers
    (ROUTERS_DIR / "local_businesses.py", ROUTERS_DIR / "wf3_local_business_router.py"),
    # Schemas
    (SCHEMAS_DIR / "local_business_schemas.py", SCHEMAS_DIR / "wf3_local_business_schemas.py"),
]

def check_files_exist():
    """Verify all source files exist before renaming."""
    print("🔍 Checking that all source files exist...")
    missing = []
    for old_path, _ in RENAMES:
        if not old_path.exists():
            missing.append(str(old_path))
            print(f"  ❌ Missing: {old_path}")
        else:
            print(f"  ✅ Found: {old_path}")
    
    if missing:
        print(f"\n❌ ERROR: {len(missing)} file(s) not found. Aborting.")
        return False
    return True

def check_no_conflicts():
    """Verify no target files already exist."""
    print("\n🔍 Checking for naming conflicts...")
    conflicts = []
    for _, new_path in RENAMES:
        if new_path.exists():
            conflicts.append(str(new_path))
            print(f"  ❌ Already exists: {new_path}")
        else:
            print(f"  ✅ Available: {new_path}")
    
    if conflicts:
        print(f"\n❌ ERROR: {len(conflicts)} file(s) already exist. Aborting.")
        return False
    return True

def execute_renames():
    """Perform the atomic renames."""
    print("\n🔄 Executing renames...")
    renamed = []
    
    try:
        for old_path, new_path in RENAMES:
            print(f"  Renaming: {old_path.name} → {new_path.name}")
            old_path.rename(new_path)
            renamed.append((old_path, new_path))
            print(f"  ✅ Success")
        
        print(f"\n✅ All {len(RENAMES)} files renamed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during rename: {e}")
        print("🔙 Rolling back...")
        
        # Rollback any successful renames
        for old_path, new_path in renamed:
            try:
                new_path.rename(old_path)
                print(f"  ✅ Rolled back: {new_path.name} → {old_path.name}")
            except Exception as rollback_error:
                print(f"  ❌ Rollback failed for {new_path}: {rollback_error}")
        
        return False

def main():
    print("=" * 60)
    print("Phase 4: WF3 (Local Business) Naming Standardization")
    print("=" * 60)
    
    # Pre-flight checks
    if not check_files_exist():
        sys.exit(1)
    
    if not check_no_conflicts():
        sys.exit(1)
    
    # Execute
    if not execute_renames():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Phase 4 rename complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update import paths in src/main.py")
    print("2. Search for any other files importing these modules")
    print("3. Run verification script")
    print("4. Commit changes")

if __name__ == "__main__":
    main()

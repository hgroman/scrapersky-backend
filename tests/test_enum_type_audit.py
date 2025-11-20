"""
Automated Enum Type Audit

This test verifies that ALL SQLAlchemy model enum column definitions
match the actual PostgreSQL enum types in the database.

CRITICAL: Run this before ANY deployment that touches model definitions.

Based on: 2025-11-20 Enum Crisis (commits 688b946, cec9541, 1b5a044)
"""

import os
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL and convert to sync
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    pytest.skip("DATABASE_URL not set", allow_module_level=True)

# Convert asyncpg URL to psycopg2
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    # Fix SSL parameters for psycopg2
    DATABASE_URL = DATABASE_URL.replace("?sslmode=", "?sslmode=")

# Create sync engine for testing
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_database_enum_columns():
    """
    Query database for all columns that use enum types.
    
    Returns dict: {(table_name, column_name): enum_type_name}
    """
    session = Session()
    try:
        query = text("""
            SELECT DISTINCT
                c.relname AS table_name,
                a.attname AS column_name,
                t.typname AS enum_type_used
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            JOIN pg_type t ON a.atttypid = t.oid
            WHERE n.nspname = 'public'
              AND t.typtype = 'e'
              AND c.relkind = 'r'
              AND NOT a.attisdropped
            ORDER BY c.relname, a.attname;
        """)
        
        result = session.execute(query)
        return {
            (row.table_name, row.column_name): row.enum_type_used
            for row in result
        }
    finally:
        session.close()


def get_model_enum_columns():
    """
    Inspect SQLAlchemy models for all Enum column definitions.
    
    Returns dict: {(table_name, column_name): enum_type_name}
    """
    from src.models import (
        LocalBusiness,
        Place,
        Domain,
        Page,
        Contact,
        SitemapFile,
        SitemapUrl,
    )
    
    models = [LocalBusiness, Place, Domain, Page, Contact, SitemapFile, SitemapUrl]
    model_enums = {}
    
    for model in models:
        table_name = model.__tablename__
        inspector = inspect(model)
        
        for column in inspector.columns:
            # Check if column type is Enum
            col_type = str(column.type)
            if 'ENUM' in col_type or hasattr(column.type, 'name'):
                # Get the enum type name from the column definition
                if hasattr(column.type, 'name') and column.type.name:
                    enum_type_name = column.type.name
                    model_enums[(table_name, column.name)] = enum_type_name
    
    return model_enums


def test_enum_types_match_database():
    """
    CRITICAL TEST: Verify all model enum types match database enum types.
    
    This test prevents production failures like:
    - "operator does not exist: column = enum_type"
    - "column is of type X but expression is of type Y"
    
    If this test fails, DO NOT DEPLOY.
    """
    db_enums = get_database_enum_columns()
    model_enums = get_model_enum_columns()
    
    mismatches = []
    missing_in_model = []
    
    # Check each database enum column
    for (table, column), db_type in db_enums.items():
        # Skip tables we don't have models for
        if table in ['file_remediation_tasks']:
            continue
            
        model_key = (table, column)
        
        if model_key not in model_enums:
            # Column exists in DB but not in model
            missing_in_model.append({
                'table': table,
                'column': column,
                'db_type': db_type,
                'issue': 'Column exists in database but not in model'
            })
        elif model_enums[model_key] != db_type:
            # Type mismatch
            mismatches.append({
                'table': table,
                'column': column,
                'db_type': db_type,
                'model_type': model_enums[model_key],
                'issue': 'Enum type name mismatch'
            })
    
    # Build error message
    errors = []
    
    if mismatches:
        errors.append("\n❌ ENUM TYPE MISMATCHES FOUND:")
        for m in mismatches:
            errors.append(
                f"  {m['table']}.{m['column']}: "
                f"DB uses '{m['db_type']}' but model uses '{m['model_type']}'"
            )
    
    if missing_in_model:
        errors.append("\n⚠️  COLUMNS IN DB BUT NOT IN MODEL:")
        for m in missing_in_model:
            errors.append(
                f"  {m['table']}.{m['column']}: "
                f"DB has column with type '{m['db_type']}' but model doesn't define it"
            )
    
    if errors:
        error_msg = "\n".join(errors)
        error_msg += "\n\n🚨 DO NOT DEPLOY UNTIL THESE ARE FIXED 🚨"
        error_msg += "\n\nSee: Documentation/Testing/KNOWN_FAILURES.md"
        error_msg += "\nSee: SOLUTION_ENUM_CRISIS_2025-11-20.md"
        pytest.fail(error_msg)
    
    # If we get here, all enum types match!
    print("\n✅ All enum types match database!")
    print(f"   Verified {len(db_enums)} enum columns")


def test_no_orphaned_enum_types():
    """
    Check for enum types that exist in database but aren't used by any column.
    
    These are usually leftovers from failed migrations and should be cleaned up.
    """
    session = Session()
    try:
        query = text("""
            SELECT t.typname AS unused_enum_type
            FROM pg_type t
            WHERE t.typtype = 'e'
              AND t.typname NOT IN (
                SELECT DISTINCT udt_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
              )
              -- Exclude Supabase internal types
              AND t.typname NOT LIKE 'aal_%'
              AND t.typname NOT LIKE 'code_%'
              AND t.typname NOT LIKE 'factor_%'
              AND t.typname NOT LIKE 'key_%'
              AND t.typname NOT LIKE 'oauth_%'
              AND t.typname NOT LIKE 'one_time_%'
              AND t.typname NOT IN ('action', 'equality_op', 'buckettype')
            ORDER BY t.typname;
        """)
        
        result = session.execute(query)
        orphaned = [row.unused_enum_type for row in result]
        
        if orphaned:
            warning_msg = f"\n⚠️  Found {len(orphaned)} orphaned enum types:\n"
            for enum_type in orphaned:
                warning_msg += f"  - {enum_type}\n"
            warning_msg += "\nThese types exist but aren't used by any column."
            warning_msg += "\nConsider dropping them to clean up the schema."
            print(warning_msg)
        else:
            print("\n✅ No orphaned enum types found!")
    finally:
        session.close()


if __name__ == "__main__":
    # Allow running directly for quick checks
    print("Running enum type audit...")
    test_enum_types_match_database()
    test_no_orphaned_enum_types()
    print("\n✅ Enum audit complete!")

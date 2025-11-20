import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from sqlalchemy.sql import text
from src.services.db_inspector import db_inspector
from src.db.session import get_session_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def inspect_schema():
    print("Starting schema inspection...")
    
    tables_to_inspect = ["tenants"]
    
    async with get_session_context() as session:
        for table in tables_to_inspect:
            print(f"\n--- Inspecting table: {table} ---")
            schema = await db_inspector.get_table_schema(table, session)
            
            if "error" in schema:
                print(f"Error inspecting {table}: {schema['error']}")
                continue
                
            print(f"Table: {schema.get('table_name')}")
            
            print("Columns:")
            for col in schema.get("columns", []):
                # Fetch udt_name for USER-DEFINED types
                udt_name = col['data_type']
                if col['data_type'] == 'USER-DEFINED':
                    try:
                        query = text(f"SELECT udt_name FROM information_schema.columns WHERE table_name = :table AND column_name = :col")
                        result = await session.execute(query, {"table": table, "col": col['column_name']})
                        udt_name = result.scalar()
                    except Exception as e:
                        udt_name = f"Error fetching udt_name: {e}"
                
                print(f"  - {col['column_name']}: {col['data_type']} (UDT: {udt_name}) (Nullable: {col['is_nullable']}, PK: {col['is_primary_key']})")
                
            print("Foreign Keys:")
            for fk in schema.get("foreign_keys", []):
                print(f"  - {fk['column_name']} -> {fk['foreign_table']}.{fk['foreign_column']}")

if __name__ == "__main__":
    asyncio.run(inspect_schema())

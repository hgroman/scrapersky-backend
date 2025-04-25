"""
Database Inspector Service

This service provides functionality to inspect and validate the database schema,
serving as the source of truth for the application. It includes methods to:
1. List all tables in the database
2. Get detailed schema information for specific tables
3. Validate model definitions against the actual schema
4. Execute schema-related SQL queries safely
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.db.engine import get_sync_engine
from src.services.core.db_service import db_service

logger = logging.getLogger(__name__)

class DatabaseInspector:
    """
    Service for inspecting the database schema and validating models.
    Acts as the source of truth for database structure.
    """

    def __init__(self):
        self._schema_cache = {}
        self._table_cache = {}
        # No need to initialize a connection here, we'll use get_session() as needed

    async def list_all_tables(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """
        List all tables in the database with basic information.
        
        Args:
            session: An existing database session to use
            
        Returns:
            List of dictionaries containing table information
        """
        query = """
        SELECT
            table_schema,
            table_name,
            (SELECT reltuples::bigint FROM pg_class WHERE oid = (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass) AS row_count,
            last_analyzed
        FROM
            pg_stat_user_tables
        WHERE
            table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY
            table_schema, table_name
        """

        try:
            results = []
            result = await session.execute(text(query))
            for row in result.fetchall():
                results.append({
                    "schema_name": row[0],
                    "table_name": row[1],
                    "row_count": row[2] or 0,
                    "last_analyzed": str(row[3]) if row[3] else None
                })
            return results
        except Exception as e:
            logger.error(f"Error listing database tables: {str(e)}")
            return []

    async def get_table_schema(self, table_name: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Get detailed schema information for a specific table.

        Args:
            table_name: The name of the table to inspect
            session: An existing database session to use

        Returns:
            Dict with table schema details:
            {
                "table_name": "domains",
                "columns": [
                    {
                        "column_name": "id",
                        "data_type": "uuid",
                        "is_nullable": false,
                        "column_default": "uuid_generate_v4()",
                        "is_primary_key": true
                    },
                    ...
                ],
                "indexes": [
                    {
                        "index_name": "domains_pkey",
                        "column_names": ["id"],
                        "is_unique": true
                    },
                    ...
                ],
                "foreign_keys": [
                    {
                        "column_name": "tenant_id",
                        "foreign_table": "tenants",
                        "foreign_column": "id"
                    },
                    ...
                ]
            }
        """
        # Check cache first
        if table_name in self._schema_cache:
            return self._schema_cache[table_name]

        result = {
            "table_name": table_name,
            "columns": [],
            "indexes": [],
            "foreign_keys": []
        }

        try:
            # Get column information
            column_query = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as is_nullable,
                c.column_default,
                CASE WHEN pk.constraint_name IS NOT NULL THEN true ELSE false END as is_primary_key,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT tc.constraint_name, ccu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = :table_name
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_name = :table_name
            ORDER BY c.ordinal_position
            """

            # Using async session
            column_result = await session.execute(
                text(column_query), 
                {"table_name": table_name}
            )
            
            for row in column_result.fetchall():
                column_info = {
                    "column_name": row[0],
                    "data_type": row[1],
                    "is_nullable": row[2],
                    "column_default": row[3],
                    "is_primary_key": row[4]
                }

                # Add length for character types
                if row[5] is not None:
                    column_info["max_length"] = row[5]

                # Add precision and scale for numeric types
                if row[6] is not None:
                    column_info["precision"] = row[6]
                    column_info["scale"] = row[7]

                result["columns"].append(column_info)

            # Get index information
            index_query = """
            SELECT
                i.relname as index_name,
                array_agg(a.attname) as column_names,
                ix.indisunique as is_unique
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                and i.oid = ix.indexrelid
                and a.attrelid = t.oid
                and a.attnum = ANY(ix.indkey)
                and t.relkind = 'r'
                and t.relname = :table_name
            GROUP BY
                i.relname,
                ix.indisunique
            ORDER BY
                i.relname;
            """

            index_result = await session.execute(
                text(index_query), 
                {"table_name": table_name}
            )
            
            for row in index_result.fetchall():
                # Handle potentially None array value
                column_names = row[1] if row[1] is not None else []

                result["indexes"].append({
                    "index_name": row[0],
                    "column_names": column_names,
                    "is_unique": row[2]
                })

            # Get foreign key information
            fk_query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = :table_name
            """

            fk_result = await session.execute(
                text(fk_query), 
                {"table_name": table_name}
            )
            
            for row in fk_result.fetchall():
                result["foreign_keys"].append({
                    "column_name": row[0],
                    "foreign_table": row[1],
                    "foreign_column": row[2]
                })

            # Cache the result
            self._schema_cache[table_name] = result
            return result

        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {str(e)}")
            return {"error": str(e), "table_name": table_name}

    async def get_sample_data(self, table_name: str, limit: int = 5, session: AsyncSession = None) -> List[Dict[str, Any]]:
        """
        Get sample data from a table (for previewing).

        Args:
            table_name: The name of the table to sample
            limit: Maximum number of rows to return
            session: An existing database session to use

        Returns:
            List of dicts with row data
        """
        try:
            # Sanitize table_name to prevent SQL injection
            if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
                raise ValueError("Invalid table name")
            
            # Limit the number of rows for safety
            safe_limit = min(limit, 100)
            
            # Use parameterized query for better security
            query = text(f"SELECT * FROM {table_name} LIMIT :limit")
            
            # Execute the query with the provided session
            result = await session.execute(query, {"limit": safe_limit})
            
            columns = [desc[0] for desc in result.keys()]
            rows = result.fetchall()
            
            formatted_results = []
            
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    # Convert non-JSON serializable types to strings
                    value = row[i]
                    if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                        value = str(value)
                    row_dict[column] = value
                formatted_results.append(row_dict)
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error getting sample data for table {table_name}: {str(e)}")
            return [{"error": str(e)}]

    async def validate_table_schema(self, table_name: str, expected_schema: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """
        Validate expected schema against actual database schema.

        Args:
            table_name: The name of the table to validate
            expected_schema: The expected schema definition
            session: An existing database session to use

        Returns:
            Dict with validation results:
            {
                "is_valid": true/false,
                "missing_columns": [],
                "type_mismatches": [],
                "extra_columns": []
            }
        """
        actual_schema = await self.get_table_schema(table_name, session)

        result = {
            "is_valid": True,
            "missing_columns": [],
            "type_mismatches": [],
            "extra_columns": []
        }

        # Extract column names from both schemas
        actual_columns = {col["column_name"]: col for col in actual_schema.get("columns", [])}
        expected_columns = {col["column_name"]: col for col in expected_schema.get("columns", [])}

        # Check for missing columns
        for col_name, col_def in expected_columns.items():
            if col_name not in actual_columns:
                result["is_valid"] = False
                result["missing_columns"].append({
                    "column_name": col_name,
                    "expected_type": col_def.get("data_type", "unknown")
                })
            else:
                # Check for type mismatches on existing columns
                actual_col = actual_columns[col_name]
                if col_def.get("data_type") and col_def["data_type"] != actual_col["data_type"]:
                    result["is_valid"] = False
                    result["type_mismatches"].append({
                        "column_name": col_name,
                        "expected_type": col_def["data_type"],
                        "actual_type": actual_col["data_type"]
                    })

        # Check for extra columns in the database
        for col_name in actual_columns:
            if col_name not in expected_columns:
                result["extra_columns"].append({
                    "column_name": col_name,
                    "data_type": actual_columns[col_name]["data_type"]
                })

        return result

    async def execute_safe_query(self, query: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Execute a safe, read-only query for database inspection.
        Only SELECT queries are allowed.

        Args:
            query: The SQL query to execute
            session: An existing database session to use

        Returns:
            Dict with query results or error
        """
        # Check if the query is read-only
        if not query.strip().lower().startswith('select'):
            return {
                "error": "Only SELECT queries are permitted for database inspection",
                "success": False
            }

        try:
            # Execute the query with the provided session
            result = await session.execute(text(query))
            
            columns = [desc[0] for desc in result.keys()]
            rows = result.fetchall()
            
            formatted_results = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    # Convert non-JSON serializable types to strings
                    value = row[i]
                    if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                        value = str(value)
                    row_dict[column] = value
                formatted_results.append(row_dict)

            return {
                "success": True,
                "columns": columns,
                "rows": formatted_results,
                "row_count": len(formatted_results)
            }
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }

    async def generate_model_code(self, table_name: str, session: AsyncSession) -> str:
        """
        Generate Python model code based on database schema.

        Args:
            table_name: The name of the table to generate model for
            session: An existing database session to use

        Returns:
            String containing Python code for the model
        """
        schema = await self.get_table_schema(table_name, session)

        # Map PostgreSQL types to Python types
        type_mapping = {
            'integer': 'int',
            'bigint': 'int',
            'smallint': 'int',
            'character varying': 'str',
            'varchar': 'str',
            'text': 'str',
            'boolean': 'bool',
            'date': 'datetime.date',
            'timestamp': 'datetime.datetime',
            'timestamp with time zone': 'datetime.datetime',
            'timestamp without time zone': 'datetime.datetime',
            'uuid': 'uuid.UUID',
            'jsonb': 'Dict[str, Any]',
            'json': 'Dict[str, Any]',
            'double precision': 'float',
            'real': 'float',
            'numeric': 'Decimal'
        }

        # Generate Python code
        class_name = ''.join(word.capitalize() for word in table_name.split('_'))
        code = f"""from typing import Optional, List, Dict, Any
import uuid
import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class {class_name}(BaseModel):
    \"\"\"
    Model for {table_name} table.
    Auto-generated from database schema.
    \"\"\"
"""

        # Add class attributes
        for column in schema.get("columns", []):
            name = column["column_name"]
            is_nullable = column["is_nullable"]
            pg_type = column["data_type"]

            # Get Python type from mapping
            py_type = type_mapping.get(pg_type, 'Any')

            # Make nullable fields Optional
            field_type = f"Optional[{py_type}]" if is_nullable else py_type

            # Add default if it's a primary key with a default value
            if column["is_primary_key"] and "uuid_generate" in str(column.get("column_default", "")):
                default = " = Field(default_factory=uuid.uuid4)"
            elif is_nullable:
                default = " = None"
            else:
                default = ""

            code += f"    {name}: {field_type}{default}\n"

        return code

# Create a singleton instance
db_inspector = DatabaseInspector()

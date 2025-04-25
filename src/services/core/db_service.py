"""
Database Service Module

This module provides a centralized service for all database operations.
It includes methods for common query patterns, connection management,
and database introspection.
"""

import json
import logging
import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import psycopg
import psycopg.rows
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from psycopg import sql

from ...db.engine import get_sync_engine
from ...session.async_session import get_session

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Centralized service for database operations.
    Provides reusable query methods, connection management, and database introspection.
    """

    @staticmethod
    @contextmanager
    def get_cursor(row_factory=psycopg.rows.dict_row):
        """
        Get a database cursor using a specific row factory (defaults to dict_row).

        Args:
            row_factory: The psycopg row factory (e.g., psycopg.rows.dict_row).

        Yields:
            A database cursor
        """
        conn = None
        cur = None
        engine = get_sync_engine()
        try:
            conn = engine.raw_connection()
            # Set row_factory on the connection *before* creating cursor (psycopg v3)
            # conn.row_factory = row_factory # Incorrect for pooled connection
            # cur = conn.cursor()
            cur = conn.cursor(row_factory=row_factory) # Pass factory here
            yield cur
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error in database cursor operation: {str(e)}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    @contextmanager
    def get_connection():
        """
        Get a database connection.

        Yields:
            A database connection
        """
        engine = get_sync_engine()
        connection = engine.raw_connection()
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def test_connection():
        """Test the database connection."""
        try:
            engine = get_sync_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

    @classmethod
    async def fetch_one(cls, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return a single row as a dictionary.

        Args:
            query: SQL query with parameters
            params: Query parameters

        Returns:
            A dictionary representing the row, or None if no rows returned
        """
        try:
            with cls.get_cursor() as cur:
                cur.execute(query, params or {})
                result = cur.fetchone()

                if not result:
                    return None

                # Ensure we return a dictionary
                if isinstance(result, dict):
                    return result
                else:
                    # Convert tuple to dictionary using column names
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, result))
                    return None

        except Exception as e:
            logger.error(f"Database error in fetch_one: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    @classmethod
    async def fetch_all(cls, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return all rows as a list of dictionaries.

        Args:
            query: SQL query with parameters
            params: Query parameters

        Returns:
            A list of dictionaries representing the rows
        """
        try:
            with cls.get_cursor() as cur:
                cur.execute(query, params or {})
                results = cur.fetchall()

                if not results:
                    return []

                # Ensure we return a list of dictionaries
                if results and isinstance(results[0], dict):
                    # Type-safe conversion to List[Dict[str, Any]]
                    return [dict(row) for row in results]
                else:
                    # Convert tuples to dictionaries using column names
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        return [dict(zip(columns, row)) for row in results]
                    return []

        except Exception as e:
            logger.error(f"Database error in fetch_all: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    @classmethod
    async def execute(cls, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a query and return the number of affected rows.

        Args:
            query: SQL query with parameters
            params: Query parameters

        Returns:
            Number of affected rows
        """
        try:
            with cls.get_cursor() as cur:
                cur.execute(query, params or {})
                # For INSERT/UPDATE/DELETE queries, rowcount gives the number of affected rows
                return cur.rowcount

        except Exception as e:
            logger.error(f"Database error in execute: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    @classmethod
    async def execute_returning(cls, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query with RETURNING clause and return the result.

        Args:
            query: SQL query with RETURNING clause
            params: Query parameters

        Returns:
            Dictionary representing the returned row
        """
        try:
            with cls.get_cursor() as cur:
                cur.execute(query, params or {})
                result = cur.fetchone()

                if not result:
                    return None

                # Ensure we return a dictionary
                if isinstance(result, dict):
                    return result
                else:
                    # Convert tuple to dictionary using column names
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, result))
                    return None

        except Exception as e:
            logger.error(f"Database error in execute_returning: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    @classmethod
    async def execute_batch(cls, query: str, params_list: List[Dict[str, Any]]) -> int:
        """
        Execute a batch of queries and return the total number of affected rows.

        Args:
            query: SQL query with parameters
            params_list: List of parameter dictionaries

        Returns:
            Total number of affected rows
        """
        try:
            if not params_list:
                return 0

            with cls.get_cursor() as cur:
                total_rows = 0
                for params in params_list:
                    cur.execute(query, params)
                    total_rows += cur.rowcount

                return total_rows

        except Exception as e:
            logger.error(f"Database error in execute_batch: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params list size: {len(params_list)}")
            raise

    @classmethod
    async def execute_transaction(cls, queries_and_params: List[Tuple[str, Dict[str, Any]]]) -> None:
        """
        Execute multiple queries in a transaction.

        Args:
            queries_and_params: List of tuples (query, params)
        """
        if not queries_and_params:
            return

        conn = None
        cur = None
        try:
            with cls.get_connection() as conn:
                # Create cursor manually, not with 'with'
                cur = conn.cursor()
                for query, params in queries_and_params:
                    cur.execute(query, params or {})
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}")
            for i, (query, params) in enumerate(queries_and_params):
                logger.error(f"Query {i}: {query}")
                logger.error(f"Params {i}: {params}")
            raise
        finally:
            # Ensure cursor is closed if it was created
            if cur:
                cur.close()

    @classmethod
    async def get_tables(cls) -> List[str]:
        """
        Get a list of all tables in the database.

        Returns:
            List of table names
        """
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """

        try:
            with cls.get_cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()

                if not results:
                    return []

                # Extract table names from results
                if results and isinstance(results[0], dict):
                    # Convert to list of strings with type assertion
                    return [dict(row)['table_name'] for row in results]
                else:
                    return [row[0] for row in results]

        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            raise

    @classmethod
    async def get_table_columns(cls, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about columns in a table.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM
                information_schema.columns
            WHERE
                table_schema = 'public'
                AND table_name = %(table_name)s
            ORDER BY
                ordinal_position
        """

        try:
            with cls.get_cursor() as cur:
                cur.execute(query, {'table_name': table_name})
                results = cur.fetchall()

                if not results:
                    return []

                # Ensure we return a list of dictionaries
                if results and isinstance(results[0], dict):
                    # Type-safe conversion to List[Dict[str, Any]]
                    return [dict(row) for row in results]
                else:
                    # Convert tuples to dictionaries using column names
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        return [dict(zip(columns, row)) for row in results]
                    return []

        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {str(e)}")
            raise

    @classmethod
    async def get_record_by_id(cls, table_name: str, record_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID with tenant isolation.

        Args:
            table_name: Name of the table
            record_id: ID of the record
            tenant_id: Tenant ID for isolation

        Returns:
            Dictionary representing the record, or None if not found
        """
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE id = %(record_id)s AND tenant_id = %(tenant_id)s
        """

        return await cls.fetch_one(query, {'record_id': record_id, 'tenant_id': tenant_id})

    @classmethod
    async def get_table_count(cls, table_name: str, tenant_id: Optional[str] = None,
                        filter_clause: Optional[str] = None,
                        filter_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Get the count of records in a table with optional filtering.

        Args:
            table_name: Name of the table
            tenant_id: Optional tenant ID for isolation
            filter_clause: Optional WHERE clause (without the "WHERE" keyword)
            filter_params: Parameters for the filter clause

        Returns:
            Record count
        """
        where_clauses = []
        params = filter_params or {}

        if tenant_id:
            where_clauses.append("tenant_id = %(tenant_id)s")
            params['tenant_id'] = tenant_id

        if filter_clause:
            where_clauses.append(filter_clause)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT COUNT(*) AS record_count
            FROM {table_name}
            {where_sql}
        """

        result = await cls.fetch_one(query, params)
        if not result:
            return 0

        # Handle different result formats
        if isinstance(result, dict):
            return result.get('record_count', 0)
        else:
            return result[0]

    @classmethod
    async def json_contains(cls, table_name: str, json_column: str, key: str, value: Any,
                      tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for records where a JSON column contains a specific key/value pair.

        Args:
            table_name: Name of the table
            json_column: Name of the JSON column
            key: JSON key to search for
            value: Value to match
            tenant_id: Optional tenant ID for isolation

        Returns:
            List of matching records
        """
        where_clauses = [f"{json_column}->%(key)s = %(value)s::jsonb"]
        params = {'key': key, 'value': json.dumps(value)}

        if tenant_id:
            where_clauses.append("tenant_id = %(tenant_id)s")
            params['tenant_id'] = tenant_id

        where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT *
            FROM {table_name}
            {where_sql}
        """

        return await cls.fetch_all(query, params)

    @classmethod
    async def create_record(cls, table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new record in the database.

        Args:
            table_name: Name of the table
            data: Dictionary of column values

        Returns:
            The created record with its ID
        """
        columns = list(data.keys())
        values = [f"%({col})s" for col in columns]

        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(values)})
            RETURNING *
        """

        return await cls.execute_returning(query, data)

    @classmethod
    async def update_record(cls, table_name: str, record_id: str, data: Dict[str, Any],
                      tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a record in the database.

        Args:
            table_name: Name of the table
            record_id: ID of the record
            data: Dictionary of column values to update
            tenant_id: Optional tenant ID for isolation

        Returns:
            The updated record or None if not found
        """
        set_clauses = [f"{col} = %({col})s" for col in data.keys()]

        where_clauses = ["id = %(record_id)s"]
        params = {**data, 'record_id': record_id}

        if tenant_id:
            where_clauses.append("tenant_id = %(tenant_id)s")
            params['tenant_id'] = tenant_id

        query = f"""
            UPDATE {table_name}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
            RETURNING *
        """

        return await cls.execute_returning(query, params)

    @classmethod
    async def delete_record(cls, table_name: str, record_id: str, tenant_id: Optional[str] = None) -> bool:
        """
        Delete a record from the database.

        Args:
            table_name: Name of the table
            record_id: ID of the record
            tenant_id: Optional tenant ID for isolation

        Returns:
            True if a record was deleted, False otherwise
        """
        where_clauses = ["id = %(record_id)s"]
        params = {'record_id': record_id}

        if tenant_id:
            where_clauses.append("tenant_id = %(tenant_id)s")
            params['tenant_id'] = tenant_id

        query = f"""
            DELETE FROM {table_name}
            WHERE {' AND '.join(where_clauses)}
        """

        rows_affected = await cls.execute(query, params)
        return rows_affected > 0

# Create singleton instance
db_service = DatabaseService()

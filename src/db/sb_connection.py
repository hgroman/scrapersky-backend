"""
Supabase Database Connection Module

This module provides a reliable connection to the Supabase PostgreSQL database.
It handles connection pooling, environment configuration, and proper error handling.
"""

import os
import time
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# Import settings from central config
from src.config.settings import settings

class DatabaseConfig:
    """Configuration for Supabase database connection."""

    def __init__(self):
        # Extract project reference from Supabase URL
        self.supabase_url = settings.supabase_url
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set")
            
        # Handle URL format with or without protocol
        if '//' in self.supabase_url:
            self.project_ref = self.supabase_url.split('//')[1].split('.')[0]
        else:
            self.project_ref = self.supabase_url.split('.')[0]

        # Database connection parameters
        self.user = f"postgres.{self.project_ref}"
        self.password = settings.supabase_db_password
        self.host = f"db.{self.project_ref}.supabase.co"
        self.port = "5432"
        self.dbname = "postgres"

        if not all([self.project_ref, self.password]):
            raise ValueError(
                "Missing required database configuration. "
                "Please ensure SUPABASE_URL and SUPABASE_DB_PASSWORD are set in .env"
            )

    @property
    def connection_string(self) -> str:
        """Generate the connection string with proper URL encoding.
        Tries pooler connection first, falls back to direct connection.
        """
        # Try pooler connection first (IPv4 compatible)
        pooler_host = os.getenv('SUPABASE_POOLER_HOST')
        pooler_port = os.getenv('SUPABASE_POOLER_PORT')
        pooler_user = os.getenv('SUPABASE_POOLER_USER')

        # Include connection timeout from settings
        timeout_param = f"connect_timeout={settings.db_connection_timeout}"

        if all([pooler_host, pooler_port, pooler_user]):
            return (
                f"postgresql://{pooler_user}:{quote_plus(self.password)}"
                f"@{pooler_host}:{pooler_port}/{self.dbname}"
                f"?sslmode=require&{timeout_param}"
            )

        # Fall back to direct connection if pooler not configured
        return (
            f"postgresql://{self.user}:{quote_plus(self.password)}"
            f"@{self.host}:{self.port}/{self.dbname}"
            f"?sslmode=require&{timeout_param}"
        )

class DatabaseConnection:
    """
    Manages database connections using a connection pool.

    This class provides both direct connection methods and a connection pool
    for better resource management in production environments.
    """

    def __init__(self, min_conn: Optional[int] = None, max_conn: Optional[int] = None):
        self.config = DatabaseConfig()
        self._pool = None
        self.min_conn = min_conn if min_conn is not None else settings.db_min_pool_size
        self.max_conn = max_conn if max_conn is not None else settings.db_max_pool_size
        self._direct_conn_attempts = 0
        self._max_direct_conn_attempts = 3
        self._table_cache: Dict[str, Dict[str, Any]] = {}  # Cache to store table existence checks
        self._cache_timestamps: Dict[str, float] = {}  # Cache timestamps for expiration

    def _ensure_pool(self):
        """Ensure the connection pool exists, create it if it doesn't."""
        if self._pool is None:
            try:
                import logging
                logging.info(f"Attempting to connect to database at {self.config.host}")
                logging.info(f"Using connection string format: postgresql://<user>@{self.config.host}:{self.config.port}/{self.config.dbname}?sslmode=require")

                # Create connection pool with settings from config
                self._pool = SimpleConnectionPool(
                    minconn=self.min_conn,
                    maxconn=self.max_conn,
                    dsn=self.config.connection_string
                )
                logging.info("Database connection pool created successfully")

                # Test the connection with a simple query that doesn't depend on specific tables
                # Get a connection directly from the pool to avoid circular dependency
                conn = self._pool.getconn()
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")  # Simple query that doesn't depend on any tables
                    cursor.close()
                    conn.commit()
                finally:
                    self._pool.putconn(conn)

                return True
            except Exception as e:
                import traceback
                logging.error(f"Database connection error: {str(e)}")
                logging.error(f"Connection traceback: {traceback.format_exc()}")
                logging.error(f"Host: {self.config.host}, Port: {self.config.port}, DB: {self.config.dbname}")
                return False
        return True

    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Get a database connection from the pool.

        Usage:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT NOW();")
        """
        import logging

        # Try to get a connection from the pool
        if not self._ensure_pool():
            logging.warning("Connection pool not available, trying direct connection")
            # If pool creation failed, try direct connection as fallback
            try:
                self._direct_conn_attempts += 1
                if self._direct_conn_attempts > self._max_direct_conn_attempts:
                    logging.error(f"Exceeded maximum direct connection attempts ({self._max_direct_conn_attempts})")
                    raise ConnectionError("Database connection is not available after multiple attempts")

                logging.info(f"Attempting direct connection (attempt {self._direct_conn_attempts})")
                conn = psycopg2.connect(
                    self.config.connection_string
                )
                try:
                    yield conn
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                return
            except Exception as e:
                logging.error(f"Direct connection failed: {str(e)}")
                raise ConnectionError(f"Database connection is not available: {str(e)}")

        # Get connection from pool
        try:
            conn = self._pool.getconn()
            try:
                # Test if connection is still alive
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()

                yield conn
            except psycopg2.OperationalError as e:
                logging.warning(f"Connection from pool is stale, creating new connection: {str(e)}")
                # Close the stale connection
                try:
                    self._pool.putconn(conn, close=True)
                except Exception:
                    pass

                # Create a new connection
                conn = psycopg2.connect(
                    self.config.connection_string
                )
                try:
                    yield conn
                    conn.commit()
                finally:
                    conn.close()
            finally:
                if conn and not conn.closed and self._pool:
                    self._pool.putconn(conn)
        except Exception as e:
            logging.error(f"Error getting connection from pool: {str(e)}")
            # Try direct connection as last resort
            try:
                logging.info("Attempting direct connection as last resort")
                conn = psycopg2.connect(
                    self.config.connection_string
                )
                try:
                    yield conn
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
            except Exception as direct_e:
                logging.error(f"Direct connection failed: {str(direct_e)}")
                raise ConnectionError(f"Database connection is not available: {str(e)}, direct connection failed: {str(direct_e)}")

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator[psycopg2.extensions.cursor, None, None]:
        """
        Get a database cursor with automatic connection management.

        Usage:
            with db.get_cursor() as cur:
                cur.execute("SELECT NOW();")
                result = cur.fetchone()
        """
        import logging

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=cursor_factory)
                try:
                    yield cursor
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    logging.error(f"Database error in cursor: {str(e)}")
                    raise
                finally:
                    cursor.close()
        except Exception as e:
            logging.error(f"Failed to get database cursor: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Test the database connection.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT NOW();")
                result = cur.fetchone()
                print(f"Connection successful! Current time: {result['now']}")
                return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False

    def close(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()

    def table_exists(self, table_name, refresh_cache=False):
        """
        Check if a table exists in the database.

        Args:
            table_name: The name of the table to check
            refresh_cache: Force refresh the cache for this table

        Returns:
            bool: True if the table exists, False otherwise
        """
        import logging

        # Check if cache is valid (not expired and not forced refresh)
        current_time = time.time()
        cache_valid = (
            table_name in self._table_cache and
            table_name in self._cache_timestamps and
            current_time - self._cache_timestamps.get(table_name, 0) < settings.cache_ttl and
            not refresh_cache
        )
        
        # Return cached result if valid
        if cache_valid:
            return self._table_cache[table_name]

        try:
            with self.get_cursor() as cur:
                # Check if the table exists in the public schema
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    )
                """, (table_name,))
                exists = cur.fetchone()

                # Extract the boolean value
                result = exists[0] if isinstance(exists, tuple) else exists.get('exists', False)

                # Cache the result with timestamp
                self._table_cache[table_name] = result
                self._cache_timestamps[table_name] = current_time

                if not result:
                    logging.warning(f"Table '{table_name}' does not exist in the database")

                return result
        except Exception as e:
            logging.error(f"Error checking if table '{table_name}' exists: {str(e)}")
            return False

    def execute_safe(self, cursor, query, params=None):
        """
        Execute a query with proper error handling.

        Args:
            cursor: The database cursor
            query: The SQL query to execute
            params: Query parameters (optional)

        Returns:
            bool: True if the query was executed successfully, False otherwise
        """
        import logging

        try:
            cursor.execute(query, params)
            return True
        except Exception as e:
            logging.error(f"Error executing query: {str(e)}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            return False

# Singleton instance for application-wide use
db = DatabaseConnection()

# Example usage:
if __name__ == "__main__":
    db.test_connection()

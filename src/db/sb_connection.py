"""
Supabase Database Connection Module

This module provides a reliable connection to the Supabase PostgreSQL database.
It handles connection pooling, environment configuration, and proper error handling.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Configuration for Supabase database connection."""
    
    def __init__(self):
        # Extract project reference from Supabase URL
        supabase_url = os.getenv('SUPABASE_URL', '')
        self.project_ref = supabase_url.split('//')[1].split('.')[0]
        
        # Database connection parameters
        self.user = f"postgres.{self.project_ref}"
        # Updated to use the all-caps environment variable for consistency
        self.password = os.getenv('SUPABASE_DB_PASSWORD')
        self.host = f"db.{self.project_ref}.supabase.co"
        self.port = "5432"
        self.dbname = "postgres"
        
        if not all([self.project_ref, self.password]):
            raise ValueError(
                "Missing required environment variables. "
                "Please ensure SUPABASE_URL and SUPABASE_DB_PASSWORD are set in .env"
            )
    
    @property
    def connection_string(self) -> str:
        """Generate the connection string with proper URL encoding."""
        return (
            f"postgresql://{self.user}:{quote_plus(self.password)}"
            f"@{self.host}:{self.port}/{self.dbname}?sslmode=require"
        )

class DatabaseConnection:
    """
    Manages database connections using a connection pool.
    
    This class provides both direct connection methods and a connection pool
    for better resource management in production environments.
    """
    
    def __init__(self, min_conn: int = 1, max_conn: int = 10):
        self.config = DatabaseConfig()
        self._pool = SimpleConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            dsn=self.config.connection_string
        )
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Get a database connection from the pool.
        
        Usage:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT NOW();")
        """
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator[psycopg2.extensions.cursor, None, None]:
        """
        Get a database cursor with automatic connection management.
        
        Usage:
            with db.get_cursor() as cur:
                cur.execute("SELECT NOW();")
                result = cur.fetchone()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
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

# Singleton instance for application-wide use
db = DatabaseConnection()

# Example usage:
if __name__ == "__main__":
    db.test_connection()

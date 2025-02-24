import asyncpg
import logging
import asyncio
import ssl
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from os import getenv
from urllib.parse import quote_plus

class AsyncDatabase:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

        # Get pooler configuration (IPv4 compatible)
        self._host = getenv('SUPABASE_POOLER_HOST')
        self._port = getenv('SUPABASE_POOLER_PORT')
        self._user = getenv('SUPABASE_POOLER_USER')
        self._password = getenv('SUPABASE_DB_PASSWORD')
        self._dbname = 'postgres'

        # Fallback to direct connection if pooler not configured
        if not all([self._host, self._port, self._user]):
            supabase_url = getenv('SUPABASE_URL', '')
            if not supabase_url:
                raise ValueError("SUPABASE_URL environment variable is required")

            project_ref = supabase_url.split('//')[1].split('.')[0]
            self._host = f"db.{project_ref}.supabase.co"
            self._port = "5432"
            self._user = f"postgres.{project_ref}"

        if not self._password:
            raise ValueError("SUPABASE_DB_PASSWORD environment variable is required")

        # Log connection details (without sensitive info)
        logging.info(f"Configured database connection for host: {self._host}")
        logging.info(f"Using connection format: postgresql://<user>@{self._host}:{self._port}/{self._dbname}?sslmode=require")

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create an SSL context for secure connection."""
        ssl_context = ssl.create_default_context()
        # Match sslmode=require behavior: require SSL but don't verify certificate
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    async def init_pool(self):
        """Initialize the connection pool if it doesn't exist or is closed."""
        if not self._pool or self._pool._closed:
            try:
                # Use SSL but don't verify certificates (matches sslmode=require behavior)
                ssl_context = self._create_ssl_context()
                self._pool = await asyncpg.create_pool(
                    host=self._host,
                    port=self._port,
                    user=self._user,
                    password=self._password,
                    database=self._dbname,
                    min_size=1,
                    max_size=10,
                    ssl=ssl_context,
                    statement_cache_size=0  # Disable statement caching for pgbouncer compatibility
                )
                logging.info("Database connection pool created successfully")
            except Exception as e:
                logging.error(f"Failed to create connection pool: {str(e)}")
                import traceback
                logging.error(f"Connection traceback: {traceback.format_exc()}")
                logging.error(f"Host: {self._host}, Port: {self._port}, DB: {self._dbname}")
                raise

    @property
    def is_closed(self) -> bool:
        """Check if the pool is closed or not initialized."""
        return self._pool is None or self._pool._closed

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection from the pool, initializing it if necessary."""
        if self.is_closed:
            await self.init_pool()

        if not self._pool:
            raise RuntimeError("Pool initialization failed")

        try:
            async with self._pool.acquire() as connection:
                yield connection
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise

    async def close(self):
        """Close the connection pool if it exists and is not already closed."""
        if self._pool and not self._pool._closed:
            await self._pool.close()
            self._pool = None
            logging.info("Connection pool closed successfully")

# Global instance
async_db = AsyncDatabase()

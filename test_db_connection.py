"""
Database Connection Test Script

This script tests the database connection with detailed logging to verify:
1. Whether pooler or direct connection is being used
2. Successful connection establishment
3. Basic query execution
"""

import logging
import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv
from src.db.sb_connection import db, DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection_info(conn_string: str) -> dict:
    """Parse and return connection information."""
    parsed = urlparse(conn_string)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'user': parsed.username,
        'dbname': parsed.path.strip('/')
    }

def test_connection():
    """Test database connection with detailed logging."""
    try:
        # Get connection string info
        config = DatabaseConfig()
        conn_info = get_connection_info(config.connection_string)
        
        # Log connection attempt details
        logger.info("Connection Configuration:")
        logger.info(f"Host: {conn_info['host']}")
        logger.info(f"Port: {conn_info['port']}")
        logger.info(f"Database: {conn_info['dbname']}")
        logger.info(f"User: {conn_info['user']}")
        
        # Check if using pooler
        is_pooler = 'pooler' in conn_info['host']
        logger.info(f"Using connection type: {'Pooler' if is_pooler else 'Direct'}")
        
        # Get host IP information
        try:
            host_info = socket.getaddrinfo(
                conn_info['host'], 
                conn_info['port'],
                proto=socket.IPPROTO_TCP
            )
            for addr_family, _, _, _, addr in host_info:
                addr_type = 'IPv6' if addr_family == socket.AF_INET6 else 'IPv4'
                logger.info(f"Resolved {addr_type} address: {addr[0]}")
        except socket.gaierror as e:
            logger.error(f"Failed to resolve host: {e}")
            return False

        # Test actual connection
        logger.info("Attempting database connection...")
        with db.get_cursor() as cur:
            # Test query
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info("Connection successful!")
            logger.info(f"PostgreSQL version: {version}")
            
            # Test schema access
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 1;
            """)
            table = cur.fetchone()
            logger.info(f"Successfully queried schema. Found table: {table}")
            
        return True

    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    success = test_connection()
    
    if success:
        logger.info("✅ All connection tests passed successfully!")
        exit(0)
    else:
        logger.error("❌ Connection test failed!")
        exit(1)

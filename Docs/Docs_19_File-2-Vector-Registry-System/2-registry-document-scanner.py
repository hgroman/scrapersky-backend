#!/usr/bin/env python3
"""
Document Registry Management Script

This script manages the document registry for ScraperSky's vector database system.
It identifies files with the `v_` prefix and adds them to the document registry table.
"""

import os
import sys
import re
import asyncio
import asyncpg
import argparse
import logging
import hashlib # Added for file_hash
from datetime import datetime, timezone # Ensure timezone aware for consistency
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Supabase Project ID (from persona)
SUPABASE_PROJECT_ID = "ddfldwzhdhhzhxywqnyz"  # Hardcoded from persona for direct use

class DocumentRegistryManager:
    def __init__(self, conn):
        self.conn = conn

    async def scan_filesystem(self):
        """Scan approved directories for documents with v_ prefix."""
        approved_dirs = await self.get_approved_directories()
        if not approved_dirs:
            logger.warning("No approved directories found. Use 1-registry-directory-manager.py to approve directories.")
            return
        
        logger.info(f"Starting scan of {len(approved_dirs)} approved director(y/ies)...")
        for dir_path in approved_dirs:
            dir_obj = Path(dir_path)
            if not dir_obj.is_dir(): # Check if it's actually a directory
                logger.warning(f"Approved path is not a directory or not found: {dir_path}")
                continue
                
            logger.info(f"Scanning approved directory: {dir_path}")
            for root, _, files in os.walk(dir_obj):
                for file in files:
                    if file.startswith('v_') and file.endswith('.md'):
                        file_path = Path(root) / file
                        await self.process_document(str(file_path), file)
                        
    async def get_approved_directories(self):
        """Get list of approved directories for scanning."""
        try:
            # Check if table exists
            exists = await self.conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'approved_scan_directories'
                )
            """)
            
            if not exists:
                logger.warning("Approved directories table doesn't exist. Run directory_approval.py --setup")
                return []
            
            # Get active approved directories
            records = await self.conn.fetch("""
                SELECT directory_path
                FROM approved_scan_directories
                WHERE active = true
            """)
            
            return [r['directory_path'] for r in records]
        except Exception as e:
            logger.error(f"Error getting approved directories: {e}")
            return []
    
    async def process_document(self, file_path, filename):
        """Process a document and update the registry."""
        # Calculate basic document metadata
        try:
            content = Path(file_path).read_text()
            word_count = len(content.split())
            char_count = len(content)
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            word_count = None
            char_count = None
        
        # Determine document type based on patterns
        doc_type = self._determine_document_type(filename, file_path)
        
        # Determine architectural layer based on filename and path
        layer = self._determine_architectural_layer(filename, file_path)
        
        # Extract key concepts (simple implementation)
        key_concepts = self._extract_key_concepts(content) if content else None
        
        # Update the registry
        await self._update_registry({
            "title": filename,
            "file_path": file_path,
            "document_type": doc_type,
            "architectural_layer": layer,
            "word_count": word_count,
            "character_count": char_count,
            "key_concepts": key_concepts,
            "primary_purpose": "documentation",
            # embedding_status and needs_update will be determined in _update_registry
            "last_seen_at": datetime.now(timezone.utc), # Renamed from last_checked and made timezone aware
            "file_hash": self._calculate_file_hash(file_path), # Added file_hash
        })
    
    async def _update_registry(self, doc):
        """Add or update a document in the registry."""
        existing_record = await self.conn.fetchrow(
            "SELECT id, file_hash as old_file_hash, embedding_status as old_embedding_status, needs_update as old_needs_update FROM document_registry WHERE title = $1",
            doc["title"]
        )

        current_embedding_status = 'not_applicable'
        current_needs_update = False

        is_v_prefixed = doc["title"].startswith("v_")

        if existing_record:
            if is_v_prefixed:
                if existing_record['old_file_hash'] != doc.get("file_hash"):
                    current_embedding_status = 'queue'
                    current_needs_update = True
                    logger.info(f"Content changed for {doc['title']}. Marked for re-vectorization.")
                else:
                    current_embedding_status = existing_record['old_embedding_status'] # Preserve existing status
                    current_needs_update = existing_record['old_needs_update'] # Preserve existing flag
                    logger.info(f"Content unchanged for {doc['title']}. Status preserved.")
            # If not v_prefixed, it remains 'not_applicable' and needs_update False by default

            await self.conn.execute(
                """
                UPDATE document_registry
                SET 
                    file_path = $1, document_type = $2, architectural_layer = $3,
                    word_count = $4, character_count = $5, key_concepts = $6,
                    primary_purpose = $7, embedding_status = $8, last_seen_at = $9,
                    file_hash = $10, needs_update = $11
                WHERE id = $12
                """,
                doc["file_path"], doc["document_type"], doc["architectural_layer"],
                doc["word_count"], doc["character_count"], doc["key_concepts"],
                doc["primary_purpose"], current_embedding_status, doc["last_seen_at"],
                doc.get("file_hash"), current_needs_update,
                existing_record['id']
            )
            logger.info(f"Updated document in registry: {doc['title']}")
        else:
            if is_v_prefixed:
                current_embedding_status = 'queue'
                current_needs_update = False # New files are queued but don't 'need update' yet
            
            await self.conn.execute(
                """
                INSERT INTO document_registry (
                    title, file_path, document_type, architectural_layer, 
                    word_count, character_count, key_concepts, primary_purpose, 
                    embedding_status, last_seen_at, file_hash, needs_update, last_embedded_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NULL)
                """,
                doc["title"], doc["file_path"], doc["document_type"], doc["architectural_layer"],
                doc["word_count"], doc["character_count"], doc["key_concepts"],
                doc["primary_purpose"], current_embedding_status, doc["last_seen_at"],
                doc.get("file_hash"), current_needs_update
            )
            logger.info(f"Added document to registry: {doc['title']}")
    
    def _calculate_file_hash(self, file_path_str):
        """Calculate SHA256 hash of a file."""
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks
        sha256 = hashlib.sha256()
        try:
            with open(file_path_str, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha256.update(data)
            return sha256.hexdigest()
        except FileNotFoundError:
            logger.warning(f"File not found for hashing: {file_path_str}")
            return None
        except Exception as e:
            logger.error(f"Error hashing file {file_path_str}: {e}")
            return None
    

    
    def _determine_document_type(self, filename, path):
        """Determine document type based on filename and path patterns."""
        lowercase_name = filename.lower()
        lowercase_path = path.lower()
        
        # Document type mapping based on location and filename patterns
        doc_type_patterns = {
            "standard": ["README", "overview"],
            "pattern": ["pattern", "convention"],
            "anti-pattern": ["anti-pattern", "pitfall", "avoid"],
            "reference": ["reference", "guide", "manual"],
            "implementation": ["implementation", "how-to"],
        }
        
        for doc_type, patterns in doc_type_patterns.items():
            for pattern in patterns:
                if pattern.lower() in lowercase_name or pattern.lower() in lowercase_path:
                    return doc_type
        
        # Default type
        return "documentation"
    
    def _determine_architectural_layer(self, filename, path):
        """Determine architectural layer based on filename and path patterns."""
        lowercase_name = filename.lower()
        lowercase_path = path.lower()
        
        # Architectural layer mapping based on filenames and paths
        layer_patterns = {
            1: ["layer1", "models", "enums"],
            2: ["layer2", "schemas", "data-access"],
            3: ["layer3", "routers", "business-logic"],
            4: ["layer4", "api", "services"],
            5: ["layer5", "config", "vector"],
            6: ["layer6", "ui", "frontend"],
            7: ["layer7", "testing", "tests"],
        }
        
        for layer, patterns in layer_patterns.items():
            for pattern in patterns:
                if pattern.lower() in lowercase_name or pattern.lower() in lowercase_path:
                    return layer
        
        # Try to extract layer from numeric pattern
        import re
        layer_match = re.search(r'layer[-_]?(\d)', lowercase_path)
        if layer_match:
            try:
                return int(layer_match.group(1))
            except ValueError:
                pass
        
        # Default - unknown layer
        return None
    
    def _extract_key_concepts(self, content, max_concepts=5):
        """Extract key concepts from document content (simple implementation)."""
        if not content:
            return None
            
        # This is a very simple implementation that just looks for capitalized phrases
        # In a production system, you'd use NLP techniques like named entity recognition,
        # keyword extraction, or topic modeling
        import re
        
        # Find capitalized phrases (potential key concepts)
        capitalized_phrases = re.findall(r'\b[A-Z][a-zA-Z0-9]*([ -][A-Z][a-zA-Z0-9]*)+\b', content)
        
        # Get most frequent capitalized phrases
        if capitalized_phrases:
            from collections import Counter
            counts = Counter(capitalized_phrases)
            key_concepts = [concept for concept, _ in counts.most_common(max_concepts)]
            return key_concepts
        
        return None

    async def mark_file_for_vectorization(self, file_path_str):
        """Mark a document for vectorization by adding v_ prefix and adding/updating minimal registry entry."""
        if not self.conn:
            logger.error("Database connection not available for marking file.")
            # Attempt to gracefully handle or raise an error if conn is essential for all ops
            # For now, let's log and return, assuming main will handle connection setup.
            print("Error: Database connection is required for marking. Please ensure the script is run in a mode that establishes a DB connection for this operation.")
            return

        file_path_obj = Path(file_path_str)
        
        if not file_path_obj.exists() or not file_path_obj.is_file():
            logger.error(f"File not found or not a file: {file_path_str}")
            return

        original_filename = file_path_obj.name
        target_filename = original_filename
        target_file_path_str = str(file_path_obj)

        if not original_filename.startswith("v_"):
            target_filename = f"v_{original_filename}"
            target_file_path_obj = file_path_obj.with_name(target_filename)
            target_file_path_str = str(target_file_path_obj)
            try:
                os.rename(file_path_obj, target_file_path_obj)
                logger.info(f"Marked file: {original_filename} -> {target_filename}")
            except OSError as e:
                logger.error(f"Error renaming file {file_path_str} to {target_filename}: {e}")
                return
        else:
            logger.info(f"File {original_filename} is already prefixed with 'v_'. Ensuring registry entry is minimal and up-to-date.")

        # Prepare minimal document data for the registry
        # For a simple mark operation, we might not calculate all details like hash immediately
        # The full scan will populate them. Or, we can choose to calculate hash here too.
        # For now, keeping it minimal as per original intent of --mark.
        doc_for_mark = {
            "title": target_filename,
            "file_path": target_file_path_str,
            "embedding_status": "queue", # Marked files are queued for vectorization
            "needs_update": False, # It's newly marked, not needing an update yet
            "last_seen_at": datetime.now(timezone.utc),
            "file_hash": self._calculate_file_hash(target_file_path_str), # Calculate hash on mark
            "document_type": None, # To be filled by full scan
            "architectural_layer": None, # To be filled by full scan
            "word_count": None, # To be filled by full scan
            "character_count": None, # To be filled by full scan
            "key_concepts": None, # To be filled by full scan
            "primary_purpose": "documentation"
        }
        
        await self._update_registry(doc_for_mark)
        logger.info(f"Ensured minimal registry entry for {target_filename} with embedding_status='queue'.")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manage document registry for ScraperSky vector database"
    )
    parser.add_argument('--scan', action='store_true', help='Scan filesystem for documents (uses approved directories)')
    parser.add_argument('--mark', help='Mark a document for vectorization by adding v_ prefix and making a minimal registry entry')

    args = parser.parse_args()

    if not args.scan and not args.mark:
        parser.print_help()
        return

    conn = None  # Initialize conn to None for the finally block
    try:
        # Connect to the database if either scan or mark is requested
        # Setting statement_cache_size=0 to fix pgbouncer compatibility issue
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        manager = DocumentRegistryManager(conn)

        if args.mark:
            mark_file_path = args.mark
            logger.info(f"Attempting to mark file: {mark_file_path}")
            await manager.mark_file_for_vectorization(mark_file_path)
            # Optionally, provide feedback after marking, e.g., a success message if not logged in method

        if args.scan:
            logger.info("Starting filesystem scan for v_ documents in approved directories...")
            await manager.scan_filesystem()
            logger.info(f"Scan complete. Registry updated.")
            
    except Exception as e:
        logger.error(f"An error occurred during main execution: {e}", exc_info=True)
    finally:
        if conn is not None:
            await conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
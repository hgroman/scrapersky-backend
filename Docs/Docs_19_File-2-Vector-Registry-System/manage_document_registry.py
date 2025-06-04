#!/usr/bin/env python3
"""
Document Registry Management Script

This script manages the enhanced document registry for ScraperSky's vector database system.
It identifies files with the `v_` prefix, adds them to the document registry, syncs with
"""

import os
import sys
import re
import asyncio
import asyncpg
import argparse
import logging
from datetime import datetime, timedelta
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

    async def scan_filesystem(self, approved_only=True):
        """Scan the filesystem for documents with v_ prefix.
        
        Args:
            approved_only: If True, only scan directories that have been approved
        """
        # Get approved directories if needed
        approved_dirs = []
        if approved_only:
            approved_dirs = await self.get_approved_directories()
            if not approved_dirs:
                logger.warning("No approved directories found. Use directory_approval.py to approve directories.")
                return
        
        # Find all files with v_ prefix in approved directories or all Docs directory
        base_path = Path(os.getcwd())
        
        if approved_only:
            # Only scan approved directories
            for dir_path in approved_dirs:
                dir_obj = Path(dir_path)
                if not dir_obj.exists():
                    logger.warning(f"Approved directory not found: {dir_path}")
                    continue
                    
                logger.info(f"Scanning approved directory: {dir_path}")
                for root, _, files in os.walk(dir_obj):
                    for file in files:
                        if file.startswith('v_') and file.endswith('.md'):
                            file_path = Path(root) / file
                            await self.process_document(str(file_path), file)
        else:
            # Scan entire Docs directory
            docs_dir = base_path / 'Docs'
            if not docs_dir.exists():
                logger.error(f"Docs directory not found at {docs_dir}")
                return
                
            for root, _, files in os.walk(docs_dir):
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
            "should_be_vectorized": filename.startswith("v_"),
            "document_type": doc_type,
            "architectural_layer": layer,
            "word_count": word_count,
            "character_count": char_count,
            "key_concepts": key_concepts,
            "primary_purpose": "documentation",
            "embedding_status": "pending" if filename.startswith("v_") else "not_applicable",
            "last_checked": datetime.now(),
        })
    
    async def _update_registry(self, doc):
        """Add or update a document in the registry."""
        # Check if document already exists in registry
        existing = await self.conn.fetchrow(
            "SELECT id FROM document_registry WHERE title = $1",
            doc["title"]
        )
        
        if existing:
            # Update existing document
            await self.conn.execute(
                """
                UPDATE document_registry
                SET 
                    file_path = $1,
                    should_be_vectorized = $2,
                    document_type = $3,
                    architectural_layer = $4,
                    word_count = $5,
                    character_count = $6,
                    key_concepts = $7,
                    primary_purpose = $8,
                    embedding_status = $9,
                    last_checked = $10
                WHERE title = $11
                """,
                doc["file_path"],
                doc["should_be_vectorized"],
                doc["document_type"],
                doc["architectural_layer"],
                doc["word_count"],
                doc["character_count"],
                doc["key_concepts"],
                doc["primary_purpose"],
                doc["embedding_status"],
                doc["last_checked"],
                doc["title"]
            )
            logger.info(f"Updated document in registry: {doc['title']}")
        else:
            # Insert new document
            await self.conn.execute(
                """
                INSERT INTO document_registry (
                    title, file_path, should_be_vectorized, document_type,
                    architectural_layer, word_count, character_count, key_concepts,
                    primary_purpose, embedding_status, last_checked
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                doc["title"],
                doc["file_path"],
                doc["should_be_vectorized"],
                doc["document_type"],
                doc["architectural_layer"],
                doc["word_count"],
                doc["character_count"],
                doc["key_concepts"],
                doc["primary_purpose"],
                doc["embedding_status"],
                doc["last_checked"]
            )
            logger.info(f"Added document to registry: {doc['title']}")
    
    async def sync_registry_status(self):
        """Sync the document registry with the project_docs table."""
        logger.info("Syncing document registry with project_docs table...")
        
        # Call the database function to sync registry
        await self.conn.execute("SELECT sync_registry_status()")
        
        # Get summary after sync
        summary = await self.conn.fetchrow("SELECT * FROM get_vectorization_summary()")
        
        logger.info(f"Sync complete. Summary: {summary}")
        return summary
    
    async def generate_report(self):
        """Generate document status report."""
        logger.info("Generating document status report...")
        
        # Get vectorization summary
        summary = await self.conn.fetchrow("""SELECT * FROM get_vectorization_summary()""")
        
        # Get document status by architectural layer
        layers = await self.conn.fetch("""
            SELECT 
              COALESCE(architectural_layer, 0) as layer,
              COUNT(*) as total,
              SUM(CASE WHEN should_be_vectorized THEN 1 ELSE 0 END) as should_be_vectorized,
              SUM(CASE WHEN is_vectorized THEN 1 ELSE 0 END) as is_vectorized
            FROM document_registry
            GROUP BY architectural_layer
            ORDER BY architectural_layer
        """)
        
        # Get pending vectorization
        pending = await self.conn.fetch("""
            SELECT title, file_path, architectural_layer
            FROM document_registry
            WHERE should_be_vectorized = true AND is_vectorized = false
            ORDER BY architectural_layer, title
        """)
        
        # Get approved directories
        approved_dirs = await self.get_approved_directories()
        
        # Generate markdown report
        report_path = "Docs/Docs_18_Vector_Operations/Registry/document_status_report.md"
        abs_report_path = os.path.abspath(report_path)
        
        os.makedirs(os.path.dirname(abs_report_path), exist_ok=True)
        with open(abs_report_path, 'w') as f:
            f.write("# Document Registry Status Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Documents:** {summary['total_documents']}\n")
            f.write(f"- **Should Be Vectorized:** {summary['should_be_vectorized']}\n")
            f.write(f"- **Currently Vectorized:** {summary['is_vectorized']}\n")
            f.write(f"- **Pending Vectorization:** {summary['pending_vectorization']}\n")
            f.write(f"- **Completion:** {summary['percent_complete']:.2f}%\n\n")
            
            # Add approved directories section
            f.write("## Approved Scan Directories\n\n")
            if approved_dirs:
                for dir_path in approved_dirs:
                    f.write(f"- `{dir_path}`\n")
            else:
                f.write("*No directories approved for scanning yet.*\n")
                f.write("*Use `directory_approval.py --approve <directory>` to approve directories.*\n")
            f.write("\n")
            
            f.write("## Status By Architectural Layer\n\n")
            f.write("| Layer | Total | Should Be Vectorized | Is Vectorized | Completion |\n")
            f.write("|-------|-------|---------------------|--------------|-----------|\n")
            
            for layer in layers:
                layer_num = layer['layer']
                layer_name = "Unknown" if layer_num == 0 else f"Layer {layer_num}"
                should_be = layer['should_be_vectorized']
                is_vectorized = layer['is_vectorized']
                completion = "N/A"
                if should_be > 0:
                    completion = f"{(is_vectorized / should_be * 100):.2f}%"
                
                f.write(f"| {layer_name} | {layer['total']} | {should_be} | {is_vectorized} | {completion} |\n")
            
            if pending:
                f.write("\n## Pending Vectorization\n\n")
                f.write("The following documents should be vectorized but are not yet in the vector database:\n\n")
                f.write("| Document | Path | Layer |\n")
                f.write("|----------|------|-------|\n")
                
                for doc in pending:
                    layer = doc['architectural_layer'] if doc['architectural_layer'] else "Unknown"
                    f.write(f"| {doc['title']} | {doc['file_path']} | {layer} |\n")
            
            f.write("\n## Next Actions\n\n")
            if not approved_dirs:
                f.write("1. Approve directories for scanning using `directory_approval.py --approve <directory>`\n")
                f.write("2. Run scanning with approved directories `manage_document_registry.py --scan --approved-only`\n")
            elif summary['pending_vectorization'] > 0:
                f.write("1. Vectorize pending documents\n")
                f.write("2. Run sync to update registry status\n")
                f.write("3. Review documents without architectural layer assignment\n")
            else:
                f.write("1. Review additional directories for vectorization candidates\n")
                f.write("2. Review documents without architectural layer assignment\n")
        
        logger.info(f"Report generated and saved to {abs_report_path}")
        return '\n'.join(report)
    
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
    
    async def create_tables(self):
        """Create tables if they don't exist."""
        try:
            # Check if table exists
            exists = await self.conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'document_registry'
                )
            """)
            
            if not exists:
                # Create table
                await self.conn.execute("""
                    CREATE TABLE document_registry (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        file_path VARCHAR(255) NOT NULL,
                        should_be_vectorized BOOLEAN NOT NULL,
                        document_type VARCHAR(255),
                        architectural_layer INTEGER,
                        word_count INTEGER,
                        character_count INTEGER,
                        key_concepts TEXT[],
                        primary_purpose VARCHAR(255),
                        embedding_status VARCHAR(255),
                        last_checked TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("Created document_registry table")
            
            # Check if approved directories table exists
            exists = await self.conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'approved_scan_directories'
                )
            """)
            
            if not exists:
                # Create table
                await self.conn.execute("""
                    CREATE TABLE approved_scan_directories (
                        id SERIAL PRIMARY KEY,
                        directory_path VARCHAR(255) NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE
                    )
                """)
                logger.info("Created approved_scan_directories table")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manage document registry for ScraperSky vector database"
    )
    parser.add_argument('--scan', action='store_true', help='Scan filesystem for documents')
    parser.add_argument('--approved-only', action='store_true', help='Only scan approved directories')
    parser.add_argument('--sync', action='store_true', help='Sync document registry with project_docs table')
    parser.add_argument('--report', action='store_true', help='Generate document status report')
    parser.add_argument('--mark', help='Mark a document for vectorization by adding v_ prefix')
    
    args = parser.parse_args()
    
    # Handle document marking (doesn't need DB connection)
    if args.mark:
        mark_file_path = args.mark
        if not os.path.exists(mark_file_path):
            logger.error(f"File not found: {mark_file_path}")
            return
            
        filename = os.path.basename(mark_file_path)
        if filename.startswith('v_'):
            logger.info(f"File already marked for vectorization: {filename}")
            return
            
        directory = os.path.dirname(mark_file_path)
        new_path = os.path.join(directory, f"v_{filename}")
        os.rename(mark_file_path, new_path)
        logger.info(f"Marked file for vectorization: {filename} -> v_{filename}")
        return
    
    # Connect to the database
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Create manager
        manager = DocumentRegistryManager(conn)
        
        # Create tables if they don't exist
        await manager.create_tables()
        
        # Process command line arguments
        if args.scan:
            await manager.scan_filesystem(approved_only=args.approved_only)
            
        if args.sync:
            await manager.sync_registry_status()
            
        if args.report:
            await manager.generate_report()
            
        # If no arguments, show help
        if not (args.scan or args.sync or args.report or args.mark):
            parser.print_help()
            
    finally:
        if 'conn' in locals() and conn is not None:
            await conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())

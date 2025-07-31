#!/usr/bin/env python3
"""
File Registry Generator for ScraperSky
======================================

This script exports the Supabase file_audit registry to a YAML file
for version control and offline reference. It can generate different
report types based on command-line arguments.

Usage: python generate_file_registry.py [--by-layer | --by-workflow | --technical-debt | --audit-progress]
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any
import asyncpg
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Database configuration (uses environment variables)
DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-0-us-west-1.pooler.supabase.com")
DB_PORT = os.getenv("SUPABASE_DB_PORT", "6543")
DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
DB_USER = os.getenv(
    "SUPABASE_DB_USER", "postgres.ddfldwzhdhhzhxywqnyz"
)  # Format: postgres.[project-ref]
DB_PASSWORD = os.getenv(
    "SUPABASE_DB_PASSWORD", ""
)  # Set in environment variable for security

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = PROJECT_ROOT / "registry"

# Ensure registry directory exists
REGISTRY_DIR.mkdir(exist_ok=True)


async def get_database_connection():
    """Establish a connection to the Supabase database."""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl="require",
            server_settings={
                "raw_sql": "true",
                "no_prepare": "true",
                "statement_cache_size": "0",
            },
        )
        logger.info("Connected to database successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)


async def get_complete_registry() -> List[Dict[str, Any]]:
    """Get the complete file registry from the database."""
    conn = await get_database_connection()

    # Query all files from the file_audit table
    rows = await conn.fetch("""
        SELECT
            id,
            file_number,
            file_path,
            file_name,
            layer_number,
            layer_name,
            status,
            workflows,
            has_technical_debt,
            technical_debt,
            jira_tickets,
            audit_status,
            audit_date,
            audited_by,
            notes,
            created_at,
            updated_at
        FROM file_audit
        ORDER BY file_number
    """)

    # Convert to list of dictionaries
    result = [dict(row) for row in rows]
    logger.info(f"Retrieved {len(result)} files from database")

    await conn.close()
    return result


async def generate_by_layer_report() -> Dict[str, Any]:
    """Generate a report of files organized by layer."""
    conn = await get_database_connection()

    # Query layer statistics
    layer_stats = await conn.fetch("""
        SELECT
            layer_number,
            layer_name,
            COUNT(*) as file_count,
            COUNT(CASE WHEN has_technical_debt = true THEN 1 END) as debt_count,
            ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as debt_percentage
        FROM file_audit
        GROUP BY layer_number, layer_name
        ORDER BY layer_number
    """)

    # Query files by layer
    files_by_layer = {}
    for layer in layer_stats:
        layer_num = layer["layer_number"]
        layer_files = await conn.fetch(
            """
            SELECT
                file_number,
                file_path,
                file_name,
                status,
                workflows,
                has_technical_debt,
                audit_status
            FROM file_audit
            WHERE layer_number = $1
            ORDER BY file_number
        """,
            layer_num,
        )

        files_by_layer[f"layer_{layer_num}"] = [dict(f) for f in layer_files]

    # Build the report
    report = {
        "generated_at": datetime.now().isoformat(),
        "report_type": "files_by_layer",
        "summary": [dict(s) for s in layer_stats],
        "layers": files_by_layer,
    }

    await conn.close()
    return report


async def generate_by_workflow_report() -> Dict[str, Any]:
    """Generate a report of files organized by workflow."""
    conn = await get_database_connection()

    # Query workflow statistics
    workflow_stats = await conn.fetch("""
        SELECT
            workflow,
            COUNT(*) as file_count
        FROM (
            SELECT unnest(workflows) as workflow
            FROM file_audit
        ) as workflow_files
        GROUP BY workflow
        ORDER BY workflow
    """)

    # Get all workflows
    workflows = [w["workflow"] for w in workflow_stats]

    # Query files by workflow
    files_by_workflow = {}
    for workflow in workflows:
        wf_files = await conn.fetch(
            """
            SELECT
                file_number,
                file_path,
                file_name,
                layer_number,
                layer_name,
                status,
                has_technical_debt,
                audit_status
            FROM file_audit
            WHERE $1 = ANY(workflows)
            ORDER BY layer_number, file_number
        """,
            workflow,
        )

        files_by_workflow[workflow] = [dict(f) for f in wf_files]

    # Build the report
    report = {
        "generated_at": datetime.now().isoformat(),
        "report_type": "files_by_workflow",
        "summary": [dict(s) for s in workflow_stats],
        "workflows": files_by_workflow,
    }

    await conn.close()
    return report


async def generate_technical_debt_report() -> Dict[str, Any]:
    """Generate a report of files with technical debt."""
    conn = await get_database_connection()

    # Query technical debt statistics
    debt_stats = await conn.fetch("""
        SELECT
            COUNT(*) as total_files,
            COUNT(CASE WHEN has_technical_debt = true THEN 1 END) as debt_files,
            ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as debt_percentage
        FROM file_audit
    """)

    # Query files with technical debt
    debt_files = await conn.fetch("""
        SELECT
            file_number,
            file_path,
            file_name,
            layer_number,
            layer_name,
            status,
            workflows,
            technical_debt,
            jira_tickets,
            audit_status
        FROM file_audit
        WHERE has_technical_debt = true
        ORDER BY layer_number, file_number
    """)

    # Group by layer
    debt_by_layer = await conn.fetch("""
        SELECT
            layer_number,
            layer_name,
            COUNT(*) as total_files,
            COUNT(CASE WHEN has_technical_debt = true THEN 1 END) as debt_files,
            ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as debt_percentage
        FROM file_audit
        GROUP BY layer_number, layer_name
        ORDER BY layer_number
    """)

    # Build the report
    report = {
        "generated_at": datetime.now().isoformat(),
        "report_type": "technical_debt",
        "summary": dict(debt_stats[0]),
        "debt_by_layer": [dict(l) for l in debt_by_layer],
        "debt_files": [dict(f) for f in debt_files],
    }

    await conn.close()
    return report


async def generate_audit_progress_report() -> Dict[str, Any]:
    """Generate a report on audit progress."""
    conn = await get_database_connection()

    # Query audit progress statistics
    progress_stats = await conn.fetch("""
        SELECT
            audit_status,
            COUNT(*) as file_count,
            ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM file_audit)::numeric * 100, 2) as percentage
        FROM file_audit
        GROUP BY audit_status
        ORDER BY audit_status
    """)

    # Query progress by layer
    progress_by_layer = await conn.fetch("""
        SELECT
            layer_number,
            layer_name,
            COUNT(*) as total_files,
            COUNT(CASE WHEN audit_status = 'NOT_STARTED' THEN 1 END) as not_started,
            COUNT(CASE WHEN audit_status = 'IN_PROGRESS' THEN 1 END) as in_progress,
            COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END) as completed,
            ROUND(COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as completion_percentage
        FROM file_audit
        GROUP BY layer_number, layer_name
        ORDER BY layer_number
    """)

    # Build the report
    report = {
        "generated_at": datetime.now().isoformat(),
        "report_type": "audit_progress",
        "summary": [dict(s) for s in progress_stats],
        "progress_by_layer": [dict(l) for l in progress_by_layer],
    }

    await conn.close()
    return report


async def main():
    """Main function to generate the file registry."""
    parser = argparse.ArgumentParser(
        description="Generate file registry reports from Supabase"
    )
    parser.add_argument(
        "--by-layer", action="store_true", help="Generate files by layer report"
    )
    parser.add_argument(
        "--by-workflow", action="store_true", help="Generate files by workflow report"
    )
    parser.add_argument(
        "--technical-debt", action="store_true", help="Generate technical debt report"
    )
    parser.add_argument(
        "--audit-progress", action="store_true", help="Generate audit progress report"
    )
    parser.add_argument("--all", action="store_true", help="Generate all reports")
    args = parser.parse_args()

    # Default to complete registry if no specific report is requested
    generate_all = args.all or not (
        args.by_layer or args.by_workflow or args.technical_debt or args.audit_progress
    )

    logger.info("Generating file registry exports...")

    # Generate the complete registry
    if generate_all:
        registry = await get_complete_registry()
        with open(REGISTRY_DIR / "file_registry_complete.yaml", "w") as f:
            yaml.dump(
                {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "complete_registry",
                    "file_count": len(registry),
                    "files": registry,
                },
                f,
                default_flow_style=False,
                sort_keys=False,
            )
        logger.info(
            f"Complete registry exported to {REGISTRY_DIR / 'file_registry_complete.yaml'}"
        )

    # Generate by layer report
    if generate_all or args.by_layer:
        layer_report = await generate_by_layer_report()
        with open(REGISTRY_DIR / "files_by_layer.yaml", "w") as f:
            yaml.dump(layer_report, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Layer report exported to {REGISTRY_DIR / 'files_by_layer.yaml'}")

    # Generate by workflow report
    if generate_all or args.by_workflow:
        workflow_report = await generate_by_workflow_report()
        with open(REGISTRY_DIR / "files_by_workflow.yaml", "w") as f:
            yaml.dump(workflow_report, f, default_flow_style=False, sort_keys=False)
        logger.info(
            f"Workflow report exported to {REGISTRY_DIR / 'files_by_workflow.yaml'}"
        )

    # Generate technical debt report
    if generate_all or args.technical_debt:
        debt_report = await generate_technical_debt_report()
        with open(REGISTRY_DIR / "technical_debt.yaml", "w") as f:
            yaml.dump(debt_report, f, default_flow_style=False, sort_keys=False)
        logger.info(
            f"Technical debt report exported to {REGISTRY_DIR / 'technical_debt.yaml'}"
        )

    # Generate audit progress report
    if generate_all or args.audit_progress:
        progress_report = await generate_audit_progress_report()
        with open(REGISTRY_DIR / "audit_progress.yaml", "w") as f:
            yaml.dump(progress_report, f, default_flow_style=False, sort_keys=False)
        logger.info(
            f"Audit progress report exported to {REGISTRY_DIR / 'audit_progress.yaml'}"
        )

    logger.info("All requested reports generated successfully!")


if __name__ == "__main__":
    asyncio.run(main())

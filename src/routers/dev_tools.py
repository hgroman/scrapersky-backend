import asyncio
import inspect
import logging
import os
import pathlib
import time
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db_session
from src.models.domain import Domain
from src.services.sitemap_import_service import SitemapImportService
from src.services.website_scan_service import WebsiteScanService

from ..auth.jwt_auth import get_current_user

# --- Corrected Imports --- #
from ..config.settings import settings  # Import settings
from ..db.sitemap_handler import SitemapDBHandler

# Import the shared scheduler instance
from ..scheduler_instance import scheduler

# RBAC imports removed
# from ..utils.permissions import require_permission, require_feature_enabled, require_role_level
# from ..constants.rbac import ROLE_HIERARCHY
from ..services.core.user_context_service import user_context_service

# Replace the old import with SQLAlchemy session
from ..session.async_session import get_session_dependency

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v3/dev-tools",
    tags=["dev-tools"],
    dependencies=[Depends(get_current_user)],
)

# Get the absolute path to the static directory using pathlib.Path
STATIC_DIR = pathlib.Path(__file__).parent.parent.parent / "static"

# Container status tracking
container_operations = {}


# Define require_dev_mode dependency function BEFORE its first use
async def require_dev_mode():
    # This function now only checks the environment setting.
    # Authentication is handled by the router's dependency on get_current_user.
    # Check the correct environment setting name
    if settings.environment.lower() not in ["development", "dev"]:
        raise HTTPException(
            status_code=403, detail="Developer tools require dev mode to be enabled."
        )
    # The rest of the original comments are no longer relevant
    pass


async def run_command(cmd: str) -> Dict[str, Any]:
    """Run a shell command and return its output."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return {
        "exit_code": process.returncode,
        "stdout": stdout.decode() if stdout else "",
        "stderr": stderr.decode() if stderr else "",
    }


@router.post("/container/rebuild")
async def rebuild_container() -> Dict[str, Any]:
    """Rebuild the Docker container without cache."""
    operation_id = str(time.time())
    container_operations[operation_id] = {
        "type": "rebuild",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "steps": [],
    }

    try:
        # Stop containers
        container_operations[operation_id]["steps"].append("Stopping containers...")
        result = await run_command("docker-compose down")
        if result["exit_code"] != 0:
            raise HTTPException(
                status_code=500, detail=f"Failed to stop containers: {result['stderr']}"
            )

        # Rebuild without cache
        container_operations[operation_id]["steps"].append(
            "Rebuilding without cache..."
        )
        result = await run_command("docker-compose build --no-cache")
        if result["exit_code"] != 0:
            raise HTTPException(
                status_code=500, detail=f"Failed to rebuild: {result['stderr']}"
            )

        # Start containers
        container_operations[operation_id]["steps"].append("Starting containers...")
        result = await run_command("docker-compose up -d")
        if result["exit_code"] != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start containers: {result['stderr']}",
            )

        # Wait for health check
        container_operations[operation_id]["steps"].append(
            "Waiting for health check..."
        )
        await asyncio.sleep(5)  # Give the container time to start

        # Check container health
        result = await run_command("docker-compose ps")
        if "Up" not in result["stdout"]:
            raise HTTPException(
                status_code=500, detail="Container failed to start properly"
            )

        container_operations[operation_id]["status"] = "complete"
        container_operations[operation_id]["completed_at"] = (
            datetime.utcnow().isoformat()
        )

        return {
            "status": "success",
            "operation_id": operation_id,
            "message": "Container rebuilt successfully",
        }

    except Exception as e:
        container_operations[operation_id]["status"] = "error"
        container_operations[operation_id]["error"] = str(e)
        container_operations[operation_id]["completed_at"] = (
            datetime.utcnow().isoformat()
        )
        raise


@router.post("/container/restart")
async def restart_container() -> Dict[str, Any]:
    """Restart the Docker container."""
    operation_id = str(time.time())
    container_operations[operation_id] = {
        "type": "restart",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "steps": [],
    }

    try:
        # Restart containers
        container_operations[operation_id]["steps"].append("Restarting containers...")
        result = await run_command("docker-compose restart")
        if result["exit_code"] != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart containers: {result['stderr']}",
            )

        # Wait for health check
        container_operations[operation_id]["steps"].append(
            "Waiting for health check..."
        )
        await asyncio.sleep(5)  # Give the container time to start

        # Check container health
        result = await run_command("docker-compose ps")
        if "Up" not in result["stdout"]:
            raise HTTPException(
                status_code=500, detail="Container failed to start properly"
            )

        container_operations[operation_id]["status"] = "complete"
        container_operations[operation_id]["completed_at"] = (
            datetime.utcnow().isoformat()
        )

        return {
            "status": "success",
            "operation_id": operation_id,
            "message": "Container restarted successfully",
        }

    except Exception as e:
        container_operations[operation_id]["status"] = "error"
        container_operations[operation_id]["error"] = str(e)
        container_operations[operation_id]["completed_at"] = (
            datetime.utcnow().isoformat()
        )
        raise


@router.get("/container/health")
async def check_container_health() -> Dict[str, Any]:
    """Check the health of the Docker container."""
    try:
        # Get container status
        result = await run_command("docker-compose ps")

        # Get container logs (last 10 lines)
        logs = await run_command("docker-compose logs --tail=10")

        # Get container stats
        stats = await run_command(
            "docker stats --no-stream --format '{{.Container}}: CPU: {{.CPUPerc}}, Memory: {{.MemUsage}}'"
        )

        return {
            "status": "Up" if "Up" in result["stdout"] else "Down",
            "details": result["stdout"],
            "logs": logs["stdout"],
            "stats": stats["stdout"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/container/status")
async def get_container_status(operation_id: str) -> Dict[str, Any]:
    """Get the status of a container operation."""
    if operation_id not in container_operations:
        raise HTTPException(status_code=404, detail="Operation not found")

    return container_operations[operation_id]


@router.get("/server/status")
async def get_server_status(request: Request) -> Dict[str, Any]:
    """Get FastAPI server status and configuration."""
    try:
        # Get server process info
        result = await run_command("ps aux | grep uvicorn")

        # Get environment variables
        env_vars = {
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
            "HOST": os.getenv("HOST", "0.0.0.0"),
            "PORT": os.getenv("PORT", "8000"),
            "WORKERS": os.getenv("WORKERS", "4"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        }

        # Get routes info
        routes_info = []
        for route in request.app.routes:
            if hasattr(route, "endpoint"):
                routes_info.append(
                    {
                        "path": route.path,
                        "methods": list(route.methods)
                        if hasattr(route, "methods")
                        else [],
                        "name": route.name,
                    }
                )

        return {
            "status": "running",
            "process_info": result["stdout"],
            "environment": env_vars,
            "routes_count": len(routes_info),
            "routes": routes_info[:10],  # Show first 10 routes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_logs(
    level: str = Query("INFO", regex="^(INFO|ERROR|DEBUG|WARNING)$"),
    lines: int = Query(50, ge=1, le=1000),
) -> Dict[str, Any]:
    """Get server logs filtered by level."""
    try:
        # Get container logs
        result = await run_command(f"docker-compose logs --tail={lines}")

        # Filter logs by level
        logs = result["stdout"].split("\n")
        filtered_logs = [log for log in logs if level in log]

        return {
            "level": level,
            "total_lines": len(filtered_logs),
            "logs": "\n".join(filtered_logs),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_class=HTMLResponse)
async def get_dev_tools_page():
    """Serve the dev tools HTML page"""
    try:
        with open(STATIC_DIR / "dev-tools.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dev tools page not found")


@router.get("/schema")
async def get_database_schema(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get detailed database schema information including:
    - Table structures
    - Column definitions
    - Foreign key relationships
    - Routes that use each table
    """
    try:
        # Get tenant ID from user context
        tenant_id = user_context_service.get_tenant_id(current_user)

        # RBAC checks removed
        logger.info(
            f"RBAC removed: Using JWT validation only for get_database_schema endpoint, tenant: {tenant_id}"
        )

        # Router owns transaction boundaries - wrap DB operations in transaction
        try:
            # Read-only transaction with session.begin()
            async with session.begin():
                # Get table information
                tables = []

                # Query to get table schema
                schema_query = """
                    SELECT
                        t.table_name,
                        array_agg(
                            json_build_object(
                                'column_name', c.column_name,
                                'data_type', c.data_type,
                                'is_nullable', c.is_nullable,
                                'column_default', c.column_default
                            )
                        ) as columns,
                        obj_description(quote_ident(t.table_name)::regclass::oid) as description
                    FROM information_schema.tables t
                    JOIN information_schema.columns c ON c.table_name = t.table_name
                    WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                    GROUP BY t.table_name;
                """

                # Execute query
                result = await session.execute(text(schema_query))

                # Process results
                for row in result:
                    row_dict = dict(row) if row else {}
                    table_info = {
                        "name": row_dict.get("table_name", ""),
                        "description": row_dict.get("description", ""),
                        "columns": row_dict.get("columns", 0),
                        "used_by_routes": await get_routes_using_table(
                            row_dict.get("table_name", ""), session
                        ),
                    }
                    tables.append(table_info)

            # Return after transaction is complete
            return {"status": "ok", "tables": tables}
        except HTTPException:
            # Propagate HTTP exceptions directly
            raise
        except Exception as e:
            # Handle database errors
            logger.error(f"Database error getting schema information: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        # Propagate HTTP exceptions from RBAC checks
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error in get_database_schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/routes")
async def get_route_information(request: Request) -> Dict[str, Any]:
    """
    Get detailed information about all API routes including:
    - Path and methods
    - Required parameters
    - Database tables used
    - Authentication requirements
    """
    try:
        routes_info = []

        # Get all routes from the FastAPI app
        for route in request.app.routes:
            if hasattr(route, "endpoint"):
                try:
                    # Get route handler source code
                    handler = route.endpoint
                    source = inspect.getsource(handler)

                    # Extract table names from SQL queries in the source
                    tables_used = extract_tables_from_source(source)

                    # Get required fields from function parameters
                    params = inspect.signature(handler).parameters
                    required_fields = [
                        name
                        for name, param in params.items()
                        if param.default == inspect.Parameter.empty
                        and name not in ["self", "cls"]
                    ]

                    # Safely get description
                    description = "No description"
                    if hasattr(route, "description") and route.description:
                        description = route.description
                    elif hasattr(handler, "__doc__") and handler.__doc__:
                        description = handler.__doc__.strip()

                    route_info = {
                        "path": route.path,
                        "methods": list(route.methods)
                        if hasattr(route, "methods")
                        else [],
                        "description": description,
                        "tables_used": list(tables_used),
                        "required_fields": required_fields,
                        "auth_required": "get_current_user" in source
                        or "verify_token" in source,
                    }
                    routes_info.append(route_info)
                except Exception as route_error:
                    # If we can't analyze a route, include basic info
                    routes_info.append(
                        {
                            "path": route.path,
                            "methods": list(route.methods)
                            if hasattr(route, "methods")
                            else [],
                            "description": "Error analyzing route",
                            "error": str(route_error),
                        }
                    )

        return {"status": "ok", "routes": routes_info}

    except Exception as e:
        logger.error(f"Error getting route information: {str(e)}")
        return {"status": "error", "error": str(e)}


async def get_routes_using_table(table_name: str, session: AsyncSession) -> List[str]:
    """
    Find all routes that use a specific table.

    Args:
        table_name: The table name to find routes for
        session: SQLAlchemy async session

    Returns:
        List of route paths that use the specified table
    """
    routes = []

    # We'll get routes when they're requested through the endpoint
    # This avoids the circular import issue
    return routes


def extract_tables_from_source(source: str) -> set:
    """Extract table names from SQL queries in source code."""
    # Common table names in our application
    common_tables = {
        "jobs",
        "domains",
        "sitemap_files",
        "sitemap_urls",
        "users",
        "roles",
        "permissions",
        "features",
    }

    found_tables = set()

    # Look for table names in FROM and JOIN clauses
    source_lower = source.lower()
    for table in common_tables:
        if f"from {table}" in source_lower or f"join {table}" in source_lower:
            found_tables.add(table)

    return found_tables


@router.get("/system-status")
async def get_system_status(
    request: Request, session: AsyncSession = Depends(get_session_dependency)
) -> Dict[str, Any]:
    """Get the status of all system components"""
    sitemap_handler = SitemapDBHandler()
    current_time = int(time.time())

    try:
        # Test database connection - use the injected session
        db_status = False
        try:
            # Router owns transaction boundaries
            async with session.begin():
                result = await session.execute(text("SELECT 1"))
                row = result.fetchone()
                db_status = row[0] == 1 if row else False
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")

        # Get database info - pass session to sitemap_handler methods
        db_info = {
            "connection": db_status,
            "type": "postgres",
            "host": os.getenv("POSTGRES_HOST", "Not configured"),
            "database": os.getenv("POSTGRES_DB", "Not configured"),
            "tables": await sitemap_handler.get_table_info(session)
            if db_status
            else [],
        }

        # Get environment info
        env_info = {
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
            "POSTGRES_HOST": bool(os.getenv("POSTGRES_HOST")),
            "POSTGRES_DB": bool(os.getenv("POSTGRES_DB")),
            "POSTGRES_USER": bool(os.getenv("POSTGRES_USER")),
            "POSTGRES_PASSWORD": bool(os.getenv("POSTGRES_PASSWORD")),
        }

        # Get routes info
        routes_info = []
        for route in request.app.routes:
            if hasattr(route, "endpoint"):
                routes_info.append(
                    {
                        "path": route.path,
                        "methods": list(route.methods)
                        if hasattr(route, "methods")
                        else [],
                        "name": route.name,
                    }
                )

        return {
            "status": "ok",
            "database": db_info,
            "environment": env_info,
            "api_version": "v1",
            "routes_count": len(routes_info),
            "routes": routes_info[:10],  # Show first 10 routes
            "timestamp": current_time,
        }

    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": current_time}


@router.get("/database/tables")
async def get_database_tables(
    session: AsyncSession = Depends(get_session_dependency),
) -> Dict[str, Any]:
    """Get information about database tables"""
    try:
        sitemap_handler = SitemapDBHandler()

        # Router owns transaction boundaries
        async with session.begin():
            tables = await sitemap_handler.get_table_info(session)

        return {"status": "ok", "tables": tables}
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}")
        return {"status": "error", "error": str(e)}


@router.get("/database/table/{table_name}")
async def get_table_fields(
    table_name: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get fields and sample data for a specific database table
    """
    try:
        # Get tenant ID from user context
        tenant_id = user_context_service.get_tenant_id(current_user)

        # RBAC checks removed
        logger.info(
            f"RBAC removed: Using JWT validation only for get_table_fields endpoint, tenant: {tenant_id}"
        )

        try:
            # Validate table name to prevent SQL injection
            valid_tables = [
                "jobs",
                "domains",
                "sitemap_files",
                "sitemap_urls",
                "profiles",
                "feature_flags",
                "tenant_features",
                "sidebar_features",
                "permissions",
                "roles",
                "role_permissions",
            ]

            if table_name not in valid_tables:
                raise HTTPException(
                    status_code=400, detail=f"Invalid table name: {table_name}"
                )

            # Router owns transaction boundaries
            async with session.begin():
                # Get column information
                column_query = text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = :table_name
                    ORDER BY ordinal_position
                """)
                columns = await session.execute(
                    column_query, {"table_name": table_name}
                )

                # Get sample data (first 10 rows)
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 10")
                sample_data = await session.execute(sample_query)

                # Process results inside transaction
                columns_result = [
                    {
                        "name": dict(col).get("column_name", ""),
                        "type": dict(col).get("data_type", ""),
                        "nullable": dict(col).get("is_nullable", "") == "YES",
                    }
                    for col in columns.fetchall()
                ]

                sample_data_result = [dict(row) for row in sample_data.fetchall()]

            # Return response after transaction completes
            return {
                "status": "ok",
                "table_name": table_name,
                "columns": columns_result,
                "sample_data": sample_data_result,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database error getting table fields: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_table_fields: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/db-tables", response_class=JSONResponse)
async def get_db_tables(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
):
    """
    Get a list of all database tables.
    """
    try:
        # Get tenant ID from user context
        tenant_id = user_context_service.get_tenant_id(current_user)

        # RBAC checks removed
        logger.info(
            f"RBAC removed: Using JWT validation only for get_db_tables endpoint, tenant: {tenant_id}"
        )

        try:
            # Router owns transaction boundaries
            async with session.begin():
                result = await session.execute(
                    text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                )
                tables = [row[0] for row in result.fetchall()]

            # Return after transaction completes
            return {"tables": tables}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database error getting database tables: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_db_tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# SQL statements for sidebar feature setup
ADD_COLUMN_SQL = """
ALTER TABLE sidebar_features ADD COLUMN IF NOT EXISTS group_name TEXT;
"""

DELETE_SQL = """
DELETE FROM sidebar_features;
"""

POPULATE_SQL = """
-- Service Pages (Feature-based)
INSERT INTO sidebar_features (
    sidebar_name, url_path, icon, feature_id, requires_permission, display_order, group_name
) VALUES
    -- Service Pages
    ('LocalMiner', '/localminer/control-center', 'Map',
     (SELECT id FROM feature_flags WHERE name = 'localminer'),
     'view_localminer', 1, 'Services'),

    ('ContentMap', '/contentmap', 'FileSearch',
     (SELECT id FROM feature_flags WHERE name = 'contentmap'),
     'view_contentmap', 2, 'Services'),

    ('FrontendScout', '/domain-staging', 'LayoutGrid',
     (SELECT id FROM feature_flags WHERE name = 'frontendscout'),
     'view_frontendscout', 3, 'Services'),

    ('SiteHarvest', '/siteharvest', 'Network',
     (SELECT id FROM feature_flags WHERE name = 'siteharvest'),
     'view_siteharvest', 4, 'Services'),

    ('EmailHunter', '/emailhunter', 'Mail',
     (SELECT id FROM feature_flags WHERE name = 'emailhunter'),
     'view_emailhunter', 5, 'Services'),

    ('ActionQueue', '/actionqueue', 'ListChecks',
     (SELECT id FROM feature_flags WHERE name = 'actionqueue'),
     'view_actionqueue', 6, 'Services'),

    ('SocialRadar', '/socialradar', 'Radar',
     (SELECT id FROM feature_flags WHERE name = 'socialradar'),
     'view_socialradar', 7, 'Services'),

    ('ContactLaunchpad', '/contact-launchpad', 'Contact',
     (SELECT id FROM feature_flags WHERE name = 'contactlaunchpad'),
     'view_contactlaunchpad', 8, 'Services'),

    -- Administration Pages
    ('Status', '/status', 'Flag',
     NULL, NULL, 9, 'Administration'),

    ('Tasks', '/tasks', 'Activity',
     NULL, 'manage_users', 10, 'Administration'),

    ('Configuration', '/configuration', 'Settings',
     NULL, 'manage_tenants', 11, 'Administration'),

    ('Features', '/features', 'Database',
     NULL, 'manage_tenants', 12, 'Administration'),

    ('Tenants', '/tenants', 'Users',
     NULL, 'manage_tenants', 13, 'Administration'),

    ('SkyLab', '/skylab', 'Bug',
     NULL, 'manage_tenants', 14, 'Administration'),

    -- Other Pages
    ('Dashboard', '/dashboard', 'Home',
     NULL, NULL, 15, 'Other'),

    ('Query', '/query', 'Search',
     NULL, NULL, 16, 'Other'),

    ('Domains View', '/domains-view', 'Globe',
     NULL, NULL, 17, 'Other');
"""

VERIFY_SQL = """
SELECT group_name, COUNT(*) FROM sidebar_features GROUP BY group_name;
"""


@router.post("/setup-sidebar", response_class=JSONResponse)
async def setup_sidebar(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
):
    """
    Set up sidebar features table with grouped items.
    Adds the group_name column and populates with standard data.
    """
    try:
        # Get tenant ID from user context
        tenant_id = user_context_service.get_tenant_id(current_user)

        # RBAC checks removed
        logger.info(
            f"RBAC removed: Using JWT validation only for setup_sidebar endpoint, tenant: {tenant_id}"
        )

        # Router owns transaction boundaries - wrap all DB operations in transaction
        try:
            logger.info(
                "Setting up sidebar features with standardized transaction handling"
            )
            async with session.begin():
                # Step 1: Add group_name column
                logger.info("Adding group_name column...")
                try:
                    await session.execute(text(ADD_COLUMN_SQL))
                    logger.info("Added group_name column")
                except Exception as e:
                    logger.warning(f"Column may already exist: {str(e)}")
                    # No need to rollback, we're in a transaction that will continue

                # Step 2: Delete existing data
                logger.info("Deleting existing sidebar items...")
                await session.execute(text(DELETE_SQL))
                logger.info("Deleted existing sidebar items")

                # Step 3: Add new data
                logger.info("Populating sidebar data...")
                await session.execute(text(POPULATE_SQL))
                logger.info("Added new sidebar items")

                # Step 4: Verify data
                logger.info("Verifying data...")
                result = await session.execute(text(VERIFY_SQL))
                counts = {}
                for row in result.fetchall():
                    group_name = row[0] or "Unknown"
                    count = row[1]
                    counts[group_name] = count

            # Return response after transaction is committed
            return {
                "success": True,
                "message": "Sidebar setup completed successfully",
                "counts": counts,
            }
        except HTTPException:
            # Propagate HTTP exceptions directly
            raise
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Database error setting up sidebar: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        # Propagate HTTP exceptions from RBAC checks
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error in setup_sidebar: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/process-pending-domains")
async def process_pending_domains_endpoint(limit: int = 5):
    """
    Manually trigger processing of pending domains.

    For development and testing purposes only.
    """
    try:
        # fmt: off
        from src.services.domain_scheduler import process_pending_domains  # noqa: E402
        # fmt: on

        await process_pending_domains(limit)
        return JSONResponse(content={"message": "Processing triggered successfully"})
    except Exception as e:
        logger.error(f"Error triggering domain processing: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/scheduler_status",
    summary="Get Scheduler Status",
    dependencies=[Depends(require_dev_mode)],
)
async def check_scheduler_status():
    """
    Returns the current status and list of jobs for the shared APScheduler instance.
    Requires dev mode.
    """
    try:
        # Access the shared scheduler instance
        status = "running" if scheduler.running else "stopped"
        jobs_info = []
        for job in scheduler.get_jobs():
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "trigger": str(job.trigger),
                    "next_run_time": job.next_run_time.isoformat()
                    if job.next_run_time
                    else None,
                    "pending": job.pending,  # Check if job is due but waiting for executor
                }
            )
        return {
            "status": status,
            "jobs": jobs_info,
            "total_jobs": len(jobs_info),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error retrieving scheduler status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve scheduler status: {str(e)}"
        )


@router.get(
    "/trigger_domain_processing",
    summary="Trigger Domain Processing Job",
    dependencies=[Depends(require_dev_mode)],
)
async def trigger_domain_processing_endpoint():
    """
    Manually triggers the 'process_pending_domains' job to run immediately.
    Requires dev mode.
    """
    job_id = "process_pending_domains"
    try:
        job = scheduler.get_job(job_id)
        if job:
            # Run the job now. Note: This might bypass max_instances if not careful,
            # but useful for dev testing. Consider adding a check or specific method if needed.
            scheduler.modify_job(job_id, next_run_time=datetime.now(scheduler.timezone))
            logger.info(f"Manually triggered job '{job_id}'.")
            return {"message": f"Job '{job_id}' triggered successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    except Exception as e:
        logger.error(f"Error triggering job '{job_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger job '{job_id}': {str(e)}"
        )


# --- Test Endpoint for Website Scan Service ---
@router.post(
    "/trigger-website-scan/{domain_id}",
    summary="Manually Trigger Website Scan",
    dependencies=[Depends(require_dev_mode)],
)
async def trigger_website_scan(
    domain_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    """
    Manually triggers the WebsiteScanService for a specific domain ID.
    Requires dev mode.
    """
    logger.info(f"Received request to manually scan website for domain ID: {domain_id}")
    scan_service = WebsiteScanService(session)
    try:
        # Fetch the domain first to ensure it exists
        domain = await session.get(Domain, domain_id)
        if not domain:
            raise HTTPException(
                status_code=404, detail=f"Domain with ID {domain_id} not found."
            )

        logger.info(f"Attempting to initiate scan for domain: {domain.domain}")
        await scan_service.initiate_scan(domain_id=domain.id)
        return {"status": "success", "message": "Website scan initiated successfully."}

    except HTTPException as http_exc:
        logger.error(
            f"HTTP error triggering website scan for domain {domain_id}: {http_exc.detail}"
        )
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error triggering website scan for domain {domain_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger website scan: {str(e)}"
        )


# --- End Test Endpoint ---


@router.post(
    "/trigger-sitemap-import/{sitemap_file_id}",
    tags=["Scheduler Triggers", "Development"],
)
async def trigger_sitemap_import_endpoint(
    sitemap_file_id: UUID = Path(
        ..., description="The UUID of the SitemapFile to process"
    ),
    session: AsyncSession = Depends(get_session_dependency),
):
    """
    Manually triggers the sitemap import process for a single SitemapFile ID.

    This bypasses the scheduler and directly calls the SitemapImportService.
    Useful for testing the import logic for a specific sitemap file.
    The SitemapFile record MUST exist in the database.
    """
    logger.info(f"Manual trigger request for SitemapFile ID: {sitemap_file_id}")
    service = SitemapImportService()
    try:
        await service.process_single_sitemap_file(
            sitemap_file_id=sitemap_file_id, session=session
        )
        logger.info(f"Manual trigger successful for SitemapFile ID: {sitemap_file_id}")
        return {
            "message": "Sitemap import process triggered successfully.",
            "sitemap_file_id": sitemap_file_id,
        }
    except Exception as e:
        logger.exception(
            f"Manual trigger failed for SitemapFile ID: {sitemap_file_id}. Error: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process sitemap file {sitemap_file_id}: {str(e)}",
        ) from e

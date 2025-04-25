"""
Database Portal Router

This module provides API endpoints for the database inspection portal,
serving as the source of truth for database schema information.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.db_inspector import db_inspector
from src.session.async_session import get_session_dependency

router = APIRouter(
    prefix="/api/v3/db-portal",
    tags=["Database Portal"],
    responses={404: {"description": "Not found"}},
)


# Request Models
class SqlQueryRequest(BaseModel):
    """Model for SQL query requests"""

    query: str = Field(..., description="SQL SELECT query to execute")


class SchemaValidationRequest(BaseModel):
    """Model for schema validation requests"""

    expected_schema: Dict[str, Any] = Field(
        ..., description="Expected schema definition"
    )


# Response Models
class TableInfo(BaseModel):
    """Basic table information"""

    schema_name: str
    table_name: str
    row_count: int
    last_analyzed: Optional[str] = None


class ColumnInfo(BaseModel):
    """Column information"""

    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str] = None
    is_primary_key: bool
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None


class IndexInfo(BaseModel):
    """Index information"""

    index_name: str
    column_names: List[str]
    is_unique: bool


class ForeignKeyInfo(BaseModel):
    """Foreign key information"""

    column_name: str
    foreign_table: str
    foreign_column: str


class TableSchema(BaseModel):
    """Complete table schema"""

    table_name: str
    columns: List[ColumnInfo]
    indexes: List[IndexInfo]
    foreign_keys: List[ForeignKeyInfo]


class ValidationResult(BaseModel):
    """Schema validation result"""

    is_valid: bool
    missing_columns: List[Dict[str, Any]]
    type_mismatches: List[Dict[str, Any]]
    extra_columns: List[Dict[str, Any]]


class QueryResult(BaseModel):
    """SQL query result"""

    success: bool
    columns: Optional[List[str]] = None
    rows: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None


# API Endpoints
@router.get("/tables", response_model=List[TableInfo], summary="List All Tables")
async def list_tables(session: AsyncSession = Depends(get_session_dependency)):
    """
    List all tables in the database with basic metadata.

    This endpoint provides a comprehensive view of all tables in the database,
    including row counts and last analyzed timestamps.
    """
    async with session.begin():
        return await db_inspector.list_all_tables(session=session)


@router.get(
    "/tables/{table_name}", response_model=TableSchema, summary="Get Table Schema"
)
async def get_table_schema(
    table_name: str, session: AsyncSession = Depends(get_session_dependency)
):
    """
    Get detailed schema information for a specific table.

    This endpoint returns comprehensive information about a table's structure,
    including columns, data types, constraints, indexes, and foreign keys.
    """
    async with session.begin():
        schema = await db_inspector.get_table_schema(table_name, session=session)
        if "error" in schema:
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found or error: {schema['error']}",
            )
        return schema


@router.get("/tables/{table_name}/sample", summary="Get Sample Data")
async def get_sample_data(
    table_name: str,
    limit: int = Query(5, ge=1, le=100),
    session: AsyncSession = Depends(get_session_dependency),
):
    """
    Get sample data from a table for preview purposes.

    This endpoint returns a limited number of rows from the specified table
    to help understand the actual data stored in it.
    """
    async with session.begin():
        data = await db_inspector.get_sample_data(table_name, limit, session=session)
        if data and "error" in data[0]:
            raise HTTPException(status_code=404, detail=data[0]["error"])
        return data


@router.post("/query", response_model=QueryResult, summary="Execute SQL Query")
async def execute_query(
    request: SqlQueryRequest, session: AsyncSession = Depends(get_session_dependency)
):
    """
    Execute a safe, read-only SQL query for database inspection.

    This endpoint allows executing SELECT queries only, with results
    returned in a structured format. Use this for more advanced
    database inspection beyond the provided schema endpoints.
    """
    async with session.begin():
        result = await db_inspector.execute_safe_query(request.query, session=session)
        if not result.get("success"):
            raise HTTPException(
                status_code=400, detail=result.get("error", "Query execution failed")
            )
        return result


@router.post(
    "/tables/{table_name}/validate",
    response_model=ValidationResult,
    summary="Validate Schema",
)
async def validate_schema(
    table_name: str,
    request: SchemaValidationRequest,
    session: AsyncSession = Depends(get_session_dependency),
):
    """
    Validate expected schema against actual database schema.

    This endpoint compares an expected schema definition against the
    actual database schema, identifying missing columns, type mismatches,
    and extra columns.
    """
    async with session.begin():
        result = await db_inspector.validate_table_schema(
            table_name, request.expected_schema, session=session
        )
        return result


@router.get("/tables/{table_name}/model", summary="Generate Model Code")
async def generate_model(
    table_name: str, session: AsyncSession = Depends(get_session_dependency)
):
    """
    Generate Python model code based on database schema.

    This endpoint creates Pydantic model code that matches the
    actual database schema, ready to be used in your application.
    """
    async with session.begin():
        code = await db_inspector.generate_model_code(table_name, session=session)
        return {"model_code": code}


@router.get("/health", summary="Database Portal Health Check")
async def health_check(session: AsyncSession = Depends(get_session_dependency)):
    """
    Check if the database portal service is healthy.

    This endpoint verifies that the database connection is working
    and the portal can retrieve basic schema information.
    """
    try:
        # Try to list tables as a basic health check
        async with session.begin():
            tables = await db_inspector.list_all_tables(session=session)
            return {
                "status": "healthy" if tables else "warning",
                "message": f"Successfully connected to database. Found {len(tables)} tables."
                if tables
                else "Connected to database but found no tables.",
                "tables_count": len(tables),
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to connect to database: {str(e)}",
        }

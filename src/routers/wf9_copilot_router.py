"""
ScraperSky Co-Pilot API

Semantic search over project documentation using vector embeddings.
Provides AI-powered answers about the codebase, architecture, and patterns.

Endpoints:
- POST /ask - Semantic search with filters
- GET /stats - Knowledge base statistics
- GET /filters - Available filter options

ARCHITECTURE NOTE: This router uses AsyncSession with the Supavisor connection
pooler, consistent with all other routers in the system.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_auth import get_current_active_user
from src.session.async_session import get_session_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/copilot", tags=["Co-Pilot"])


# =============================================================================
# Request/Response Models
# =============================================================================


class AskRequest(BaseModel):
    """Request model for Co-Pilot questions with optional filters."""

    question: str = Field(..., description="Natural language question")
    limit: Optional[int] = Field(5, ge=1, le=50, description="Max results to return")
    threshold: Optional[float] = Field(
        0.70, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )
    # Filters
    layers: Optional[List[int]] = Field(
        None, description="Filter by architectural layers (0-7)"
    )
    workflows: Optional[List[str]] = Field(
        None, description="Filter by workflows (e.g., ['WF1', 'WF4'])"
    )
    doc_types: Optional[List[str]] = Field(
        None, description="Filter by document types"
    )
    # Content options
    include_content: Optional[bool] = Field(
        False, description="Include full document content in results"
    )
    include_patterns: Optional[bool] = Field(
        False, description="Also search fix_patterns knowledge base"
    )


class SearchResult(BaseModel):
    """Individual search result from project_docs."""

    id: int
    title: str
    similarity: float
    content: Optional[str] = None
    # Metadata (when available)
    architectural_layer: Optional[int] = None
    document_type: Optional[str] = None
    source: str = "project_docs"


class PatternResult(BaseModel):
    """Individual search result from fix_patterns."""

    id: str
    title: str
    similarity: float
    problem_type: Optional[str] = None
    severity: Optional[str] = None
    problem_description: Optional[str] = None
    solution_steps: Optional[str] = None
    source: str = "fix_patterns"


class AskResponse(BaseModel):
    """Response model for Co-Pilot answers."""

    question: str
    results: List[SearchResult]
    patterns: Optional[List[PatternResult]] = None
    total_results: int
    filters_applied: Dict[str, Any]


class StatsResponse(BaseModel):
    """Knowledge base statistics."""

    total_documents: int
    total_patterns: int
    documents_by_layer: Dict[str, int]
    documents_by_type: Dict[str, int]
    documents_by_workflow: Dict[str, int]
    patterns_by_type: Dict[str, int]
    patterns_by_severity: Dict[str, int]


class FiltersResponse(BaseModel):
    """Available filter options."""

    layers: List[Dict[str, Any]]
    workflows: List[str]
    doc_types: List[str]
    pattern_types: List[str]
    severities: List[str]


# =============================================================================
# Helper Functions
# =============================================================================


async def get_embedding(text_input: str) -> List[float]:
    """Generate embedding for text using OpenAI."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.embeddings.create(
        input=[text_input.replace("\n", " ")],
        model="text-embedding-ada-002",
    )
    return response.data[0].embedding


def format_vector_for_postgres(embedding: List[float]) -> str:
    """Format embedding vector for PostgreSQL halfvec type."""
    # Format as PostgreSQL array literal: [0.1, 0.2, ...]
    return "[" + ",".join(str(x) for x in embedding) + "]"


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/ask", response_model=AskResponse)
async def ask_copilot(
    payload: AskRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Semantic search against ScraperSky documentation with optional filters.

    **Filters:**
    - `layers`: Filter by architectural layer (0-7)
    - `workflows`: Filter by workflow (WF1-WF7)
    - `doc_types`: Filter by document type

    **Options:**
    - `include_content`: Return full document content
    - `include_patterns`: Also search fix_patterns for code issues
    """
    try:
        # Generate embedding for the question
        embedding = await get_embedding(payload.question)
        vector_str = format_vector_for_postgres(embedding)

        # Build metadata filter for the RPC function
        metadata_filter: Dict[str, Any] = {}
        if payload.layers:
            metadata_filter["architectural_layer"] = payload.layers
        if payload.doc_types:
            metadata_filter["document_type"] = payload.doc_types

        # Call the RPC function using raw SQL through SQLAlchemy
        # The function: perform_semantic_search_direct(halfvec, double, int, jsonb)
        # Use CAST() instead of :: to avoid conflicts with SQLAlchemy parameter binding
        query = text("""
            SELECT id, title, content, similarity
            FROM perform_semantic_search_direct(
                CAST(:embedding AS halfvec),
                CAST(:threshold AS double precision),
                CAST(:limit AS integer),
                CAST(:metadata_filter AS jsonb)
            )
        """)

        result = await session.execute(
            query,
            {
                "embedding": vector_str,
                "threshold": float(payload.threshold),
                "limit": int(payload.limit),
                "metadata_filter": json.dumps(metadata_filter),
            },
        )
        rows = result.fetchall()

        # Build results
        results = []
        for row in rows:
            results.append(
                SearchResult(
                    id=row.id,
                    title=row.title,
                    similarity=row.similarity,
                    content=row.content if payload.include_content else None,
                    source="project_docs",
                )
            )

        # If workflow filter specified, filter results by checking document_registry
        if payload.workflows and results:
            result_ids = [r.id for r in results]
            # Build OR condition for workflow array contains
            workflow_conditions = " OR ".join(
                [f"associated_workflow @> :wf_{i}::jsonb" for i in range(len(payload.workflows))]
            )
            workflow_query = text(f"""
                SELECT id FROM document_registry
                WHERE id = ANY(:ids) AND ({workflow_conditions})
            """)
            params = {"ids": result_ids}
            for i, wf in enumerate(payload.workflows):
                params[f"wf_{i}"] = json.dumps([wf])

            workflow_result = await session.execute(workflow_query, params)
            valid_ids = {row.id for row in workflow_result.fetchall()}
            results = [r for r in results if r.id in valid_ids]

        # Optional: Search fix_patterns
        patterns = None
        if payload.include_patterns:
            pattern_query = text("""
                SELECT id, title, problem_type, severity,
                       problem_description, solution_steps
                FROM fix_patterns
                LIMIT 10
            """)
            pattern_result = await session.execute(pattern_query)
            pattern_rows = pattern_result.fetchall()

            if pattern_rows:
                patterns = [
                    PatternResult(
                        id=str(p.id),
                        title=p.title,
                        similarity=0.75,  # Placeholder until proper vector search
                        problem_type=p.problem_type,
                        severity=p.severity,
                        problem_description=p.problem_description,
                        solution_steps=p.solution_steps,
                    )
                    for p in pattern_rows[:5]
                ]

        return AskResponse(
            question=payload.question,
            results=results,
            patterns=patterns,
            total_results=len(results) + (len(patterns) if patterns else 0),
            filters_applied={
                "layers": payload.layers,
                "workflows": payload.workflows,
                "doc_types": payload.doc_types,
                "include_content": payload.include_content,
                "include_patterns": payload.include_patterns,
            },
        )

    except Exception as e:
        logger.error(f"Co-Pilot error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Co-Pilot error: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Get knowledge base statistics.

    Returns counts of documents and patterns by various dimensions.
    """
    try:
        # Total documents (active only)
        docs_result = await session.execute(
            text("SELECT COUNT(*) FROM document_registry WHERE embedding_status = 'active'")
        )
        total_docs = docs_result.scalar() or 0

        # Total patterns
        patterns_result = await session.execute(
            text("SELECT COUNT(*) FROM fix_patterns")
        )
        total_patterns = patterns_result.scalar() or 0

        # Documents by layer
        layers_result = await session.execute(
            text("""
                SELECT architectural_layer, COUNT(*) as cnt
                FROM document_registry
                WHERE embedding_status = 'active' AND architectural_layer IS NOT NULL
                GROUP BY architectural_layer
            """)
        )
        layer_counts = {f"Layer {row.architectural_layer}": row.cnt for row in layers_result.fetchall()}

        # Documents by type
        types_result = await session.execute(
            text("""
                SELECT document_type, COUNT(*) as cnt
                FROM document_registry
                WHERE embedding_status = 'active' AND document_type IS NOT NULL
                GROUP BY document_type
            """)
        )
        type_counts = {row.document_type: row.cnt for row in types_result.fetchall()}

        # Documents by workflow (from associated_workflow array)
        workflows_result = await session.execute(
            text("""
                SELECT unnest(associated_workflow) as workflow, COUNT(*) as cnt
                FROM document_registry
                WHERE embedding_status = 'active' AND associated_workflow IS NOT NULL
                GROUP BY workflow
            """)
        )
        workflow_counts = {row.workflow: row.cnt for row in workflows_result.fetchall()}

        # Patterns by type
        pattern_types_result = await session.execute(
            text("SELECT problem_type, COUNT(*) as cnt FROM fix_patterns GROUP BY problem_type")
        )
        pattern_type_counts = {row.problem_type: row.cnt for row in pattern_types_result.fetchall()}

        # Patterns by severity
        severity_result = await session.execute(
            text("SELECT severity, COUNT(*) as cnt FROM fix_patterns GROUP BY severity")
        )
        severity_counts = {row.severity: row.cnt for row in severity_result.fetchall()}

        return StatsResponse(
            total_documents=total_docs,
            total_patterns=total_patterns,
            documents_by_layer=layer_counts,
            documents_by_type=type_counts,
            documents_by_workflow=workflow_counts,
            patterns_by_type=pattern_type_counts,
            patterns_by_severity=severity_counts,
        )

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/filters", response_model=FiltersResponse)
async def get_filters(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Get available filter options for the Co-Pilot search.

    Returns all valid values for layers, workflows, document types, etc.
    """
    try:
        # Get distinct layers
        layers_result = await session.execute(
            text("""
                SELECT DISTINCT architectural_layer
                FROM document_registry
                WHERE embedding_status = 'active' AND architectural_layer IS NOT NULL
                ORDER BY architectural_layer
            """)
        )
        layers = [
            {
                "value": row.architectural_layer,
                "label": f"Layer {row.architectural_layer}",
                "description": get_layer_description(row.architectural_layer),
            }
            for row in layers_result.fetchall()
        ]

        # Get distinct document types
        types_result = await session.execute(
            text("""
                SELECT DISTINCT document_type
                FROM document_registry
                WHERE embedding_status = 'active' AND document_type IS NOT NULL
                ORDER BY document_type
            """)
        )
        doc_types = [row.document_type for row in types_result.fetchall()]

        # Get distinct workflows
        workflows_result = await session.execute(
            text("""
                SELECT DISTINCT unnest(associated_workflow) as workflow
                FROM document_registry
                WHERE embedding_status = 'active' AND associated_workflow IS NOT NULL
                ORDER BY workflow
            """)
        )
        workflows = [row.workflow for row in workflows_result.fetchall()]

        # Get distinct pattern types
        pattern_types_result = await session.execute(
            text("SELECT DISTINCT problem_type FROM fix_patterns ORDER BY problem_type")
        )
        pattern_types = [row.problem_type for row in pattern_types_result.fetchall()]

        # Get distinct severities
        severity_result = await session.execute(
            text("SELECT DISTINCT severity FROM fix_patterns ORDER BY severity")
        )
        severities = [row.severity for row in severity_result.fetchall()]

        return FiltersResponse(
            layers=layers,
            workflows=workflows,
            doc_types=doc_types,
            pattern_types=pattern_types,
            severities=severities,
        )

    except Exception as e:
        logger.error(f"Filters error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Filters error: {str(e)}")


def get_layer_description(layer: int) -> str:
    """Return human-readable description for architectural layer."""
    descriptions = {
        0: "Foundation/Core",
        1: "Models & Enums",
        2: "Schemas",
        3: "Routers",
        4: "Services",
        5: "Configuration",
        6: "UI Components",
        7: "Testing",
    }
    return descriptions.get(layer, f"Layer {layer}")

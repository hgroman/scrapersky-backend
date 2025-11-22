"""
ScraperSky Co-Pilot API

Semantic search over project documentation using vector embeddings.
Provides AI-powered answers about the codebase, architecture, and patterns.

Endpoints:
- POST /ask - Semantic search with filters
- GET /stats - Knowledge base statistics
- GET /filters - Available filter options
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from supabase import create_client

from src.auth.jwt_auth import get_current_active_user

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


def get_supabase_client():
    """Create and return a Supabase client."""
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )


async def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-ada-002",
    )
    return response.data[0].embedding


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/ask", response_model=AskResponse)
async def ask_copilot(
    payload: AskRequest,
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
        supabase = get_supabase_client()
        embedding = await get_embedding(payload.question)

        # Build metadata filter
        metadata_filter = {}
        if payload.layers:
            metadata_filter["architectural_layer"] = payload.layers
        if payload.doc_types:
            metadata_filter["document_type"] = payload.doc_types

        # Primary search: project_docs
        doc_result = supabase.rpc(
            "perform_semantic_search_direct",
            {
                "query_embedding_param": embedding,
                "match_count_param": payload.limit,
                "match_threshold_param": payload.threshold,
                "metadata_filter_param": metadata_filter,
            },
        ).execute()

        # Build results with optional content
        results = []
        for r in doc_result.data:
            result = SearchResult(
                id=r["id"],
                title=r["title"],
                similarity=r["similarity"],
                content=r.get("content") if payload.include_content else None,
                source="project_docs",
            )
            results.append(result)

        # If workflow filter specified, filter results by checking document_registry
        if payload.workflows:
            # Get document IDs that match workflow filter
            workflow_query = supabase.table("document_registry").select(
                "id"
            ).or_(
                ",".join([f"associated_workflow.cs.{{{w}}}" for w in payload.workflows])
            ).execute()

            valid_ids = {r["id"] for r in workflow_query.data}
            results = [r for r in results if r.id in valid_ids]

        # Optional: Search fix_patterns
        patterns = None
        if payload.include_patterns:
            # Direct query to fix_patterns
            pattern_query = supabase.table("fix_patterns").select(
                "id, title, problem_type, severity, problem_description, solution_steps"
            ).limit(10).execute()

            if pattern_query.data:
                patterns = [
                    PatternResult(
                        id=str(p["id"]),
                        title=p["title"],
                        similarity=0.75,  # Placeholder until we add proper vector search
                        problem_type=p.get("problem_type"),
                        severity=p.get("severity"),
                        problem_description=p.get("problem_description"),
                        solution_steps=p.get("solution_steps"),
                    )
                    for p in pattern_query.data[:5]
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
        raise HTTPException(status_code=500, detail=f"Co-Pilot error: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Get knowledge base statistics.

    Returns counts of documents and patterns by various dimensions.
    """
    try:
        supabase = get_supabase_client()

        # Total documents (active only)
        docs_count = supabase.table("document_registry").select(
            "id", count="exact"
        ).eq("embedding_status", "active").execute()

        # Total patterns
        patterns_count = supabase.table("fix_patterns").select(
            "id", count="exact"
        ).execute()

        # Documents by layer
        layers_query = supabase.table("document_registry").select(
            "architectural_layer"
        ).eq("embedding_status", "active").not_.is_("architectural_layer", "null").execute()

        layer_counts = {}
        for r in layers_query.data:
            layer = f"Layer {r['architectural_layer']}"
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        # Documents by type
        types_query = supabase.table("document_registry").select(
            "document_type"
        ).eq("embedding_status", "active").not_.is_("document_type", "null").execute()

        type_counts = {}
        for r in types_query.data:
            doc_type = r["document_type"]
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        # Documents by workflow (from associated_workflow array)
        workflow_counts = {}
        workflows_query = supabase.table("document_registry").select(
            "associated_workflow"
        ).eq("embedding_status", "active").not_.is_("associated_workflow", "null").execute()

        for r in workflows_query.data:
            if r["associated_workflow"]:
                for wf in r["associated_workflow"]:
                    workflow_counts[wf] = workflow_counts.get(wf, 0) + 1

        # Patterns by type
        pattern_types_query = supabase.table("fix_patterns").select(
            "problem_type"
        ).execute()

        pattern_type_counts = {}
        for r in pattern_types_query.data:
            ptype = r["problem_type"]
            pattern_type_counts[ptype] = pattern_type_counts.get(ptype, 0) + 1

        # Patterns by severity
        severity_query = supabase.table("fix_patterns").select(
            "severity"
        ).execute()

        severity_counts = {}
        for r in severity_query.data:
            sev = r["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return StatsResponse(
            total_documents=docs_count.count or 0,
            total_patterns=patterns_count.count or 0,
            documents_by_layer=layer_counts,
            documents_by_type=type_counts,
            documents_by_workflow=workflow_counts,
            patterns_by_type=pattern_type_counts,
            patterns_by_severity=severity_counts,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/filters", response_model=FiltersResponse)
async def get_filters(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Get available filter options for the Co-Pilot search.

    Returns all valid values for layers, workflows, document types, etc.
    """
    try:
        supabase = get_supabase_client()

        # Get distinct layers
        layers_query = supabase.table("document_registry").select(
            "architectural_layer"
        ).eq("embedding_status", "active").not_.is_("architectural_layer", "null").execute()

        unique_layers = sorted(set(r["architectural_layer"] for r in layers_query.data))
        layers = [
            {"value": layer_num, "label": f"Layer {layer_num}", "description": get_layer_description(layer_num)}
            for layer_num in unique_layers
        ]

        # Get distinct document types
        types_query = supabase.table("document_registry").select(
            "document_type"
        ).eq("embedding_status", "active").not_.is_("document_type", "null").execute()

        doc_types = sorted(set(r["document_type"] for r in types_query.data))

        # Get distinct workflows
        workflows_query = supabase.table("document_registry").select(
            "associated_workflow"
        ).eq("embedding_status", "active").not_.is_("associated_workflow", "null").execute()

        workflows = set()
        for r in workflows_query.data:
            if r["associated_workflow"]:
                workflows.update(r["associated_workflow"])
        workflows = sorted(workflows)

        # Get distinct pattern types
        pattern_types_query = supabase.table("fix_patterns").select(
            "problem_type"
        ).execute()

        pattern_types = sorted(set(r["problem_type"] for r in pattern_types_query.data))

        # Get distinct severities
        severity_query = supabase.table("fix_patterns").select(
            "severity"
        ).execute()

        severities = sorted(set(r["severity"] for r in severity_query.data))

        return FiltersResponse(
            layers=layers,
            workflows=workflows,
            doc_types=doc_types,
            pattern_types=pattern_types,
            severities=severities,
        )

    except Exception as e:
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

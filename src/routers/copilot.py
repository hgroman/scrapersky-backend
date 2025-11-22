"""
ScraperSky Co-Pilot API

Semantic search over project documentation using vector embeddings.
Provides AI-powered answers about the codebase, architecture, and patterns.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from supabase import create_client

from src.auth.jwt_auth import get_current_active_user

router = APIRouter(prefix="/api/v3/copilot", tags=["Co-Pilot"])


class AskRequest(BaseModel):
    """Request model for Co-Pilot questions."""

    question: str
    limit: Optional[int] = 5
    threshold: Optional[float] = 0.70


class SearchResult(BaseModel):
    """Individual search result."""

    id: int
    title: str
    similarity: float
    content: Optional[str] = None


class AskResponse(BaseModel):
    """Response model for Co-Pilot answers."""

    question: str
    results: List[SearchResult]


@router.post("/ask", response_model=AskResponse)
async def ask_copilot(
    payload: AskRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Semantic search against ScraperSky documentation.

    Takes a natural language question and returns the most relevant
    documents from the knowledge base ranked by similarity.
    """
    try:
        # Generate embedding via OpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        embedding_response = await client.embeddings.create(
            input=[payload.question.replace("\n", " ")],
            model="text-embedding-ada-002",  # Must match existing 162 doc embeddings
        )
        embedding = embedding_response.data[0].embedding

        # Query Supabase vector database
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        )

        result = supabase.rpc(
            "perform_semantic_search_direct",
            {
                "query_embedding_param": embedding,
                "match_count_param": payload.limit,
                "match_threshold_param": payload.threshold,
                "metadata_filter_param": {},
            },
        ).execute()

        return AskResponse(
            question=payload.question,
            results=[SearchResult(**r) for r in result.data],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Co-Pilot error: {str(e)}")

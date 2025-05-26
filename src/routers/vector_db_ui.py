"""
Vector DB UI Router

This module provides API endpoints for interacting with the Vector DB Knowledge System.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv

from src.db.session import get_session_dependency

# Load environment variables
load_dotenv()

# Router definition
router = APIRouter(prefix="/api/v3/vector-db", tags=["vector-db"])


class PatternSearchRequest(BaseModel):
    """Request model for pattern search."""
    query: str
    limit: Optional[int] = 5


class PatternResponse(BaseModel):
    """Response model for pattern data."""
    id: str
    title: str
    problem_type: str
    code_type: str
    severity: str
    problem_description: str
    solution_steps: str
    similarity: Optional[float] = None


@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns(session: AsyncSession = Depends(get_session_dependency)):
    """Get all patterns from the Vector DB."""
    query = """
    SELECT 
        id, 
        title, 
        problem_type, 
        code_type, 
        severity, 
        problem_description, 
        solution_steps
    FROM 
        fix_patterns
    ORDER BY 
        title
    """
    
    result = await session.execute(query)
    patterns = result.fetchall()
    
    if not patterns:
        return []
    
    return [
        PatternResponse(
            id=str(pattern.id),
            title=pattern.title,
            problem_type=pattern.problem_type,
            code_type=pattern.code_type,
            severity=pattern.severity,
            problem_description=pattern.problem_description,
            solution_steps=pattern.solution_steps
        )
        for pattern in patterns
    ]


@router.post("/search", response_model=List[PatternResponse])
async def search_patterns(
    request: PatternSearchRequest,
    session: AsyncSession = Depends(get_session_dependency)
):
    """Search patterns using vector similarity."""
    # Connect to OpenAI to generate embedding
    try:
        import httpx
        import json
        
        # OpenAI API configuration
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        EMBEDDING_MODEL = "text-embedding-ada-002"
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": request.query,
                "model": EMBEDDING_MODEL
            }
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            response_data = response.json()
            embedding = response_data["data"][0]["embedding"]
            
            # Convert embedding to string format for vector type
            embedding_str = f"[{','.join(str(x) for x in embedding)}]"
            
            # Connect to database directly for vector search
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
                DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
                
            conn = await asyncpg.connect(
                DATABASE_URL,
                ssl="require",
                statement_cache_size=0
            )
            
            # Search using pattern_vector
            results = await conn.fetch(
                """
                SELECT 
                    id, 
                    title, 
                    problem_type,
                    code_type,
                    severity,
                    problem_description,
                    solution_steps,
                    1 - (pattern_vector <=> $1::vector) as similarity
                FROM 
                    fix_patterns
                ORDER BY 
                    similarity DESC
                LIMIT $2
                """,
                embedding_str,
                request.limit
            )
            
            await conn.close()
            
            return [
                PatternResponse(
                    id=str(result["id"]),
                    title=result["title"],
                    problem_type=result["problem_type"],
                    code_type=result["code_type"],
                    severity=result["severity"],
                    problem_description=result["problem_description"],
                    solution_steps=result["solution_steps"],
                    similarity=float(result["similarity"])
                )
                for result in results
            ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching patterns: {str(e)}")


@router.get("/pattern/{pattern_id}", response_model=Dict[str, Any])
async def get_pattern_detail(
    pattern_id: str,
    session: AsyncSession = Depends(get_session_dependency)
):
    """Get detailed information about a specific pattern."""
    query = """
    SELECT 
        id, 
        title, 
        problem_type, 
        code_type, 
        severity, 
        problem_description, 
        solution_steps,
        code_before,
        code_after,
        verification_steps,
        learnings,
        prevention_guidance,
        description,
        tags,
        layers,
        workflows,
        file_types,
        applied_count,
        success_rate,
        confidence_score,
        created_by,
        created_at,
        updated_at
    FROM 
        fix_patterns
    WHERE 
        id = :pattern_id
    """
    
    result = await session.execute(query, {"pattern_id": pattern_id})
    pattern = result.fetchone()
    
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    # Convert to dictionary
    pattern_dict = {
        "id": str(pattern.id),
        "title": pattern.title,
        "problem_type": pattern.problem_type,
        "code_type": pattern.code_type,
        "severity": pattern.severity,
        "problem_description": pattern.problem_description,
        "solution_steps": pattern.solution_steps,
        "code_before": pattern.code_before,
        "code_after": pattern.code_after,
        "verification_steps": pattern.verification_steps,
        "learnings": pattern.learnings,
        "prevention_guidance": pattern.prevention_guidance,
        "description": pattern.description,
        "tags": pattern.tags,
        "layers": pattern.layers,
        "workflows": pattern.workflows,
        "file_types": pattern.file_types,
        "applied_count": pattern.applied_count,
        "success_rate": pattern.success_rate,
        "confidence_score": pattern.confidence_score,
        "created_by": pattern.created_by,
        "created_at": pattern.created_at.isoformat() if pattern.created_at else None,
        "updated_at": pattern.updated_at.isoformat() if pattern.updated_at else None
    }
    
    return pattern_dict

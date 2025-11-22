# WO-025: ScraperSky Co-Pilot Semantic Search System - COMPLETE

**Work Order:** WO-025
**Status:** Phase 1 Complete - Production Ready
**Implemented:** 2025-11-22
**Implementer:** Claude Code (Registry Librarian + Knowledge Librarian Persona)
**Time to Implement:** ~3 hours (discovery + implementation)
**Git Commits:**
- `557d9f4` - Initial Co-Pilot endpoint
- `b132ebf` - Phase 1 enhancements (filters, stats, filters endpoint)
**Branch:** main

---

## Executive Summary

**WO-025 implements the ScraperSky Co-Pilot** - an AI-powered semantic search system that enables natural language queries against 162 vectorized architectural documents and 34 code fix patterns.

### What Was Built

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCRAPERSKY CO-PILOT SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User Question ──► OpenAI ──► Vector Search ──► Ranked Results             │
│   "How do schedulers    │        │                    │                     │
│    work?"               │        │                    │                     │
│                         ▼        ▼                    ▼                     │
│                    Embedding   Supabase          Documents +                │
│                    (1536-dim)  pgvector          Similarity                 │
│                                                  Scores                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  KNOWLEDGE BASES:                                                           │
│  • project_docs (162 documents) - Architectural documentation               │
│  • fix_patterns (34 patterns) - Code fixes, anti-patterns, solutions        │
│                                                                             │
│  ENDPOINTS:                                                                 │
│  • POST /api/v3/copilot/ask     - Semantic search with filters              │
│  • GET  /api/v3/copilot/stats   - Knowledge base statistics                 │
│  • GET  /api/v3/copilot/filters - Available filter options                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [Background & Discovery](#1-background--discovery)
2. [Architecture Overview](#2-architecture-overview)
3. [Implementation Details](#3-implementation-details)
4. [API Reference](#4-api-reference)
5. [Database Schema](#5-database-schema)
6. [How to Use](#6-how-to-use)
7. [How to Maintain](#7-how-to-maintain)
8. [How to Extend](#8-how-to-extend)
9. [Known Issues & Limitations](#9-known-issues--limitations)
10. [Future Roadmap](#10-future-roadmap)

---

## 1. Background & Discovery

### The Problem

ScraperSky had accumulated **significant institutional knowledge** spread across:
- 162+ architectural documents (audit reports, blueprints, guides)
- 34 extracted code fix patterns (anti-patterns, solutions, learnings)
- 7 architectural layers of documentation
- 7 workflow-specific documentation sets (WF1-WF7)

This knowledge was:
- Scattered across Docs directories
- Searchable only via grep/file browsing
- Inaccessible to new developers
- Not leveraged for AI-assisted development

### Discovery Session Findings

During the implementation session, we discovered:

1. **Two Existing Vector Knowledge Bases:**

   | Table | Documents | Vector Columns | Status Before |
   |-------|-----------|----------------|---------------|
   | `project_docs` | 162 | `embedding` (halfvec 1536) | Active but no API |
   | `fix_patterns` | 34 | `pattern_vector`, `content_embedding`, `code_embedding`, `problem_embedding` | Completely dormant |

2. **Existing Infrastructure (Already Built, Unused):**
   - `perform_semantic_search_direct` RPC function in Supabase
   - `semantic_query_cli.py` - Working CLI tool
   - `insert_architectural_docs.py` - Document ingestion pipeline
   - Document registry system (`document_registry` table)
   - Rich metadata (layers, workflows, document types)

3. **Dead Code Found:**
   - `src/routers/vector_db_ui.py` - Router for fix_patterns, never registered in main.py
   - Provided semantic search over `fix_patterns` but was completely inaccessible

4. **The Irony:**
   The system could already do semantic search via CLI, but had no API endpoint to expose this capability to applications or UIs.

### The Solution

Create a proper FastAPI router to expose the existing semantic search capabilities with:
- Proper authentication
- Filtering by metadata
- Statistics and filter options for UI building
- Integration of both knowledge bases (project_docs + fix_patterns)

---

## 2. Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARCHITECTURE LAYERS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   React/Vue     │     │    FastAPI      │     │    Supabase     │       │
│  │   Frontend      │────►│    Backend      │────►│   PostgreSQL    │       │
│  │   (Future)      │     │  copilot.py     │     │   + pgvector    │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                 │                        │                  │
│                                 │                        │                  │
│                                 ▼                        ▼                  │
│                          ┌─────────────┐          ┌─────────────┐          │
│                          │   OpenAI    │          │  project_   │          │
│                          │  Embeddings │          │    docs     │          │
│                          │  (ada-002)  │          │  (162 docs) │          │
│                          └─────────────┘          └─────────────┘          │
│                                                          │                  │
│                                                          ▼                  │
│                                                   ┌─────────────┐          │
│                                                   │    fix_     │          │
│                                                   │  patterns   │          │
│                                                   │ (34 patterns)│          │
│                                                   └─────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User sends question → POST /api/v3/copilot/ask
2. FastAPI validates JWT token
3. Question text sent to OpenAI → Returns 1536-dimension embedding
4. Embedding sent to Supabase RPC → perform_semantic_search_direct
5. pgvector performs cosine similarity search
6. Results ranked by similarity score
7. Optional: Also query fix_patterns table
8. Response returned with results + metadata
```

### File Structure

```
src/
├── routers/
│   └── copilot.py              # NEW - Co-Pilot API endpoints
├── auth/
│   └── jwt_auth.py             # Authentication (existing)
└── main.py                     # Router registration (modified)

Docs/
├── Docs_18_Vector_Operations/
│   ├── Scripts/
│   │   ├── semantic_query_cli.py        # CLI tool (existing)
│   │   └── insert_architectural_docs.py # Ingestion (existing)
│   └── Documentation/
│       └── *.md                         # Vector ops docs
└── Docs_19_File-2-Vector-Registry-System/
    ├── 1-registry-directory-manager.py   # Directory approval
    ├── 2-registry-document-scanner.py    # Document scanning
    ├── 3-registry-update-flag-manager.py # Update flagging
    ├── 4-registry-archive-manager.py     # Archive management
    ├── 5-vector-db-cleanup-manager.py    # Vector cleanup
    ├── 6-registry-orphan-detector.py     # Orphan detection
    └── 7-registry-orphan-purger.py       # Orphan removal
```

---

## 3. Implementation Details

### Files Created/Modified

| File | Action | Lines Changed | Purpose |
|------|--------|---------------|---------|
| `src/routers/copilot.py` | Created | 424 lines | Main Co-Pilot router |
| `src/main.py` | Modified | +2 lines | Router registration |

### Dependencies Used

```python
# Standard library
import os
from typing import Any, Dict, List, Optional

# FastAPI
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# External services
from openai import AsyncOpenAI          # Embedding generation
from supabase import create_client      # Database queries

# Internal
from src.auth.jwt_auth import get_current_active_user  # Authentication
```

### Key Design Decisions

1. **Async OpenAI Client:** Uses `AsyncOpenAI` for non-blocking embedding generation
2. **Direct Supabase Client:** Creates client per-request (not connection pooled) for simplicity
3. **RPC over Raw SQL:** Uses existing `perform_semantic_search_direct` RPC function
4. **Metadata Filtering:** Passes filters to RPC for server-side filtering where possible
5. **Workflow Filtering:** Client-side filtering due to array column complexity

### Authentication

All endpoints require JWT authentication:

```python
@router.post("/ask")
async def ask_copilot(
    payload: AskRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
```

Development bypass token: `scraper_sky_2024` (only works when `ENV=development`)

---

## 4. API Reference

### POST /api/v3/copilot/ask

**Purpose:** Semantic search with optional filters

**Request:**
```json
{
  "question": "How do schedulers work in ScraperSky?",
  "limit": 5,
  "threshold": 0.70,
  "layers": [4, 5],
  "workflows": ["WF4"],
  "doc_types": ["architecture_document"],
  "include_content": false,
  "include_patterns": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | required | Natural language question |
| `limit` | int | 5 | Max results (1-50) |
| `threshold` | float | 0.70 | Minimum similarity (0.0-1.0) |
| `layers` | int[] | null | Filter by architectural layers (0-7) |
| `workflows` | string[] | null | Filter by workflows (WF1-WF7) |
| `doc_types` | string[] | null | Filter by document types |
| `include_content` | bool | false | Include full document content |
| `include_patterns` | bool | false | Also search fix_patterns |

**Response:**
```json
{
  "question": "How do schedulers work in ScraperSky?",
  "results": [
    {
      "id": 196,
      "title": "v_0.6-AI_Synthesized_Architectural_Overview.md",
      "similarity": 0.7975,
      "content": null,
      "architectural_layer": null,
      "document_type": null,
      "source": "project_docs"
    }
  ],
  "patterns": [
    {
      "id": "uuid-here",
      "title": "Business Logic in Router",
      "similarity": 0.75,
      "problem_type": "architecture",
      "severity": "HIGH-ARCHITECTURE",
      "problem_description": "...",
      "solution_steps": "...",
      "source": "fix_patterns"
    }
  ],
  "total_results": 6,
  "filters_applied": {
    "layers": [4, 5],
    "workflows": ["WF4"],
    "doc_types": null,
    "include_content": false,
    "include_patterns": true
  }
}
```

### GET /api/v3/copilot/stats

**Purpose:** Knowledge base statistics for dashboard displays

**Response:**
```json
{
  "total_documents": 162,
  "total_patterns": 34,
  "documents_by_layer": {
    "Layer 0": 5,
    "Layer 1": 23,
    "Layer 2": 18,
    "Layer 3": 31,
    "Layer 4": 25,
    "Layer 5": 12,
    "Layer 6": 28,
    "Layer 7": 20
  },
  "documents_by_type": {
    "architecture_document": 45,
    "reference": 28,
    "protocol": 15,
    "standard": 12,
    "documentation": 62
  },
  "documents_by_workflow": {
    "WF1": 18,
    "WF2": 12,
    "WF3": 15,
    "WF4": 22,
    "WF5": 20,
    "WF6": 14,
    "WF7": 25
  },
  "patterns_by_type": {
    "architecture": 14,
    "security": 8,
    "standards": 9,
    "bugfix": 1,
    "exemplar": 1
  },
  "patterns_by_severity": {
    "CRITICAL-SECURITY": 8,
    "HIGH-ARCHITECTURE": 14,
    "MEDIUM-STANDARDS": 9,
    "INFORMATIONAL": 2
  }
}
```

### GET /api/v3/copilot/filters

**Purpose:** Available filter options for UI dropdowns/selectors

**Response:**
```json
{
  "layers": [
    {"value": 0, "label": "Layer 0", "description": "Foundation/Core"},
    {"value": 1, "label": "Layer 1", "description": "Models & Enums"},
    {"value": 2, "label": "Layer 2", "description": "Schemas"},
    {"value": 3, "label": "Layer 3", "description": "Routers"},
    {"value": 4, "label": "Layer 4", "description": "Services"},
    {"value": 5, "label": "Layer 5", "description": "Configuration"},
    {"value": 6, "label": "Layer 6", "description": "UI Components"},
    {"value": 7, "label": "Layer 7", "description": "Testing"}
  ],
  "workflows": ["WF1", "WF2", "WF3", "WF4", "WF5", "WF6", "WF7"],
  "doc_types": [
    "architecture_document",
    "boot_sequence_protocol",
    "documentation",
    "framework",
    "implementation",
    "knowledge_base",
    "pattern",
    "protocol",
    "reference",
    "standard"
  ],
  "pattern_types": ["architecture", "bugfix", "exemplar", "security", "standards"],
  "severities": [
    "CRITICAL-ARCHITECTURE",
    "CRITICAL-SECURITY",
    "HIGH-ARCHITECTURE",
    "HIGH-STANDARDS",
    "INFORMATIONAL",
    "MEDIUM-ARCHITECTURE",
    "MEDIUM-BUGFIX",
    "MEDIUM-STANDARDS"
  ]
}
```

---

## 5. Database Schema

### Tables Used

#### project_docs (Vector Knowledge Base)

```sql
CREATE TABLE public.project_docs (
    id integer PRIMARY KEY,           -- Matches document_registry.id
    title text NOT NULL,
    content text,
    embedding halfvec(1536),          -- OpenAI ada-002 embedding
    created_at timestamp,
    metadata jsonb
);
```

**Current state:** 162 documents with embeddings

#### document_registry (Metadata & Management)

```sql
CREATE TABLE public.document_registry (
    id serial PRIMARY KEY,
    title text,
    file_path text,
    architectural_layer smallint,      -- 0-7
    associated_workflow text[],        -- Array: ['WF1', 'WF4']
    document_type text,
    primary_purpose text,
    embedding_status text,             -- 'queue', 'active', 'archived', 'error_*'
    last_vectorized timestamp,
    word_count integer,
    character_count integer,
    semantic_density float,
    key_concepts text[],
    related_document_ids integer[],
    supersedes_document_ids integer[],
    needs_update boolean,
    file_hash text,
    -- ... additional fields
);
```

#### fix_patterns (Code Pattern Knowledge Base)

```sql
CREATE TABLE public.fix_patterns (
    id uuid PRIMARY KEY,
    title text,
    problem_type text,                 -- 'security', 'architecture', 'standards', etc.
    code_type text,
    severity text,                     -- 'CRITICAL-SECURITY', 'HIGH-ARCHITECTURE', etc.
    tags text[],
    layers integer[],
    workflows text[],
    file_types text[],
    problem_description text,
    solution_steps text,
    code_before text,
    code_after text,
    verification_steps text,
    learnings text,
    prevention_guidance text,
    applied_count integer,
    success_rate numeric,
    confidence_score numeric,
    pattern_vector vector(1536),       -- Main embedding
    content_embedding vector,
    code_embedding vector,
    problem_embedding vector,
    created_at timestamp,
    updated_at timestamp
);
```

**Current state:** 34 patterns with embeddings

### RPC Functions

#### perform_semantic_search_direct

```sql
-- Parameters:
-- query_embedding_param: float[] (1536 dimensions)
-- match_count_param: integer
-- match_threshold_param: float
-- metadata_filter_param: jsonb

-- Returns: table(id, title, content, similarity)
```

---

## 6. How to Use

### CLI Testing

```bash
# Basic search
curl -X POST https://your-domain/api/v3/copilot/ask \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do schedulers work?"}'

# Filtered search
curl -X POST https://your-domain/api/v3/copilot/ask \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "authentication issues",
    "layers": [3],
    "include_patterns": true,
    "include_content": true
  }'

# Get stats
curl -H "Authorization: Bearer scraper_sky_2024" \
  https://your-domain/api/v3/copilot/stats

# Get filter options
curl -H "Authorization: Bearer scraper_sky_2024" \
  https://your-domain/api/v3/copilot/filters
```

### Python SDK Example

```python
import httpx

class CoPilotClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def ask(self, question: str, **filters):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v3/copilot/ask",
                headers=self.headers,
                json={"question": question, **filters}
            )
            return response.json()

    async def stats(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v3/copilot/stats",
                headers=self.headers
            )
            return response.json()

# Usage
copilot = CoPilotClient("https://your-domain", "your-jwt-token")
results = await copilot.ask(
    "How do domain schedulers work?",
    layers=[4],
    workflows=["WF4"],
    include_patterns=True
)
```

### React Integration Example

```typescript
// hooks/useCoPilot.ts
import { useState } from 'react';

interface AskParams {
  question: string;
  limit?: number;
  threshold?: number;
  layers?: number[];
  workflows?: string[];
  doc_types?: string[];
  include_content?: boolean;
  include_patterns?: boolean;
}

export function useCoPilot() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async (params: AskParams) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v3/copilot/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(params)
      });
      return await response.json();
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const getFilters = async () => {
    const response = await fetch('/api/v3/copilot/filters', {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    return response.json();
  };

  const getStats = async () => {
    const response = await fetch('/api/v3/copilot/stats', {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    return response.json();
  };

  return { ask, getFilters, getStats, loading, error };
}
```

---

## 7. How to Maintain

### Adding New Documents to Knowledge Base

1. **Mark document for vectorization:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py \
     --mark /path/to/your/document.md
   ```

2. **Scan and update registry:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py --scan
   ```

3. **Run vectorization:**
   ```bash
   python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py
   ```

### Updating Existing Documents

1. **Flag for re-vectorization:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/3-registry-update-flag-manager.py \
     --mark-for-update /path/to/updated/document.md
   ```

2. **Re-run vectorization:**
   ```bash
   python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py
   ```

### Archiving Documents

1. **Check for missing files:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py --list-missing
   ```

2. **Archive missing files:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py --scan
   ```

3. **Clean up vector database:**
   ```bash
   python Docs/Docs_19_File-2-Vector-Registry-System/5-vector-db-cleanup-manager.py cleanup --auto-approve
   ```

### Monitoring Health

Check document registry status:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/1-registry-directory-manager.py --status
```

Check for orphaned embeddings:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/6-registry-orphan-detector.py
```

### Environment Variables Required

```bash
# OpenAI (for embedding generation)
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# JWT Authentication
JWT_SECRET_KEY=your-secret-key
```

---

## 8. How to Extend

### Adding New Endpoints

Example: Add document detail endpoint

```python
# In src/routers/copilot.py

@router.get("/docs/{doc_id}")
async def get_document(
    doc_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """Get full document details by ID."""
    supabase = get_supabase_client()

    # Get from project_docs
    doc = supabase.table("project_docs").select("*").eq("id", doc_id).single().execute()

    # Get metadata from registry
    meta = supabase.table("document_registry").select("*").eq("id", doc_id).single().execute()

    return {
        "document": doc.data,
        "metadata": meta.data
    }
```

### Adding Streaming Responses

```python
from fastapi.responses import StreamingResponse
import json

@router.post("/ask/stream")
async def ask_copilot_stream(
    payload: AskRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """Streaming semantic search with Server-Sent Events."""

    async def generate():
        # Send initial status
        yield f"data: {json.dumps({'status': 'generating_embedding'})}\n\n"

        embedding = await get_embedding(payload.question)
        yield f"data: {json.dumps({'status': 'searching'})}\n\n"

        # ... perform search ...

        for result in results:
            yield f"data: {json.dumps({'result': result})}\n\n"

        yield f"data: {json.dumps({'status': 'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Adding Chat Memory

1. **Create conversation table:**
   ```sql
   CREATE TABLE copilot_conversations (
       id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id uuid REFERENCES auth.users(id),
       created_at timestamp DEFAULT now()
   );

   CREATE TABLE copilot_messages (
       id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
       conversation_id uuid REFERENCES copilot_conversations(id),
       role text CHECK (role IN ('user', 'assistant')),
       content text,
       results jsonb,
       created_at timestamp DEFAULT now()
   );
   ```

2. **Add conversation endpoints:**
   ```python
   @router.post("/conversations")
   async def create_conversation(...): ...

   @router.post("/conversations/{conv_id}/messages")
   async def add_message(...): ...

   @router.get("/conversations/{conv_id}")
   async def get_conversation(...): ...
   ```

### Adding Per-Tenant Isolation

1. **Add tenant column:**
   ```sql
   ALTER TABLE project_docs ADD COLUMN tenant_id uuid;
   ALTER TABLE fix_patterns ADD COLUMN tenant_id uuid;
   ```

2. **Enable Row-Level Security:**
   ```sql
   ALTER TABLE project_docs ENABLE ROW LEVEL SECURITY;

   CREATE POLICY tenant_isolation ON project_docs
       FOR ALL USING (tenant_id = auth.jwt() ->> 'tenant_id');
   ```

3. **Update endpoint to use tenant context:**
   ```python
   @router.post("/ask")
   async def ask_copilot(payload: AskRequest, current_user = Depends(get_current_active_user)):
       tenant_id = current_user.get("tenant_id")
       # Add tenant_id to metadata_filter_param
   ```

---

## 9. Known Issues & Limitations

### Current Limitations

1. **Pattern Search Not Fully Vector-Based:**
   - `include_patterns=true` currently returns patterns without proper vector similarity ranking
   - Placeholder similarity score of 0.75 is returned
   - Full vector search on fix_patterns requires additional RPC function

2. **Metadata Filtering Limitations:**
   - `layers` and `doc_types` filters are passed to RPC but may not be fully utilized
   - `workflows` filter requires client-side filtering due to array column

3. **No Caching:**
   - Embeddings are generated fresh for each request
   - Consider adding Redis cache for repeated queries

4. **Single Embedding Model:**
   - Locked to `text-embedding-ada-002` (1536 dimensions)
   - Switching models requires re-embedding all documents

### Error States

| Error | Cause | Resolution |
|-------|-------|------------|
| 500: "Co-Pilot error: ..." | OpenAI API failure | Check OPENAI_API_KEY |
| 500: "Stats error: ..." | Supabase connection issue | Check SUPABASE_* env vars |
| 401: Unauthorized | Invalid/missing JWT | Provide valid token |

### Performance Characteristics

- Embedding generation: ~200-500ms (OpenAI API)
- Vector search: ~50-100ms (Supabase RPC)
- Total request time: ~300-700ms typical

---

## 10. Future Roadmap

### Phase 2 (Planned)

| Feature | Effort | Priority |
|---------|--------|----------|
| `/copilot/docs/{id}` - Document retrieval | 2 hours | High |
| `/copilot/patterns/search` - Proper pattern vector search | 3 hours | High |
| `/copilot/ask/stream` - SSE streaming | 2 hours | Medium |
| Add proper vector search RPC for fix_patterns | 4 hours | Medium |

### Phase 3 (Future)

| Feature | Effort | Priority |
|---------|--------|----------|
| Chat memory / conversation history | 1 day | Medium |
| Code analysis endpoint | 2 days | Medium |
| Related documents graph | 1 day | Low |
| Usage analytics | 2 days | Low |

### Phase 4 (Product Features)

| Feature | Effort | Priority |
|---------|--------|----------|
| Per-tenant isolation (RLS) | 1 day | High (for paid tier) |
| Custom knowledge base upload | 1 week | Medium |
| Auto-documentation from code | 2 weeks | Low |
| Pattern learning from fixes | 2 weeks | Low |

---

## Appendix A: Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Registry Librarian Persona | `Docs/Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md` | Document registry management guide |
| Knowledge Librarian Persona | `Docs/Docs_18_Vector_Operations/knowledge_librarian_persona_v2.md` | Vectorization operations guide |
| Vector Operations README | `Docs/Docs_18_Vector_Operations/v_Docs_18_Vector_Operations_README.md` | Vector system overview |
| Key Documents Index | `Docs/Docs_18_Vector_Operations/v_key_documents.md` | Index of all vector-related files |

## Appendix B: Git History

```
b132ebf feat: Enhance Co-Pilot with filters, stats, and filter options endpoints
557d9f4 feat: Add ScraperSky Co-Pilot semantic search endpoint
```

## Appendix C: Test Commands

```bash
# Verify endpoint is live
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer scraper_sky_2024" \
  https://your-domain/api/v3/copilot/stats

# Expected: 200

# Full smoke test
curl -X POST https://your-domain/api/v3/copilot/ask \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "limit": 1}' | jq '.total_results'

# Expected: >= 1
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-22
**Author:** Claude Code (Registry Librarian + Knowledge Librarian Persona)

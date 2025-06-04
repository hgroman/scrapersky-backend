# ScraperSky Vector Database: Complete Reference Guide

**Date:** 2025-06-03  
**Version:** 1.1  
**Status:** Active  

## Purpose

This document serves as the comprehensive reference guide for the ScraperSky Vector Database system. It consolidates references to all key documents, scripts, and tools related to the vector database, ensuring that all AI pairing partners and personas have a complete understanding of the system.

## Vector Database Overview

The ScraperSky Vector Database is a semantic search system built on Supabase PostgreSQL with the pgvector extension. It stores embeddings of architectural documents, enabling semantic search across the codebase's architectural standards, patterns, and guidelines.

## Key Documents

### Core Documentation

1. **Entry Point:** [`README_Vector_DB.md`](../../../README_Vector_DB.md)
   - High-level overview of the vector database
   - Purpose and context
   - Links to detailed documentation

2. **Technical Reference:** [`v_living_document.md`](./v_living_document.md)
   - Comprehensive technical details
   - Database schema and setup
   - Embedding generation

3. **MCP Server Integration:** [`v_mcp_guide.md`](./v_mcp_guide.md)
   - **CRITICAL:** Contains the correct function name and project ID
   - Example queries for all common operations
   - Troubleshooting guidance

4. **Knowledge Librarian Persona:** [`Path1_Knowledge_Librarian_Persona.md`](../../Docs_16_ScraperSky_Code_Canon/Path1_Knowledge_Librarian_Persona.md)
   - Instructions for the Knowledge Librarian AI persona
   - Responsibilities and operational parameters
   - References to the authoritative documentation sources

5. **AI Guides Reference:** [`35-LAYER5_VECTOR_DATABASE_REFERENCE.md`](../../Docs_1_AI_GUIDES/35-LAYER5_VECTOR_DATABASE_REFERENCE.md)
   - Pointer to all authoritative documentation sources
   - Clear identification of which documents are authoritative

### Registry and Maintenance

6. **Document Registry:** [`document_registry.md`](../Registry/document_registry.md)
   - Current list of documents in the vector database
   - Documents not yet ingested with reasons

7. **Registry Generator:** [`generate_document_registry.py`](../Scripts/generate_document_registry.py)
   - Script to update the document registry
   - Connects to the database and generates markdown table

8. **Documentation Loader:** [`load_documentation.py`](../Scripts/load_documentation.py)
   - Script to load all vector database documentation into the vector database
   - Ensures documentation is searchable within the system itself

### Scripts and Tools

9. **Document Insertion:** [`insert_architectural_docs.py`](../Scripts/insert_architectural_docs.py)
   - Script to insert architectural documents into the vector database
   - Generates embeddings and inserts into the database

10. **Testing Script:** [`simple_test.py`](../Scripts/simple_test.py)
    - Script to test vector database functionality
    - Performs semantic search and verifies results

11. **NaN Issue Resolution:** [`v_nan_issue_resolution.md`](./v_nan_issue_resolution.md)
    - Resolution for the "Similarity: nan" issue
    - Vector normalization fix

## CRITICAL: MCP Server Integration

To query the vector database, you **MUST** use the following specific parameters:

1. **Function Name:** `mcp4_execute_sql` (not just "execute_sql")
2. **Project ID:** `ddfldwzhdhhzhxywqnyz` (always use this exact ID)

Example query for semantic search:
```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT * FROM search_docs('your search query', 0.5);"
})
```

## Document Registry Management

The document registry is maintained using the `generate_document_registry.py` script, which:
- Connects directly to the vector database using asyncpg
- Generates a markdown table of all documents in the database
- Identifies documents that are not yet ingested
- Prevents documents from being listed in both categories
- Outputs the registry to `document_registry.md`

To update the document registry:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/generate_document_registry.py
```

## Loading Vector Database Documentation

To ensure that all documentation about the vector database is searchable within the vector database itself, use the `load_documentation.py` script:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/load_documentation.py
```

This script will:
1. Load all key vector database documents into the database
2. Update existing documents if they've changed
3. Generate embeddings for semantic search
4. Update the document registry

## Test Questions

The following questions can be used to test understanding of the vector database system:

1. **MCP Query Test**: "How do I query the vector database to find documents related to transaction management?"
   - Expected: Use `mcp4_execute_sql` with project ID `ddfldwzhdhhzhxywqnyz` and a search_docs query

2. **Registry Check**: "How can I check which documents are currently in the vector database and which still need to be ingested?"
   - Expected: Reference the document registry or run the registry generator script

3. **Registry Update**: "What script should I run to update the document registry after adding new documents to the vector database?"
   - Expected: Run `generate_document_registry.py` in the Docs_18_Vector_Operations/Scripts directory

4. **Project ID Verification**: "What is the correct project ID to use when querying the vector database through the MCP server?"
   - Expected: `ddfldwzhdhhzhxywqnyz`

5. **Document Count**: "How many documents are currently in the vector database and how can I verify this count?"
   - Expected: 21 documents, verify by checking the document registry or querying the database

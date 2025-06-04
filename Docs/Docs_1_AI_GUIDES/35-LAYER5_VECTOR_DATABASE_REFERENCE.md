# LAYER5: Vector Database Reference Guide

**Status:** Active  
**Version:** 1.0  
**Last Updated:** 2025-06-03  

## Purpose

This document serves as a pointer to the authoritative sources of information about the ScraperSky Vector Database. It ensures that all AI pairing partners and personas have a consistent understanding of how to interact with the vector database.

## Authoritative Documentation Sources

The following are the **ONLY** authoritative sources for vector database information:

1. **Entry Point:** `README_Vector_DB.md` (project root)
   - High-level overview of the vector database
   - Purpose and context
   - Links to detailed documentation

2. **Technical Reference:** `Docs/Docs_18_Vector_Operations/Documentation/v_living_document.md`
   - Comprehensive technical details
   - Database schema and setup
   - Embedding generation

3. **MCP Connectivity:** `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md`
   - **CRITICAL:** Contains the correct function name and project ID
   - Example queries for all common operations
   - Troubleshooting guidance for manual operations

4. **Asyncpg Connectivity:** `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md`
   - Documents both database connectivity methods (MCP and asyncpg)
   - Explains when to use each method and technical requirements
   - Implementation details for vector operations scripts

5. **Document Loading Guide:** `Docs/Docs_18_Vector_Operations/Documentation/v_Add_docs_to_register_and_vector_db.md`
   - Step-by-step process for adding documents to the vector database
   - Registry update procedures
   - Verification steps

6. **Document Registry:** 
   - `Docs/Docs_18_Vector_Operations/Registry/document_registry.md` (current registry)
   - `Docs/Docs_18_Vector_Operations/Scripts/generate_document_registry.py` (script to update registry)
   - Provides a complete list of documents in the vector database
   - Identifies documents that are not yet ingested

7. **Knowledge Librarian Persona:** `Docs/Docs_18_Vector_Operations/Documentation/v_knowledge_librarian_persona.md`
   - Instructions for the Knowledge Librarian AI persona
   - Responsibilities and operational parameters
   - References to the authoritative documentation sources

## Critical Information

When interacting with the vector database, always remember:

1. **Two Connectivity Methods:**
   - **MCP Method:** Use for manual operations and ad-hoc queries (see `v_db_connectivity_mcp_4_manual_ops.md`)
   - **Asyncpg Method:** Used in vector database scripts with specific technical requirements (see `v_db_connectivity_async_4_vector_ops.md`)
   - Each method has its own specific implementation requirements

2. **MCP Function Name:** Always use `mcp4_execute_sql` (not just "execute_sql")
3. **Project ID:** Always use `ddfldwzhdhhzhxywqnyz` as the project_id parameter
4. **Search Function:** Use `search_docs('query text', threshold)` for semantic search
5. **Embedding Format:** Ensure embeddings are properly normalized to prevent "Similarity: nan" issues

## Do Not Use

The following documents are **NOT** authoritative and should not be referenced:

- `Docs/Docs_Archive/vector_db_mcp_guide.md` (superseded by consolidated guide)
- `Docs/Docs_Archive/mcp_server_section.md` (superseded by consolidated guide)
- `Docs/Docs_16_ScraperSky_Code_Canon/` (now an archive directory, superseded by `Docs/Docs_18_Vector_Operations/`)
- Any other documents discussing vector database implementation not listed in the authoritative sources

## For More Information

For detailed information about vector database implementation, refer to the authoritative documentation sources listed above. Do not create new documentation about the vector database without updating this reference guide.

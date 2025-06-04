# ScraperSky Vector Database System

**Date:** 2025-06-03  
**Version:** 1.0  
**Status:** Active  

## Purpose

This directory contains all resources related to the ScraperSky Vector Database system, which serves as the foundation for the Knowledge Librarian AI persona and enables semantic search across architectural documentation.

## Directory Structure

The Vector DB resources are organized as follows:

```
Docs_18_Vector_Operations/
├── Documentation/  (Core documentation files)
│   ├── v_living_document.md         (Technical reference)
│   ├── v_mcp_guide.md               (MCP server integration guide)
│   ├── v_complete_reference.md      (Comprehensive reference guide)
│   ├── v_key_documents.md           (List of key vector DB documents)
│   ├── v_knowledge_librarian_persona.md  (Knowledge Librarian AI persona)
│   └── v_nan_issue_resolution.md    (Resolution for "Similarity: nan" issue)
├── Scripts/        (Python scripts for managing the vector DB)
│   ├── insert_architectural_docs.py    (Document insertion script)
│   ├── simple_test.py                  (Testing script)
│   ├── generate_document_registry.py   (Registry generation script)
│   └── load_documentation.py           (Documentation loader script)
├── Registry/       (Document registry)
│   └── v_document_registry.md      (Auto-generated registry of documents)
└── Setup/          (Setup and infrastructure documentation)
    └── v_supabase_setup.md         (Supabase vector setup guide)
```

## Naming Conventions

- **Vectorized Documents:** Files with the `v_` prefix are specifically marked for inclusion in the vector database
- **Supporting Files:** Scripts, tools, and other supporting files maintain their original naming

The `v_` prefix serves as a clear visual indicator of which documents are intended to be embedded in the vector database.

## Key Documentation

1. **v_living_document.md**: The comprehensive technical reference for the vector database system.
2. **v_mcp_guide.md**: Guide for interacting with the vector database through the MCP server.
3. **v_complete_reference.md**: A consolidated reference guide that links to all other documentation.
4. **v_key_documents.md**: A list of all key documents related to the vector database.
5. **v_nan_issue_resolution.md**: Documentation of the "Similarity: nan" issue and its resolution.

## Scripts

1. **v_insert_architectural_docs.py**: Script for inserting architectural documents into the vector database.
2. **v_simple_test.py**: Script for testing vector database functionality.
3. **v_generate_document_registry.py**: Script for generating the document registry.
4. **v_load_documentation.py**: Script for loading vector database documentation into the database itself.

## Critical Information

- **MCP Function:** `mcp4_execute_sql`
- **Project ID:** `ddfldwzhdhhzhxywqnyz`
- **Database Table:** `public.project_docs`
- **Search Function:** `search_docs(query_text, similarity_threshold)`

## Maintenance Procedures

### Updating the Document Registry

After adding new documents to the vector database, update the registry:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/generate_document_registry.py
```

### Loading Vector DB Documentation

To ensure all vector database documentation is searchable within the system:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/load_documentation.py
```

### Testing Vector DB Functionality

To verify that the vector database is working correctly:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/simple_test.py
```

## Historical Context

The original vector database implementation and documentation can be found in the `Docs/Docs_16_ScraperSky_Code_Canon/` directory. These documents are preserved for historical context but are no longer part of the active operational documentation. The new structure with the `v_` prefix naming convention provides a more consistent and maintainable approach to vector database documentation and scripts.

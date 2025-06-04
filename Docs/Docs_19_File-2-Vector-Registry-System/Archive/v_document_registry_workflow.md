# Document Registry Workflow Guide

**Date:** 2025-06-03
**Status:** Active
**Version:** 1.0
**Author:** Cascade AI

## Overview

This document outlines the workflow for managing ScraperSky's enhanced document registry system. The document registry is a database-driven solution that tracks which documents should be included in the vector database, their current embedding status, architectural relevance, and relationships to other documents.

## Purpose

The enhanced document registry system serves several critical purposes:

1. **Single Source of Truth** - Provides a definitive list of documents that should be vectorized
2. **Architectural Context** - Maps documents to ScraperSky's 7-layer architecture
3. **Status Tracking** - Monitors which documents have been embedded and which are pending
4. **Relationship Mapping** - Tracks how documents relate to each other
5. **Technical Debt Management** - Links documentation to technical debt items

## Key Components

1. **Database Tables**:
   - `document_registry` - Main registry of all documents
   - `document_relationships` - Tracks relationships between documents
   - `document_versions` - Records document version history
   - `technical_debt_mappings` - Links documents to technical debt items

2. **Views and Functions**:
   - `document_status_dashboard` - Current status by architectural layer
   - `document_review_schedule` - Schedule of pending document reviews
   - `pending_vectorization` - Documents that should be vectorized but aren't
   - `sync_registry_status()` - Syncs registry with `project_docs` table
   - `find_pattern_documents()` - Finds documents related to a pattern
   - `get_vectorization_summary()` - Gets summary statistics

3. **Management Script**:
   - `manage_document_registry.py` - Scans filesystem, syncs with database, generates reports

## Standard Workflows

### 1. Adding a New Document

When creating a new document that should be included in the vector database:

1. **Create Document with `v_` Prefix**:
   ```bash
   # Create a new document in the appropriate directory
   touch Docs/Docs_18_Vector_Operations/Documentation/v_my_new_document.md
   ```

2. **Scan Registry to Add Document**:
   ```bash
   # From the project root
   cd Docs/Docs_18_Vector_Operations/Scripts
   python manage_document_registry.py --scan
   ```

3. **Modify Document Metadata (Optional)**:
   ```sql
   -- Using MCP to update metadata
   UPDATE document_registry 
   SET 
     architectural_layer = 5,
     document_type = 'reference',
     primary_purpose = 'implementation guide',
     maintainer = 'Henry Groman',
     review_frequency = 'quarterly',
     next_review_date = '2025-09-03'
   WHERE title = 'v_my_new_document.md';
   ```

4. **Add Document to Vector Database**:
   ```bash
   # Use existing script to add document to vector database
   python insert_document.py --file "Docs/Docs_18_Vector_Operations/Documentation/v_my_new_document.md"
   ```

5. **Sync Registry Status**:
   ```bash
   # Sync registry with project_docs
   python manage_document_registry.py --sync
   ```

6. **Generate Report (Optional)**:
   ```bash
   # Generate status report
   python manage_document_registry.py --report
   ```

### 2. Checking Document Status

To check the current status of the document registry:

1. **Generate Status Report**:
   ```bash
   # Generate comprehensive report
   python manage_document_registry.py --report
   ```

2. **Query Database Directly**:
   ```sql
   -- Using MCP to get summary statistics
   SELECT * FROM get_vectorization_summary();
   
   -- View documents by architectural layer
   SELECT * FROM document_status_dashboard;
   
   -- View documents pending vectorization
   SELECT * FROM pending_vectorization;
   ```

### 3. Document Relationship Management

To establish relationships between documents:

1. **Add Relationship**:
   ```sql
   -- Using MCP to add a relationship
   INSERT INTO document_relationships (
     source_document_id, 
     target_document_id,
     relationship_type,
     strength,
     notes
   )
   VALUES (
     (SELECT id FROM document_registry WHERE title = 'v_document_a.md'),
     (SELECT id FROM document_registry WHERE title = 'v_document_b.md'),
     'implements',  -- relationship type
     0.8,  -- strength (0.0-1.0)
     'Document A implements the pattern described in Document B'
   );
   ```

2. **Query Related Documents**:
   ```sql
   -- Using MCP to find related documents
   SELECT r2.title, r.relationship_type, r.strength
   FROM document_relationships r
   JOIN document_registry r1 ON r.source_document_id = r1.id
   JOIN document_registry r2 ON r.target_document_id = r2.id
   WHERE r1.title = 'v_document_a.md';
   ```

### 4. Technical Debt Tracking

To track technical debt items mentioned in documents:

1. **Add Technical Debt Item**:
   ```sql
   -- Using MCP to add a technical debt item
   INSERT INTO technical_debt_mappings (
     document_id,
     debt_category,
     affected_files,
     priority,
     remediation_strategy,
     completed,
     notes
   )
   VALUES (
     (SELECT id FROM document_registry WHERE title = 'v_technical_debt_review.md'),
     'inconsistent transactions',
     ARRAY['app/routers/users.py', 'app/routers/orders.py'],
     'high',
     'Refactor transaction management to use consistent pattern',
     false,
     'Identified during 2025 Q2 architecture review'
   );
   ```

2. **Query Technical Debt by Priority**:
   ```sql
   -- Using MCP to find high priority technical debt
   SELECT 
     r.title as document,
     t.debt_category,
     t.priority,
     t.affected_files,
     t.remediation_strategy
   FROM technical_debt_mappings t
   JOIN document_registry r ON t.document_id = r.id
   WHERE t.priority = 'high' AND t.completed = false
   ORDER BY t.debt_category;
   ```

### 5. Complete Synchronization

To perform a complete synchronization of the document registry:

```bash
# From the project root
cd Docs/Docs_18_Vector_Operations/Scripts
python manage_document_registry.py --scan --sync --report
```

This will:
1. Scan the filesystem for documents with `v_` prefix
2. Add/update them in the document registry
3. Sync the registry with the `project_docs` table
4. Generate a status report

## Integration with Knowledge Librarian Persona

The enhanced document registry is fully compatible with the Knowledge Librarian persona's workflow:

1. The Knowledge Librarian can query the registry to understand what documents are available
2. The registry provides architectural context to help the Knowledge Librarian understand document relationships
3. The status tracking enables the Knowledge Librarian to know which documents are embedded and which are not
4. Technical debt mappings provide the Knowledge Librarian with refactoring guidance

## Registry Management Best Practices

1. **Keep `v_` Prefix Convention**:
   - Only use the `v_` prefix for documents that should be vectorized
   - Scripts and supporting files should not have the `v_` prefix

2. **Update Registry Regularly**:
   - Run `manage_document_registry.py --scan --sync` after adding new documents
   - Generate reports (`--report`) before major refactoring efforts

3. **Maintain Architectural Mapping**:
   - Always assign an appropriate architectural layer to new documents
   - Use the document type and purpose fields to clarify document intent

4. **Track Document Relationships**:
   - Add relationships between related documents
   - Use the strength field to indicate relationship importance

5. **Technical Debt Management**:
   - Link technical debt items to relevant documentation
   - Update the completion status as debt is addressed

## Registry Schema Reference

For reference, here's the full schema of the main `document_registry` table:

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | TEXT | Document title (filename) |
| file_path | TEXT | Relative path from project root |
| architectural_layer | SMALLINT | Layer in ScraperSky architecture (1-7) |
| associated_workflow | TEXT[] | Array of workflows this document relates to |
| document_type | TEXT | Document type (standard, pattern, etc.) |
| primary_purpose | TEXT | Primary purpose of document |
| should_be_vectorized | BOOLEAN | Whether document should be vectorized |
| is_vectorized | BOOLEAN | Whether document is currently vectorized |
| embedding_status | TEXT | Status of embedding process |
| last_vectorized | TIMESTAMP | When document was last vectorized |
| last_checked | TIMESTAMP | When document status was last checked |
| word_count | INTEGER | Number of words in document |
| character_count | INTEGER | Number of characters in document |
| semantic_density | FLOAT | Measure of semantic information density |
| key_concepts | TEXT[] | Key concepts extracted from document |
| related_document_ids | INTEGER[] | IDs of related documents |
| supersedes_document_ids | INTEGER[] | IDs of documents this supersedes |
| superseded_by_document_id | INTEGER | ID of document that supersedes this |
| maintainer | TEXT | Document maintainer |
| review_frequency | TEXT | How often document should be reviewed |
| next_review_date | DATE | When document should next be reviewed |
| notes | TEXT | General notes about document |
| created_at | TIMESTAMP | When record was created |
| updated_at | TIMESTAMP | When record was last updated |

## Conclusion

The enhanced document registry system provides a robust foundation for managing ScraperSky's vectorized documentation. By following the workflows and best practices outlined in this guide, you can ensure that the vector database remains accurate, up-to-date, and aligned with ScraperSky's architectural principles.

For more information, refer to:
- The `document_status_report.md` in the Registry directory
- The database views and functions created by the registry system
- The `manage_document_registry.py` script documentation

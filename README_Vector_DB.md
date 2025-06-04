# ScraperSky Vector DB: AI-Driven Technical Debt Elimination

## Purpose
This document serves as the primary entry point for developers and AI pairing partners to understand and interact with the ScraperSky Vector Database system. The vector database provides semantic search capabilities across architectural documentation, enabling pattern-based refactoring and architectural compliance verification.

## Core Context & The Project's Journey

ScraperSky is a FastAPI-based web scraping and analytics platform that has undergone a dramatic transformation from an "over-engineered nightmare" into a disciplined, 7-layered architectural system. This journey is defined by a militant effort to eliminate technical debt (e.g., inconsistent transactions, raw SQL, scattered logic) and enforce strict standards. The Vector DB is a direct response to the challenge of enabling AI partners to effectively contribute to this refactoring effort by providing a comprehensive, synthesized knowledge base, ensuring "zero-effort" access to architectural truth.

## Project Context
The ScraperSky backend uses a vector database implemented in Supabase PostgreSQL with the pgvector extension. This enables semantic search across architectural documents, allowing AI pairing partners to find relevant architectural patterns, conventions, and examples.

## Current Status
- ✅ Database setup complete with Supabase
- ✅ 21 core architectural documents loaded
- ✅ OpenAI integration functional
- ✅ Search functionality verified
- ✅ ScraperSky Librarian persona established

## CRITICAL: Database Connectivity

The vector database system uses two distinct connectivity methods:

### 1. MCP Method (For Manual Operations)
To perform manual queries and operations on the vector database, you **MUST** use the following specific parameters:

- **Function Name:** `mcp4_execute_sql` (not just "execute_sql")
- **Project ID:** `ddfldwzhdhhzhxywqnyz` (always use this exact ID)

Example query for semantic search:
```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT * FROM search_docs('your search query', 0.5);"
})
```

See `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md` for complete details.

### 2. Asyncpg Method (For Vector Database Scripts)
Vector database scripts like `insert_architectural_docs.py` use direct asyncpg connections with specific technical requirements. Do not modify these connection patterns without consulting the connectivity guide.

See `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md` for complete implementation details.

## Key Files
- `Docs/Docs_18_Vector_Operations/Documentation/v_living_document.md` - Primary reference
- `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md` - MCP connectivity for manual operations
- `Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md` - Asyncpg connectivity for vector scripts
- `Docs/Docs_18_Vector_Operations/Documentation/v_Add_docs_to_register_and_vector_db.md` - Document loading process guide
- `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py` - Document insertion
- `Docs/Docs_18_Vector_Operations/Scripts/simple_test.py` - Testing functionality
- `Docs/Docs_18_Vector_Operations/Registry/document_registry.md` - Local document tracking registry
- `Docs/Docs_18_Vector_Operations/Documentation/v_complete_reference.md` - Complete reference guide

## ScraperSky Librarian Persona

The ScraperSky Librarian is an AI persona designed to manage the Vector DB without requiring technical intervention from users. This persona handles all aspects of Vector DB management, including document discovery, loading, searching, and analysis.

### Activating the Librarian

To activate the Librarian persona in any new chat session with your AI pairing partner, simply type:

```
Activate ScraperSky Librarian persona
```

### Zero-Effort Workflows

1. **Finding Patterns**
   ```
   Find patterns about: [topic]
   ```
   Example: "Find patterns about: authentication in Layer 4"

2. **Adding Documents**
   ```
   Add this document to the Vector DB: [document path]
   ```
   Example: "Add this document to the Vector DB: Docs/API_Standards/versioning.md"

3. **Discovering Documents**
   ```
   Find documents about [topic] that should be added to the Vector DB
   ```
   Example: "Find documents about API versioning that should be added to the Vector DB"

4. **Checking Status**
   ```
   What's in the Vector DB now?
   ```

5. **Comparing Documents**
   ```
   Compare this document against our Vector DB knowledge: [document path]
   ```
   Example: "Compare this document against our Vector DB knowledge: Docs/Docs_10_Final_Audit/Audit Reports Layer 1/Layer1_Models_Enums_Audit_Report.md"

### No Technical Knowledge Required

The Librarian persona handles all technical aspects:
- Running insertion scripts
- Executing database queries
- Managing OpenAI API calls
- Tracking document status
- Updating memory records

## Technical Debt Elimination Strategy

The Vector DB is a central component in our comprehensive technical debt elimination strategy:

### Process Overview
1. Load architectural standards and patterns into Vector DB
2. Process audit reports for each layer (1-4) and workflow
3. Compare audit findings against architectural standards
4. Identify patterns to apply for remediation
5. Track implementation of fixes across the codebase

### Current Focus Areas
- Layer 1: Models and Enums
- Layer 2: Data Access
- Layer 3: Business Logic
- Layer 4: API Services
- Cross-cutting workflows

### Implementation Approach
- Use Vector DB to identify applicable patterns for each audit finding
- Prioritize fixes based on security and architectural impact
- Apply consistent patterns across similar issues
- Document all changes in DART
- Verify fixes against architectural standards

## Currently Loaded Documents

The Librarian persona automatically tracks all documents in the Vector DB. To see the current list, simply ask:
```
What's in the Vector DB now?
```

The current knowledge base includes 13 core architectural documents covering:
- Layer 4 Services architecture
- Authentication patterns
- Transaction management
- API versioning standards
- Error handling patterns
- Security requirements
- And more...

## Cost Considerations

The Vector DB incurs OpenAI API costs in two scenarios:

1. **When Adding Documents**: Each document added requires generating embeddings via OpenAI API
2. **When Searching**: Each search query requires generating an embedding for the query text

The costs are relatively minimal:
- Document embedding: ~$0.0004-0.0008 per document
- Search query: ~$0.0001 per query

## Getting Started with the Librarian Persona

The ScraperSky Librarian persona is designed to eliminate all technical overhead when working with the Vector DB:

1. **Activate the Persona**:
   ```
   Activate ScraperSky Librarian persona
   ```
   This single command activates all Vector DB capabilities without requiring technical setup.

2. **Start Working Immediately**:
   No need to share context, status, or copy-paste any information. The persona maintains all necessary context through the memory system.

3. **Focus on Strategic Questions**:
   ```
   Which patterns should we apply to fix the Layer 1 model issues?
   ```
   ```
   How do our current API endpoints compare to the v3 versioning standard?
   ```
   ```
   What architectural patterns address the security findings in the audit?
   ```

## Troubleshooting

If you encounter issues, the Librarian persona can help diagnose and resolve them. Common issues include:

- **API Key Problems**: The Librarian will verify API key configuration
- **Database Connection**: Connection string format will be validated
- **Missing Embeddings**: The Librarian can identify and fix documents with NULL embeddings
- **Search Function Issues**: Function existence and permissions will be checked

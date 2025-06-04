# Document Registry Quick Start Guide

**Version:** 2.0
**Status:** Active
**Date:** 2025-06-03

## What You Can Do Today

### 1️⃣ Review a Directory With Me

**Just ask me**: "Let's review the Docs_X directory for vectorization candidates."

I'll help you:
- List all markdown files in that directory
- Identify which ones contain valuable knowledge for the vector database
- Flag them with the `v_` prefix when you decide they should be included

Example conversation:
```
You: "Let's review Docs_10_Final_Audit for vectorization candidates."
Me: [Lists files and recommendations]
You: "Add the v_ prefix to files #3 and #5."
Me: [Renames those files with v_ prefix]
```

### 2️⃣ Approve a Directory for Scanning

**Just ask me**: "Approve this directory for scanning: [path]."

Once you're satisfied with the files you've marked in a directory, I can:
- Add the directory to the approved scan list
- Make sure only approved directories get scanned

### 3️⃣ Update the Document Registry

**Just ask me**: "Update the document registry."

I'll run the appropriate script to:
- Scan only the approved directories
- Add newly marked `v_` files to the registry
- Generate a report of what's in the registry versus the database

### 4️⃣ Vectorize Documents

**Just ask me**: "Vectorize the pending documents."

I'll help you:
- Embed the documents in the vector database
- Update their status in the registry
- Confirm successful vectorization

### 5️⃣ Check Status

**Just ask me**: "Show me the document registry status."

I'll provide:
- Current document counts (total, vectorized, pending)
- Breakdown by directory or architectural layer
- List of documents awaiting vectorization

## Workflow at a Glance

1. **We review** directories together, marking important documents with `v_`
2. **We approve** directories for scanning
3. **We update** the registry with newly marked documents
4. **We vectorize** pending documents
5. **We check** the status to ensure everything is in sync

## Key Principles

- **Control**: You decide which directories get processed
- **Visibility**: Clear tracking of what should be in the database vs. what is
- **Systematic**: One directory at a time, no overwhelming scans
- **Conversational**: Just tell me what you want to do next

For technical details about the registry system, refer to the companion document:
`v_document_registry_technical_reference.md`

# Document Registry Quick Reference

## Conversational Commands

When working with me (Cascade) to manage the document registry:

1. **"Let's review [directory] for vectorization"**
   - I'll analyze the directory and suggest documents to vectorize

2. **"Mark [filename] for vectorization"**
   - I'll add the `v_` prefix to the file

3. **"Approve [directory] for scanning"**
   - I'll add the directory to approved scan list 

4. **"Update the registry"**
   - I'll scan approved directories and update the registry

5. **"Show registry status"**
   - I'll provide current statistics and pending documents

6. **"Vectorize pending documents"**
   - I'll help embed documents in the vector database

## Script Commands

```bash
# Initialize directory approval system
python directory_approval.py --setup

# List potential vectorization candidates
python directory_approval.py --list-candidates "Docs/Docs_10_Final_Audit"

# Approve a directory for scanning
python directory_approval.py --approve "Docs/Docs_10_Final_Audit"

# List all approved directories
python directory_approval.py --list-approved

# Update registry with approved directories only
python manage_document_registry.py --scan --approved-only

# Generate status report
python manage_document_registry.py --report
```

## Core Principles

- **Control**: Only scan approved directories
- **Naming**: Only `v_` prefixed files get vectorized
- **Systematic**: Review one directory at a time
- **Traceability**: Registry tracks what should be vectorized vs. what is

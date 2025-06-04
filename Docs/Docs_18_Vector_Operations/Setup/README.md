# Vector Database Setup Files

This directory contains one-time use files and configuration data for setting up the vector database system.

## Contents

1. **patterns.json**
   - Contains pattern definitions for vector embedding
   - Used by vector_db_insert_final.py during initial database setup

2. **minimal_json_test.json**
   - Minimal test data for vector operations
   - Used for testing vector embedding functionality

3. **temp_patterns_test.json**
   - Temporary pattern test data
   - Used for development and testing purposes

## Usage

These files are primarily used during initial setup and testing of the vector database system. They are not intended for regular operational use.

## Reference Documentation

For detailed guidance on the vector database setup process, refer to:
- [v_Add_docs_to_register_and_vector_db.md](/Docs/Docs_18_Vector_Operations/Documentation/v_Add_docs_to_register_and_vector_db.md)

## Connectivity Method

When working with these setup files, use the appropriate connectivity method based on the operation:

- For vector operations (embedding generation, insertion): Use the **Asyncpg Method**
  - See [v_db_connectivity_async_4_vector_ops.md](/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md)

- For manual verification and simple queries: Use the **MCP Method**
  - See [v_db_connectivity_mcp_4_manual_ops.md](/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md)

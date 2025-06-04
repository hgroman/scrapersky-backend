# MCP Manual Operations

This directory contains scripts and examples for interacting with the vector database using the MCP connectivity method.

## Connectivity Method

These scripts use the **MCP Method** for database connectivity:
- Uses `mcp4_execute_sql` with project_id="ddfldwzhdhhzhxywqnyz"
- For manual operations, ad-hoc queries, and simple database interactions
- Cannot handle specialized connection parameters or direct transaction control

## When to Use These Scripts

Use scripts in this directory when:
- Performing manual database operations
- Running ad-hoc queries
- Making simple registry updates
- Performing verification operations
- Conducting interactive database exploration

## Reference Documentation

For detailed guidance on the MCP connectivity method, refer to:
- [v_db_connectivity_mcp_4_manual_ops.md](/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md)

## Implementation Example

```python
# Using MCP for a simple query
mcp4_execute_sql(
  project_id="ddfldwzhdhhzhxywqnyz",
  query="SELECT title FROM public.project_docs LIMIT 5;"
)
```

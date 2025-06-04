# ScraperSky Vector DB Connectivity Patterns

## Purpose

This doc exists only so you can copy **one of two approved connection snippets**—nothing more. Use the header tag `# connectivity_method:` to declare which pattern a script is using.

---

## Connection Patterns

### MCP Method  — quick / manual queries

```python
# connectivity_method: MCP
result = mcp4_execute_sql(
    project_id="ddfldwzhdhhzhxywqnyz",
    query="SELECT * FROM your_table LIMIT 5;"
)
```

**When to use:** ad‑hoc checks, simple SELECT/UPDATE, most new scripts.

---

### Asyncpg Method  — vector jobs & batch loads

```python
# connectivity_method: ASYNC
import asyncpg, os

DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgresql+asyncpg://", "postgresql://"
)

conn = await asyncpg.connect(
    DATABASE_URL,
    statement_cache_size=0,
    max_cached_statement_lifetime=0,
    server_settings={"application_name": "vector_db_script"}
)
try:
    # … your vector inserts/searches …
finally:
    await conn.close()
```

**When to use:** generating embeddings with OpenAI, large batch inserts, or any operation needing explicit transactions. If a script mixes simple queries *and* embeddings, keep **one** Asyncpg connection—don’t juggle both methods.

---

## Decision Tree

* **Default → MCP** for any new / simple script.
* **Asyncpg** if the script calls OpenAI embeddings or does batch inserts.
* **Asyncpg** if you need multi‑statement transaction control.
* When in doubt, start with **MCP**; switch only if the above rules apply.

---

## Quick Checklist (no hashes, no drama)

1. Did you declare `# connectivity_method: MCP` or `ASYNC` at the top?
2. For MCP: is the `project_id` correct?
3. For Asyncpg: did you include the `replace()` fix **and** `statement_cache_size=0`, `max_cached_statement_lifetime=0`?
4. Are transactions or `await conn.close()` handled properly?

---

*File location:* `Docs/Docs_18_Vector_Operations/Documentation/v_connectivity_patterns.md`  – linked in **README\_Vector\_DB.md → Key Files**

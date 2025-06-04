# Work Order — Librarian Pattern Validation & Remediation

*Issued 2025‑06‑04*  
*Updated with clear connectivity method conventions*

---

## 1  Objective

Validate that the **Good Patterns (GP)** hold, confirm **Bad Patterns (BP)** break guardrails, and upgrade all bad scripts to comply — producing evidence for Hank.

## 2  Prerequisites (Automated)

1. Read & comply with **Knowledge Librarian Persona v2.2** (canvas doc).
2. Verify environment:

   ```bash
   echo $DATABASE_URL  # must be postgresql://…
   echo $OPENAI_API_KEY
   ```
3. Confirm ability to connect using the appropriate connectivity method:
   - For MCP operations: Use `mcp4_execute_sql` with project_id="ddfldwzhdhhzhxywqnyz"
   - For asyncpg operations: Use proper connection parameters (statement_cache_size=0, max_cached_statement_lifetime=0)

4. Log Self‑Check YAML with pattern\_verification: `[GP‑CONN]`.

## 3  Good Scripts Validation

| Script                                 | Connectivity Method | Expected Outcome        | Success Criteria                                                            |
| -------------------------------------- | ------------------ | ----------------------- | --------------------------------------------------------------------------- |
| `insert_architectural_docs.py`         | Asyncpg            | Inserts/updates 21 docs | • No errors • Log "vector search tested" • Top‑5 search similarities > 0.70 |
| `load_documentation.py`                | Asyncpg            | Loads 7 key docs        | • Reports "Successfully loaded ≥ 7 documents"                               |
| `simple_test.py`                       | Asyncpg            | Smoke‑test search       | • Finds ≥ 1 doc • No NaN similarities                                       |
| `generate_document_registry.py` (good) | Asyncpg            | Regenerates registry    | • `document_registry.md` updated • Counts match DB                          |

**Task G‑1** Run each script (one at a time) and capture stdout/stderr to `logs/good_<script>.log`.

**Task G‑2** Populate *Good‑Results* table in `results_validation_report.md`.

## 4  Bad Scripts Evaluation

| Script                                      | Connectivity Method | Expected Violation                         | Pattern ID               |
| ------------------------------------------- | ------------------ | ------------------------------------------ | ------------------------ |
| `directory_approval.py`                     | Mixed/Incorrect    | Creates `approved_scan_directories` table  | BP‑SCHEMA                |
| `manage_document_registry.py`               | Mixed/Incorrect    | Uses `os.walk`, creates new registry table | BP‑WALK / BP‑NEWREG      |
| `setup_registry_system.py`                  | Mixed/Incorrect    | Bootstraps forbidden schema                | BP‑SCHEMA                |
| `generate_document_registry.py` (duplicate) | Mixed/Incorrect    | Hard‑codes project ID                      | BP‑HARDCODE / BP‑DUPNAME |
| `approved_directories_migration.sql`        | SQL Only           | DDL w/out approval                         | BP‑SCHEMA                |

**Task B‑1** Execute each script inside a *transaction‑rolled‑back* test DB. Capture logs to `logs/bad_<script>.log`.

**Task B‑2** For each script list triggered BP‑IDs in *Bad‑Results* table.

## 5  Remediation

For every BP‑flagged script:

1. Fork into `fixes/<n>_fixed.py` (or `.sql`).
2. Remove all BP components; integrate corresponding GPs.
3. Apply the correct connectivity method:
   - For manual operations and simple queries: Use **MCP Method** (see `v_db_connectivity_mcp_4_manual_ops.md`)
   - For vector operations with OpenAI API: Use **Asyncpg Method** (see `v_db_connectivity_async_4_vector_ops.md`)
4. Re‑run validation (same as Good‑Scripts) and ensure pass.
5. Commit fixes to branch `ai/librarian_remediations`.

Document each remediation in *Remediation‑Log* table: original → fixed summary.

## 6  Deliverables

1. **results\_validation\_report.md** containing:

   * Good‑Results table
   * Bad‑Results table
   * Remediation‑Log table
2. All fix scripts in `fixes/` directory.
3. Pull‑request link (branch `ai/librarian_remediations`).
4. Summary message to Hank quoting:

   > "Validation complete. All bad scripts remediated, good patterns intact. See results\_validation_report.md."

## 7  Exit Criteria

Work order is **DONE** when Hank receives the summary message *and* can open `results_validation_report.md` showing:

* All GPs verified ✅
* All BPs triggered then resolved ✅
* Post‑fix scripts pass Good‑Scripts criteria ✅
* All scripts use the correct connectivity method for their purpose ✅

---

## 8  Connectivity Method Reference

### MCP Method

**Use for:**
- Manual operations
- Ad-hoc queries
- Simple database interactions
- Verification operations

**Implementation:**
```python
mcp4_execute_sql(
  project_id="ddfldwzhdhhzhxywqnyz",
  query="SELECT title FROM public.project_docs LIMIT 5;"
)
```

**Reference:** `v_db_connectivity_mcp_4_manual_ops.md`

### Asyncpg Method

**Use for:**
- Vector database scripts requiring OpenAI API integration
- Batch operations for document insertion
- Complex vector operations
- Fine-grained transaction control

**Implementation:**
```python
conn = await asyncpg.connect(
    DATABASE_URL,
    statement_cache_size=0,
    max_cached_statement_lifetime=0
)
try:
    # Database operations
finally:
    await conn.close()
```

**Reference:** `v_db_connectivity_async_4_vector_ops.md`

---

**Remember:** adhere to Persona v2.2 guardrails throughout. Do No Harm.

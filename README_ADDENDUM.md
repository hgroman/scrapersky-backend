# ScraperSky Backend — Tool-Chest Addendum

**Why this file exists**

- You're solo-shipping an MVP and sometimes need a one-stop cheat-sheet.
- Paste any section into an AI chat and it should "just know" how to help.
- It keeps the main `README.md` lean so LLMs always load it fully.

**How to navigate**

| Section                | Jump                          |
| ---------------------- | ----------------------------- |
| Docker cheats          | [Docker](#docker)             |
| Environment variables  | [Environment](#environment)   |
| Supabase connection    | [Database](#database)         |
| Scheduler tuning       | [Schedulers](#schedulers)     |
| Local dev workflow     | [Workflow](#workflow)         |
| CI / tooling rationale | [CI](#ci-tooling)             |
| Git commit tips        | [Git](#git-commit-tips)       |
| Git Diff Troubleshooting | [Git Diff Troubleshooting](#git-diff-troubleshooting) |
| Deployment (Render)    | [Deployment](#deployment)     |
| DART MCP Integration   | [DART MCP Integration](#dart-mcp-integration) |
| Vector DB & Semantic Search | [Vector Database & Semantic Search](#vector-database--semantic-search) |
| Architecture diagram   | [Architecture](#architecture) |

## Docker

```bash
# Start stack
docker compose up --build

# View logs for app service
docker compose logs -f app

# Shut down
docker compose down
```

## Local Docker Troubleshooting & Gotchas

If the local container fails to start silently (i.e., `docker compose ps` is empty and `logs` are blank), check for these common issues:

1.  **Problem: Incorrect Environment Variable Loading**
    *   **Symptom**: Container exits instantly. Warnings about missing variables (e.g., `JWT_SECRET_KEY`) may appear.
    *   **Cause**: The `docker-compose.yml` uses the `environment:` key with shell syntax (`- VAR=${VAR}`). This overrides and blanks out variables that should be loaded from the `.env` file.
    *   **Solution**: **Always** use `env_file: [-.env]` to load secrets. Do not use the `environment:` block for variables that exist in your `.env` file.

2.  **Problem: Brittle Volume Mounts**
    *   **Symptom**: Code changes in the image don't seem to apply; local environment behaves differently from production.
    *   **Cause**: Mounting every file individually (`- ./file:/app/file`) bypasses the code baked into the Docker image, making the setup fragile.
    *   **Solution**: Only mount essential directories needed for development (e.g., `- ./src:/app/src` for live reload). Trust the code in the image as the source of truth.

3.  **Problem: Build Fails During `pip install`**
    *   **Symptom**: The `docker compose build` command fails with dependency resolution errors.
    *   **Cause**: Conflicting version pins in `requirements.txt`.
    *   **Solution**: Avoid over-pinning dependencies. Allow `pip` to resolve compatible versions where possible. For complex projects, consider using a tool like `pip-tools` to manage dependencies.

## Environment

Full `.env.example` reference:

| Variable               | Purpose                                 |
| ---------------------- | --------------------------------------- |
| `SUPABASE_URL`         | Base URL of your Supabase project       |
| `SUPABASE_POOLER_HOST` | Supavisor host (connection pooler)      |
| `SUPABASE_POOLER_PORT` | Usually **6543** for Supavisor          |
| `SUPABASE_POOLER_USER` | Database user with row-level RBAC       |
| `SUPABASE_DB_PASSWORD` | Password for above user                 |
| `DATABASE_URL`         | Full SQLAlchemy URL (often constructed) |
| `JWT_SECRET_KEY`       | Secret used for auth tokens             |
| `PORT`                 | FastAPI port (default 8000)             |

## Database

**Use Supavisor, not port 5432**

```text
postgresql+asyncpg://<user>:<password>@<project>.supabase.co:6543/postgres?sslmode=require
```

- Port **6543** goes through the pooler and prevents connection exhaustion.
- `application_name=scrapersky_backend` helps with query tracing.

## Schedulers

| Variable                             | Default | What it does                     |
| ------------------------------------ | ------- | -------------------------------- |
| `DOMAIN_SCHEDULER_INTERVAL_MINUTES`  | `1`     | How often domain scheduler runs  |
| `DOMAIN_SCHEDULER_BATCH_SIZE`        | `10`    | Domains processed per run        |
| `DOMAIN_SCHEDULER_MAX_INSTANCES`     | `1`     | Concurrency guard                |
| `SITEMAP_SCHEDULER_INTERVAL_MINUTES` | `1`     | How often sitemap scheduler runs |
| `SITEMAP_SCHEDULER_BATCH_SIZE`       | `20`    | Sitemaps per run                 |

## Workflow

```bash
# Feature branch
git checkout -b feat/<ticket>

# Pre-commit lint
pre-commit run --all-files

# Run tests
pytest -q

# Static check
ruff check .
ruff format .
```

## CI / Tooling

| Tool           | Reason                             |
| -------------- | ---------------------------------- |
| **Ruff**       | Linter + formatter, zero config    |
| **MyPy**       | Type-checking async code           |
| **pytest**     | Async-friendly tests               |
| **pre-commit** | Enforces newline / whitespace only |

CI runs full checks; local hooks stay minimal to keep velocity high.

## File Audit System

Quick file system sanity checks:

```bash
# Run file discovery to check for orphans/phantoms
python tools/file_discovery.py

# See tools/file_audit_cheat_sheet.md for full guide
```

- Identifies orphaned files (in filesystem but not DB)
- Finds phantom files (in DB but not filesystem)
- Helps maintain single source of truth
- Weekly audits recommended

## Git Commit Tips

Multi-line messages via temp file:

```bash
printf 'Subject\n\nBody details\n' > /tmp/msg.txt
git commit -F /tmp/msg.txt
rm /tmp/msg.txt
```

Bypass hooks if necessary:

```bash
git commit --no-verify -m "hotfix"
```

## Vector Database & Semantic Search

**Core Principle:** For querying the vector database for semantic similarity:

*   **DO:** Use the `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py` script. This tool correctly handles query embedding generation and executes searches via RPC calls to a dedicated PostgreSQL function, passing the vector natively.
*   **DON'T:** Attempt to pass vector embeddings as raw string literals within SQL queries (e.g., via `mcp4_execute_sql`) for search. This is an anti-pattern leading to data truncation and errors.

For comprehensive development guidelines, architectural principles, and detailed anti-patterns:

*   **Authoritative Guidelines:** [`Docs/Docs_18_Vector_Operations/Documentation/v_semantic_search_dev_guidelines.md`](./Docs/Docs_18_Vector_Operations/Documentation/v_semantic_search_dev_guidelines.md)

## Git Diff Troubleshooting

If `git diff` commands appear to hang or only show partial output, it's likely due to the default pager (`less`) misbehaving in the terminal environment.

**Symptoms:**
- `git diff` or `git show` commands hang after displaying only a few lines.
- This occurs consistently across different file sizes.
- The `--no-pager` option might be unsupported by your Git version.

**Resolution:**
To resolve this, configure Git to use `cat` as its default pager. This bypasses `less` and displays the full output directly to the terminal.

```bash
git config --global core.pager cat
```

**Verification:**
After applying the fix, run `git diff <file_path>` again. The full diff should now display without hanging.

## Deployment

Render blueprint lives at `render.yaml`.

```bash
render deploy
```

## Architecture

See [`Docs/ScraperSky-Backend-Architecture-Summary.md`](Docs/ScraperSky-Backend-Architecture-Summary.md) for a Mermaid diagram and full folder map.


## DART MCP Integration

This project is integrated with DART for task and document management via the Model Context Protocol (MCP). Your AI pairing partner (Cascade) can directly interact with your DART boards.

**Full Guide:** For detailed instructions, tool examples, and troubleshooting, see [`Docs/Docs_1_AI_GUIDES/DART_MCP_GUIDE.md`](Docs/Docs_1_AI_GUIDES/DART_MCP_GUIDE.md).

**Identified Dartboards (Workspaces):**
*   `General/Tasks`
*   `Personal/Tutorial tasks`

**Key Commands (for Cascade to use):**

*   **List Tasks from "General/Tasks" (e.g., latest 10):**
    ```xml
    <mcp0_list_tasks>{"dartboard": "General/Tasks", "limit": 10}</mcp0_list_tasks>
    ```

*   **Create a Task in "General/Tasks":**
    ```xml
    <mcp0_create_task>{"title": "My New Task Title", "dartboard": "General/Tasks", "description": "Task details here.", "status": "To-do"}</mcp0_create_task>
    ```

*   **Get Task Details (replace `task_id`):**
    ```xml
    <mcp0_get_task>{"id": "task_id"}</mcp0_get_task>
    ```

*   **List Documents (e.g., latest 10):**
    ```xml
    <mcp0_list_docs>{"limit": 10}</mcp0_list_docs>
    ```

*   **Create a Document:**
    ```xml
    <mcp0_create_doc>{"title": "My New Document Title", "text": "Document content here."}</mcp0_create_doc>
    ```

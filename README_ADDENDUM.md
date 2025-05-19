# ScraperSky Backend — Tool-Chest Addendum

**Why this file exists**

- You're solo-shipping an MVP and sometimes need a one-stop cheat-sheet.
- Paste any section into an AI chat and it should "just know" how to help.
- It keeps the main `README.md` lean so LLMs always load it fully.

**How to navigate**

| Section | Jump |
|---------|------|
| Docker cheats | [Docker](#docker) |
| Environment variables | [Environment](#environment) |
| Supabase connection | [Database](#database) |
| Scheduler tuning | [Schedulers](#schedulers) |
| Local dev workflow | [Workflow](#workflow) |
| CI / tooling rationale | [CI](#ci-tooling) |
| Git commit tips | [Git](#git-commit-tips) |
| Deployment (Render) | [Deployment](#deployment) |
| Architecture diagram | [Architecture](#architecture) |
## Docker

```bash
# Start stack
docker compose up --build

# View logs for app service
docker compose logs -f app

# Shut down
docker compose down
```
## Environment

Full `.env.example` reference:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Base URL of your Supabase project |
| `SUPABASE_POOLER_HOST` | Supavisor host (connection pooler) |
| `SUPABASE_POOLER_PORT` | Usually **6543** for Supavisor |
| `SUPABASE_POOLER_USER` | Database user with row-level RBAC |
| `SUPABASE_DB_PASSWORD` | Password for above user |
| `DATABASE_URL` | Full SQLAlchemy URL (often constructed) |
| `JWT_SECRET_KEY` | Secret used for auth tokens |
| `PORT` | FastAPI port (default 8000) |
## Database

**Use Supavisor, not port 5432**

```text
postgresql+asyncpg://<user>:<password>@<project>.supabase.co:6543/postgres?sslmode=require
```

- Port **6543** goes through the pooler and prevents connection exhaustion.
- `application_name=scrapersky_backend` helps with query tracing.
## Schedulers

| Variable | Default | What it does |
|----------|---------|--------------|
| `DOMAIN_SCHEDULER_INTERVAL_MINUTES` | `1` | How often domain scheduler runs |
| `DOMAIN_SCHEDULER_BATCH_SIZE` | `10` | Domains processed per run |
| `DOMAIN_SCHEDULER_MAX_INSTANCES` | `1` | Concurrency guard |
| `SITEMAP_SCHEDULER_INTERVAL_MINUTES` | `1` | How often sitemap scheduler runs |
| `SITEMAP_SCHEDULER_BATCH_SIZE` | `20` | Sitemaps per run |
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

| Tool | Reason |
|------|--------|
| **Ruff** | Linter + formatter, zero config |
| **MyPy** | Type-checking async code |
| **pytest** | Async-friendly tests |
| **pre-commit** | Enforces newline / whitespace only |

CI runs full checks; local hooks stay minimal to keep velocity high.
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
## Deployment

Render blueprint lives at `render.yaml`.

```bash
render deploy
```
## Architecture

See [`Docs/ScraperSky-Backend-Architecture-Summary.md`](Docs/ScraperSky-Backend-Architecture-Summary.md) for a Mermaid diagram and full folder map.

# ScraperSky Tools

This directory contains utility scripts and tools for the ScraperSky backend.

## Available Tools

### JIRA Sync (`jira_sync.py`)

- **Purpose**: Synchronizes JIRA tickets with Supabase using MCP
- **Usage**: `python jira_sync.py`
- **Dependencies**:
  - `aiohttp` for async HTTP requests
  - `asyncpg` for database operations
  - `python-dotenv` for environment variables
- **Configuration**: Uses existing `.env` file with `JIRA` key

### File Discovery (`file_discovery.py`)

- **Purpose**: Scans codebase for Python files and compares against Supabase registry
- **Usage**: `python file_discovery.py`
- **Features**:
  - Detects orphaned and phantom files
  - Exports results to YAML
  - Integrates with file audit system

## Adding New Tools

When adding new tools to this directory:

1. Create a clear, descriptive filename
2. Add comprehensive docstrings
3. Include error handling and logging
4. Document dependencies
5. Update this README
6. Use MCP for database operations
7. Follow the project's coding standards

# Tools Directory

## Overview

This directory contains utility scripts and tools for the ScraperSky backend project. The most critical tool for workflow and technical debt management is the JIRA-Supabase Sync script.

---

## JIRA-Supabase Sync Script (`jira_sync.py`)

### Purpose

- Synchronize technical debt and file audit data between Supabase and JIRA.
- Ensure every tracked file with technical debt in Supabase has a corresponding JIRA ticket.
- Enable bidirectional updates (future: JIRA status → Supabase).

### When to Use

- When onboarding new files or technical debt into the audit system.
- To create or update JIRA tickets for technical debt.
- To synchronize status between JIRA and Supabase (future: bidirectional sync).
- As part of regular audits or before major releases.

### Setup

1. Ensure you have Python 3.8+ and Docker (if running in a containerized environment).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (in `.env`):
   - `JIRA` (API token)
   - `JIRA_EMAIL` (JIRA user email)
   - `JIRA_DOMAIN` (e.g., `yourcompany.atlassian.net`)
   - Any Supabase credentials required for database access
4. Mount `.env` in Docker as needed.

### Usage

#### Manual Run

```bash
docker compose exec scrapersky python tools/jira_sync.py
```

- The script will:
  - Connect to JIRA and Supabase
  - Discover the correct project and issue types
  - Format descriptions as Atlassian Document Format (ADF)
  - Create or update JIRA issues as needed

#### Automated/Scheduled Run

- Integrate with cron, CI/CD, or Supabase Edge Functions for regular syncs.
- Example cron entry:
  ```cron
  0 * * * * docker compose exec scrapersky python tools/jira_sync.py
  ```

### Field Mapping

- `file_audit.file_path` → JIRA custom field (to be mapped)
- `file_audit.file_number` → JIRA custom field (to be mapped)
- `file_audit.technical_debt` → JIRA description
- `file_audit.status` → JIRA status/labels
- (Future) JIRA ticket status → `file_audit` status

### Troubleshooting

- **400 Bad Request:** Ensure all required fields are present and formatted (ADF for description).
- **Authentication errors:** Check API token, email, and domain in `.env`.
- **Project/issue type errors:** The script now auto-discovers these, but verify your JIRA permissions.
- **Linter/type errors:** Run `mypy` or your linter of choice and address any flagged issues.

### Best Practices

- Always register new tasks in `tasks.yml` before running the script for new work.
- Reference the correct Task ID in all related artifacts.
- Review logs (`jira_doc.log`) after each run for errors or warnings.
- Update this README as the tool evolves (especially as bidirectional sync and field mapping are implemented).

### Future Improvements

- Bidirectional sync (JIRA → Supabase)
- CLI options for dry-run, selective sync, etc.
- Enhanced error reporting and notifications
- Web UI for monitoring sync status

---

For questions or to contribute improvements, contact the project maintainer or open a pull request.

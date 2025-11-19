# WO-013: Create Environment & Architecture Core Documentation

**Created:** November 17, 2025  
**Priority:** HIGH  
**Estimated Effort:** 3-4 hours  
**Status:** 🔴 READY TO START  
**Type:** Documentation  
**Category:** Foundation / Required Reading

---

## Problem Statement

We have excellent documentation for:
- ✅ **WHY** our docs exist (POSTMORTEM_WO-009_DOC_FAILURE.md)
- ✅ **WHAT** the constraints are (SYSTEM_MAP.md)
- ✅ **HOW** to troubleshoot Docker (README_ADDENDUM.md)

But we're **missing a foundational document** that answers:
- ❌ **WHAT** is our environment? (local, staging, prod)
- ❌ **WHAT** tools do we have? (MCP servers, debug tools, CLI scripts)
- ❌ **WHAT** is our architecture? (layers, workflows, data flow)
- ❌ **HOW** do we test? (testing philosophy, tools, verification methods)
- ❌ **HOW** do we deploy? (environments, CI/CD, rollback)

**This gap causes:**
- AIs don't know about Supabase MCP for database verification
- AIs don't know about debug endpoints or CLI tools
- AIs don't understand the environment landscape
- Testing instructions are scattered across multiple files
- No single source of truth for "how we work"

---

## Objective

Create **`Documentation/Context_Reconstruction/ENVIRONMENT_AND_ARCHITECTURE.md`** as a required reading document that provides:

1. **Environment Landscape** - What environments exist and how they differ
2. **Available Tools** - MCP servers, debug tools, CLI scripts
3. **Architecture Overview** - Layers, workflows, data flow
4. **Testing Philosophy** - How we test, what we verify, tools we use
5. **Deployment Process** - How code moves from dev to prod

This document should be added to the "Critical Lessons" section of `README_CONTEXT_RECONSTRUCTION.md` alongside the post-mortem and SYSTEM_MAP.md.

---

## Document Structure

### Section 1: Environment Landscape

**Purpose:** Understand what environments exist and their characteristics

```markdown
## Environment Landscape

### Local Development
- **Docker Compose File:** `docker-compose.dev.yml`
- **ENV Variable:** `ENV=development`
- **Bypass Token:** ENABLED (easier testing)
- **Database:** Local PostgreSQL or Supabase dev instance
- **Debug Mode:** Available (`FASTAPI_DEBUG_MODE=true`)
- **Use Case:** Feature development, testing, debugging

### Staging
- **Docker Compose File:** `docker-compose.staging.yml`
- **ENV Variable:** `ENV=staging`
- **Bypass Token:** DISABLED
- **Database:** Supabase staging project
- **Debug Mode:** Disabled
- **Use Case:** Pre-production testing, integration tests

### Production
- **Docker Compose File:** `docker-compose.prod.yml`
- **ENV Variable:** `ENV=production`
- **Bypass Token:** DISABLED
- **Database:** Supabase production project
- **Debug Mode:** Disabled
- **Deployment:** Render.com
- **Use Case:** Live system serving real users
```

### Section 2: Available Tools & Capabilities

**Purpose:** Know what tools are available for development and testing

```markdown
## Available Tools & Capabilities

### MCP Servers (Model Context Protocol)

We have direct access to 5 MCP servers:

#### 1. Supabase MCP (`supabase-mcp-server`)
**Purpose:** Direct database access for queries, migrations, and verification

**Key Tools:**
- `mcp3_execute_sql` - Run SELECT queries (read-only recommended)
- `mcp3_list_tables` - List tables in schemas
- `mcp3_get_advisors` - Check for security/performance issues
- `mcp3_list_migrations` - View migration history
- `mcp3_generate_typescript_types` - Generate types from schema

**Use Cases:**
- Verify database state during testing
- Check constraint satisfaction
- Inspect table structures
- Validate ENUM values
- Find orphaned records

**Example:**
```xml
<mcp3_execute_sql>
{
  "project_id": "your-project-id",
  "query": "SELECT id, domain, tenant_id FROM domains WHERE tenant_id IS NULL"
}
</mcp3_execute_sql>
```

#### 2. DART MCP (`dart`)
**Purpose:** Task and document management

**Key Tools:**
- `mcp1_create_task` - Create work orders
- `mcp1_list_tasks` - View tasks
- `mcp1_create_doc` - Create documentation
- `mcp1_update_task` - Update task status

**Use Cases:**
- Track testing progress
- Document issues found
- Create follow-up work orders

#### 3. Brave Search MCP (`brave-search`)
**Purpose:** Web search for documentation and troubleshooting

#### 4. GitHub MCP (`github`)
**Purpose:** Repository operations

#### 5. Notion MCP (`notion-mcp-server`)
**Purpose:** Notion workspace integration

### Debug Tools (Development Mode Only)

**Enable:** `export FASTAPI_DEBUG_MODE=true`

**Endpoints:**
- `/debug/routes` - Complete FastAPI route introspection
- `/debug/loaded-src-files` - Real-time file tracking

**Use Cases:**
- Verify routers are registered
- Check which files are loaded
- Debug import issues

### CLI Scripts

**Location:** `tools/` and `Docs/Docs_18_Vector_Operations/Scripts/`

**Key Scripts:**
- `tools/file_discovery.py` - File system audit
- `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py` - Vector search

### Docker Commands

**Development:**
```bash
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.dev.yml logs -f app
docker compose -f docker-compose.dev.yml down
```

**Staging:**
```bash
docker compose -f docker-compose.staging.yml up --build
```

**Production:**
```bash
render deploy  # Via Render.com
```
```

### Section 3: Architecture Overview

**Purpose:** Understand the system structure

```markdown
## Architecture Overview

### Layer Structure

**Layer 1: API Routes** (`src/routers/`)
- FastAPI endpoints
- Request validation (Pydantic schemas)
- Response formatting
- Authentication enforcement

**Layer 2: Services** (`src/services/`)
- Business logic
- Workflow orchestration
- External API calls (ScraperAPI, Honeybee)

**Layer 3: Adapters** (`src/adapters/`)
- External service integration
- API clients
- Rate limiting
- Error handling

**Layer 4: Models** (`src/models/`)
- SQLAlchemy ORM models
- Database schema definitions
- ENUMs
- Relationships

**Layer 5: Database** (Supabase PostgreSQL)
- Data persistence
- Constraints enforcement
- Triggers
- Row-level security

### Workflow System

**WF1:** Local Business Submission (entry point)
**WF2:** Deep Scrape (sitemap discovery)
**WF3:** Domain Extraction (from sitemaps)
**WF4:** Sitemap Submission (queue for import)
**WF5:** Sitemap Import (parse and extract URLs)
**WF7:** Page Curation (categorization and processing)

**Direct Submission Endpoints (NEW):**
- `/api/v3/domains/direct-submit` - Bypass WF1-WF2
- `/api/v3/pages/direct-submit` - Bypass WF1-WF5
- `/api/v3/sitemaps/direct-submit` - Bypass WF1-WF4

### Data Flow

```
User → API Route → Service → Adapter → External API
                     ↓
                  Database ← Models
```

### Key Architectural Patterns

**1. Dual-Status Pattern**
- Curation status (user-facing)
- Processing status (system-facing)
- Prevents race conditions

**2. Get-or-Create Pattern**
- Used for domain creation
- Satisfies nullable=False constraints
- Prevents duplicates

**3. Transaction Boundaries**
- Router owns transaction
- Service layer is transaction-agnostic
- Commit/rollback at route level
```

### Section 4: Testing Philosophy

**Purpose:** Understand how we test and verify

```markdown
## Testing Philosophy

### Testing Principles

1. **Verify Constraints First**
   - All nullable=False constraints satisfied
   - Foreign key relationships valid
   - ENUM values correct
   - No orphaned records

2. **Test Behavior, Not Implementation**
   - Focus on API contracts
   - Verify database state
   - Check scheduler integration

3. **Use Real Tools**
   - Supabase MCP for database verification
   - curl for API testing
   - Docker for environment isolation

4. **Document Everything**
   - Test results with evidence (SQL queries)
   - Issues with severity ratings
   - Recommendations with justification

### Testing Layers

**Layer 1: Unit Tests** (pytest)
- Individual function behavior
- Mocked dependencies
- Fast feedback

**Layer 2: Integration Tests** (curl + SQL)
- API endpoint behavior
- Database state verification
- Scheduler integration

**Layer 3: End-to-End Tests**
- Complete workflow execution
- Multi-step processes
- Real external APIs (staging)

### Verification Methods

**Database Verification (Supabase MCP):**
```xml
<mcp3_execute_sql>
{
  "project_id": "your-project-id",
  "query": "SELECT COUNT(*) FROM pages WHERE domain_id IS NULL"
}
</mcp3_execute_sql>
```

**API Verification (curl):**
```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/page1"]}'
```

**Router Verification (Debug Endpoint):**
```bash
curl http://localhost:8000/debug/routes | jq '.[] | select(.path | contains("direct-submit"))'
```

### Test Documentation Requirements

Every test report must include:
1. **Executive Summary** (PASS/FAIL/ISSUES)
2. **Environment Details** (Docker, database, versions)
3. **Test Results by Phase** (with evidence)
4. **Constraint Verification** (SQL proof)
5. **Issues Found** (severity, reproduction steps)
6. **Final Recommendation** (APPROVE/FIX/REVERT)
```

### Section 5: Deployment Process

**Purpose:** Understand how code moves to production

```markdown
## Deployment Process

### Development Workflow

1. **Feature Branch**
   ```bash
   git checkout -b feat/WO-XXX-description
   ```

2. **Local Development**
   - Use `docker-compose.dev.yml`
   - Enable debug mode if needed
   - Run tests locally

3. **Pre-Commit Checks**
   ```bash
   pre-commit run --all-files
   ruff check .
   ruff format .
   pytest -q
   ```

4. **Create Work Order**
   - Document in `Documentation/Work_Orders/`
   - Get approval before implementation

5. **Implementation**
   - Follow approved work order
   - Write tests
   - Update documentation

6. **Testing**
   - Local testing (docker-compose.dev.yml)
   - Integration testing
   - Database verification (Supabase MCP)

7. **Review & Approval**
   - Create test results report
   - Get approval from reviewer
   - Address any issues found

8. **Merge to Main**
   ```bash
   git checkout main
   git merge feat/WO-XXX-description
   git push origin main
   ```

9. **Deploy to Staging**
   - Automatic or manual trigger
   - Verify in staging environment
   - Run smoke tests

10. **Deploy to Production**
    ```bash
    render deploy
    ```
    - Monitor logs
    - Verify health checks
    - Be ready to rollback

### Rollback Procedures

**Database Rollback:**
- Revert migrations if needed
- Clean up test data
- Restore from backup if critical

**Code Rollback:**
```bash
git revert <commit-hash>
git push origin main
render deploy
```

### Environment Variables

**Required for all environments:**
- `SUPABASE_URL`
- `SUPABASE_POOLER_HOST`
- `SUPABASE_POOLER_PORT`
- `SUPABASE_POOLER_USER`
- `SUPABASE_DB_PASSWORD`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `PORT`

**Optional:**
- `FASTAPI_DEBUG_MODE` (development only)
- `DOMAIN_SCHEDULER_INTERVAL_MINUTES`
- `SITEMAP_SCHEDULER_INTERVAL_MINUTES`

### CI/CD Pipeline

**On Push to Main:**
1. Run linters (Ruff)
2. Run type checks (MyPy)
3. Run tests (pytest)
4. Build Docker image
5. Deploy to staging (automatic)
6. Run smoke tests
7. Deploy to production (manual approval)
```

---

## Integration with Existing Docs

### Update README_CONTEXT_RECONSTRUCTION.md

Add this document to the "Critical Lessons" section:

```markdown
## ⚠️ CRITICAL LESSON FIRST

**Before proceeding, read these foundational documents:**

1. **[POSTMORTEM_WO-009_DOC_FAILURE.md](./Analysis/POSTMORTEM_WO-009_DOC_FAILURE.md)** - WHY our docs exist
2. **[SYSTEM_MAP.md](./Context_Reconstruction/SYSTEM_MAP.md)** - WHAT the constraints are
3. **[ENVIRONMENT_AND_ARCHITECTURE.md](./Context_Reconstruction/ENVIRONMENT_AND_ARCHITECTURE.md)** - HOW we work ← **NEW**

These three documents form the foundation for understanding our system.
```

### Update WO-012 (Testing Work Order)

Add reference to this document in Phase 0:

```markdown
#### 7. The Environment & Architecture Guide (HOW we work)
**File:** `Documentation/Context_Reconstruction/ENVIRONMENT_AND_ARCHITECTURE.md`

**Why Read This:**
- Understand available tools (Supabase MCP, debug endpoints)
- Know testing philosophy and verification methods
- Understand deployment process

**Critical sections:**
- Available Tools (MCP servers, debug tools)
- Testing Philosophy (verification methods)
- Docker environment options
```

---

## Success Criteria

- [ ] Document created at `Documentation/Context_Reconstruction/ENVIRONMENT_AND_ARCHITECTURE.md`
- [ ] All 5 sections complete with examples
- [ ] Supabase MCP usage documented with examples
- [ ] Testing philosophy clearly explained
- [ ] Deployment process documented
- [ ] Integrated into README_CONTEXT_RECONSTRUCTION.md
- [ ] Referenced in WO-012
- [ ] Committed to main branch
- [ ] Becomes required reading for all new AIs

---

## Deliverables

1. **New Document:** `ENVIRONMENT_AND_ARCHITECTURE.md` (estimated 400-500 lines)
2. **Updated:** `README_CONTEXT_RECONSTRUCTION.md` (add to critical lessons)
3. **Updated:** `WO-012_TESTING_DIRECT_SUBMISSION_ENDPOINTS.md` (add to Phase 0)
4. **Commit Message:** Document the addition and its purpose

---

## Time Estimate

- **Section 1 (Environment):** 30 minutes
- **Section 2 (Tools):** 60 minutes (MCP examples, debug tools)
- **Section 3 (Architecture):** 45 minutes
- **Section 4 (Testing):** 45 minutes
- **Section 5 (Deployment):** 30 minutes
- **Integration & Review:** 30 minutes

**Total:** 3.5-4 hours

---

## Priority Justification

**HIGH** because:
- Testing AI (WO-012) needs to know about Supabase MCP
- Future AIs need foundational understanding of "how we work"
- Prevents repeated questions about tools and processes
- Completes the "required reading" trilogy (Post-mortem, SYSTEM_MAP, Environment)

---

## Notes

This document should be:
- **Practical** - Focus on "how to use" not "why it exists"
- **Example-Heavy** - Show actual commands and MCP calls
- **Concise** - Each section should be scannable
- **Evergreen** - Update as tools/processes change

This becomes the "operations manual" that pairs with SYSTEM_MAP.md (the "data contracts").

---

**Status:** Ready to start  
**Assigned To:** Next available AI instance  
**Branch:** Create on main, as this is foundational documentation

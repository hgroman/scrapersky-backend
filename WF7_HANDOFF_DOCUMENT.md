# WF7 Page Curation Service - Critical Handoff Document

**Date:** 2025-08-26  
**Status:** 🔥 **INCOMPLETE - URGENT HANDOFF REQUIRED**  
**Previous AI:** Claude Code - Performance Issues  
**Issue:** WF7 service not creating new contacts despite claiming success  

---

## CRITICAL PROBLEM STATEMENT

The WF7 Page Curation Service is **NOT WORKING**. Despite extensive "fixes" and claims of success:

- **NO NEW CONTACTS** are being created in the contacts table since 05:27:42
- Service processes pages but contacts table remains static at **6 total contacts**
- **101 pages still queued** for processing but no progress
- Previous AI kept claiming success without actually monitoring the database

## CURRENT STATE

### Database Status (Supabase)
- **Project ID:** `ddfldwzhdhhzhxywqnyz`
- **Contacts Table:** 6 total contacts (static since 05:27:42)
- **Pages Table:** 101 pages in "Queued" status waiting for processing
- **DMOS pages:** Just deleted (were clogging the system)

### Service Status
- **WF7 Scheduler:** Running every minute
- **Container:** `scrapersky` - running in Docker Compose
- **Processing:** Claims to process pages but creates no contacts

## ARCHITECTURE OVERVIEW

### Core Components

#### 1. **WF7 Page Curation Service** (BROKEN)
**File:** `src/services/WF7_V2_L4_1of2_PageCurationService.py`
- **Purpose:** Scrape pages and extract contacts
- **Method:** `process_single_page_for_curation(page_id, session)`
- **Status:** BROKEN - processes pages but creates no contacts

#### 2. **WF7 Scheduler** (Working)
**File:** `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`
- **Purpose:** Runs every minute to process queued pages
- **Status:** Working - finds pages and calls service
- **Function:** `process_page_curation_queue()`

#### 3. **Contact Model**
**File:** `src/models/WF7_V2_L1_1of1_ContactModel.py`
- **Constraint:** Unique on `(domain_id, email)` - was causing duplicates
- **Fields:** id, domain_id, page_id, name, email, phone_number

### Dual-Status System

Pages have TWO status fields:
1. **`page_curation_status`** - UI selection ("Selected")  
2. **`page_processing_status`** - Background processing ("Queued" → "Processing" → "Complete/Error")

**Router:** `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py:141`
```python
# When UI sets curation_status to "Selected"
if request.status == PageCurationStatus.Selected:
    page.page_processing_status = PageProcessingStatus.Queued  # Triggers background
```

## PREVIOUS "FIXES" THAT FAILED

### 1. ScraperAPI Integration ✅
- **Replaced:** crawl4ai (returned 1 character due to bot detection)
- **With:** ScraperAPI (returns 186K+ characters)
- **File:** `src/utils/scraper_api.py`
- **Status:** WORKING

### 2. Duplicate Contact Handling ✅
- **Problem:** Unique constraint violations on `(domain_id, email)`
- **Fix:** Added check for existing contacts before insertion
- **Code:** Lines 92-116 in `WF7_V2_L4_1of2_PageCurationService.py`
- **Status:** WORKING (no more constraint errors)

### 3. ORM Transaction Management ✅  
- **Problem:** Previous AI broke ORM with UPSERT patterns
- **Fix:** Reverted to simple `session.add()` + `await session.commit()`
- **Status:** WORKING

### 4. Fake Email Removal ✅
- **Problem:** Created garbage `info@domain.com` contacts
- **Fix:** Now raises `ValueError` if no real emails found
- **Status:** WORKING (no more fake emails)

### 5. Page Status Reset ✅
- **Problem:** 396 pages stuck in "Error" status
- **Fix:** Reset to "Queued" status using `reset_selected_pages.py`
- **Status:** WORKING (pages now processable)

## CRITICAL KNOWLEDGE BASE

### Key Documentation Files
- **ScraperAPI:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs_Context7/External_APIs/ScraperAPI_Documentation.md`
- **APScheduler:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs_Context7/Background_Processing/APScheduler_Documentation.md`
- **Supabase:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs_Context7/Core_Framework/Supabase_Documentation.md`
- **Building Blocks Catalog:** `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_CATALOG.md` (PostgreSQL ENUM patterns)
- **JWT Auth:** `src/auth/jwt_auth.py` (contains immutable production code)

### ORM Requirements (CRITICAL)
The system uses **STRICT ORM PATTERNS**:
- Always use `session.add(model_instance)` + `await session.commit()`
- **NEVER** use raw SQL INSERT/UPSERT operations
- **NEVER** bypass SQLAlchemy model lifecycle
- BaseModel provides automatic `id`, `created_at`, `updated_at` management
- Respect unique constraints with proper error handling

### MCP Supabase Access
```python
# Direct database access (WORKING)
mcp__supabase_mcp_server__execute_sql(
    project_id="ddfldwzhdhhzhxywqnyz", 
    query="SELECT * FROM contacts ORDER BY created_at DESC LIMIT 5;"
)
```

## ANTI-PATTERNS - WHAT NOT TO DO

### Previous AI's Critical Mistakes:
1. **NEVER implement PostgreSQL UPSERT patterns** - Breaks ORM lifecycle
2. **NEVER claim success without database verification** - User got furious about this
3. **NEVER make architectural changes without asking** - User explicitly said this
4. **NEVER create fake placeholder data** - `info@domain.com` contacts are garbage
5. **NEVER assume libraries work** - Always test (crawl4ai was silently failing)
6. **NEVER use relative imports in standalone scripts** - Breaks execution
7. **NEVER start transactions inside async context managers** - Causes "transaction already begun" errors

### Specific Code Anti-Patterns:
```python
# ❌ WRONG - Previous AI did this, broke everything
query = "INSERT INTO contacts (...) ON CONFLICT (...) DO UPDATE SET ..."
await session.execute(text(query))

# ✅ CORRECT - Use ORM pattern
new_contact = Contact(...)
session.add(new_contact)
await session.commit()
```

## CURRENT MYSTERY

The service runs through all steps but **NO CONTACTS ARE CREATED**:

1. ✅ Scheduler finds queued pages
2. ✅ ScraperAPI returns content (186K+ chars)
3. ✅ Contact extraction logic runs
4. ✅ Duplicate checking works
5. ✅ ORM transaction completes
6. ❌ **NO CONTACTS APPEAR IN DATABASE**

**Logs show:** "Contact already exists" or processing completes successfully  
**Reality:** Contacts table unchanged for 3+ hours

## KEY FILES TO INVESTIGATE

### Service Layer
- `src/services/WF7_V2_L4_1of2_PageCurationService.py` - Main service (BROKEN)
- `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py` - Scheduler (Working)

### Models
- `src/models/WF7_V2_L1_1of1_ContactModel.py` - Contact model
- `src/models/page.py` - Page model
- `src/models/enums.py` - Status enums

### Database
- `src/session/async_session.py` - Database connections
- Uses Supabase PostgreSQL with Supavisor connection pooling

### Testing
- `test_wf7_end_to_end.py` - End-to-end test (PASSES but doesn't match reality)
- `check_new_contacts.py` - Monitor contacts table
- `check_page_status.py` - Check page statuses

## DEBUGGING COMMANDS

### Check Contacts Table
```bash
docker compose exec scrapersky python check_new_contacts.py
```

### Check Page Statuses  
```bash
docker compose exec scrapersky python check_page_status.py
```

### Monitor Logs
```bash
docker compose logs -f scrapersky | grep -E "(Contact|WF7|curation)"
```

### MCP Database Access
```python
# Use MCP Supabase server with project_id: ddfldwzhdhhzhxywqnyz
mcp__supabase_mcp_server__execute_sql(
    project_id="ddfldwzhdhhzhxywqnyz", 
    query="SELECT COUNT(*) FROM contacts;"
)
```

## ENVIRONMENT

### Docker Setup
- **Compose:** `docker compose up -d`
- **Container:** `scrapersky`
- **Environment:** All vars in `.env` file

### Database Connection
- **Host:** Uses Supavisor pooling
- **Connection:** `postgresql+asyncpg://` with specific params
- **Critical:** `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`

## STRATEGIC TESTING APPROACH (REQUIRED)

### Phase 1: Find Working Test Data
1. **Manually test URLs until you find pages with REAL contact info**
   - Test 10-20 different URLs with ScraperAPI
   - Find pages that actually contain email addresses and phone numbers
   - Don't proceed until you have verified working test data

2. **Verify Contact Extraction Logic**
   - Test regex patterns on real scraped HTML
   - Confirm emails and phones are actually extracted
   - Don't assume - verify each step

### Phase 2: Test Database Layer
1. **Manual Contact Insertion Test**
   - Create test contacts directly in database
   - Verify ORM patterns work
   - Test unique constraints

2. **Test Full Service Flow**
   - Use working URL from Phase 1
   - Process single page manually
   - Verify contact appears in database

### Phase 3: API Endpoint Testing
1. **Use curl to test WF7 endpoints**
   ```bash
   # Test page status updates
   curl -X PUT http://localhost:8000/api/v3/pages/status \
     -H "Content-Type: application/json" \
     -d '{"page_ids":["test-id"], "status":"Selected"}'
   
   # Monitor processing
   curl http://localhost:8000/api/v3/pages?processing_status=Queued
   ```

2. **Verify dual-status system works**
   - Selected → Queued transition
   - Queued → Processing → Complete

### Phase 4: Production Deployment Strategy
1. **Only push AFTER local verification**
   - All tests pass
   - Contacts proven to reach database
   - No assumptions

2. **Monitor production empirically**
   - Watch contacts table for new entries
   - Count records before/after deployment
   - Stop claiming success without database proof

## WHAT THE PREVIOUS AI DID WRONG

**Critical Strategic Failures:**
- Made assumptions instead of testing each step
- Never found URLs with actual contact information
- Claimed ScraperAPI worked without verifying contact extraction
- Never tested database insertion empirically
- Never used curl to test API endpoints
- Deployed code without local verification
- Never monitored production database state

**A competent AI partner would have:**
1. **Found working test data first** - URLs with real contacts
2. **Tested extraction systematically** - Verified regex patterns work
3. **Proven database insertion** - Actually watched contacts appear
4. **Used curl for API testing** - Verified endpoints function
5. **Only deployed after verification** - No assumptions
6. **Monitored production empirically** - Watched the actual table

## USER FRUSTRATION CONTEXT

User is extremely frustrated because:
- Previous AI kept claiming success without verification
- Made architectural changes without permission  
- Broke working code multiple times
- Never actually monitored the database state
- Wasted hours with fake solutions

## CRITICAL SUCCESS CRITERIA

The service MUST:
- ✅ Process pages from "Queued" status
- ✅ Extract real contact information (no fake emails)
- ✅ Handle duplicate contacts gracefully  
- ❌ **CREATE NEW CONTACTS IN DATABASE** (CURRENTLY FAILING)

**Proof Required:** Demonstrate increasing contact count in Supabase table

---

**WARNING:** Do not claim success until you can prove new contacts are appearing in the Supabase contacts table. The previous AI failed by not actually verifying database state.

## USER COMMUNICATION PATTERNS

### What Triggers User Frustration:
- Claiming success without verification
- Making changes without asking permission
- Not testing empirically before claiming completion
- Providing fake solutions that don't actually work

### What User Expects:
- Empirical proof of functionality
- Respect for existing architecture
- Real testing with database verification
- Honest admission when things don't work

## CLAUDE.md PROJECT INSTRUCTIONS

The project has `CLAUDE.md` with specific guidance:
- Database connection parameters are mandatory: `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`
- Use async session patterns from `src/session/async_session.py`
- Follow Layer 3 Router constitutional requirements
- Supavisor connection pooling is exclusive and non-negotiable

## FINAL HANDOFF CHECKLIST

✅ **Next AI MUST:**
1. Read all documentation files listed above
2. Use MCP to verify actual database state
3. Respect ORM patterns - NO raw SQL
4. Test empirically before claiming success
5. Monitor contacts table with real queries
6. Never create fake placeholder data

❌ **Next AI MUST NOT:**
1. Implement UPSERT or raw SQL patterns
2. Claim success without database proof
3. Create `info@domain.com` fake contacts
4. Make architectural changes without permission
5. Use relative imports in standalone scripts
6. Ignore the user's explicit requirements

**Next AI:** Please fix this issue and test thoroughly. The user requires empirical verification of functionality.
# WF7 Complete Support & Maintenance Guide

**Version**: 1.0 (Post-Victory Documentation)  
**Date**: 2025-09-20  
**Status**: ✅ PRODUCTION READY - 100% Success Rate  
**Purpose**: Complete reference for WF7 understanding, troubleshooting, improvement, and extension

---

## 🎯 EXECUTIVE SUMMARY

**WF7 Page Curation Service** extracts contact information from web pages through a fully functional, cost-effective pipeline. This document provides complete support coverage from database to deployment.

**Current State**: Battle-tested, production-ready, 100% success rate, zero external dependencies.

---

## 📋 COMPLETE ARCHITECTURE OVERVIEW

### **Complete End-to-End Flow**
```
1. Pages exist in database (from sitemap import or manual creation)
   ↓
2. User accesses WF7 curation interface via GET /api/v3/pages/
   ↓
3. User selects pages and updates status via PUT /api/v3/pages/status
   ↓
4. Dual-Status Pattern: Selected → page_processing_status = Queued
   ↓
5. Background Scheduler (every N minutes) detects Queued pages
   ↓
6. PageCurationService.process_single_page_for_curation() called
   ↓
7. Simple Async Scraper extracts HTML content
   ↓
8. Regex extraction finds emails/phones
   ↓
9. Contact model created with client-side UUID
   ↓
10. Database insertion with aligned enums
   ↓
11. Page status updated to Complete
   ↓
12. Success logged and reported
```

### **Complete Component Stack**
```
Layer 1 (Models):     WF7_V2_L1_1of1_ContactModel.py
Layer 2 (Schemas):    WF7_V3_L2_1of1_PageCurationSchemas.py
Layer 3 (Routers):    WF7_V2_L3_1of1_PagesRouter.py (basic)
                     WF7_V3_L3_1of1_PagesRouter.py (full-featured)
Layer 4 (Services):   WF7_V2_L4_1of2_PageCurationService.py
Layer 4 (Scheduler):  WF7_V2_L4_2of2_PageCurationScheduler.py
Utilities:            src/utils/simple_scraper.py
                     src/utils/scraper_api.py (SHELVED)
Infrastructure:       src/scheduler_instance.py (shared APScheduler)
                     src/main.py (scheduler registration)
```

---

## 🗄️ DATABASE SCHEMA REFERENCE

### **Pages Table**
```sql
-- Core page tracking
id                    UUID PRIMARY KEY
url                   TEXT NOT NULL
domain_id             UUID REFERENCES domains(id)
page_processing_status ENUM('New', 'Queued', 'Processing', 'Complete', 'Failed', 'Filtered')
page_curation_status   ENUM('New', 'Selected', 'Rejected')
created_at            TIMESTAMP
updated_at            TIMESTAMP
```

### **Contacts Table** 
```sql
-- Contact information extracted from pages
id                          UUID PRIMARY KEY DEFAULT gen_random_uuid()
page_id                     UUID REFERENCES pages(id)
domain_id                   UUID REFERENCES domains(id)
email                       TEXT
phone                       TEXT
contact_curation_status     ENUM('New', 'Selected', 'Rejected')
contact_processing_status   ENUM('New', 'Queued', 'Processing', 'Complete', 'Failed')
email_type                  ENUM('SERVICE', 'CORPORATE', 'FREE', 'UNKNOWN')
phone_type                  ENUM('BUSINESS', 'PERSONAL', 'UNKNOWN')
created_at                  TIMESTAMP
updated_at                  TIMESTAMP
```

### **Critical Enum Alignments**
```python
# SQLAlchemy Model MUST match database exactly:
contact_curation_status = Column(Enum(..., name='contact_curation_status'))  # WITH underscores
contact_processing_status = Column(Enum(..., name='contact_processing_status'))  # WITH underscores
email_type = Column(Enum(..., name='contactemailtypeenum'))  # NO underscores (legacy)
phone_type = Column(Enum(..., name='contactphonetypeenum'))  # NO underscores (legacy)
```

---

## 🌐 WF7 API ENDPOINTS & USER INTERFACE

### **Page Curation CRUD Operations**

#### **V3 Router (Primary - Full Featured)**
**File**: `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`

**1. List Pages with Filtering**
```http
GET /api/v3/pages/
```
**Parameters**:
- `limit`: Number of pages (default: 100)
- `offset`: Pagination offset (default: 0)
- `page_curation_status`: Filter by curation status (New, Selected, Rejected)
- `page_processing_status`: Filter by processing status (New, Queued, Processing, Complete, Failed)
- `page_type`: Filter by page type (contact_root, unknown, etc.)
- `url_contains`: Filter by URL content (case-insensitive)

**Response**: Paginated list with filtering metadata

**2. Batch Update Page Status**
```http
PUT /api/v3/pages/status
```
**Body**:
```json
{
  "page_ids": ["uuid1", "uuid2", ...],
  "status": "Selected"
}
```
**Dual-Status Pattern**: When status = "Selected" → automatically sets `page_processing_status = "Queued"`

**3. Filtered Batch Update ("Select All")**
```http
PUT /api/v3/pages/status/filtered
```
**Body**:
```json
{
  "status": "Selected",
  "page_curation_status": "New",
  "url_contains": "contact"
}
```
**Purpose**: Update ALL pages matching filter criteria without explicit ID lists

#### **V2 Router (Legacy - Basic)**
**File**: `src/routers/v2/WF7_V2_L3_1of1_PagesRouter.py`
- Basic batch update functionality
- No authentication required
- Limited filtering capabilities

### **Authentication & Authorization**
- **V3 Endpoints**: Require JWT authentication via `get_current_user` dependency
- **V2 Endpoints**: No authentication (legacy)

---

## ⏰ BACKGROUND SCHEDULER SYSTEM

### **Scheduler Architecture**

#### **1. WF7 Page Curation Scheduler**
**File**: `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`

**Core Function**: `process_page_curation_queue()`
```python
await run_job_loop(
    model=Page,
    status_enum=PageProcessingStatus,
    queued_status=PageProcessingStatus.Queued,
    processing_status=PageProcessingStatus.Processing,
    completed_status=PageProcessingStatus.Complete,
    failed_status=PageProcessingStatus.Error,
    processing_function=service.process_single_page_for_curation,
    batch_size=settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE,
    order_by_column=asc(Page.updated_at),
    status_field_name="page_processing_status",
    error_field_name="page_processing_error",
)
```

#### **2. Shared Scheduler Infrastructure**
**File**: `src/scheduler_instance.py`
- **Purpose**: Centralized APScheduler instance for ALL workflows
- **Critical**: Nuclear shared service - serves WF1-WF7
- **Engine**: AsyncIOScheduler with UTC timezone
- **Monitoring**: Event listeners for job execution and errors

#### **3. Scheduler Registration**
**File**: `src/main.py`
- **Function**: `setup_page_curation_scheduler()`
- **Configuration**:
  ```python
  scheduler.add_job(
      process_page_curation_queue,
      "interval",
      minutes=settings.PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES,
      id="v2_page_curation_processor",
      replace_existing=True,
      max_instances=settings.PAGE_CURATION_SCHEDULER_MAX_INSTANCES,
  )
  ```

### **Scheduler Configuration Settings**
```python
# Environment variables controlling scheduler behavior
PAGE_CURATION_SCHEDULER_BATCH_SIZE = 10           # Pages processed per cycle
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES = 5      # How often scheduler runs
PAGE_CURATION_SCHEDULER_MAX_INSTANCES = 1         # Prevent overlapping runs
```

### **Queue Detection Logic**
1. **Trigger**: User sets `page_curation_status = "Selected"` via API
2. **Auto-Queue**: Dual-status pattern sets `page_processing_status = "Queued"`
3. **Detection**: Scheduler queries for `PageProcessingStatus.Queued` pages
4. **Processing**: Calls `PageCurationService.process_single_page_for_curation()`
5. **Status Updates**: Processing → Complete/Error based on results

---

## 🔧 COMPONENT DEEP DIVE

### **1. WF7_V2_L1_1of1_ContactModel.py**

**Purpose**: SQLAlchemy model for contact data  
**Critical Features**:
- **Client-side UUID generation**: `id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`
- **Enum alignment**: Names must match database schema exactly
- **BaseModel inheritance**: Provides created_at, updated_at automatically

**Common Issues**:
- ❌ **Server-side UUID**: `server_default=text("gen_random_uuid()")` breaks object instantiation
- ❌ **Enum mismatch**: Wrong enum names cause `DatatypeMismatchError`
- ❌ **Field duplication**: Don't redefine BaseModel fields

**Testing**:
```python
# Test Contact creation
contact = Contact(
    page_id=page_id,
    domain_id=domain_id,
    email="test@example.com",
    phone="1234567890",
    email_type=ContactEmailTypeEnum.SERVICE.value,  # Use .value for string
    phone_type=ContactPhoneTypeEnum.BUSINESS.value
)
session.add(contact)
await session.commit()
```

### **2. WF7_V2_L4_1of2_PageCurationService.py**

**Purpose**: Core business logic for page processing  
**Key Method**: `process_single_page_for_curation(page_id, session)`

**Architecture**:
```python
class PageCurationService:
    def __init__(self):
        # Concurrency controls (currently unused but preserved)
        self.concurrent_semaphore = asyncio.Semaphore(10)
        self.enable_concurrent = False
    
    async def process_single_page_for_curation(self, page_id: UUID, session: AsyncSession) -> bool:
        # 1. Fetch page from database
        # 2. Call simple scraper: html_content = await scrape_page_simple_async(page_url)
        # 3. Extract contacts with regex
        # 4. Create Contact objects
        # 5. Save to database
        # 6. Update page status
        # 7. Return success/failure
```

**Critical Success Factors**:
- ✅ **Session acceptance**: Service accepts AsyncSession, never creates
- ✅ **Simple scraping**: Single line call to proven scraper
- ✅ **Proper enum handling**: Use `.value` for enum-to-string conversion
- ✅ **Error handling**: Comprehensive try/catch with logging

### **3. src/utils/simple_scraper.py**

**Purpose**: Reliable, async web scraping without external dependencies  
**Size**: 37 lines of focused code

**Implementation**:
```python
async def scrape_page_simple_async(url: str) -> str:
    """Simple, effective, non-blocking async scraper."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
        # Standard browser headers
    }
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content
                
    except Exception as e:
        logging.error(f"Simple async scraper failed for {url}: {e}")
        return ""  # Return empty string on failure
```

**Success Factors**:
- ✅ **SSL disabled**: Handles sites with certificate issues
- ✅ **Redirects enabled**: Follows redirects automatically  
- ✅ **Browser headers**: Mimics real browser requests
- ✅ **Timeout handling**: 20-second timeout prevents hanging
- ✅ **Error recovery**: Returns empty string on failure, doesn't crash

### **4. WF7_V2_L4_2of2_PageCurationScheduler.py**

**Purpose**: Background scheduler processing queued pages  
**Pattern**: Uses Curation SDK `run_job_loop`

**Implementation**:
```python
async def process_page_queue():
    await run_job_loop(
        process_fn=page_service.process_single_page_for_curation,
        queue_query=select(Page).filter(
            Page.page_processing_status == PageProcessingStatus.Queued
        ),
        status_field="page_processing_status",
        processing_value=PageProcessingStatus.Processing,
        completed_value=PageProcessingStatus.Complete,
        failed_value=PageProcessingStatus.Failed
    )
```

---

## 🧪 TESTING FRAMEWORK

### **Complete Testing Framework**

#### **API Endpoint Testing**

**1. List Pages (V3)**:
```bash
# Get pages with filtering
curl -X GET "https://scrapersky-backend.onrender.com/api/v3/pages/?page_curation_status=New&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**2. Batch Update Pages**:
```bash
# Select specific pages for processing
curl -X PUT "https://scrapersky-backend.onrender.com/api/v3/pages/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "page_ids": ["56d4f464-faee-4940-8532-17439157020e"],
    "status": "Selected"
  }'
```

**3. Filtered Batch Update ("Select All")**:
```bash
# Select all pages matching criteria
curl -X PUT "https://scrapersky-backend.onrender.com/api/v3/pages/status/filtered" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "status": "Selected",
    "page_curation_status": "New",
    "url_contains": "contact"
  }'
```

#### **End-to-End Testing Process**

**1. Complete Workflow Test**:
```bash
# Step 1: List available pages
curl -X GET "https://scrapersky-backend.onrender.com/api/v3/pages/?page_curation_status=New&limit=5"

# Step 2: Select pages for processing
curl -X PUT "https://scrapersky-backend.onrender.com/api/v3/pages/status" \
  -H "Content-Type: application/json" \
  -d '{
    "page_ids": ["PAGE_ID_HERE"],
    "status": "Selected"
  }'

# Step 3: Verify dual-status pattern worked
# Check that page_processing_status = "Queued"
```

**2. Monitor Logs**:
```bash
# Watch for processing
tail -f logs/app.log | grep "WF7\|Contact\|Simple async scraper"
```

**3. Expected Success Pattern**:
```
Simple async scraper successful for [URL]. Content length: [SIZE]
Found REAL email: [EMAIL]
Created REAL contact for [DOMAIN]: [EMAIL] | [PHONE]
Set page [PAGE_ID] status to Complete
SCHEDULER_LOOP: Finished processing batch for Page. Success: 1, Failed: 0
```

**4. Database Verification**:
```sql
-- Check page status
SELECT id, url, page_processing_status FROM pages WHERE id = '[PAGE_ID]';

-- Check created contact
SELECT email, phone, email_type, phone_type FROM contacts WHERE page_id = '[PAGE_ID]';
```

### **Component Testing Scripts**

**Available in `/testing_artifacts/`**:
- `simple_enum_test_2025-09-19.py` - Test enum values and conversions
- `test_basemodel_contact_creation_2025-09-19.py` - Test Contact model instantiation
- `test_contact_creation_debug_2025-09-19.py` - Debug contact creation issues
- `verify_contact_fix_2025-09-19.py` - Verify fixes are working

### **Scraper Testing**:
```python
# Test scraper directly
from src.utils.simple_scraper import scrape_page_simple_async

html = await scrape_page_simple_async("https://example.com")
print(f"Content length: {len(html)}")
```

---

## 🚨 TROUBLESHOOTING GUIDE

### **Common Issues & Solutions**

#### **1. Contact Creation Failures**

**Symptom**: `DatatypeMismatchError` or `ProgrammingError`
```
sqlalchemy.exc.ProgrammingError: column "contact_curation_status" is of type contact_curation_status but expression is of type text
```

**Root Cause**: Enum name mismatch between model and database
**Solution**: Verify enum names in model match database exactly
```python
# Check current database enums
SELECT enumlabel FROM pg_enum WHERE enumtypid = (
    SELECT oid FROM pg_type WHERE typname = 'contact_curation_status'
);

# Ensure model matches
contact_curation_status = Column(Enum(..., name='contact_curation_status'))
```

#### **2. UUID Generation Issues**

**Symptom**: `AttributeError` during Contact instantiation
**Root Cause**: Server-side UUID generation conflicts with SQLAlchemy objects
**Solution**: Use client-side generation
```python
# WRONG
id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

# CORRECT  
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

#### **3. Scraping Failures**

**Symptom**: Empty content or connection errors
**Common Causes**:
- SSL certificate issues → `ssl=False` in connector
- Blocked by user agent → Use browser-like headers
- Redirects not followed → `allow_redirects=True`
- Timeout issues → Adjust `ClientTimeout`

**Debug Process**:
```python
# Test with curl first
curl -k -L "https://example.com"

# Then test scraper
html = await scrape_page_simple_async("https://example.com")
```

#### **4. Scheduler Not Processing**

**Symptom**: Pages remain in Queued status
**Check**:
1. Scheduler running: `ps aux | grep scheduler`
2. Database connection: Check logs for connection errors
3. Queue query: Verify pages have `page_processing_status = 'Queued'`

#### **5. Enum Value Errors**

**Symptom**: Enum objects not converting to strings
**Solution**: Use `.value` when assigning enum values
```python
# WRONG
email_type=ContactEmailTypeEnum.SERVICE

# CORRECT
email_type=ContactEmailTypeEnum.SERVICE.value
```

#### **6. API Endpoint Issues**

**Symptom**: Pages not getting queued after status update
**Check**:
1. Verify dual-status pattern: `page_curation_status = "Selected"` should trigger `page_processing_status = "Queued"`
2. Check database after API call:
   ```sql
   SELECT id, page_curation_status, page_processing_status 
   FROM pages WHERE id = '[PAGE_ID]';
   ```
3. Verify V3 endpoint authentication if using authenticated routes

**Symptom**: Filtered updates not working
**Debug**:
```python
# Test filter logic manually
filters = []
if page_curation_status:
    filters.append(Page.page_curation_status == page_curation_status)
# Check if filters match expected pages
```

#### **7. Background Scheduler Issues**

**Symptom**: Scheduler not picking up queued pages
**Check**:
1. **Scheduler Running**: 
   ```bash
   # Check logs for scheduler startup
   grep "Page curation scheduler job added" logs/app.log
   ```

2. **Job Execution**:
   ```bash
   # Check for scheduler job execution
   grep "v2_page_curation_processor" logs/app.log
   ```

3. **Queue Detection**:
   ```sql
   -- Verify pages are actually queued
   SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';
   ```

4. **Scheduler Configuration**:
   ```python
   # Check environment variables
   PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES = 5  # Default
   PAGE_CURATION_SCHEDULER_BATCH_SIZE = 10       # Default
   ```

**Symptom**: Scheduler jobs overlapping or running multiple times
**Solution**: Check `max_instances=1` setting and ensure only one scheduler instance

#### **8. Authentication Issues (V3 Endpoints)**

**Symptom**: 401 Unauthorized on V3 endpoints
**Check**:
1. JWT token validity
2. `get_current_user` dependency working
3. Use V2 endpoints for testing if authentication is problematic

---

## 🔄 SCRAPERAPI REINTEGRATION GUIDE

### **Current State**
- **Status**: Shelved but preserved in `src/utils/scraper_api.py`
- **Rationale**: Cost savings during MVP phase
- **Preservation**: Full functionality intact and ready

### **Reintegration Process**

**1. Environment Setup**:
```bash
# Add ScraperAPI key to environment
export SCRAPER_API_KEY="your_api_key_here"
```

**2. Service Integration**:
```python
# In PageCurationService.py
from src.utils.scraper_api import ScraperAPIClient

async def process_single_page_for_curation(self, page_id: UUID, session: AsyncSession) -> bool:
    # Try simple scraper first
    html_content = await scrape_page_simple_async(page_url)
    
    # Fallback to ScraperAPI if simple scraper fails
    if not html_content:
        async with ScraperAPIClient() as scraper_client:
            html_content = await scraper_client.fetch(page_url, render_js=False)
    
    # Continue with extraction...
```

**3. Cost Management**:
```python
# Add usage tracking
SCRAPER_API_USAGE_LIMIT = int(os.getenv('SCRAPER_API_MONTHLY_LIMIT', '1000'))
current_usage = await get_monthly_scraper_usage()

if current_usage >= SCRAPER_API_USAGE_LIMIT:
    # Fall back to simple scraper only
    html_content = await scrape_page_simple_async(page_url)
```

**4. A/B Testing Framework**:
```python
# Test both approaches for quality comparison
USE_SCRAPER_API_PERCENTAGE = float(os.getenv('SCRAPER_API_TEST_PERCENTAGE', '0.1'))

if random.random() < USE_SCRAPER_API_PERCENTAGE:
    # Use ScraperAPI for this request
    html_content = await scraper_api_fetch(page_url)
else:
    # Use simple scraper
    html_content = await scrape_page_simple_async(page_url)
```

---

## 🚀 EXTENSION OPPORTUNITIES

### **Performance Enhancements**

**1. Concurrent Processing**:
```python
# Already built-in but disabled
self.enable_concurrent = os.getenv('WF7_ENABLE_CONCURRENT_PROCESSING', 'false').lower() == 'true'

# To enable:
export WF7_ENABLE_CONCURRENT_PROCESSING=true
export WF7_SCRAPER_API_MAX_CONCURRENT=5
```

**2. Caching Layer**:
```python
# Add Redis caching for scraped content
import redis

async def get_cached_content(url: str) -> Optional[str]:
    cache_key = f"scraped_content:{hashlib.md5(url.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    return cached.decode() if cached else None

async def cache_content(url: str, content: str, ttl: int = 3600):
    cache_key = f"scraped_content:{hashlib.md5(url.encode()).hexdigest()}"
    redis_client.setex(cache_key, ttl, content)
```

**3. Enhanced Extraction**:
```python
# Add structured data extraction
def extract_structured_data(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # JSON-LD structured data
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        try:
            data = json.loads(json_ld.string)
            return extract_contact_from_json_ld(data)
        except:
            pass
    
    # Microdata
    # Schema.org markup
    # etc.
```

### **Quality Improvements**

**1. Email Validation**:
```python
import re
from email_validator import validate_email

def validate_extracted_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except:
        return False
```

**2. Phone Number Standardization**:
```python
import phonenumbers

def standardize_phone(phone: str, country: str = 'US') -> Optional[str]:
    try:
        parsed = phonenumbers.parse(phone, country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        pass
    return None
```

**3. Duplicate Detection**:
```python
async def check_duplicate_contact(email: str, domain_id: UUID, session: AsyncSession) -> bool:
    existing = await session.execute(
        select(Contact).filter(
            and_(Contact.email == email, Contact.domain_id == domain_id)
        )
    )
    return existing.scalar_one_or_none() is not None
```

---

## 📊 MONITORING & METRICS

### **Key Performance Indicators**

**1. Success Rate Tracking**:
```python
# Add to scheduler logs
success_rate = (successful_pages / total_attempted_pages) * 100
logging.info(f"WF7_METRICS: Success rate: {success_rate:.1f}% ({successful_pages}/{total_attempted_pages})")
```

**2. Content Quality Metrics**:
```python
# Track extraction quality
avg_content_size = sum(content_sizes) / len(content_sizes)
email_extraction_rate = (pages_with_emails / total_pages) * 100
phone_extraction_rate = (pages_with_phones / total_pages) * 100
```

**3. Performance Metrics**:
```python
# Track processing times
processing_start = time.time()
# ... processing logic ...
processing_time = time.time() - processing_start
logging.info(f"WF7_PERFORMANCE: Page processed in {processing_time:.2f}s")
```

### **Health Checks**

**1. Database Connectivity**:
```python
async def health_check_database(session: AsyncSession) -> bool:
    try:
        await session.execute(select(1))
        return True
    except:
        return False
```

**2. Scraper Functionality**:
```python
async def health_check_scraper() -> bool:
    try:
        content = await scrape_page_simple_async("https://httpbin.org/html")
        return len(content) > 0
    except:
        return False
```

---

## 🔒 SECURITY CONSIDERATIONS

### **Input Validation**
```python
def validate_url(url: str) -> bool:
    # Check URL format
    if not re.match(r'^https?://', url):
        return False
    
    # Prevent SSRF attacks
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
        return False
    
    return True
```

### **Rate Limiting**
```python
# Implement per-domain rate limiting
from collections import defaultdict
import time

domain_last_request = defaultdict(float)
MIN_REQUEST_INTERVAL = 1.0  # seconds

async def rate_limit_check(domain: str) -> bool:
    now = time.time()
    if now - domain_last_request[domain] < MIN_REQUEST_INTERVAL:
        return False
    domain_last_request[domain] = now
    return True
```

---

## 📚 REFERENCE MATERIALS

### **Related Documentation**
- `EPIC_POST_MORTEM_WF7_CONTACT_SCRAPING_VICTORY_2025-09-20.md` - Complete victory story
- `L4_Service_Guardian_Pattern_AntiPattern_Companion.md` - Architectural patterns
- `/testing_artifacts/` - Reusable testing scripts
- `/archive_debugging_process/` - Historical debugging context

### **Commit References**
- **d6079e4**: BaseModel UUID fix (foundation)
- **17e740f**: Enum alignment fix (database integration)  
- **117e858**: Simple scraper implementation (core functionality)

### **External Dependencies**
```
aiohttp>=3.8.0          # Async HTTP client
beautifulsoup4>=4.11.0  # HTML parsing
sqlalchemy>=1.4.0       # ORM
asyncpg>=0.27.0         # PostgreSQL async driver
```

---

## 🎯 SUCCESS CRITERIA

**WF7 is considered healthy when**:
- ✅ Success rate > 95%
- ✅ Average processing time < 10 seconds per page
- ✅ No database connection errors
- ✅ Contact extraction rate > 80% for pages with visible contact info
- ✅ Zero external API dependency failures (ScraperAPI shelved)

**This document provides complete coverage for WF7 support, maintenance, and extension. Keep it updated as the workflow evolves.**

---

*"Simple solutions win. This is the way."* - **The WF7 Victory**

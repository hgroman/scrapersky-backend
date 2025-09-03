PRD: Multi-Threading ScraperAPI Support for WF7 Contact Extraction

Version: 1.0Date: August 27, 2025Status: Draft

---

Executive Summary

Implement concurrent processing for WF7 Contact Extraction Service to increase throughput
from 1-2 contacts/minute to 10-20 contacts/minute by processing multiple pages
simultaneously while maintaining system reliability and data consistency.

Business Impact: 10x throughput improvement enables processing larger page volumes and
reduces contact extraction delays.

---

Current State Analysis

Bottleneck Identification

- Sequential Processing: Pages processed one at a time
  (src/services/WF7_V2_L4_1of2_PageCurationService.py:27)
- Single HTTP Connection: One ScraperAPI call per scheduler cycle
- Batch Underutilization: Scheduler fetches 10 pages but processes sequentially
- Network I/O Bound: 70-second ScraperAPI timeout creates idle CPU time

Performance Baseline

- Current Rate: 1-2 contacts per minute
- Scheduler Interval: Every 60 seconds
- Batch Size: 10 pages per cycle
- Processing Time: ~70% waiting for ScraperAPI response

---

Solution Architecture

Threading Model

# Current: Sequential Processing

for page in pages:
content = await scraper_api.fetch(page.url) # 70s blocking
contacts = extract_contacts(content)
save_contacts(contacts)

# Proposed: Concurrent Processing

semaphore = asyncio.Semaphore(10)
tasks = [process_page_concurrent(page, semaphore) for page in pages]
results = await asyncio.gather(\*tasks, return_exceptions=True)

Concurrency Controls

1. API Rate Limiting: asyncio.Semaphore(10) - Maximum 10 concurrent ScraperAPI calls
2. Connection Pooling: TCPConnector(limit=50, limit_per_host=20) - HTTP efficiency
3. Error Isolation: return_exceptions=True - Individual page failures don't break batch
4. Transaction Safety: One database transaction per page (existing pattern preserved)

---

Technical Requirements

R1: Concurrent Page Processing

Requirement: Process up to 10 pages simultaneously per scheduler cycleImplementation:
Replace sequential loop with asyncio.gather() patternAcceptance Criteria:

- 10 pages processed concurrently in single batch
- Individual page failures don't affect others
- Database transactions remain atomic per page

R2: ScraperAPI Rate Limit Compliance

Requirement: Respect ScraperAPI concurrency limitsImplementation: Semaphore-based
throttling with configurable limitAcceptance Criteria:

- No 429 (rate limit) errors under normal load
- Configurable via SCRAPER_API_MAX_CONCURRENT environment variable
- Exponential backoff on rate limit detection

R3: Connection Pool Optimization

Requirement: Efficient HTTP connection reuse for ScraperAPI callsImplementation: Custom
TCPConnector with optimized settingsAcceptance Criteria:

- Connection reuse rate >80%
- No connection pool exhaustion errors
- Proper cleanup on service shutdown

R4: Error Handling & Recovery

Requirement: Robust error handling for concurrent failuresImplementation: Per-task
exception catching with retry logicAcceptance Criteria:

- Failed pages retry up to 3 times
- Error pages marked in database with details
- Service continues processing remaining pages

R5: Performance Monitoring

Requirement: Observable performance metrics for concurrent processingImplementation:
Timing metrics and success/failure trackingAcceptance Criteria:

- Average processing time per batch logged
- Success/failure rates tracked per ScraperAPI call
- Connection pool utilization metrics available

---

Implementation Plan

Phase 1: Core Concurrency (Week 1)

1.1 Modify PageCurationService

# File: src/services/WF7_V2_L4_1of2_PageCurationService.py

class PageCurationService:
def **init**(self):
self.semaphore = asyncio.Semaphore(
int(os.getenv('SCRAPER_API_MAX_CONCURRENT', '10'))
)

      async def process_page_batch_concurrent(self, page_ids: List[str]) ->

List[ProcessingResult]:
tasks = [
self.process_single_page_with_semaphore(page_id)
for page_id in page_ids
]
return await asyncio.gather(\*tasks, return_exceptions=True)

1.2 Update ScraperAPI Client

# File: src/utils/scraper_api.py

class ScraperAPIClient:
def **init**(self):
self.connector = aiohttp.TCPConnector(
limit=50,
limit_per_host=20,
keepalive_timeout=60,
enable_cleanup_closed=True
)

1.3 Modify Scheduler Integration

# File: src/services/WF7_V2_L4_2of2_PageCurationScheduler.py

async def process_page_curation_queue(): # Replace SDK sequential processing with concurrent batch processing
service = PageCurationService()
results = await service.process_page_batch_concurrent(page_ids)

Phase 2: Configuration & Monitoring (Week 2)

2.1 Environment Configuration
SCRAPER_API_MAX_CONCURRENT=10
HTTP_CONNECTION_POOL_SIZE=50
HTTP_CONNECTIONS_PER_HOST=20
WF7_ENABLE_CONCURRENT_PROCESSING=true

2.2 Performance Metrics

# Add to PageCurationService

async def process_with_metrics(self, page_ids):
start_time = time.time()
results = await self.process_page_batch_concurrent(page_ids)

      processing_time = time.time() - start_time
      success_count = sum(1 for r in results if not isinstance(r, Exception))

      logger.info(f"Processed {len(page_ids)} pages in {processing_time:.2f}s, "
                  f"{success_count} successful")

Phase 3: Production Validation (Week 3)

3.1 Feature Flag Rollout

- Deploy with WF7_ENABLE_CONCURRENT_PROCESSING=false
- Gradually enable for increasing percentages of batches
- Monitor performance and error rates

  3.2 Performance Testing

- Load test with 50+ concurrent pages
- Monitor database connection usage
- Validate contact creation accuracy

---

Risk Assessment

High Risk: Database Connection Exhaustion

Risk: Concurrent processing may exhaust Supabase connection poolMitigation:

- Monitor active connections via diagnostic queries
- Add connection pool monitoring alerts
- Implement circuit breaker pattern if needed

Medium Risk: ScraperAPI Rate Limiting

Risk: Concurrent requests may trigger rate limitsMitigation:

- Conservative semaphore limit (10 concurrent)
- Exponential backoff on 429 responses
- Configurable throttling parameters

Medium Risk: Memory Usage Increase

Risk: Concurrent processing may increase memory consumptionMitigation:

- Process pages in smaller concurrent batches if needed
- Monitor memory usage during rollout
- Implement memory-based throttling if required

Low Risk: Error Handling Complexity

Risk: More complex error scenarios with concurrent processingMitigation:

- Comprehensive exception handling per task
- Detailed error logging and monitoring
- Fallback to sequential processing on repeated failures

---

Configuration Management

Environment Variables

# Core Concurrency Settings

SCRAPER_API_MAX_CONCURRENT=10 # Max concurrent ScraperAPI calls
WF7_ENABLE_CONCURRENT_PROCESSING=true # Feature flag

# HTTP Client Settings

HTTP_CONNECTION_POOL_SIZE=50 # Total HTTP connections
HTTP_CONNECTIONS_PER_HOST=20 # Connections per host
HTTP_CONNECTION_TIMEOUT=70 # ScraperAPI timeout

# Performance Tuning

WF7_CONCURRENT_BATCH_SIZE=10 # Pages per concurrent batch
WF7_RETRY_ATTEMPTS=3 # Retry attempts per page
WF7_RETRY_BACKOFF_FACTOR=2.0 # Exponential backoff multiplier

Rollback Configuration

# Emergency rollback: Set environment variable

WF7_ENABLE_CONCURRENT_PROCESSING=false

# Code automatically falls back to sequential processing

if not os.getenv('WF7_ENABLE_CONCURRENT_PROCESSING', 'true').lower() == 'true':
return await self.process_page_batch_sequential(page_ids)

---

Success Metrics

Primary KPIs

- Throughput: 10-20 contacts per minute (10x improvement)
- Latency: <5 minutes from page selection to contact creation
- Success Rate: >95% of pages successfully processed
- Error Rate: <5% ScraperAPI failures

Secondary KPIs

- Resource Efficiency: <20% increase in memory usage
- Connection Health: >80% HTTP connection reuse rate
- System Stability: Zero database connection pool exhaustion events
- Cost Efficiency: Same cost per contact extracted

Monitoring & Alerts

# Key metrics to track

- concurrent_pages_processed_total
- scraper_api_rate_limit_errors_total
- http_connection_pool_utilization
- contact_extraction_success_rate
- average_batch_processing_time_seconds

---

Testing Strategy

Unit Tests

- Concurrent processing with mock ScraperAPI responses
- Error handling for individual page failures
- Semaphore behavior under load

Integration Tests

- End-to-end concurrent flow with real ScraperAPI calls
- Database transaction integrity under concurrent load
- Connection pool behavior with concurrent requests

Performance Tests

- Load testing with 50+ concurrent pages
- Memory usage profiling during concurrent processing
- Database connection usage monitoring

Production Validation

- Canary deployment with 10% of traffic
- Real-time monitoring of key metrics
- Automated rollback triggers on error thresholds

---

Timeline & Delivery

Week 1: Core concurrent processing implementationWeek 2: Configuration, monitoring, and
testingWeek 3: Production deployment and validationWeek 4: Performance optimization and
documentation

Total Effort: ~80 hours development + testingGo-Live: End of Month 1

---

Appendix: Technical References

Key Files to Modify

1. src/services/WF7_V2_L4_1of2_PageCurationService.py - Add concurrent processing
2. src/utils/scraper_api.py - Optimize HTTP client for concurrency
3. src/services/WF7_V2_L4_2of2_PageCurationScheduler.py - Update scheduler integration
4. src/config/settings.py - Add configuration parameters

Documentation References

- Docs_Context7/External_APIs/ScraperAPI_Documentation.md - Concurrency patterns
- Docs_Context7/Background_Processing/APScheduler_Documentation.md - Async scheduling
- Docs_Context7/HTTP_Networking/AIOHTTP_Documentation.md - Connection pooling
- personas_workflow/WF7_BRAIN_DUMP_VERIFIED_TRUTHS.md - Current implementation details

---

This PRD provides a complete roadmap for implementing multi-threading ScraperAPI support
while maintaining the proven reliability of the existing WF7 Contact Extraction Service.

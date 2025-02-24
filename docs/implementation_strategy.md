# ScraperSky Batch Processing Implementation Strategy

## Phase 1: Test Infrastructure Setup

### 1.1 Base Test Framework

```python
# tests/test_sitemap_batch.py

import pytest
import pytest_asyncio
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
from src.models import BatchScrapingRequest, BatchScrapingResponse
```

### 1.2 Test Categories

#### A. Single URL Preservation Tests

```python
@pytest.mark.asyncio
async def test_single_url_functionality():
    """Verify existing endpoint remains unchanged"""
    test_cases = [
        {"url": "https://valid.com", "expected": "success"},
        {"url": "invalid-url", "expected": "error"},
        {"url": "https://timeout.com", "expected": "timeout"}
    ]
    # Verify each case maintains current behavior
```

#### B. Batch Processing Tests

```python
@pytest.mark.asyncio
async def test_batch_basic_functionality():
    """Verify basic batch processing"""
    test_urls = [
        "https://test1.com",
        "https://test2.com",
        "https://test3.com"
    ]
    # Verify concurrent processing
    # Verify status tracking
    # Verify completion states
```

#### C. Error Handling Tests

```python
@pytest.mark.asyncio
async def test_batch_error_isolation():
    """Verify errors don't stop batch processing"""
    test_urls = [
        "https://valid1.com",
        "invalid-url",
        "https://valid2.com"
    ]
    # Verify valid URLs complete
    # Verify error reporting
    # Verify batch continues
```

#### D. Database Operation Tests

```python
@pytest.mark.asyncio
async def test_database_operations():
    """Verify database operations"""
    # Test single inserts
    # Test batch inserts
    # Verify data integrity
```

#### E. Performance Tests

```python
@pytest.mark.asyncio
async def test_concurrent_processing():
    """Verify performance improvements"""
    # Measure sequential vs concurrent
    # Verify resource usage
    # Check rate limiting
```

## Phase 2: Model Implementation

### 2.1 New Request/Response Models

```python
# src/models.py

class BatchScrapingRequest(BaseModel):
    urls: List[str]
    tenant_id: str
    batch_options: Optional[Dict[str, Any]] = None

class BatchScrapingResponse(BaseModel):
    batch_id: str
    status_url: str
    total_urls: int
    estimated_completion_time: Optional[datetime]

class BatchStatus(BaseModel):
    batch_id: str
    total_urls: int
    completed_urls: int
    failed_urls: int
    in_progress_urls: int
    status: str  # "pending", "processing", "completed", "failed"
    url_statuses: Dict[str, URLStatus]
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    errors: List[Dict[str, Any]]
```

## Phase 3: Database Enhancement

### 3.1 Batch Database Operations

```python
# src/db/domain_handler.py

class DomainDBHandler:
    @staticmethod
    async def batch_insert_domains(domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert multiple domains efficiently"""
        # Implementation with proper error handling
        # Return results for each domain
```

### 3.2 Status Tracking Enhancement

```python
# src/db/status_handler.py

class BatchStatusHandler:
    """Handle batch job status tracking"""
    async def update_batch_status()
    async def update_url_status()
    async def get_batch_status()
```

## Phase 4: Endpoint Implementation

### 4.1 New Batch Endpoint

```python
# src/routers/sitemap_scraper.py

@router.post("/scrapersky/batch", response_model=BatchScrapingResponse)
async def batch_scan_sitemaps(request: BatchScrapingRequest):
    """Process multiple URLs concurrently"""
    # Implementation details
```

### 4.2 Batch Processing Logic

```python
async def process_batch(batch_id: str, urls: List[str], tenant_id: str):
    """Core batch processing logic"""
    # Concurrent processing implementation
    # Status tracking
    # Error handling
```

## Phase 5: Testing & Verification

### 5.1 Test Execution Order

1. Run single URL preservation tests
2. Run batch functionality tests
3. Run error handling tests
4. Run database operation tests
5. Run performance tests

### 5.2 Verification Checklist

- [ ] All existing single URL tests pass
- [ ] Batch processing handles multiple URLs
- [ ] Error isolation works correctly
- [ ] Database operations maintain consistency
- [ ] Performance improvements verified
- [ ] Resource usage within limits
- [ ] Rate limiting respected
- [ ] Status tracking accurate
- [ ] Error reporting comprehensive

## Phase 6: Performance Optimization

### 6.1 Concurrency Control

- Implement URL processing pools
- Add rate limiting
- Monitor resource usage

### 6.2 Database Optimization

- Connection pool management
- Batch insert optimization
- Index usage verification

## Phase 7: Monitoring & Logging

### 7.1 Enhanced Logging

```python
# src/utils/logging.py

class BatchLogger:
    """Enhanced logging for batch operations"""
    # Implementation details
```

### 7.2 Metrics Collection

- Processing time per URL
- Batch completion rates
- Error rates
- Resource usage metrics

## Phase 8: Documentation

### 8.1 API Documentation

- Single URL endpoint (preserved)
- New batch endpoint
- Status endpoints
- Error codes and handling

### 8.2 Integration Guide

- Migration guide
- Best practices
- Rate limiting guidelines
- Error handling recommendations

## Implementation Sequence

1. **Day 1: Test Infrastructure**

   - Set up test framework
   - Implement base test cases
   - Verify test infrastructure

2. **Day 2: Models & Database**

   - Implement new models
   - Add batch database operations
   - Test database functions

3. **Day 3: Core Implementation**

   - Add batch endpoint
   - Implement concurrent processing
   - Basic error handling

4. **Day 4: Status & Monitoring**

   - Enhance status tracking
   - Add comprehensive logging
   - Implement metrics collection

5. **Day 5: Testing & Optimization**

   - Run all test categories
   - Optimize performance
   - Fine-tune resource usage

6. **Day 6: Documentation & Cleanup**
   - Complete documentation
   - Clean up code
   - Final testing

## Success Criteria Verification

### Functionality

- [ ] Single URL processing unchanged
- [ ] Batch processing working
- [ ] Error handling robust
- [ ] Status tracking accurate

### Performance

- [ ] Concurrent processing verified
- [ ] Resource usage optimized
- [ ] Database operations efficient

### Reliability

- [ ] Error isolation working
- [ ] Recovery mechanisms tested
- [ ] Data consistency maintained

### Documentation

- [ ] API docs complete
- [ ] Integration guide ready
- [ ] Test coverage documented

## Rollback Plan

### Immediate Rollback

1. Revert to previous version
2. Verify single URL functionality
3. Notify affected systems

### Gradual Rollback

1. Disable batch endpoint
2. Process batch requests sequentially
3. Monitor and adjust

## Final Verification

### System Tests

- [ ] Load testing
- [ ] Stress testing
- [ ] Recovery testing
- [ ] Integration testing

### Documentation Review

- [ ] API documentation complete
- [ ] Integration guide reviewed
- [ ] Error handling documented
- [ ] Performance guidelines documented

This strategy document serves as our comprehensive guide through the implementation process. Each phase must be completed and verified before moving to the next. All changes must be tracked and documented.

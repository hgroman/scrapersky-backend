# BATCH PROCESSING ARCHITECTURE RECOMMENDATIONS

**Document ID:** 07-53-BATCH-PROCESSING-ARCHITECTURE-RECOMMENDATIONS
**Date:** 2025-03-28
**Status:** Proposal
**Priority:** High
**Related Documents:**

- 07-51-BATCH-PROCESSING-DEBUG-PLAN
- 07-52-BATCH-PROCESSING-DEBUG-FINDINGS

## 1. Executive Summary

Our investigation of background task failures in the batch processing system has highlighted significant architectural concerns. This document proposes a comprehensive redesign of our background processing architecture to address these issues and build a more robust, maintainable system.

The key recommendations are:

1. **Replace FastAPI Background Tasks with Redis Queue**
2. **Implement Dedicated Worker Processes**
3. **Simplify Dependency Management**
4. **Enhance Monitoring and Observability**

## 2. Current Architecture Analysis

### 2.1 Current Design

The current batch processing architecture relies on FastAPI's background tasks, with the following characteristics:

1. **FastAPI Background Tasks**: Uses `BackgroundTasks.add_task()` in HTTP handlers
2. **Dynamic Imports**: Delayed imports in background tasks to avoid circular dependencies
3. **Self-Contained Sessions**: Background tasks create their own database sessions
4. **In-Process Execution**: Tasks run within the main API server process

### 2.2 Identified Issues

Our diagnostic investigation revealed several critical issues:

1. **Reliability Concerns**: Background tasks appear to be failing silently with no execution evidence
2. **Complexity**: Dynamic imports and circular dependency workarounds create maintenance challenges
3. **Limited Scalability**: In-process execution limits the number of concurrent tasks
4. **Observability Gaps**: Lack of comprehensive monitoring for background task lifecycle
5. **Restart Vulnerability**: Tasks are lost on server restarts or crashes

## 3. Architectural Recommendations

### 3.1 Redis-Based Task Queue

**Recommendation**: Replace FastAPI background tasks with a Redis-based task queue.

**Implementation**:

1. Add Redis as a dependency in the project
2. Use `rq` (Redis Queue) or `arq` (Async Redis Queue) library for task management
3. Modify batch creation endpoint to enqueue tasks instead of using background tasks

**Benefits**:

- **Persistence**: Tasks survive server restarts or crashes
- **Visibility**: Task queue provides monitoring and inspection capabilities
- **Throttling**: Control concurrent task execution
- **Retry Logic**: Built-in error handling and retry capabilities

**Example Implementation**:

```python
# Task definition in batch_processor_service.py
async def process_batch_task(batch_id: str, tenant_id: str, user_id: str, domains: list):
    """Process a batch of domains - designed to be run by a worker process."""
    # Implementation without circular dependency concerns

# Router implementation
@router.post("/batch")
async def create_batch_endpoint(request: BatchRequest, ...):
    async with session.begin():
        # Create batch record
        batch = await create_batch(...)

    # Enqueue task instead of using background_tasks.add_task
    await arq_redis.enqueue_job(
        'process_batch',
        batch_id,
        tenant_id,
        user_id,
        domains
    )

    return {"batch_id": batch_id, ...}
```

### 3.2 Dedicated Worker Processes

**Recommendation**: Implement dedicated worker processes separate from the API server.

**Implementation**:

1. Create worker modules that consume from the Redis queue
2. Deploy workers as separate processes/containers
3. Configure workers with appropriate resource limits and restart policies

**Benefits**:

- **Isolation**: API server stability not affected by background processing
- **Scalability**: Workers can be scaled independently from API server
- **Resource Management**: Workers can be optimized for computation vs API for I/O
- **Failure Containment**: Worker failures don't impact API availability

**Example Worker Configuration**:

```python
# worker.py
from arq.connections import RedisSettings
from arq.worker import Worker

async def process_batch(ctx, batch_id, tenant_id, user_id, domains):
    # Implementation of batch processing

async def startup(ctx):
    # Setup database connection pool and other resources

async def shutdown(ctx):
    # Clean up resources

class WorkerSettings:
    redis_settings = RedisSettings(host='redis')
    functions = [process_batch]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 3600  # 1 hour
```

### 3.3 Dependency Structure Simplification

**Recommendation**: Refactor the dependency structure to eliminate circular imports.

**Implementation**:

1. Create a dedicated module for shared functionality
2. Implement clear separation of concerns
3. Use dependency injection instead of direct imports

**Target Structure**:

```
src/
  services/
    batch/
      models.py             # Data models for batch operations
      queue.py              # Task queue integration
      api_service.py        # Services used by API routes
      worker_service.py     # Services used by worker processes
      shared.py             # Shared functionality
    page_scraper/
      models.py             # Data models
      api_service.py        # API-facing services
      worker_service.py     # Worker-facing services
```

**Benefits**:

- **Maintainability**: Clear separation reduces complexity
- **Testability**: Easier to write unit tests for isolated components
- **Scalability**: Services can evolve independently

### 3.4 Enhanced Monitoring and Observability

**Recommendation**: Implement comprehensive monitoring for task processing.

**Implementation**:

1. Add structured logging throughout task lifecycle
2. Implement metrics collection (Prometheus)
3. Create dashboard for task queue health (Grafana)
4. Set up alerts for stuck or failed tasks

**Key Metrics**:

- Queue depth and latency
- Task processing time
- Success/failure rates
- Resource utilization

**Benefits**:

- **Visibility**: Real-time insights into processing status
- **Proactive Resolution**: Early detection of issues
- **Capacity Planning**: Data-driven scaling decisions

## 4. Implementation Roadmap

### Phase 1: Immediate Stability (Week 1)

1. Deploy diagnostics from 07-51-BATCH-PROCESSING-DEBUG-PLAN
2. Fix identified syntax errors in background task processor
3. Implement the monitoring script (`batch_task_monitor.py`)

### Phase 2: Redis Queue Integration (Weeks 2-3)

1. Add Redis and task queue library dependencies
2. Create basic worker implementation
3. Modify batch creation endpoint to use task queue
4. Add robust error handling and retry logic

### Phase 3: Background Task Migration (Weeks 3-4)

1. Refactor dependency structure
2. Implement worker process with proper separation
3. Add monitoring and metrics collection
4. Test recovery from various failure scenarios

### Phase 4: Deployment and Optimization (Weeks 5-6)

1. Deploy worker containers alongside API server
2. Set up monitoring dashboards
3. Configure auto-scaling based on queue depth
4. Document architecture and operations procedures

## 5. Success Criteria

The implementation will be considered successful when:

1. **Reliability**: Batch processing operates consistently with zero silent failures
2. **Visibility**: Operators can view the status of any batch job in real-time
3. **Recoverability**: The system automatically recovers from server crashes or restarts
4. **Maintainability**: Code structure eliminates circular dependencies
5. **Scalability**: Processing capacity can easily scale with demand

## 6. Alternative Approaches Considered

### 6.1 Celery Task Queue

**Assessment**: Would work but adds more dependencies than necessary (RabbitMQ, etc.)

### 6.2 Direct Processing in API Request

**Assessment**: Would eliminate background task issues but block API responses for potentially long operations

### 6.3 Scheduled Polling Job

**Assessment**: Viable as an interim solution (implemented in batch_task_monitor.py) but less efficient than event-driven processing

## 7. Resource Requirements

1. **Redis Instance**: For task queue storage
2. **Worker Containers**: At least 2 for redundancy, auto-scaled based on queue depth
3. **Monitoring Stack**: Prometheus and Grafana for metrics collection and visualization

## 8. Conclusion

The proposed architecture addresses the fundamental issues with the current background task implementation while providing a foundation for future scalability. By moving to a dedicated task queue with separate worker processes, we can achieve higher reliability, better observability, and easier maintenance of our batch processing system.

The architectural changes are significant but can be implemented incrementally, with immediate fixes to stabilize the current system while working toward the robust long-term solution.

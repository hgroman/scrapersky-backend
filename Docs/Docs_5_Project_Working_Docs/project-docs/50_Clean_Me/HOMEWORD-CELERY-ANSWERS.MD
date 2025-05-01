# CELERY INTEGRATION HOMEWORK ANSWERS

## 1. Deployment & Infrastructure

- **How many Render.com services/instances do you plan to run?**

  - Currently running 1 instance on a starter plan
  - For MVP, we'll keep everything in the same container (Celery workers, Beat, and FastAPI)

- **Do you want to host Celery workers in the same container as FastAPI, or each in separate services?**

  - For MVP, we'll host everything in the same container to simplify the implementation
  - This approach prioritizes simplicity for initial functionality testing

- **What are the resource constraints on each service?**

  - Current Docker container specifications:
    - Memory limit: 512MB
    - CPU limit: 0.5 cores
    - Memory reservation: 256MB
    - CPU reservation: 0.25 cores
  - These constraints will initially apply to the combined FastAPI/Celery container

- **Do you intend to scale up from the Starter plan if needed?**
  - No immediate plans to scale up for the MVP phase
  - Will consider scaling options after functionality is proven

## 2. Supavisor Connection Limits

- **What is your desired or configured pool_size in production?**

  - Production: min=2, max=20 connections (from docker-compose.prod.yml)
  - Development: min=5, max=10 connections

- **Have you tested the upper bound on concurrent tasks from Celery?**
  - No formal testing of concurrent task limits has been conducted yet
  - Will start with conservative concurrency settings for MVP
  - Critical to maintain Supavisor connection pooling requirements

## 3. Task Workloads

- **How many domain/page items do you handle every 5 minutes?**

  - For MVP, processing speed is not critical
  - We can process items as slowly as needed to validate functionality

- **Do you anticipate heavy CPU or memory usage in these tasks?**

  - Running scrapers which could vary in resource usage
  - Some scraping operations may be memory or CPU intensive depending on the target site
  - Need to monitor resource usage during initial implementation

- **Is APScheduler definitely being replaced by Celery Beat?**
  - Current implementation uses APScheduler 3.10.4
  - Plan is to replace APScheduler with Celery Beat for all scheduled tasks

## 4. Authentication & Security

- **For user-specific tasks, do you need any user tokens or is it always a "system" user context?**

  - No specific requirements identified at this time
  - No prior experience with Celery authentication patterns
  - Will start with system-level authentication for MVP

- **Are there sensitive data privacy concerns?**
  - Current authentication is JWT-based at the router boundary
  - RBAC and tenant isolation have been removed from the codebase
  - No specific sensitive data handling requirements identified for Celery tasks

## 5. Logging & Monitoring

- **Do you have a central log aggregator?**

  - No central log aggregator is currently in use
  - Relying on standard application logging

- **Do you plan on using Flower or Celery's built-in events?**
  - No immediate plans to use Flower
  - Will rely on Celery's default logging and monitoring for MVP

## 6. Testing & QA

- **Do you have a dedicated staging environment?**

  - No separate staging environment
  - Local Docker container development serves as the testing environment

- **Any plan for load testing or stress testing?**
  - No formal load testing plan for the initial implementation
  - Will test functionality first, then address performance if needed

## 7. Future Scalability

- **Are you planning to horizontally scale Celery workers or just vertically scale?**

  - Plan to scale either horizontally or vertically after the MVP phase
  - Decision on scaling approach will depend on performance observations

- **Do you foresee any long-running tasks?**
  - No long-running tasks expected initially
  - Future website scraping tasks might become long-running
  - Will address specialized configuration needs if/when they arise

## 8. Additional Edge Constraints

- **Are there file-handling tasks, or do you only store textual metadata?**

  - Based on the codebase, primarily dealing with website metadata
  - No significant file handling operations identified

- **Any third-party integrations we must consider?**
  - Integration with ScraperAPI for web scraping
  - No other rate-limited API integrations identified as critical constraints

## Critical Implementation Requirements

The following requirements must be maintained throughout the Celery implementation:

1. **Supavisor Connection Parameters**:

   - `raw_sql=true`
   - `no_prepare=true`
   - `statement_cache_size=0`

2. **Session Management**:

   - Isolated database sessions for each operation
   - Proper transaction handling following existing patterns
   - Background session handler pattern for Celery tasks

3. **Error Handling**:
   - Comprehensive error logging
   - Task status updates on failures

This MVP implementation will focus on validating functionality rather than optimizing for scale or performance, with the intention to expand and optimize once the core functionality is proven.

# Transaction Management Comprehensive Guide: ScraperSky Standard

## 1. Executive Summary

This document establishes the authoritative standard for database transaction management across all ScraperSky services. The guidance here is **mandatory** for all database interactions. Transaction management issues have been a persistent source of bugs and system instability in the ScraperSky backend. Following these standards will ensure consistent, reliable, and maintainable database operations.

## 2. Core Principle

> **"Routers own transaction boundaries, services are transaction-aware but do not create transactions."**

This single guiding principle forms the foundation of our transaction management strategy. It establishes clear separation of concerns and prevents the most common transaction errors encountered in our codebase.

## 3. Key Sources

This guide consolidates the proven patterns established in several key project documents:

1. **[204-TRANSACTION-MANAGEMENT-PATTERN.md](Feature-Alignment-Testing-Plan/204-TRANSACTION-MANAGEMENT-PATTERN.md)** - Establishes the foundational pattern
2. **[323-MODERNIZED-SITEMAP-TRANSACTION-FIX-SUMMARY.md](Feature-Alignment-Testing-Plan/323-MODERNIZED-SITEMAP-TRANSACTION-FIX-SUMMARY.md)** - Demonstrates application to the ContentMap service
3. **[214-TRANSACTION-MANAGEMENT-FIX-SUMMARY.md](Feature-Alignment-Testing-Plan/214-TRANSACTION-MANAGEMENT-FIX-SUMMARY.md)** - Documents consistent implementation across multiple components

## 4. Responsibility Assignment

| Component           | Transaction Responsibility                               |
| ------------------- | -------------------------------------------------------- |
| **Router**          | Creates and manages transaction boundaries               |
| **Service**         | Uses provided session, checks transaction state          |
| **Repository**      | Uses provided session, never manages transactions        |
| **Background Task** | Creates its own session and manages its own transactions |

## 5. Implementation Patterns

### 5.1 Router Implementation

```python
@router.post("/endpoint")
async def create_entity(
    request: EntityCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    # Router is responsible for transaction boundary
    async with session.begin():
        # Pass session to service
        entity = await entity_service.create_entity(
            session=session,
            data=request.dict()
        )

    # Return response after transaction is committed
    return EntityResponse.model_validate(entity)
```

### 5.2 Service Implementation

```python
async def create_entity(self, session: AsyncSession, data: dict) -> Entity:
    # Check transaction state (for logging/debugging)
    in_transaction = session.in_transaction()
    logger.debug(f"Transaction state in create_entity: {in_transaction}")

    try:
        # Use session directly without managing transactions
        entity = Entity(**data)
        session.add(entity)

        # Flush to get generated values but don't commit
        await session.flush()

        return entity
    except Exception as e:
        # Log error but don't handle transaction - let it propagate
        logger.error(f"Error creating entity: {str(e)}")
        raise  # Must raise for proper transaction handling
```

### 5.3 Background Task Implementation

```python
async def process_background_task(job_id: str, data: dict):
    # Import session factory
    from src.db.session import get_session

    # Create a new dedicated session for the background task
    async with get_session() as bg_session:
        try:
            # Explicitly manage transaction
            async with bg_session.begin():
                logger.info(f"Starting background processing for job: {job_id}")

                # Process data within transaction
                result = await service.process_data(
                    session=bg_session,
                    job_id=job_id,
                    data=data
                )

                logger.info(f"Background processing completed for job: {job_id}")
                return result
        except Exception as e:
            # Log errors but don't propagate since this is a background task
            logger.error(f"Error in background task {job_id}: {str(e)}")

            # Optional: Record error in database with a new session
            try:
                async with get_session() as error_session:
                    async with error_session.begin():
                        await job_service.update_job_status(
                            session=error_session,
                            job_id=job_id,
                            status="failed",
                            error=str(e)
                        )
            except Exception as inner_e:
                logger.error(f"Failed to record error state: {str(inner_e)}")
```

## 6. Common Anti-Patterns to Avoid

| Anti-Pattern                                     | Why It's Problematic                                                         | Correct Approach                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Nested Transactions**                          | Causes "A transaction is already begun on this Session" errors               | Ensure routers own transaction boundaries, services don't create transactions |
| **Service-Created Transactions**                 | Creates inconsistent transaction boundaries, violates separation of concerns | Services should use provided session, never create transaction boundaries     |
| **Using Session Factory in Services**            | Creates multiple uncorrelated session objects                                | Services should use the session passed from routers                           |
| **Reusing Request Sessions in Background Tasks** | Sessions may be closed when task executes                                    | Background tasks must create their own session                                |
| **Swallowing Exceptions in Transaction**         | Prevents proper transaction rollback                                         | Propagate exceptions to allow transaction manager to handle rollback          |
| **Using `session.commit()` Directly**            | Bypasses context manager, creates inconsistent state                         | Always use `async with session.begin()` for transaction management            |

## 7. Transaction Management for Specific Patterns

### 7.1 Error Handling in Transaction

```python
async with session.begin():
    try:
        # Transaction work here
        result = await service.do_work(session)
        return result
    except ValueError as e:
        # Handle expected errors with appropriate response
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log unexpected errors before re-raising
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    # Transaction is committed if no exceptions, rolled back otherwise
```

### 7.2 Transaction-Aware Service Methods

```python
async def update_entity(self, session: AsyncSession, entity_id: str, data: dict):
    # Check transaction state
    in_transaction = session.in_transaction()
    logger.debug(f"Transaction state in update_entity: {in_transaction}")

    # Find entity
    entity = await self._get_entity_by_id(session, entity_id)
    if not entity:
        raise ValueError(f"Entity {entity_id} not found")

    # Update fields
    for key, value in data.items():
        if hasattr(entity, key):
            setattr(entity, key, value)

    # No need to call session.commit() - flush only
    await session.flush()
    return entity
```

### 7.3 FastAPI Background Tasks

```python
@router.post("/scan")
async def scan_domain(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session)
):
    # Create job record within transaction
    async with session.begin():
        job = await job_service.create_job(
            session=session,
            job_type="domain_scan",
            data=request.dict()
        )

    # Add background task to run after response is sent
    # Important: Don't pass the current session to background task
    background_tasks.add_task(
        process_domain_scan,
        job_id=job.id,
        domain=request.domain
    )

    # Return response immediately
    return {"job_id": job.id, "status": "processing"}
```

## 8. Ensuring Compliance

To ensure your code follows these transaction management patterns:

1. **Review every router endpoint** to verify it creates proper transaction boundaries
2. **Check every service method** to confirm it doesn't create its own transactions
3. **Verify background tasks** create their own sessions and manage their own transactions
4. **Add transaction state logging** to help debug transaction issues
5. **Write tests** that specifically verify transaction behavior
6. **Add linting rules** to check for common anti-patterns

## 9. Transaction Management Benefits

Proper implementation of this transaction management pattern provides:

1. **Reliability**: Consistent transaction boundaries prevent errors
2. **Clarity**: Clear responsibility assignment improves code understanding
3. **Performance**: Properly managed transactions improve database efficiency
4. **Maintainability**: Consistent patterns make code easier to maintain
5. **Debugging**: Transaction state logging simplifies troubleshooting
6. **Concurrency**: Proper isolation prevents race conditions

## 10. Conclusion

Transaction management is a critical aspect of database interaction in the ScraperSky backend. By following the patterns established in this document—specifically that **routers own transaction boundaries and services are transaction-aware but do not create transactions**—we can ensure reliable, maintainable database operations.

This document serves as the definitive guide for all transaction management across the entire codebase. All deviations from this pattern must be explicitly justified, documented, and approved by the system architect.

# Comprehensive Cleanup Guide for Code Changes

## Files Modified

1. `src/services/page_scraper/processing_service.py` - Primary file modified with incorrect changes

## Summary of Errors

### 1. Tenant Isolation Not Removed

Despite repeated instructions to remove tenant isolation, tenant_id parameters and filters were incorrectly maintained:

```python
# INCORRECT: Maintained tenant_id parameter
async def initiate_batch_scan(
    self,
    session: AsyncSession,
    domains: List[str],
    tenant_id: str,  # Should be removed
    user_id: str = "system",
    max_pages: int = 1000,
    batch_id: Optional[str] = None,
    raw_sql: bool = True,
    no_prepare: bool = True,
    statement_cache_size: int = 0
) -> Dict[str, Any]:
```

```sql
# INCORRECT: SQL query with tenant_id filter
SELECT * FROM domains
WHERE domain = :domain_url
AND tenant_id = :tenant_id  # Should be removed
LIMIT 1
```

```python
# INCORRECT: Using tenant_id in the validate_domain method
async def validate_domain(self, domain: str, tenant_id: str) -> Tuple[bool, str, Optional[Domain]]:
```

**Required Fix**: Remove all tenant_id parameters from method signatures and remove tenant_id filters from all SQL queries.

### 2. PgBouncer vs. Supavisor Confusion

Incorrectly focused on PgBouncer compatibility instead of using Supavisor as specified in the documentation:

```python
# INCORRECT: Comments referencing PgBouncer
# Apply execution options to the session engine directly
session.bind.engine.update_execution_options(
    no_parameters=no_prepare,  # Disable prepared statements for Supavisor
    statement_cache_size=statement_cache_size  # Disable statement caching
)
logger.info("Applied Supavisor compatibility options to session")
```

**Required Fix**: Use proper Supavisor connection pooling as specified in the documentation, not PgBouncer workarounds.

### 3. Job ID UUID Handling Issues

Made changes to UUID handling without properly understanding the architecture:

```python
# INCORRECT: Converting batch_id to UUID
batch_uuid = uuid.UUID(batch_id)
```

**Required Fix**: Ensure proper UUID standardization is followed according to the UUID standardization guide.

### 4. Bypassing Service Methods

Instead of fixing the proper service methods, incorrect workarounds were implemented:

```python
# INCORRECT: Direct SQL instead of using proper service methods
batch_query = text("""
    INSERT INTO batch_jobs (
        batch_id, tenant_id, created_by, processor_type,
        status, total_domains, completed_domains, failed_domains,
        progress, options, batch_metadata
    ) VALUES (
        :batch_id, :tenant_id, :created_by, :processor_type,
        :status, :total_domains, :completed_domains, :failed_domains,
        :progress, :options, :batch_metadata
    )
    RETURNING id
""")
```

**Required Fix**: Use the proper service methods and fix any issues with them directly, rather than bypassing them.

### 5. Execution Options Implementation

Incorrectly applied execution options:

```python
# INCORRECT: Directly modifying engine execution options
session.bind.engine.update_execution_options(
    no_parameters=no_prepare,
    statement_cache_size=statement_cache_size
)
```

**Required Fix**: Apply execution options according to the Supavisor connection pooling standards, which should be configured at the connection/engine level consistently.

## Detailed Changes Made to Each File

### src/services/page_scraper/processing_service.py

1. **validate_domain Method**:

   - Changed to be a pure validation function without database queries (this part was correct)
   - But still maintained tenant_id parameter incorrectly

2. **initiate_domain_scan Method**:

   - Added execution options but incorrectly focused on PgBouncer compatibility
   - Used raw SQL with tenant_id filter which should be removed

3. **initiate_batch_scan Method**:

   - Added raw_sql, no_prepare, statement_cache_size parameters
   - Incorrectly maintained tenant_id parameter
   - Bypassed batch_processor_service.process_domains_batch with direct SQL
   - Added PgBouncer-specific comments and logic

4. **get_batch_status Method**:
   - Added raw_sql, no_prepare, statement_cache_size parameters
   - Incorrectly maintained tenant_id parameter
   - Bypassed batch_processor_service.get_batch_status with direct SQL
   - Added incorrect UUID conversion logic

## Correct Implementation Guidelines

1. **Remove Tenant Isolation**:

   - Remove all tenant_id parameters from method signatures
   - Remove tenant_id filtering from SQL queries
   - Update comments and documentation to reflect tenant isolation removal

2. **Use Supavisor Connection Pooling**:

   - Follow the standards in DATABASE_CONNECTION_STANDARDS.md
   - Configure connection pooling at the engine creation level
   - Use proper execution options specific to Supavisor

3. **Fix Service Methods**:

   - Fix any issues with batch_processor_service.process_domains_batch and get_batch_status directly
   - Don't create workarounds with direct SQL unless absolutely necessary

4. **UUID Standardization**:
   - Follow the guidelines in UUID_STANDARDIZATION_GUIDE.md
   - Ensure consistent UUID handling across the codebase

## Testing Approach

After making corrections, test with:

1. Batch domain scanner test:

   ```
   curl -X POST http://localhost:8000/api/v3/batch_page_scraper/batch -H "Content-Type: application/json" -d '{"domains": ["bbc.com", "nytimes.com"]}' | jq
   ```

2. Batch status check:

   ```
   curl http://localhost:8000/api/v3/batch_page_scraper/batch/{batch_id}/status | jq
   ```

3. Individual job status check:

   ```
   curl http://localhost:8000/api/v3/batch_page_scraper/job/{job_id}/status | jq
   ```

4. UI testing:
   ```
   open http://localhost:8000/static/batch-domain-scanner.html
   ```

Verify that all operations complete without prepared statement errors and that tenant_id is not being used anywhere.

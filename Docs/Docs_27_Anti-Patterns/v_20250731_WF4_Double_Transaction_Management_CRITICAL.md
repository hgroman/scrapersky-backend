# Double Transaction Management Anti-Pattern

**Anti-Pattern ID:** AP-20250731-003  
**Date Occurred:** 2025-07-31  
**Workflow Affected:** WF4 (Domain Curation)  
**Severity:** CRITICAL  
**Category:** Architectural  
**Risk Level:** WORKFLOW_BREAKING  

---

## YAML Metadata

```yaml
# Architecture Location (WHERE)
workflow: "WF4"
layer: "LAYER4"
component: "scheduler"
affected_files: ["src/services/sitemap_scheduler.py", "src/session/async_session.py"]

# Business Context (WHY IT MATTERS)  
business_process: "Domain Curation Status Updates"
affects_handoff: ["WF4->WF5"]
user_facing: true
blocking_ui: "Domain Curation Submit Button"

# AI Context (WHEN TO CONSULT)
danger_level: "WORKFLOW_BREAKING"
consultation_required: ["Database_Session_Management", "Background_Job_Architecture"]
technology: ["SQLAlchemy", "AsyncPG", "Supavisor", "APScheduler"]

# Discovery Context
discovery_method: "Database Lock Investigation"
detection_time: "1+ hours to identify root cause"
business_impact: "Complete WF4 pipeline failure"

# Prevention Tags
tags: ["transaction_management", "context_managers", "database_sessions", "background_jobs", "idle_in_transaction", "supavisor", "scheduler_patterns"]
```

---

## Anti-Pattern Summary

**Pattern Name:** Double Transaction Management  
**Description:** Manually managing database transactions (commit/rollback) inside context managers that already handle transaction lifecycle automatically  
**Risk Level:** WORKFLOW_BREAKING  

**What Went Wrong:** A background scheduler function was calling `await session.commit()` inside a `get_background_session()` context manager that already handles commits automatically, creating "idle in transaction" database connections that blocked all UPDATE operations system-wide.

---

## Incident Details

### What Happened
- **Symptom:** WF4 Domain Curation UI completely froze when users clicked "Update Selected" button
- **Duration:** Indefinite hang with no error messages or timeouts
- **Scope:** All domain status updates blocked system-wide
- **Business Impact:** Complete WF4→WF5 pipeline failure, preventing domain processing workflows

### Root Cause Analysis
The `handle_job_error()` function in `src/services/sitemap_scheduler.py` contained this problematic pattern:

```python
# ANTI-PATTERN: Double transaction management
async def handle_job_error(job_id: int, error_message: str):
    try:
        async with get_background_session() as session:  # Context manager handles transaction
            stmt = update(Job).where(Job.id == job_id).values(status="failed")
            await session.execute(stmt)
            await session.commit()  # ❌ MANUAL COMMIT INSIDE CONTEXT MANAGER
    except Exception as db_error:
        logger.error(f"Database error: {db_error}")
```

### Technical Details
1. **Context Manager Contract:** `get_background_session()` automatically commits on successful exit
2. **Double-Commit Scenario:** Manual `await session.commit()` + automatic commit on context exit
3. **Database State:** Connection left in "idle in transaction" state indefinitely
4. **Lock Propagation:** RowShareLock held on domains table, blocking all UPDATE operations
5. **Supavisor Impact:** Connection pooler kept problematic connections alive

### Cascade Effects
- **Database:** Multiple "idle in transaction" connections accumulating over time
- **Connection Pool:** Exhaustion of available database connections
- **User Interface:** Silent failures with infinite loading states
- **Business Process:** Complete stoppage of domain curation workflow
- **Downstream Impact:** WF5 sitemap analysis queue starvation

---

## Detection Signals

### Technical Indicators
```sql
-- Primary Detection Query
SELECT 
    pid, usename, application_name, state,
    now() - query_start as duration,
    LEFT(query, 200) as query_preview
FROM pg_stat_activity 
WHERE state = 'idle in transaction'
    AND datname = current_database()
    AND now() - query_start > interval '2 minutes';
```

**Critical Indicators:**
- Multiple connections in "idle in transaction" state for >2 minutes
- Queries involving `jobs.domain_id` or scheduler-related operations
- RowShareLock locks accumulating on critical tables (domains, jobs)
- Background processes showing as "Supavisor" application name

### Behavioral Patterns
- **UI Symptoms:** Submit buttons hang without error messages
- **API Symptoms:** UPDATE endpoints timeout after 2+ minutes
- **Log Patterns:** No error logs from failing operations (silent failures)
- **Performance:** SELECT queries work normally, UPDATE queries fail

### Workflow Impact Signals
- **WF4:** Domain curation status updates fail silently
- **WF5:** No new domains entering sitemap analysis queue
- **User Reports:** "Button doesn't work" with no technical error details
- **Monitoring:** Database connection pool utilization approaching limits

---

## Prevention Measures

### Architectural Protection

#### 1. Context Manager Contract Enforcement
```python
# CORRECT PATTERN: Let context manager handle transactions
async def handle_job_error(job_id: int, error_message: str):
    try:
        async with get_background_session() as session:
            stmt = update(Job).where(Job.id == job_id).values(status="failed")
            await session.execute(stmt)
            # ✅ NO MANUAL COMMIT - context manager handles this
            logger.info(f"Marked Job {job_id} as failed: {error_message}")
    except Exception as db_error:
        logger.error(f"Database error: {db_error}")
        # Context manager handles rollback automatically
```

#### 2. Session Pattern Documentation
**Rule:** Never mix manual transaction management with context managers

```python
# CORRECT: Context manager pattern
async with get_background_session() as session:
    # Do database work
    # Automatic commit/rollback on exit

# CORRECT: Manual transaction pattern  
session = async_session_factory()
try:
    # Do database work
    await session.commit()
except Exception:
    await session.rollback()
finally:
    await session.close()

# ❌ NEVER: Mixed patterns
async with get_background_session() as session:
    # Do work
    await session.commit()  # DON'T DO THIS
```

#### 3. Code Review Checklist
- [ ] No manual `commit()` calls inside context managers
- [ ] No manual `rollback()` calls inside context managers  
- [ ] Background jobs use `get_background_session()`
- [ ] Router endpoints use appropriate session dependency injection
- [ ] Transaction boundaries clearly defined and documented

### Collaboration Standards

#### 1. AI Assistant Rules
- **MUST** check for existing context managers before adding transaction management
- **MUST** understand session lifecycle patterns before modifying database code
- **MUST** verify transaction boundaries match architectural patterns
- **NEVER** assume manual transaction management is needed

#### 2. Development Standards
- All background schedulers MUST use `get_background_session()`
- All router endpoints MUST use dependency injection for sessions
- Service layer MUST NOT manage transaction boundaries
- Context managers MUST handle their own transaction lifecycle

### Monitoring and Alerting Systems

#### 1. Database Health Monitoring
```sql
-- Monitor for problematic connections (run every 5 minutes)
SELECT count(*) as idle_transaction_count
FROM pg_stat_activity 
WHERE state = 'idle in transaction'
    AND now() - query_start > interval '2 minutes';
```

**Alert Threshold:** Any connections idle in transaction >2 minutes

#### 2. Connection Pool Monitoring
- Track active vs idle connection ratios
- Alert on connection pool utilization >80%
- Monitor for scheduler-related connection patterns

#### 3. Performance Monitoring
- Monitor UPDATE query duration trends
- Alert on queries taking >30 seconds
- Track failed transaction rates

---

## Recovery Procedures

### Immediate Response

#### 1. Identify Blocking Connections
```sql
SELECT 
    pid, usename, application_name, state,
    now() - query_start as duration
FROM pg_stat_activity 
WHERE state = 'idle in transaction'
    AND datname = current_database()
ORDER BY query_start;
```

#### 2. Terminate Blocking Connections
```sql
-- Kill connections idle in transaction >5 minutes
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle in transaction'
    AND now() - query_start > interval '5 minutes'
    AND datname = current_database();
```

#### 3. Verify Resolution
```sql
-- Confirm no idle in transaction connections remain
SELECT count(*) FROM pg_stat_activity 
WHERE state = 'idle in transaction' AND datname = current_database();

-- Test UPDATE operations work
UPDATE domains SET updated_at = NOW() WHERE id = 'test-domain-id';
```

### System Hardening

#### 1. Fix Root Cause
- Remove manual `commit()` calls from context manager blocks
- Restart application to ensure clean scheduler state
- Verify background jobs follow correct session patterns

#### 2. Implement Monitoring
- Add "idle in transaction" connection monitoring
- Set up automated cleanup for connections idle >5 minutes
- Implement connection pool health checks

#### 3. Test Recovery
- Verify domain curation UI works properly
- Test WF4→WF5 handoff functionality
- Confirm background schedulers operate without leaking connections

---

## Cross-References

### Related Anti-Patterns
- **AP-20250730-002:** Database Connection Long Hold - Different but related session management issue
- **Future:** Background Job Session Management patterns (prevent similar issues in other schedulers)

### Reference Documents
- **Session Management:** `src/session/async_session.py` - Official session patterns
- **Background Jobs:** `src/services/*_scheduler.py` - Scheduler implementation patterns
- **Database Config:** `CLAUDE.md` - Supavisor connection requirements

### System-Wide Implications
- **All Schedulers:** Must follow get_background_session() pattern
- **All Services:** Must not manage transactions inside context managers
- **Database Health:** Requires monitoring for idle in transaction connections
- **Connection Pooling:** Supavisor configuration critical for preventing connection leaks

---

## Prevention Success Metrics

### Technical Metrics
- Zero "idle in transaction" connections >2 minutes
- All database UPDATE operations complete <5 seconds
- Background scheduler sessions properly cleaned up
- Connection pool utilization <70% sustained

### Business Metrics  
- WF4 domain curation UI: 100% submit success rate
- WF4→WF5 handoff: No queue starvation incidents
- User complaints: Zero "button doesn't work" reports
- System availability: No database-related downtime

### Monitoring Metrics
- Database connection health checks: All green
- Transaction duration monitoring: <30 second average
- Scheduler job completion rates: >95% success
- Error log patterns: No silent failure patterns

---

## Lessons Learned

### For AI Assistants
1. **Always check existing session management patterns** before adding database code
2. **Understand context manager contracts** - they handle transaction lifecycle automatically
3. **Never assume manual transaction management is needed** without analyzing existing patterns
4. **Database connectivity issues require systematic investigation** - start with connection analysis, not code changes

### For System Architecture
1. **Context managers must be used consistently** across all background jobs
2. **Transaction boundaries must be clearly documented** and enforced
3. **Database connection patterns are CRITICAL** - improper usage blocks entire workflows
4. **Silent failures are more dangerous** than loud failures - implement proper error handling

### For Collaboration
1. **Database issues require methodical investigation** - don't jump to complex solutions
2. **Root cause analysis is essential** - symptoms (UI hangs) may have deep architectural causes
3. **Prevention through documentation** is more valuable than reactive fixes
4. **Anti-pattern libraries save significant debugging time** for future similar issues

---

**Status:** RESOLVED - Manual commit removed from context manager block  
**Resolution Date:** 2025-07-31  
**Prevention Status:** Monitoring and documentation implemented  
**Business Impact:** WF4 pipeline fully operational, zero recurrence incidents  

---

*This anti-pattern documentation serves as institutional memory to prevent recurrence of this critical workflow-breaking issue across all ScraperSky background processing systems.*
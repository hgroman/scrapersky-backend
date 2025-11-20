# Testing Checklists

**Purpose:** Ensure complete test coverage before declaring work done

---

## SQLAlchemy Model Changes

### ENUM Column Testing
Use when adding/modifying ENUM columns.

- [ ] **CREATE**: Insert record with each enum value
- [ ] **READ**: Retrieve record by ID
- [ ] **FILTER**: Query with `WHERE enum_column = value` ⚠️ CRITICAL
- [ ] **UPDATE**: Change enum value
- [ ] **LIST**: Verify enum serialization in responses
- [ ] **COMPARISON**: Test enum equality in queries
- [ ] **DEFAULT**: Verify default value works

**Why FILTER is critical:** Schedulers use WHERE clauses. Missing `native_enum=True` breaks filtering but not INSERT/SELECT.

**Reference:** KNOWN_FAILURES.md - 2025-11-20 Incomplete ENUM Migration

---

### Foreign Key Testing

- [ ] **VALID FK**: Insert with valid foreign key
- [ ] **INVALID FK**: Attempt insert with invalid FK (should fail)
- [ ] **NULL FK**: Test nullable FK behavior
- [ ] **CASCADE**: Verify cascade delete if configured
- [ ] **QUERY**: Join across FK relationship

---

### Constraint Testing

- [ ] **NOT NULL**: Attempt insert with NULL (should fail)
- [ ] **UNIQUE**: Attempt duplicate insert (should fail)
- [ ] **CHECK**: Test constraint boundaries
- [ ] **DEFAULT**: Verify default values

---

## Database Migration Testing

### Pre-Migration

- [ ] **BACKUP**: Verify backup exists
- [ ] **DATA AUDIT**: Check for NULL values if adding NOT NULL
- [ ] **ENUM VALUES**: Verify all enum values exist in data
- [ ] **FK TARGETS**: Verify all FK targets exist

### Post-Migration

- [ ] **SCHEMA**: Verify schema matches expected
- [ ] **DATA INTEGRITY**: All records migrated
- [ ] **CONSTRAINTS**: All constraints active
- [ ] **INDEXES**: Indexes created

### Application Testing

- [ ] **STARTUP**: Application starts without ORM errors
- [ ] **QUERIES**: Test actual query patterns (not just CRUD)
- [ ] **SCHEDULERS**: Let schedulers run and process work
- [ ] **ROUTERS**: Test endpoints with filters

---

## Scheduler Testing

### Query Pattern Testing

- [ ] **EMPTY QUEUE**: Scheduler handles no work
- [ ] **SINGLE ITEM**: Process one item
- [ ] **BATCH**: Process multiple items
- [ ] **FILTER**: WHERE clause works correctly ⚠️ CRITICAL
- [ ] **STATUS UPDATE**: Status transitions work
- [ ] **ERROR HANDLING**: Failed items handled correctly

**Why FILTER is critical:** Schedulers query by status. Broken WHERE clauses cause silent failures.

---

## Router Testing

### Endpoint Testing

- [ ] **SUCCESS**: 200 response with valid data
- [ ] **FILTER**: Query params work (status, pagination)
- [ ] **NOT FOUND**: 404 for missing resources
- [ ] **VALIDATION**: 422 for invalid input
- [ ] **AUTH**: 401 for missing/invalid auth

### Status Filtering

- [ ] **SINGLE STATUS**: Filter by one status value
- [ ] **MULTIPLE STATUS**: Filter by multiple values
- [ ] **INVALID STATUS**: Handle invalid status gracefully
- [ ] **ENUM SERIALIZATION**: Status values serialize correctly

---

## Integration Testing

### End-to-End Workflow

- [ ] **TRIGGER**: Workflow starts correctly
- [ ] **TRANSITIONS**: All status transitions work
- [ ] **COMPLETION**: Workflow completes successfully
- [ ] **ERROR PATH**: Errors handled gracefully
- [ ] **MONITORING**: Logs show expected behavior

---

## Deployment Checklist

### Pre-Deployment

- [ ] **ALL TESTS PASS**: Automated tests pass
- [ ] **MANUAL TESTING**: Checklists completed
- [ ] **LOGS CLEAN**: No errors in dev environment
- [ ] **ROLLBACK PLAN**: Documented and tested

### Post-Deployment

- [ ] **HEALTH CHECK**: Application responds
- [ ] **SCHEDULERS**: All schedulers running
- [ ] **LOGS**: Monitor for 30 minutes
- [ ] **METRICS**: Check error rates

---

## When to Use This

**Before committing:**
- Review relevant checklist
- Verify all items checked

**Before declaring "PRODUCTION READY":**
- Complete ALL relevant checklists
- Document any skipped items with justification

**After production incident:**
- Add new checklist items based on what was missed

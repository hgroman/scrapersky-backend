# Known Failure Modes

**Purpose:** Learn from production incidents - know what breaks and how to test for it

**Last Updated:** 2025-11-20

---

## SQLAlchemy ENUM Columns

### Missing native_enum=True (2025-11-20)

**Incident:** [INCIDENTS/2025-11-20-incomplete-enum-migration.md](../INCIDENTS/2025-11-20-incomplete-enum-migration.md)  
**Commits:** 688b946 (broken), 5db86af (fixed)

#### Symptom
```
operator does not exist: domain_extraction_status = domain_extraction_status_enum
HINT: No operator matches the given name and argument types. You might need to add explicit type casts.
```

#### What Works
- ✅ INSERT (creating records)
- ✅ SELECT by ID (retrieving by primary key)
- ✅ Application startup

#### What Breaks
- ❌ WHERE clauses with enum comparison
- ❌ Filtering by enum values
- ❌ Scheduler queries (`WHERE status = 'Queued'`)

#### Why It's Hidden
Tests that only INSERT and SELECT by ID will pass. The failure only appears when:
- Schedulers run and query by status
- Routers filter by enum values
- Any WHERE clause compares enum columns

#### The Fix
```python
# ❌ BROKEN
domain_extraction_status = Column(
    Enum(
        DomainExtractionStatusEnum,
        name="domain_extraction_status_enum",
        create_type=False,
    ),
    ...
)

# ✅ FIXED
domain_extraction_status = Column(
    Enum(
        DomainExtractionStatusEnum,
        name="domain_extraction_status_enum",
        create_type=False,
        native_enum=True,  # CRITICAL
        values_callable=lambda x: [e.value for e in x],  # CRITICAL
    ),
    ...
)
```

#### Test Pattern
```python
def test_enum_column_with_filtering():
    """Test ENUM column supports WHERE clauses (what schedulers do)"""
    # Create record
    obj = LocalBusiness(
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(obj)
    session.commit()
    
    # CRITICAL: Test filtering (this is what breaks)
    queued = session.query(LocalBusiness).filter(
        LocalBusiness.domain_extraction_status == DomainExtractionStatusEnum.Queued
    ).all()
    
    assert len(queued) > 0, "Filter by enum failed - missing native_enum=True?"
```

#### Prevention
- Always copy the complete pattern from working columns
- Test filtering, not just INSERT/SELECT
- Let schedulers run with actual work in dev environment

---

## Foreign Key Constraint Violations

### Missing Tenant ID Validation

**Pattern:** Adding FK constraints to existing tables with data

#### What Breaks
- Migration fails if any NULL values exist
- Migration fails if any invalid FK references exist

#### Test Pattern
```python
def test_fk_constraint_enforcement():
    """Test FK constraint blocks invalid references"""
    with pytest.raises(IntegrityError):
        obj = Place(
            tenant_id=uuid.uuid4(),  # Invalid - doesn't exist
            ...
        )
        session.add(obj)
        session.commit()
```

#### Prevention
- Pre-migration audit: `SELECT COUNT(*) WHERE tenant_id IS NULL`
- Pre-migration audit: `SELECT COUNT(*) WHERE tenant_id NOT IN (SELECT id FROM tenants)`
- Test invalid FK insertion fails

---

## Scheduler Silent Failures

### No Work to Process

**Pattern:** Scheduler runs but has no work, so broken queries never execute

#### What's Hidden
- Broken WHERE clauses
- Invalid enum comparisons
- Missing indexes

#### What Appears to Work
- Scheduler starts
- Scheduler logs "0 items found"
- No errors in logs

#### Test Pattern
```python
def test_scheduler_with_actual_work():
    """Test scheduler with queued items, not empty queue"""
    # Create work for scheduler
    business = LocalBusiness(
        domain_extraction_status=DomainExtractionStatusEnum.Queued
    )
    session.add(business)
    session.commit()
    
    # Run scheduler
    await process_domain_extraction_queue()
    
    # Verify work was processed
    session.refresh(business)
    assert business.domain_extraction_status != DomainExtractionStatusEnum.Queued
```

#### Prevention
- Always test schedulers with queued work
- Don't trust "0 items found" as success
- Monitor scheduler success rates, not just execution

---

## Template for New Failures

```markdown
### [Failure Name] (YYYY-MM-DD)

**Incident:** [Link to incident doc]
**Commits:** [broken commit], [fixed commit]

#### Symptom
[Error message or behavior]

#### What Works
- ✅ [What appears to work]

#### What Breaks
- ❌ [What actually breaks]

#### Why It's Hidden
[Why tests might pass but production fails]

#### The Fix
[Code showing broken vs fixed]

#### Test Pattern
[Copy-paste test code]

#### Prevention
[How to avoid this in future]
```

---

## How to Use This

**When testing risky changes:**
1. Search this file for similar patterns
2. Copy the test pattern
3. Verify your code doesn't have the same issue

**After production incident:**
1. Add entry to this file
2. Include test pattern
3. Update CHECKLISTS.md if new category

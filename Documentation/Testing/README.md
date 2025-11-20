# Testing Framework

**Purpose:** Prevent production defects through systematic testing patterns

**Last Updated:** 2025-11-20

---

## Philosophy

Documentation doesn't prevent bugs. **Checklists, patterns, and known failures do.**

This framework provides:
1. **Checklists** - Force consideration of edge cases
2. **Patterns** - Copy-paste complete test implementations
3. **Known Failures** - Learn from production incidents
4. **Examples** - Working test code

---

## Quick Start

### Before Writing Tests

1. Check **[CHECKLISTS.md](./CHECKLISTS.md)** - What to test
2. Check **[KNOWN_FAILURES.md](./KNOWN_FAILURES.md)** - What breaks
3. Copy pattern from **[PATTERNS.md](./PATTERNS.md)** or **[Examples/](./Examples/)**

### After Production Incident

1. Document failure in **[KNOWN_FAILURES.md](./KNOWN_FAILURES.md)**
2. Add test pattern to **[PATTERNS.md](./PATTERNS.md)**
3. Create example in **[Examples/](./Examples/)**

---

## Files

| File | Purpose | When to Use |
|------|---------|-------------|
| [CHECKLISTS.md](./CHECKLISTS.md) | Checkbox lists for test coverage | Before declaring tests complete |
| [PATTERNS.md](./PATTERNS.md) | Copy-paste test implementations | When writing new tests |
| [KNOWN_FAILURES.md](./KNOWN_FAILURES.md) | Production bugs → test patterns | When testing risky areas |
| [Examples/](./Examples/) | Working test code | When learning patterns |

---

## Testing Types

### Model Testing
- ENUM columns (see: KNOWN_FAILURES.md - 2025-11-20)
- Foreign key constraints
- Nullable constraints
- Unique constraints

### Scheduler Testing
- Query patterns (WHERE clauses)
- Status transitions
- Batch processing
- Error handling

### Router Testing
- Endpoint responses
- Status filtering
- Pagination
- Error cases

---

## Integration with Incidents

Every production incident should generate:
1. Entry in `KNOWN_FAILURES.md`
2. Test pattern in `PATTERNS.md`
3. Example test in `Examples/`
4. Checklist item if new category

**See:** [Documentation/INCIDENTS/](../INCIDENTS/) for production incidents

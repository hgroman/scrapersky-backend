# ORM-ONLY PRINCIPLE: ABSOLUTE PROHIBITION OF RAW SQL

## FUNDAMENTAL RULE

⚠️ **THE SINGLE MOST IMPORTANT RULE IN OUR CODEBASE** ⚠️

**NEVER USE RAW SQL IN APPLICATION CODE**

This rule is NON-NEGOTIABLE and has NO EXCEPTIONS.

## What This Means

### ✅ ALWAYS DO THIS:

- Use SQLAlchemy ORM methods for ALL database operations
- Access data through model classes (Domain, User, etc.)
- Let the ORM handle SQL generation
- Use model methods like `update_from_metadata()`

### ❌ NEVER DO THIS:

- Write SQL strings with `text()` in application code
- Use `session.execute()` with raw SQL
- Manually construct INSERT, UPDATE, or SELECT statements
- Bypass ORM models for database operations

## Quick Reference

```
⚠️ CRITICAL ARCHITECTURAL PRINCIPLE ⚠️
┌─────────────────────────────────────────────────────┐
│ NEVER USE RAW SQL IN APPLICATION CODE               │
│                                                     │
│ ✅ ALWAYS use ORM methods                           │
│ ❌ NEVER write raw SQL queries                      │
│                                                     │
│ The only place 'raw_sql=true' should appear is in   │
│ connection configuration settings, NEVER in actual  │
│ application logic.                                  │
└─────────────────────────────────────────────────────┘
```

## Visual Guide

```
CONNECTION CONFIGURATION vs APPLICATION CODE
┌───────────────────────────────────────┐    ┌───────────────────────────────────────┐
│ CONNECTION CONFIGURATION               │    │ APPLICATION CODE                      │
├───────────────────────────────────────┤    ├───────────────────────────────────────┤
│                                       │    │                                       │
│ engine = create_async_engine(        │    │ # CORRECT ✅                          │
│   connection_string,                 │    │ domain = await Domain.get_by_id(      │
│   execution_options={                │    │   session, domain_id)                 │
│     "raw_sql": True,  # CORRECT HERE │    │ domain.update_from_metadata(metadata) │
│     "no_prepare": True               │    │                                       │
│   }                                  │    │ # WRONG ❌                            │
│ )                                    │    │ query = text("""                      │
│                                       │    │   UPDATE domains SET...               │
│                                       │    │   WHERE id = :id                      │
│                                       │    │ """)                                  │
└───────────────────────────────────────┘    └───────────────────────────────────────┘
```

## The Only Exception

The **ONLY** place where `raw_sql=true` should appear is in connection configuration settings:

```python
# THIS IS THE ONLY PLACE WHERE "raw_sql" SHOULD APPEAR
# This is for SUPAVISOR COMPATIBILITY ONLY
engine = create_async_engine(
    connection_string,
    execution_options={
        "raw_sql": True,  # ONLY HERE!
        "no_prepare": True
    },
)
```

## Why This Rule Exists

1. **Type Safety**: ORM provides field validation and type checking
2. **Consistency**: Ensures field names match across the application
3. **Maintainability**: Changes to database schema are reflected in code
4. **Prevention of Errors**: Avoids field mismatch errors that cost days to debug

## Real-World Cost of Violations

Recent violations of this principle in the Domain Scheduler resulted in:

- 8+ wasted hours of debugging time
- Multiple failed deployment attempts
- Complex and unnecessary work orders
- Frustration and decreased productivity

## If You See Raw SQL in Application Code

If you encounter raw SQL in application code:

1. **STOP** - Do not proceed with the implementation
2. **REWRITE** - Convert to ORM methods immediately
3. **REPORT** - Document the change in your PR

## Code Smells - Watch For These Warning Signs

If you see any of these patterns, it's likely raw SQL is being used improperly:

- Imports of `sqlalchemy.sql.text` or `text` from SQLAlchemy
- Strings containing SQL keywords (SELECT, UPDATE, INSERT, DELETE)
- Triple-quoted strings (`"""`) followed by SQL-like syntax
- Use of `session.execute()` with string parameters
- Manual string formatting or concatenation of SQL queries

## FAQ

### "But what if I need a complex query that's hard to express with ORM?"

Answer: SQLAlchemy ORM offers advanced querying capabilities including joins, subqueries, and CTE expressions. Consult with the team before assuming ORM can't handle your case.

### "What about performance? Isn't raw SQL faster?"

Answer: Modern ORMs have minimal overhead. Any performance gain from raw SQL is vastly outweighed by the maintenance and reliability costs.

### "How do I convert existing raw SQL to ORM?"

Answer: Use the `Domain.update_from_metadata()` method as a reference implementation. The Google Maps API module also demonstrates proper ORM patterns.

## Transition Checklist

When converting from raw SQL to ORM:

- [ ] Identify all fields being accessed in the raw query
- [ ] Verify those field names in the SQLAlchemy model
- [ ] Replace `text()` queries with ORM method calls
- [ ] Test thoroughly, especially edge cases
- [ ] Document the conversion in your PR

## Remember

```
"The only SQL you should ever write is SELECT * FROM good_practices;"
```

## External References

### Supabase Documentation on SQLAlchemy

While the [Supabase documentation](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT) mentions `raw_sql=true` as a connection parameter, this is **ONLY** for the connection configuration with Supavisor, **NOT** for application code.

The document states:

> When using transaction mode, you should use the NullPool setting and the required connection parameters.

These connection parameters (`raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`) are exclusively for the database connection configuration, not permission to write raw SQL in application code.

**REMEMBER**: Connection configuration settings are completely separate from application code patterns. The presence of `raw_sql=true` in our connection settings is NOT permission to use raw SQL in business logic.

## Direct Link to Supabase Documentation

[Using SQLAlchemy with Supabase](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)

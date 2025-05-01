# DATABASE SCHEMA CHANGE GUIDE

This document provides guidance on the correct approach to database schema changes in the ScraperSky project. It outlines the tools, patterns, and verification steps to ensure schema changes are safe, consistent, and aligned with the project's architectural principles.

## 1. CRITICAL PRINCIPLES FOR SCHEMA CHANGES

### Standard Approach

All database schema changes MUST:

- Be performed through **dedicated scripts** (not ad-hoc)
- Include appropriate **error handling**
- Provide **verification steps** to confirm changes
- Follow the **database connection standards** in [07-DATABASE_CONNECTION_STANDARDS.md](./07-DATABASE_CONNECTION_STANDARDS.md)
- Have **corresponding model updates** in the associated SQLAlchemy models

### INCORRECT (DANGEROUS) Approaches

The following patterns are **STRICTLY FORBIDDEN** and may cause data corruption or loss:

```python
# ❌ INCORRECT: Direct schema changes in application code
async def start_service():
    async with engine.begin() as conn:
        await conn.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
```

```python
# ❌ INCORRECT: Schema changes without proper error handling
async def add_column():
    async with engine.connect() as conn:
        await conn.execute("ALTER TABLE jobs ADD COLUMN priority INTEGER")
        # Missing error handling and verification
```

### CORRECT Approach

```python
# ✅ CORRECT: Schema change through a dedicated script
async def add_status_column_to_table():
    """Add status column to a specific table."""
    try:
        # First check if the column already exists
        column_exists = await check_column_exists('table_name', 'status')

        if column_exists:
            logger.info("Status column already exists")
            return True

        # Add the column with proper error handling
        async with engine.begin() as conn:
            await conn.execute(text(
                """
                ALTER TABLE table_name
                ADD COLUMN status VARCHAR(50) DEFAULT 'pending'
                """
            ))
            logger.info("Added status column successfully")

        # Verify the column was added
        verify_success = await check_column_exists('table_name', 'status')
        if not verify_success:
            logger.error("Failed to verify column addition")
            return False

        return True

    except Exception as e:
        logger.error(f"Error adding column: {str(e)}")
        return False
```

## 2. AVAILABLE TOOLS

ScraperSky provides several tools to support database schema changes:

### 1. Schema Inspection

`scripts/db/inspect_table.py`: Examine table structure, constraints, and data.

```bash
# List all tables with row counts
python scripts/db/inspect_table.py

# View schema details for a specific table
python scripts/db/inspect_table.py places_searches

# View data in a table with filter
python scripts/db/inspect_table.py places_searches --limit 10 --where "created_at > '2025-01-01'"
```

### 2. Schema Fix Script Template

Use the pattern from `scripts/fixes/fix_place_searches_schema.py` to create dedicated schema change scripts.

### 3. Connection Testing

`scripts/db/test_connection.py`: Verify database connectivity with the current configuration.

```bash
# Test database connection
python scripts/db/test_connection.py
```

### 4. SQLAlchemy ORM Access

The database engine and session factories provide structured access for schema operations:

```python
from src.db.engine import engine
from sqlalchemy import text

async def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                )
                """
            ))
            exists = result.scalar()
            return bool(exists)
    except Exception as e:
        logger.error(f"Error checking if column exists: {str(e)}")
        return False
```

## 3. SCHEMA CHANGE PATTERNS

### Creating a New Table

```python
async def create_new_table():
    """Create a new table if it doesn't exist."""
    try:
        # Check if table exists
        table_exists = await check_table_exists('new_table')
        if table_exists:
            logger.info("Table already exists")
            return True

        # Create the table
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE new_table (
                    id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
                )
            """))
            logger.info("Table created successfully")

        # Verify creation
        verify_success = await check_table_exists('new_table')
        if not verify_success:
            logger.error("Failed to verify table creation")
            return False

        return True

    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        return False
```

### Adding a Column

```python
async def add_column():
    """Add a column to an existing table."""
    try:
        # Check if column exists
        column_exists = await check_column_exists('table_name', 'new_column')
        if column_exists:
            logger.info("Column already exists")
            return True

        # Add the column
        async with engine.begin() as conn:
            await conn.execute(text("""
                ALTER TABLE table_name
                ADD COLUMN new_column VARCHAR(100) DEFAULT 'default_value'
            """))
            logger.info("Column added successfully")

        # Verify addition
        verify_success = await check_column_exists('table_name', 'new_column')
        if not verify_success:
            logger.error("Failed to verify column addition")
            return False

        return True

    except Exception as e:
        logger.error(f"Error adding column: {str(e)}")
        return False
```

### Changing a Column Type

```python
async def change_column_type():
    """Change a column's data type."""
    try:
        # Check if column has the correct type
        # (implementation depends on specific needs)

        # Change the column type
        async with engine.begin() as conn:
            await conn.execute(text("""
                ALTER TABLE table_name
                ALTER COLUMN column_name TYPE new_type USING column_name::new_type
            """))
            logger.info("Column type changed successfully")

        # Verify change
        # (implementation depends on specific needs)

        return True

    except Exception as e:
        logger.error(f"Error changing column type: {str(e)}")
        return False
```

### Adding an Index

```python
async def add_index():
    """Add an index to a table."""
    try:
        # Check if index exists
        index_exists = await check_index_exists('table_name', 'index_name')
        if index_exists:
            logger.info("Index already exists")
            return True

        # Add the index
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE INDEX index_name ON table_name (column_name)
            """))
            logger.info("Index added successfully")

        # Verify addition
        verify_success = await check_index_exists('table_name', 'index_name')
        if not verify_success:
            logger.error("Failed to verify index addition")
            return False

        return True

    except Exception as e:
        logger.error(f"Error adding index: {str(e)}")
        return False
```

## 4. MODEL UPDATES

After schema changes, the corresponding SQLAlchemy models must be updated:

```python
# Before schema change
class Entity(Base):
    __tablename__ = "entities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)

# After schema change - added status column
class Entity(Base):
    __tablename__ = "entities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # Added column
```

## 5. VERIFICATION STEPS

All schema changes should include verification:

1. **Check schema changes were applied**:

```python
async def verify_column_addition(table_name: str, column_name: str) -> bool:
    """Verify that a column was added to a table."""
    return await check_column_exists(table_name, column_name)
```

2. **Verify data integrity**:

```python
async def verify_data_integrity(table_name: str, column_name: str) -> bool:
    """Verify that a column contains expected values."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE {column_name} IS NULL
                AND NOT (column_can_be_null)
                """
            ))
            invalid_count = result.scalar()
            return invalid_count == 0
    except Exception as e:
        logger.error(f"Error verifying data integrity: {str(e)}")
        return False
```

3. **Test API functionality** that depends on the schema:

```bash
# Run API tests after schema changes
python scripts/testing/test_api_after_schema_change.py
```

## 6. REAL-WORLD EXAMPLE

The Google Maps API implementation included a schema change to add status tracking columns:

```python
async def add_columns_to_place_searches():
    """Add the missing columns to the place_searches table."""

    # First check if the table exists
    if not await check_table_exists('place_searches'):
        logger.error("The place_searches table does not exist! Please create it first.")
        return False

    # Check if status column already exists
    status_exists = await check_column_exists('place_searches', 'status')
    updated_at_exists = await check_column_exists('place_searches', 'updated_at')

    if status_exists and updated_at_exists:
        logger.info("Both columns already exist. No changes needed.")
        return True

    # Add the missing columns
    try:
        async with engine.begin() as conn:
            if not status_exists:
                logger.info("Adding 'status' column to place_searches table...")
                await conn.execute(text(
                    """
                    ALTER TABLE place_searches
                    ADD COLUMN status VARCHAR(50) DEFAULT 'pending'
                    """
                ))
                logger.info("Added 'status' column successfully.")

            if not updated_at_exists:
                logger.info("Adding 'updated_at' column to place_searches table...")
                await conn.execute(text(
                    """
                    ALTER TABLE place_searches
                    ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
                    """
                ))
                logger.info("Added 'updated_at' column successfully.")

            logger.info("All schema changes committed successfully.")
            return True
    except Exception as e:
        logger.error(f"Error adding columns: {str(e)}")
        return False
```

## 7. INTEGRATION WITH EXISTING CODE

After schema changes, related code must be updated:

1. **Update service implementation** to use new columns:

```python
async def update_status(session: AsyncSession, job_id: str, status: str) -> bool:
    """Update job status in database."""
    stmt = update(Job).where(
        Job.id == job_id
    ).values(
        status=status,
        updated_at=datetime.utcnow()  # Use new column
    )
    await session.execute(stmt)
    return True
```

2. **Update router endpoints** to return new fields:

```python
@router.get("/status/{job_id}")
async def get_status(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> Dict:
    async with session.begin():
        job = await job_service.get_by_id(session, job_id)

    return {
        "status": job.status,  # Return new field
        "updated_at": job.updated_at  # Return new field
    }
```

## 8. CONCLUSION

Following these schema change patterns ensures:

- **Consistency**: All schema changes follow the same pattern
- **Safety**: Changes are verified before and after execution
- **Rollback**: In case of errors, changes can be safely rolled back
- **Documentation**: All changes are documented in code
- **Maintainability**: Future developers can understand the changes

Always create dedicated scripts for schema changes, verify the changes were applied correctly, and update the corresponding SQLAlchemy models.

## Reference Materials

- [07-DATABASE_CONNECTION_STANDARDS.md](./07-DATABASE_CONNECTION_STANDARDS.md) - For database connection patterns
- [13-TRANSACTION_MANAGEMENT_GUIDE.md](./13-TRANSACTION_MANAGEMENT_GUIDE.md) - For transaction management principles
- [16-UUID_STANDARDIZATION_GUIDE.md](./16-UUID_STANDARDIZATION_GUIDE.md) - For UUID field standardization
- [07-26-GOOGLE-MAPS-API-FIX-IMPLEMENTATION-2025-03-26.md](/project-docs/07-database-connection-audit/07-26-GOOGLE-MAPS-API-FIX-IMPLEMENTATION-2025-03-26.md) - Real-world implementation example

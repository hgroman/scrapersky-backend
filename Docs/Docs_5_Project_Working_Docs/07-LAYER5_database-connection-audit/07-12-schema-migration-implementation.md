# 07-12 Schema Migration Implementation

## Overview

This document provides the exact steps needed to implement the schema migrations required to fix the sitemap service. The goal is to resolve the issues identified during testing with minimal changes to ensure functionality.

## Schema Issues to Fix

1. **Missing `url_count` column in `sitemap_files` table**
2. **Type mismatch between job_id (string) and database (UUID)**

## Implementation Plan

### Step 1: Create Alembic Migration Script

Run the following command to create a new migration:

```bash
# Navigate to project root
cd .

# Create migration script
alembic revision -m "add_url_count_to_sitemap_files"
```

### Step 2: Edit the Migration Script

Edit the newly created migration script in the `migrations/versions/` directory:

```python
"""add_url_count_to_sitemap_files

Revision ID: {revision_id}
Revises: {previous_revision}
Create Date: {date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '{revision_id}'
down_revision: Union[str, None] = '{previous_revision}'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add url_count column to sitemap_files
    op.add_column('sitemap_files', sa.Column('url_count', sa.Integer(), nullable=True, server_default='0'))

    # Add a comment to the column
    op.execute("COMMENT ON COLUMN sitemap_files.url_count IS 'Number of URLs found in this sitemap file'")


def downgrade() -> None:
    # Remove url_count column if needed to rollback
    op.drop_column('sitemap_files', 'url_count')
```

### Step 3: Create a Second Migration for Job ID Type (Optional)

If you decide to change the job_id type (this is optional, as we can handle type conversion in the code instead):

```bash
alembic revision -m "fix_job_id_type_in_jobs_table"
```

Edit this migration script:

```python
"""fix_job_id_type_in_jobs_table

Revision ID: {revision_id}
Revises: {previous_revision}
Create Date: {date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '{revision_id}'
down_revision: Union[str, None] = '{previous_revision}'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The following operations use raw SQL to avoid SQLAlchemy
    # type compatibility issues during migration

    # First create a new column with the correct type
    op.execute('ALTER TABLE jobs ADD COLUMN job_id_str VARCHAR')

    # Copy data from UUID column to string column
    op.execute('UPDATE jobs SET job_id_str = job_id::text')

    # Drop the old column
    op.execute('ALTER TABLE jobs DROP COLUMN job_id')

    # Rename the new column to the original name
    op.execute('ALTER TABLE jobs RENAME COLUMN job_id_str TO job_id')


def downgrade() -> None:
    # Reverse the process if needed
    op.execute('ALTER TABLE jobs ADD COLUMN job_id_uuid UUID')
    op.execute('UPDATE jobs SET job_id_uuid = job_id::uuid WHERE job_id ~ \'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$\'')
    op.execute('ALTER TABLE jobs DROP COLUMN job_id')
    op.execute('ALTER TABLE jobs RENAME COLUMN job_id_uuid TO job_id')
```

### Step 4: Update SQLAlchemy Model (sitemap_files)

Update the SQLAlchemy model in `/src/models/sitemap.py` to include the new column:

```python
# Add this field to the SitemapFile model
url_count = Column(Integer, nullable=True, default=0, comment="Number of URLs found in this sitemap file")
```

### Step 5: Run Migrations

Run the migrations to apply the changes:

```bash
cd .
# alembic upgrade head
# Use Supabase CLI instead
supabase migration up --linked
```

### Step 6: Test the Changes

Run the debug script to verify the changes work:

```bash
# Run the debug script
python project-docs/07-database-connection-audit/scripts/debug_sitemap_flow.py
```

## Alternative Approach: Code Changes Only

Since we can't directly modify the database schema due to authentication issues or permission restrictions, we will implement the code-only solution:

### For `url_count` issue:

We've already made the necessary changes:

1. Removed the `url_count` field from the `SitemapFile` model and references in the `background_service.py`.
2. The code now avoids trying to store data in the non-existent column.

### For job_id type issue:

We've updated the `job_service.py` to properly handle string and UUID job_ids:

```python
# In job_service.py, we've updated get_by_id to handle string job_ids with proper conversion
if isinstance(job_id, str):
    # Try as a UUID string
    try:
        job_uuid = uuid.UUID(str(job_id))
        job_uuid_str = str(job_uuid)

        # Use string comparison instead of UUID comparison to avoid type issues
        query = select(Job).where(
            Job.job_id == job_uuid_str
        )

        logger.debug(f"Looking up job by string job_id: {job_uuid_str}")
    except ValueError:
        logger.warning(f"Invalid UUID format for job_id: {job_id}")
        return None
```

## Revised Testing Plan

1. Run the debug script without any database migrations and verify:

   - No errors related to missing url_count column
   - No errors related to job_id type mismatch
   - Job creation and updates work properly

2. Test the actual API endpoint:
   - Use Postman or curl to call the `/api/v3/sitemap/scan` endpoint
   - Verify the job is created and processed
   - Check the job status endpoint works

## Rollback Plan

If issues arise, you can:

1. Roll back the migrations:

```bash
alembic downgrade {revision_before_our_changes}
```

2. Revert any code changes made to models

## Success Criteria

The implementation is successful when:

1. The debug script runs without errors
2. The sitemap scanning functionality works end-to-end
3. No schema-related errors appear in logs

## Expected Outcome

After these changes, the sitemap service should function properly with:

- Proper database schema compatibility
- Full end-to-end processing capability
- No errors related to missing columns or type mismatches

Execute the migration script:

```bash
cd .
# alembic upgrade head
# Use Supabase CLI instead
supabase migration up --linked
```

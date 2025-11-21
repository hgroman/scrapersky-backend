# Work Order: WO-024 - Safe Enum Purge

**Status**: Ready for Execution
**Target**: Production Database
**Risk**: Low (Verified Unused Types)

## 1. Context & Objective
We have identified **21 orphaned PostgreSQL Enum types** that are not used by any column in the database. These are technical debt ("ghosts") from previous schema versions or failed migrations.

**The Objective**: Safely `DROP` these 21 specific types to clean the database schema.

**The Constraint**: We must **NOT** drop any type that is currently in use (specifically `sitemapimportprocessingstatus` and `SitemapAnalysisStatusEnum`), as doing so would delete the associated data columns.

## 2. Strict Guardrails (READ THIS FIRST)
1.  **DO NOT** run a blanket "cleanup script". Run **ONLY** the specific SQL provided below.
2.  **DO NOT** drop `sitemapimportprocessingstatus`. It is ACTIVE.
3.  **DO NOT** drop `SitemapAnalysisStatusEnum`. It is ACTIVE.
4.  **DO NOT** drop `place_status_enum`. It is ACTIVE.
5.  **Stop immediately** if you encounter an error saying "cannot drop type ... because other objects depend on it". **Do not use CASCADE.**

## 3. Execution Instructions

### Step 1: Verification (Pre-Flight)
Run this query to confirm these types exist and have 0 column references:

```sql
WITH enum_types AS (
    SELECT t.oid, t.typname
    FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    GROUP BY t.oid, t.typname
),
column_usage AS (
    SELECT t.typname, c.table_name, c.column_name
    FROM information_schema.columns c
    JOIN enum_types t ON c.udt_name = t.typname
)
SELECT 
    et.typname,
    COUNT(cu.column_name) as usage_count
FROM enum_types et
LEFT JOIN column_usage cu ON et.typname = cu.typname
WHERE et.typname IN (
    'action', 'app_role', 'batch_job_status', 'brevo_sync_status',
    'contactcurationstatus', 'contactemailtypeenum', 'contactprocessingstatus',
    'dart_status_enum', 'discovery_method', 'domain_status', 'equality_op',
    'feature_priority', 'feature_status', 'hubotsyncstatus',
    'hubsyncprocessingstatus', 'job_type', 'request_status', 'search_status',
    'sitemap_import_curation_status', 'sitemapimportcurationstatus',
    'sitemapimportcurationstatusenum'
)
GROUP BY et.typname;
```
**Success Criteria**: All returned rows must have `usage_count = 0`.

### Step 2: The Purge (Execution)
Execute the following SQL block. This uses `DROP TYPE` without `CASCADE` to ensure safety. If a type is used, it will fail safely.

```sql
BEGIN;

-- 1. Sitemap Ghosts
DROP TYPE IF EXISTS sitemap_import_curation_status;
DROP TYPE IF EXISTS sitemapimportcurationstatus;
DROP TYPE IF EXISTS sitemapimportcurationstatusenum;

-- 2. CRM / Contact Ghosts
DROP TYPE IF EXISTS contactcurationstatus;
DROP TYPE IF EXISTS contactprocessingstatus;
DROP TYPE IF EXISTS contactemailtypeenum;
DROP TYPE IF EXISTS brevo_sync_status;
DROP TYPE IF EXISTS hubotsyncstatus;
DROP TYPE IF EXISTS hubsyncprocessingstatus;

-- 3. Legacy / System Ghosts
DROP TYPE IF EXISTS domain_status;
DROP TYPE IF EXISTS batch_job_status;
DROP TYPE IF EXISTS job_type;
DROP TYPE IF EXISTS request_status;
DROP TYPE IF EXISTS search_status;
DROP TYPE IF EXISTS discovery_method;
DROP TYPE IF EXISTS feature_status;
DROP TYPE IF EXISTS feature_priority;
DROP TYPE IF EXISTS app_role;
DROP TYPE IF EXISTS action;
DROP TYPE IF EXISTS equality_op;
DROP TYPE IF EXISTS dart_status_enum;

COMMIT;
```

### Step 3: Confirmation
Run the verification query from Step 1 again.
**Success Criteria**: The query should return **0 rows** (types no longer exist).

## 4. Confirmation Request
Please confirm:
1.  You have read the Guardrails.
2.  You understand that `brevo_sync_status` is safe to drop because the column uses `crm_sync_status`.
3.  You are ready to execute.

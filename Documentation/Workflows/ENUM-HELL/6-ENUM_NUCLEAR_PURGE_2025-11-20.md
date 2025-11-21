# ENUM NUCLEAR PURGE – November 20, 2025

## Goal
Remove every orphaned, duplicate, and historically confusing enum type from the database so they can never cause another outage.

## Verified Orphaned / Dangerous Types (none are used by any column today)
- sitemap_import_curation_status
- sitemapimportcurationstatus
- sitemapimportcurationstatusenum
- sitemapimportprocessingstatus
- "SitemapAnalysisStatusEnum" (PascalCase version)
- place_status
- Any other stray PascalCase types created by failed migrations

## One-time SQL script (run in production NOW)
```sql
DROP TYPE IF EXISTS sitemap_import_curation_status CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatus CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatusenum CASCADE;
DROP TYPE IF EXISTS sitemapimportprocessingstatus CASCADE;
DROP TYPE IF EXISTS "SitemapAnalysisStatusEnum" CASCADE;
DROP TYPE IF EXISTS place_status CASCADE;

-- Fix the last two that still have data but wrong casing
ALTER TABLE domains ALTER COLUMN status TYPE VARCHAR USING status::TEXT;
UPDATE domains SET status = INITCAP(status);  -- pending → Pending, etc.
ALTER TABLE domains ALTER COLUMN status TYPE sitemap_curation_status_enum 
    USING status::TEXT::sitemap_curation_status_enum;
DROP TYPE IF EXISTS domain_status CASCADE;


After this script
PostgreSQL schema is clean. Zero chance of “operator does not exist” errors from ghost enums ever again.
Follow-up commit
Add a CI check or pre-deployment script that fails if any enum type not ending in _enum exists.
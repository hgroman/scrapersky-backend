# Domain Purge Procedure
**Purpose:** Complete removal of domain(s) and all related data from the system  
**Created:** November 21, 2025  
**Last Updated:** November 21, 2025

---

## ⚠️ WARNING

This procedure **permanently deletes** domains and all associated data:
- Pages (scraped content, contacts)
- Sitemap files and URLs
- Background jobs and tasks
- All processing history

**This operation cannot be undone.**

---

## When to Use This

Use this procedure when you need to completely remove domains from the system:
- Domains with aggressive WAF/bot protection
- Sites that are permanently down
- Domains added by mistake
- Testing cleanup
- Compliance/legal removal requests

---

## Prerequisites

1. **Access:** Supabase SQL editor or psql with admin privileges
2. **Verification:** Confirm domain names are correct (typos cannot be undone)
3. **Backup:** Consider taking a backup if you might need to restore

---

## Foreign Key Dependencies

The following tables reference `domains.id`:
- `contacts` - Extracted contact information
- `jobs` - Background processing jobs
- `pages` - Individual page records
- `sitemap_files` - Discovered sitemap files
- `sitemap_urls` - Individual URLs from sitemaps
- `tasks` - Scheduled/queued tasks

**Deletion Order:** Children first, then parent (domains table last)

---

## Procedure: Single Domain Purge

### Step 1: Verify Domain Exists

```sql
-- Check domain exists and note its ID
SELECT 
    id,
    domain,
    sitemap_curation_status,
    sitemap_analysis_status,
    created_at
FROM domains 
WHERE domain = 'example.com';
```

**Expected:** 1 row returned with domain details

---

### Step 2: Check Impact (Optional but Recommended)

```sql
-- Count all related records before deletion
WITH domain_ids AS (
    SELECT id FROM domains WHERE domain = 'example.com'
)
SELECT 
    'contacts' as table_name, COUNT(*) as row_count 
    FROM contacts WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'pages', COUNT(*) FROM pages WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'sitemap_files', COUNT(*) FROM sitemap_files WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'sitemap_urls', COUNT(*) FROM sitemap_urls WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks WHERE domain_id IN (SELECT id FROM domain_ids);
```

**Expected:** Row counts for each table (may be 0 for some)

---

### Step 3: Delete Child Records (In Order)

```sql
-- 3a. Delete contacts (leaf node - no children)
DELETE FROM contacts 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned

-- 3b. Delete pages (leaf node - no children)
DELETE FROM pages 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned

-- 3c. Delete sitemap_urls (leaf node - no children)
DELETE FROM sitemap_urls 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned

-- 3d. Delete sitemap_files (parent of pages via sitemap_file_id)
DELETE FROM sitemap_files 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned

-- 3e. Delete jobs (may contain domain references in result_data JSONB)
DELETE FROM jobs 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned

-- 3f. Delete tasks (scheduled/queued operations)
DELETE FROM tasks 
WHERE domain_id IN (
    SELECT id FROM domains WHERE domain = 'example.com'
);
-- Note the row count returned
```

---

### Step 4: Delete Parent Record

```sql
-- 4. Delete the domain itself (parent table)
DELETE FROM domains 
WHERE domain = 'example.com';
-- Expected: 1 row deleted
```

---

### Step 5: Verify Complete Removal

```sql
-- Confirm domain is gone
SELECT domain, sitemap_curation_status 
FROM domains 
WHERE domain = 'example.com';
-- Expected: 0 rows returned

-- Verify no orphaned records (should all be 0)
SELECT 
    'contacts' as table_name, COUNT(*) as orphaned_rows
    FROM contacts WHERE domain_id NOT IN (SELECT id FROM domains)
UNION ALL
SELECT 'pages', COUNT(*) FROM pages WHERE domain_id NOT IN (SELECT id FROM domains)
UNION ALL
SELECT 'sitemap_files', COUNT(*) FROM sitemap_files WHERE domain_id NOT IN (SELECT id FROM domains)
UNION ALL
SELECT 'sitemap_urls', COUNT(*) FROM sitemap_urls WHERE domain_id NOT IN (SELECT id FROM domains)
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs WHERE domain_id NOT IN (SELECT id FROM domains)
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks WHERE domain_id NOT IN (SELECT id FROM domains);
-- Expected: All counts should be 0
```

---

## Procedure: Bulk Domain Purge

For multiple domains at once:

### Step 1: Verify All Domains Exist

```sql
-- Check all domains exist
SELECT 
    id,
    domain,
    sitemap_curation_status,
    sitemap_analysis_status
FROM domains 
WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com');
-- Expected: N rows (one per domain)
```

---

### Step 2: Check Total Impact

```sql
-- Count all related records across all domains
WITH domain_ids AS (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
)
SELECT 
    'contacts' as table_name, COUNT(*) as row_count 
    FROM contacts WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'pages', COUNT(*) FROM pages WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'sitemap_files', COUNT(*) FROM sitemap_files WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'sitemap_urls', COUNT(*) FROM sitemap_urls WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs WHERE domain_id IN (SELECT id FROM domain_ids)
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks WHERE domain_id IN (SELECT id FROM domain_ids);
```

---

### Step 3: Delete Child Records (Bulk)

```sql
-- 3a. Delete contacts
DELETE FROM contacts 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);

-- 3b. Delete pages
DELETE FROM pages 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);

-- 3c. Delete sitemap_urls
DELETE FROM sitemap_urls 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);

-- 3d. Delete sitemap_files
DELETE FROM sitemap_files 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);

-- 3e. Delete jobs
DELETE FROM jobs 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);

-- 3f. Delete tasks
DELETE FROM tasks 
WHERE domain_id IN (
    SELECT id FROM domains 
    WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com')
);
```

---

### Step 4: Delete Parent Records (Bulk)

```sql
-- 4. Delete all domains
DELETE FROM domains 
WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com');
-- Expected: N rows deleted (one per domain)
```

---

### Step 5: Verify Complete Removal

```sql
-- Confirm all domains are gone
SELECT domain 
FROM domains 
WHERE domain IN ('domain1.com', 'domain2.com', 'domain3.com');
-- Expected: 0 rows returned
```

---

## Procedure: Pattern-Based Purge

For domains matching a pattern (USE WITH EXTREME CAUTION):

### Step 1: Preview Matches

```sql
-- ALWAYS preview before deleting
SELECT 
    id,
    domain,
    sitemap_curation_status,
    created_at
FROM domains 
WHERE domain LIKE '%pattern%'
ORDER BY domain;
-- Review carefully - ensure only intended domains match
```

---

### Step 2: If Confirmed, Use Bulk Procedure

Replace the `WHERE domain IN (...)` clauses with `WHERE domain LIKE '%pattern%'`

**⚠️ WARNING:** Pattern matching is dangerous. Always preview first.

---

## Alternative: Soft Delete (Recommended for Production)

Instead of hard deletion, mark domains as blocked:

```sql
-- Add blocked status and reason (preserves audit trail)
UPDATE domains 
SET 
    sitemap_curation_status = 'Archived',
    sitemap_analysis_status = 'failed',
    updated_at = NOW()
WHERE domain IN ('domain1.com', 'domain2.com');

-- Optional: Add a blocked_reason field to domains table
-- ALTER TABLE domains ADD COLUMN blocked_reason TEXT;
-- UPDATE domains 
-- SET blocked_reason = 'Aggressive WAF - permanent removal 2025-11-21'
-- WHERE domain IN ('domain1.com', 'domain2.com');
```

**Benefits:**
- Preserves audit trail
- Can be reversed
- Prevents re-discovery
- Maintains referential integrity

---

## Troubleshooting

### Error: Foreign Key Constraint Violation

**Cause:** Attempting to delete parent before children

**Fix:** Ensure you delete in the correct order (children first)

---

### Error: Permission Denied

**Cause:** Insufficient database privileges

**Fix:** Use service role key or admin account

---

### Orphaned Records After Deletion

**Cause:** New records created during deletion process

**Fix:** Re-run the orphan check query and delete any found

```sql
-- Find and delete orphaned contacts
DELETE FROM contacts 
WHERE domain_id NOT IN (SELECT id FROM domains);

-- Repeat for other tables
```

---

## Post-Deletion Checklist

- [ ] Verified domain(s) no longer in `domains` table
- [ ] Confirmed 0 orphaned records in child tables
- [ ] Documented reason for deletion (in incident log or work order)
- [ ] Updated any blocklists or filters to prevent re-discovery
- [ ] Notified team if domains were in active use

---

## Automation Script (Python)

For programmatic purging via MCP tools:

```python
from supabase_mcp import execute_sql

def purge_domains(project_id: str, domains: list[str]) -> dict:
    """
    Completely purge domains and all related data.
    
    Args:
        project_id: Supabase project ID
        domains: List of domain names to purge
        
    Returns:
        dict with row counts for each table
    """
    results = {}
    
    # Step 1: Verify domains exist
    domain_list = "', '".join(domains)
    verify_query = f"""
        SELECT id, domain FROM domains 
        WHERE domain IN ('{domain_list}');
    """
    verified = execute_sql(project_id, verify_query)
    results['verified_domains'] = len(verified)
    
    if results['verified_domains'] == 0:
        return {'error': 'No domains found'}
    
    # Step 2: Delete children (in order)
    tables = ['contacts', 'pages', 'sitemap_urls', 'sitemap_files', 'jobs', 'tasks']
    
    for table in tables:
        delete_query = f"""
            DELETE FROM {table} 
            WHERE domain_id IN (
                SELECT id FROM domains WHERE domain IN ('{domain_list}')
            );
        """
        execute_sql(project_id, delete_query)
        results[f'{table}_deleted'] = 'success'
    
    # Step 3: Delete parent
    domain_delete = f"""
        DELETE FROM domains WHERE domain IN ('{domain_list}');
    """
    execute_sql(project_id, domain_delete)
    results['domains_deleted'] = len(domains)
    
    return results

# Usage:
# purge_domains('ddfldwzhdhhzhxywqnyz', ['example.com', 'test.com'])
```

---

## Related Documentation

- [SYSTEM_MAP.md](../Context_Reconstruction/SYSTEM_MAP.md) - Database schema and relationships
- [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md) - Detailed table definitions
- [INCIDENTS/](../INCIDENTS/) - Past incidents involving data cleanup

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-21 | Initial creation | System |
| | Added all 6 child tables | |
| | Added soft delete alternative | |
| | Added Python automation script | |

---

**Remember:** This is a destructive operation. Always verify domain names before executing. Consider soft delete for production use.

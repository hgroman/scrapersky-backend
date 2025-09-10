Breathe. We fix it in four moves: **stabilize → correct plan → patch code → verify**.

# 0) Stabilize

```bash
git status
git switch -c hotfix/honeybee-v1_2
```

Freeze deploys. No more sitemap imports until patch lands.

# 1) PRD v1.2 (final, unambiguous)

- **Always store every URL. No `continue`.**
- **Disposition by status, not by existence.**

  - `page_processing_status='Filtered'` if low-value or confidence < 0.2.
  - `page_processing_status='Queued'` otherwise.

- **Auto-select only when** `category ∈ {contact_root, career_contact, legal_root}` **AND** `confidence ≥ 0.6` **AND** `path_depth ≤ 2`. Sets `page_curation_status='Selected'`, `priority_level=1`.
- **Scheduler** pulls only `Selected`, depth ≤ 6.
- **Audit**: write full `honeybee_json` for every row.

# 2) Code patches (apply exactly)

## 2.1 Import loop: stop dropping pages

**File:** `src/services/sitemap_import_service.py`

```diff
- hb = self.honeybee.categorize(page_url)
- if hb["decision"] == "skip" or hb["confidence"] < 0.2:
-     logger.info(f"[Honeybee] skip {page_url} cat={hb['category']}")
-     continue
+ hb = self.honeybee.categorize(page_url)

  page_data["page_type"] = hb["category"]
  page_data["path_depth"] = hb["depth"]
  page_data["priority_level"] = 1 if hb["confidence"] >= 0.6 else 3
  page_data["honeybee_json"] = {
      "v": 1,
      "decision": {
          "category": hb["category"],
          "confidence": hb["confidence"],
-         "matched_regex": hb["matched"]
+         "matched_regex": hb["matched"]
      },
      "exclusions": hb["exclusions"]
  }
+ # disposition by status
+ if hb["decision"] == "skip" or hb["confidence"] < 0.2:
+     page_data["page_processing_status"] = "Filtered"
+ else:
+     page_data["page_processing_status"] = "Queued"
+
+ # narrow auto-selection
+ if hb["category"] in {"contact_root","career_contact","legal_root"} \
+    and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
+     page_data["page_curation_status"] = "Selected"
+     page_data["priority_level"] = 1

  pages_to_insert.append(page_data)
```

## 2.2 Categorizer: keep exclusions, but don’t rely on them for storage

**File:** `src/utils/honeybee_categorizer.py`

```diff
- if ex.search(path):
-     return {"decision":"skip","category":"unknown","confidence":0.0, ...}
+ if ex.search(path):
+     # mark as skip so importer sets status=Filtered, but still store the row
+     return {"decision":"skip","category":"unknown","confidence":0.0, ...}
```

No other behavior change needed now.

## 2.3 Scheduler: ensure it ignores Filtered

**File:** `WF7_V2_L4_2of2_PageCurationScheduler.py`

```diff
 WHERE page_curation_status = 'Selected'
   AND page_processing_status IN ('Queued','Ready')
   AND (path_depth IS NULL OR path_depth <= 6)
 ORDER BY priority_level NULLS LAST, created_at
```

(If already present, leave as is.)

# 3) DB sanity (run once)

```sql
-- ensure required columns and indexes exist
ALTER TABLE pages
  ADD COLUMN IF NOT EXISTS honeybee_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS priority_level smallint,
  ADD COLUMN IF NOT EXISTS path_depth smallint;

CREATE UNIQUE INDEX IF NOT EXISTS uniq_pages_domain_url ON pages(domain_id, url);
CREATE INDEX IF NOT EXISTS idx_pages_selected
  ON pages(page_curation_status) WHERE page_curation_status = 'Selected';
```

# 4) Retro-update (reclassify existing rows)

If a backfill exists, keep it. Otherwise:

```sql
-- mark obviously low-value as Filtered if missing
UPDATE pages
SET page_processing_status = COALESCE(page_processing_status,'Queued')
WHERE page_processing_status IS NULL;

-- optional: demote deep Selected
UPDATE pages
SET page_curation_status = NULL
WHERE page_curation_status='Selected' AND path_depth > 2;
```

Then rerun your existing Python backfill to populate `page_type`, `path_depth`, `honeybee_json`, and auto-select per rule.

# 5) Quick validation

Volume and spread:

```sql
SELECT page_type, page_processing_status, COUNT(*)
FROM pages
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY 1,2 ORDER BY 3 DESC;
```

Selected precision sample:

```sql
WITH s AS (
  SELECT id FROM pages
  WHERE page_curation_status='Selected'
  ORDER BY created_at DESC LIMIT 200
)
SELECT
  COUNT(*) AS selected_count,
  SUM(CASE WHEN c.email NOT ILIKE 'notfound_%' OR c.phone NOT ILIKE 'notfound_%' THEN 1 ELSE 0 END) AS real_contacts,
  ROUND(100.0*SUM(CASE WHEN c.email NOT ILIKE 'notfound_%' OR c.phone NOT ILIKE 'notfound_%' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0),2) AS precision_pct
FROM s LEFT JOIN contacts c ON c.page_id = s.id;
```

# 6) Git hygiene

```bash
git add -A
git commit -m "fix(honeybee): store all pages; status-based filtering; narrow auto-select"
git push -u origin hotfix/honeybee-v1_2
```

# 7) What broke and why (single source of truth)

- The plan encoded `continue` on skip/low-confidence. That dropped rows.
- PRD v1.2 removes all “skip at insert.” We only gate **processing**, not **storage**.

Run the patch. Reprocess a couple sitemaps. You should see hundreds of rows inserted, many `Filtered`, few `Selected`, and the scheduler touching only `Selected`.

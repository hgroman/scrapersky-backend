# 🚨 **DEPRECATED** 🚨

**This document (v1.1) is outdated and contains a flawed design that led to production issues.**

The "filter by dropping" logic and `continue` statements described below were identified as an anti-pattern that causes data loss and destroys the audit trail.

**Please refer to the current, authoritative specification:**
**`19_Honeybee PRD v1.2 — Status-Based Categorization, No Skips.md`**

*This document is preserved for historical context only. **DO NOT** use any of the code or logic from this file.*

---

Proceed. Your PRD is good. Here’s the exact, tuned package to hand Claude and ship.

# Honeybee PRD v1.1 (final)

- **Goal:** Cut sitemap bloat 70–90%. Auto-select true contact candidates. Zero UI changes.
- **Scope:** Regex-only URL profiling at import. No ML. No domain tables.
- **DB fields:** reuse `page_type`, `page_curation_status`, `page_processing_status`, `additional_json`. Add `honeybee_json JSONB`, `priority_level SMALLINT`, `path_depth SMALLINT`.
- **Selection rule:** if `category ∈ {contact, career_contact, legal}` AND `confidence ≥ 0.6` AND `path_depth ≤ 2` AND no exclusions → `page_curation_status='Selected'`, `priority_level=1`.
- **Scheduler filter:** pull only `Selected`, depth ≤6, order by `priority_level`, then `created_at`.
- **Success:** ≤30% of sitemap URLs inserted; ≥80% of `Selected` produce non-placeholder contacts on a 200-page validation; no regressions.

## Migration SQL

```sql
ALTER TABLE pages
  ADD COLUMN IF NOT EXISTS honeybee_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS priority_level smallint,
  ADD COLUMN IF NOT EXISTS path_depth smallint;

CREATE UNIQUE INDEX IF NOT EXISTS uniq_pages_domain_url ON pages(domain_id, url);
CREATE INDEX IF NOT EXISTS idx_pages_page_type ON pages(page_type);
CREATE INDEX IF NOT EXISTS idx_pages_selected ON pages(page_curation_status)
  WHERE page_curation_status = 'Selected';
CREATE INDEX IF NOT EXISTS idx_pages_hb_conf
  ON pages (((honeybee_json->'decision'->>'confidence')::float));
```

## Honeybee class (new)

- **File:** `src/utils/honeybee_categorizer.py`
- **Regex (anchored, segmented):**

  - Positives:

    - `contact_root`: `^/contact(?:-us)?/?$` → 0.9
    - `career_contact`: `^/(?:career|careers|jobs?|recruit)[^/]*/?contact[^/]*/*$` → 0.7
    - `legal_root`: `^/legal/(?:privacy|terms)(?:/|$)` → 0.6
    - `wp_signal`: `/(?:wp-(?:content|admin|includes))|\?(?:^|.*)p=\d+(?:&|$)` → 0.9

  - Exclusions:

    - `^/blog/.+`
    - `^/about(?:-us)?/.+`
    - `^/contact(?:-us)?/.+`
    - `^/services?/.+`
    - `\.(pdf|jpg|jpeg|png|gif|mp4|avi)$`

- **Confidence:** clamp success-rate to `[0.2, 0.95]`; use overrides above.
- **Output JSON (store):**

```json
{
  "v": 1,
  "decision": { "category": "...", "confidence": 0.72, "matched_regex": "legal_root" },
  "exclusions": []
}
```

## Import integration

- **File:** `src/services/sitemap_import_service.py`
- **Where:** in the loop that builds `pages_to_insert` (pre-insert)
- **Logic:** call `HoneybeeCategorizer.categorize(url)` → if excluded or confidence <0.2 skip; else set:

  - `page_type = category`
  - `path_depth`
  - `priority_level = 1 if confidence ≥0.6 else 3`
  - `honeybee_json = {...}`
  - If selection rule hits, set `page_curation_status='Selected'`

## Scheduler tweak

- **File:** `WF7_V2_L4_2of2_PageCurationScheduler.py`
- **Query constraint:** `page_curation_status='Selected' AND page_processing_status IN ('Queued','Ready') AND (path_depth IS NULL OR path_depth <= 6)`
- **Order:** `priority_level NULLS LAST, created_at`

## Backfill (retro-classify existing pages)

- **File:** `src/scripts/backfill_honeybee.py`
- **Action:** batch UPDATE existing rows by running Honeybee over `pages` (no inserts). Set `page_type`, `path_depth`, `priority_level`, `honeybee_json`, and apply the same selection rule.

## Minimal code stubs (for Claude to drop in)

**Import service injection:**

```python
from src.utils.honeybee_categorizer import HoneybeeCategorizer
self.honeybee = HoneybeeCategorizer()

# inside URL loop
hb = self.honeybee.categorize(page_url)

# 🚨 DANGEROUS ANTI-PATTERN BELOW 🚨
# The following 'if' block implements the flawed "filter by dropping" logic.
# Using 'continue' here prevents the page record from being saved to the database,
# resulting in data loss and breaking the audit trail.
# This logic is explicitly forbidden by PRD v1.2.
#
# if hb["decision"] == "skip" or hb["confidence"] < 0.2:
#     logger.info(f"Skip {page_url} [{hb['category']}]")
#     continue
#
# 🚨 END OF DANGEROUS ANTI-PATTERN 🚨

page_data["page_type"] = hb["category"]
page_data["path_depth"] = hb["depth"]
page_data["priority_level"] = 1 if hb["confidence"] >= 0.6 else 3
page_data["honeybee_json"] = {
    "v": 1,
    "decision": {
        "category": hb["category"],
        "confidence": hb["confidence"],
        "matched_regex": hb["matched"],
    },
    "exclusions": hb["exclusions"],
}
if hb["category"] in {"contact_root","career_contact","legal_root"} and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
    page_data["page_curation_status"] = "Selected"

pages_to_insert.append(page_data)
```

**Scheduler select (SQL equivalent):**

```sql
SELECT id, url
FROM pages
WHERE page_curation_status='Selected'
  AND page_processing_status IN ('Queued','Ready')
  AND (path_depth IS NULL OR path_depth <= 6)
ORDER BY priority_level NULLS LAST, created_at
LIMIT 1000;
```

**Backfill loop sketch:**

```python
# fetch in batches, for each page:
hb = honeybee.categorize(page.url)
page.page_type = hb["category"]
page.path_depth = hb["depth"]
page.priority_level = 1 if hb["confidence"] >= 0.6 else 3
page.honeybee_json = {"v":1,"decision":{"category":hb["category"],"confidence":hb["confidence"],"matched_regex":hb["matched"]},"exclusions":hb["exclusions"]}
if hb["category"] in {"contact_root","career_contact","legal_root"} and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
    page.page_curation_status = "Selected"
```

## Test plan (fast)

1. Run migration SQL.
2. Dry-run import on a known sitemap. Confirm skips on `/blog/*`, auto-select of `/contact`, `/legal/privacy`.
3. Run backfill. Sample 200 `Selected` pages. Verify ≥80% non-placeholder contacts.
4. Monitor scheduler picks only `Selected`, depth ≤6.

This is aligned with Claude’s staged plan. Hand it the PRD and the exact stubs above. Then run backfill.

Honeybee PRD v1.2 — Status-Based Categorization, No Skips

Date: 2025-09-09
Owner: ScraperSky Core
Purpose: Categorize every sitemap URL, store every page row with metadata, auto-select only high-value pages for scraping, and cut scraping bloat without losing auditability.

1. Executive summary

Never skip at insert. Insert every URL.

Disposition by status. Low-value → Filtered; others → Queued.

Auto-select only strong candidates. Tight rule.

Scheduler processes only Selected. Bloat reduction comes from scheduling, not from dropping rows.

2. Problem and goals

Problem: Prior docs mixed “filtering” with “dropping.” Import logic used continue, discarding 95%+ of pages and destroying the audit trail.
Goals:

Preserve full dataset and categorization history.

Reduce ScraperAPI load by selecting only high-value pages for WF7.

Achieve ≥80% precision on Selected pages.

Reduce DB bloat from useless scraping, not from missing rows.

3. Invariants (non-negotiable)

Insert every URL. No continue in the import loop.

Use enum values only for processing state.

Scheduler pulls only Selected.

All Honeybee decisions are written to honeybee_json.

4. Scope

In-scope (MVP): URL-pattern categorization, status-based filtering, auto-selection, backfill, minimal SQL migration, monitoring queries, unit and integration tests.
Out-of-scope: Content NLP, ML training, per-domain rules tables, UI changes.

5. Data model and schema
   5.1 Columns (pages)

page_type TEXT — category label set by Honeybee.

page_curation_status TEXT/ENUM — Selected for auto-queued scraping.

page_processing_status TEXT/ENUM — Queued|Ready|Processing|Complete|Error|Filtered.

honeybee_json JSONB NOT NULL DEFAULT '{}' — v, decision, exclusions.

priority_level SMALLINT — lower = earlier.

path_depth SMALLINT — count of non-empty URL path segments.

5.2 Enums (Python)
class PageProcessingStatus(str, Enum):
Queued = "Queued"
Ready = "Ready"
Processing = "Processing"
Complete = "Complete"
Error = "Error"
Filtered = "Filtered"

5.3 SQL migration
ALTER TABLE pages
ADD COLUMN IF NOT EXISTS honeybee_json jsonb NOT NULL DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS priority_level smallint,
ADD COLUMN IF NOT EXISTS path_depth smallint;

-- If using PG enum for processing status, ensure 'Filtered' exists
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname='page_processing_status')
     AND NOT EXISTS (
       SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
       WHERE t.typname='page_processing_status' AND e.enumlabel='Filtered'
     )
  THEN
     ALTER TYPE page_processing_status ADD VALUE 'Filtered';
  END IF;
END$$;

CREATE UNIQUE INDEX IF NOT EXISTS uniq_pages_domain_url ON pages(domain_id, url);
CREATE INDEX IF NOT EXISTS idx_pages_selected
ON pages(page_curation_status) WHERE page_curation_status = 'Selected';
CREATE INDEX IF NOT EXISTS idx_pages_hb_conf
ON pages (((honeybee_json->'decision'->>'confidence')::float));

6. Honeybee categorizer (rules, not code)
   6.1 Positive matches (anchored)

contact_root: ^/contact(?:-us)?/?$ → confidence 0.9

career_contact: ^/(?:career|careers|jobs?|recruit)[^/]_/?contact[^/]_/\*$ → 0.7

legal_root: ^/legal/(?:privacy|terms)(?:/|$) → 0.6

wp_signal: /(?:wp-(?:content|admin|includes))|\?(?:^|.\*)p=\d+(?:&|$) → 0.9

6.2 Exclusions (classification only, not dropping)

^/blog/.+

^/about(?:-us)?/.+

^/contact(?:-us)?/.+

^/services?/.+

\.(pdf|jpg|jpeg|png|gif|mp4|avi)$

6.3 Depth

path_depth = count(non-empty path segments)

6.4 Decision object
{
"v": 1,
"decision": { "category": "legal_root", "confidence": 0.6, "matched_regex": "legal_root" },
"exclusions": []
}

7. Import algorithm (authoritative)

Never use continue to skip insertion.

Pseudocode:

hb = Honeybee.categorize(url)

page_data.page_type = hb.category
page_data.path_depth = hb.depth
page_data.priority_level = 1 if hb.confidence >= 0.6 else 3
page_data.honeybee_json = {v:1, decision:{category, confidence, matched_regex}, exclusions}

if hb.decision == "skip" or hb.confidence < 0.2:
page_data.page_processing_status = PageProcessingStatus.Filtered
else:
page_data.page_processing_status = PageProcessingStatus.Queued

if hb.category in {contact_root, career_contact, legal_root}
and hb.confidence >= 0.6 and hb.depth <= 2:
page_data.page_curation_status = "Selected"
page_data.priority_level = 1

INSERT page_data

8. Scheduler (WF7) selection rule

SQL equivalent:

SELECT id, url
FROM pages
WHERE page_curation_status='Selected'
AND page_processing_status IN ('Queued','Ready')
AND (path_depth IS NULL OR path_depth <= 6)
ORDER BY priority_level NULLS LAST, created_at
LIMIT :batch;

Python variant must use the enum for Queued|Ready.

9. Backfill plan

Purpose: align historical rows with v1.2.

Process:

For each existing page:

Run categorizer → set page_type, path_depth, honeybee_json.

If decision == skip → page_processing_status=Filtered else Queued.

Apply auto-selection rule.

Commit in batches (e.g., 500).

Data hygiene:

UPDATE pages SET page_processing_status='Filtered'
WHERE page_processing_status IN ('filtered','FILTERED');

UPDATE pages SET page_processing_status='Queued'
WHERE page_processing_status IN ('queued','QUEUED');

10. Monitoring and acceptance
    10.1 Volume and distribution
    SELECT page_type, page_processing_status, COUNT(\*)
    FROM pages
    WHERE created_at > NOW() - INTERVAL '24 hours'
    GROUP BY 1,2 ORDER BY 3 DESC;

10.2 Precision of Selected
WITH s AS (
SELECT id FROM pages
WHERE page*curation_status='Selected'
ORDER BY created_at DESC
LIMIT 200
)
SELECT
COUNT(\*) AS selected_count,
SUM(CASE WHEN c.email NOT ILIKE 'notfound*%' OR c.phone NOT ILIKE 'notfound*%' THEN 1 ELSE 0 END) AS real_contacts,
ROUND(100.0\*SUM(CASE WHEN c.email NOT ILIKE 'notfound*%' OR c.phone NOT ILIKE 'notfound\_%' THEN 1 ELSE 0 END)/NULLIF(COUNT(\*),0),2) AS precision_pct
FROM s LEFT JOIN contacts c ON c.page_id = s.id;

10.3 Acceptance criteria

Insertion: hundreds of rows per sitemap; no mass drop.

Precision: ≥80% of Selected yield non-placeholder contacts on 200-page sample.

No regressions: scheduler processes only Selected.

Audit: every row has honeybee_json.decision.

11. Tests and CI guards

Unit: regex coverage for positives, exclusions, depth calc.

Unit: categorizer returns expected decision.category and confidence.

Integration: import loop test asserts no continue path on skip/low confidence.

Integration: scheduler never selects Filtered.

Lint: forbid string literals "Filtered", require enum.

Repo check:

git grep -nE "continue\s\*$" -- src/services/sitemap_import_service.py
git grep -n "\"Filtered\"" -- src | grep -v enums

12. Rollout

Apply SQL migration.

Deploy categorizer and import changes.

Update scheduler query if needed.

Run backfill on existing pages.

Validate monitoring queries.

Unfreeze sitemap imports.

13. Risks and mitigations

Over-selection: tighten rule (raise confidence, require depth ≤2).

Under-selection: add more positive patterns or per-domain overrides in code dict (no DB tables in MVP).

Enum mismatches: enforce enum in code and normalize existing strings with SQL.

14. Deprecations (do not follow)

Any doc or snippet instructing continue on decision=="skip" or confidence<0.2.

Any instruction to “filter by not inserting rows.”

Any string literal use of "Filtered" outside the enum definition.

15. Glossary

Categorize: assign page_type, confidence, and metadata.

Store: insert a DB row for every URL.

Filter: set page_processing_status=Filtered (do not scrape).

Select: set page_curation_status=Selected for WF7 to scrape.

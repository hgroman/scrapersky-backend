Correct. I’ll align “Mayday” with the enum pivot and remove all string literals.

# What to change

## 1) Python enum (ALREADY EXISTS)

**File:** `src/models/enums.py` (line 88)

```python
class PageProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Filtered = "Filtered"   # ← already added during debugging
```

## 2) DB type safety

- If the column is **TEXT**: no DB change.
- If the column is a **Postgres ENUM**: add the value.

```sql
-- only if page_processing_status uses a PG ENUM type
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    WHERE t.typname = 'page_processing_status' AND e.enumlabel = 'Filtered'
  ) THEN
    ALTER TYPE page_processing_status ADD VALUE 'Filtered';
  END IF;
END$$;
```

## 3) Import loop: use enum, not strings

**File:** `src/services/sitemap_import_service.py`

```python
from src.models.enums import PageProcessingStatus

# ...
hb = self.honeybee.categorize(page_url)

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

# disposition by status (enum)
if hb["decision"] == "skip" or hb["confidence"] < 0.2:
    page_data["page_processing_status"] = PageProcessingStatus.Filtered
else:
    page_data["page_processing_status"] = PageProcessingStatus.Queued

# narrow auto-selection
if hb["category"] in {"contact_root","career_contact","legal_root"} \
   and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
    page_data["page_curation_status"] = "Selected"
    page_data["priority_level"] = 1
```

## 4) Scheduler: enum-safe filter

**File:** `WF7_V2_L4_2of2_PageCurationScheduler.py`

```python
from src.models.enums import PageProcessingStatus

stmt = (
  select(Page)
  .where(
    Page.page_curation_status == 'Selected',
    Page.page_processing_status.in_([PageProcessingStatus.Queued, PageProcessingStatus.Ready]),
    (Page.path_depth.is_(None) | (Page.path_depth <= 6)),
  )
  .order_by(Page.priority_level.asc().nullslast(), Page.created_at.asc())
  .limit(batch_size)
)
```

## 5) Backfill: enum-safe update

```python
from src.models.enums import PageProcessingStatus
# ...
if r["decision"] == "skip":
    pg.page_processing_status = PageProcessingStatus.Filtered
else:
    pg.page_processing_status = PageProcessingStatus.Queued
```

## 6) Data hygiene

Normalize any legacy string rows:

```sql
UPDATE pages SET page_processing_status='Filtered'
WHERE page_processing_status IN ('filtered','FILTERED');

UPDATE pages SET page_processing_status='Queued'
WHERE page_processing_status IN ('queued','QUEUED');
```

## 7) Tests to prevent regressions

- Assert `PageProcessingStatus.Filtered` exists.
- Import loop never `continue`s on skip/low-confidence.
- Scheduler never selects rows with `Filtered`.

This reconciles the pivot: status-based filtering, enum-correct, no silent drops.

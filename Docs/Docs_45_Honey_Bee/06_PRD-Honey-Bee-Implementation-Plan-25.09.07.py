Proceed to execution. Use these exact steps and snippets.

# Stage 1 — DB migration (run now)

```sql
ALTER TABLE pages
  ADD COLUMN IF NOT EXISTS honeybee_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS priority_level smallint,
  ADD COLUMN IF NOT EXISTS path_depth smallint;

CREATE UNIQUE INDEX IF NOT EXISTS uniq_pages_domain_url ON pages(domain_id, url);
CREATE INDEX IF NOT EXISTS idx_pages_page_type ON pages(page_type);
CREATE INDEX IF NOT EXISTS idx_pages_selected
  ON pages(page_curation_status) WHERE page_curation_status = 'Selected';
CREATE INDEX IF NOT EXISTS idx_pages_hb_conf
  ON pages (((honeybee_json->'decision'->>'confidence')::float));
```

# Stage 2 — Honeybee class (new file)

`src/utils/honeybee_categorizer.py`

```python
import re
from urllib.parse import urlparse

class HoneybeeCategorizer:
    R_POS = {
        "contact_root": re.compile(r"^/contact(?:-us)?/?$", re.I),
        "career_contact": re.compile(r"^/(?:career|careers|jobs?|recruit)[^/]*/?contact[^/]*/*$", re.I),
        "legal_root": re.compile(r"^/legal/(?:privacy|terms)(?:/|$)", re.I),
    }
    R_EX = [
        re.compile(r"^/blog/.+", re.I),
        re.compile(r"^/about(?:-us)?/.+", re.I),
        re.compile(r"^/contact(?:-us)?/.+", re.I),
        re.compile(r"^/services?/.+", re.I),
        re.compile(r"\.(pdf|jpg|jpeg|png|gif|mp4|avi)$", re.I),
    ]
    R_WP = re.compile(r"/(?:wp-(?:content|admin|includes))|\?(?:^|.*)p=\d+(?:&|$)", re.I)
    CONF = {"contact_root": 0.9, "career_contact": 0.7, "legal_root": 0.6, "wp_prospect": 0.9}

    @staticmethod
    def _depth(path: str) -> int:
        return sum(1 for s in path.split("/") if s)

    def categorize(self, url: str) -> dict:
        p = urlparse(url)
        path = p.path or "/"
        q = "?" + p.query if p.query else ""
        for ex in self.R_EX:
            if ex.search(path):
                return {"decision":"skip","category":"unknown","confidence":0.0,"matched":None,"exclusions":["rule_hit"],"depth":self._depth(path)}
        for name, rgx in self.R_POS.items():
            if rgx.match(path):
                return {"decision":"include","category":name,"confidence":self.CONF.get(name,0.5),"matched":name,"exclusions":[],"depth":self._depth(path)}
        if self.R_WP.search(path+q):
            return {"decision":"include","category":"wp_prospect","confidence":self.CONF["wp_prospect"],"matched":"wp_signal","exclusions":[],"depth":self._depth(path)}
        return {"decision":"include","category":"unknown","confidence":0.2,"matched":None,"exclusions":[],"depth":self._depth(path)}
```

# Stage 3 — Import integration (inject pre-insert)

`src/services/sitemap_import_service.py` (top)

```python
from src.utils.honeybee_categorizer import HoneybeeCategorizer
```

`__init__`:

```python
self.honeybee = HoneybeeCategorizer()
```

in the loop building `pages_to_insert`:

```python
hb = self.honeybee.categorize(page_url)
if hb["decision"] == "skip" or hb["confidence"] < 0.2:
    logger.info(f"[Honeybee] skip {page_url} cat={hb['category']}")
    continue

page_data["page_type"] = hb["category"]
page_data["path_depth"] = hb["depth"]
page_data["priority_level"] = 1 if hb["confidence"] >= 0.6 else 3
page_data["honeybee_json"] = {
    "v":1,
    "decision":{"category":hb["category"],"confidence":hb["confidence"],"matched_regex":hb["matched"]},
    "exclusions":hb["exclusions"]
}
if hb["category"] in {"contact_root","career_contact","legal_root"} and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
    page_data["page_curation_status"] = "Selected"
```

# Stage 4 — Scheduler query tweak

`WF7_V2_L4_2of2_PageCurationScheduler.py` selection:

```python
stmt = (
    select(Page)
    .where(
        Page.page_curation_status == 'Selected',
        Page.page_processing_status.in_(('Queued','Ready')),
        (Page.path_depth.is_(None) | (Page.path_depth <= 6)),
    )
    .order_by(Page.priority_level.asc().nullslast(), Page.created_at.asc())
    .limit(batch_size)
)
```

# Stage 5 — Backfill script (batch UPDATE, no inserts)

`src/scripts/backfill_honeybee.py`

```python
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from src.config.database import engine
from src.models.page import Page
from src.utils.honeybee_categorizer import HoneybeeCategorizer

async def run():
    hb = HoneybeeCategorizer()
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with Session() as s:
        offset, size = 0, 500
        while True:
            rows = (await s.execute(
                select(Page).order_by(Page.created_at).offset(offset).limit(size)
            )).scalars().all()
            if not rows: break
            for pg in rows:
                r = hb.categorize(pg.url)
                if r["decision"] == "skip":  # still store decision for audit
                    pg.honeybee_json = {"v":1,"decision":{"category":"unknown","confidence":0.0,"matched_regex":None},"exclusions":r["exclusions"]}
                    pg.page_type = "unknown"; pg.path_depth = r["depth"]; pg.priority_level = 3
                    continue
                pg.page_type = r["category"]
                pg.path_depth = r["depth"]
                pg.priority_level = 1 if r["confidence"] >= 0.6 else 3
                pg.honeybee_json = {"v":1,"decision":{"category":r["category"],"confidence":r["confidence"],"matched_regex":r["matched"]},"exclusions":r["exclusions"]}
                if r["category"] in {"contact_root","career_contact","legal_root"} and r["confidence"] >= 0.6 and r["depth"] <= 2:
                    pg.page_curation_status = "Selected"
            await s.commit()
            offset += size

if __name__ == "__main__":
    asyncio.run(run())
```

# Stage 6 — Fast validation queries

Inserted share:

```sql
-- % of sitemap URLs inserted after Honeybee
SELECT
  COUNT(*) AS inserted,
  ROUND(100.0*COUNT(*)/NULLIF((SELECT COUNT(*) FROM sitemap_urls_source),0),2) AS pct_vs_source
FROM pages
WHERE created_at > NOW() - INTERVAL '1 day';
```

Precision of `Selected`:

```sql
-- Assumes contacts table with non-placeholder detection
WITH sel AS (
  SELECT id FROM pages
  WHERE page_curation_status='Selected' AND created_at > NOW() - INTERVAL '1 day'
)
SELECT
  COUNT(*) AS selected_count,
  SUM(CASE WHEN c.email NOT ILIKE 'notfound_%' OR c.phone NOT ILIKE 'notfound_%' THEN 1 ELSE 0 END) AS real_contacts,
  ROUND(100.0*SUM(CASE WHEN c.email NOT ILIKE 'notfound_%' OR c.phone NOT ILIKE 'notfound_%' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0),2) AS precision_pct
FROM sel s
LEFT JOIN contacts c ON c.page_id = s.id;
```

# Git hygiene (suggested)

* Commit 1: `feat(db): add honeybee fields + indexes`
* Commit 2: `feat(honeybee): categorizer with segmented regex + depth`
* Commit 3: `feat(import): inject honeybee + auto-select`
* Commit 4: `feat(scheduler): filter by Selected and depth`
* Commit 5: `chore(backfill): retro-classify pages`

Hand this to Claude and execute the six stages.

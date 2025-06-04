# ScraperSky Vector DB — Condensed Living Doc
*Version 1.3 &nbsp;•&nbsp; Updated 2025‑06‑03*

---

## 1&nbsp;&nbsp;Executive Snapshot
- **Status:** Foundational vector DB is live and healthy.  
- **Hot Fix:** “Similarity: nan” bug resolved (see `Docs_18_Vector_Operations/vector_db_nan_issue_resolution.md`).  
- **Content Loaded:** 12 core architectural docs embedded and searchable.  
- **Next Goal:** steady ingestion & curation of *all* remaining project docs.

---

## 2&nbsp;&nbsp;Core Setup (One‑Time ✅)
| Area | Key Actions | Where to Look |
|------|-------------|---------------|
| **Schema** | `project_docs` table (`id, title, content, embedding VECTOR(1536), created_at`) & `vector` extension | _Section 1. Database Schema_ |
| **AI Integration** | `ai` schema, secure key set/get functions, `openai_embed_production`, `pg_net` enabled | `Docs_18_Vector_Operations/*.sql` |
| **Search** | `search_docs(query_text, threshold=0.7)` with graceful fallbacks | same folder |
| **Validation** | Verified schema, embeddings (0 nulls), and search accuracy | `scripts/vector_db_simple_test.py` |

> **Do NOT rerun** any SQL blocks marked “✅ COMPLETED”.

---

## 3&nbsp;&nbsp;Daily Ops (Ongoing 🔄)
| Task | Frequency | Command / Note |
|------|-----------|----------------|
| **Add / update docs** | When docs change | `vector_db_insert_architectural_docs.py --file=<path>` |
| **Key rotation** | 90 days or on compromise | `SELECT ai.openai_api_key_set('new‑key');` |
| **Performance check** | Monthly | `EXPLAIN ANALYZE SELECT * FROM search_docs('test');` |
| **Null‑embedding scan** | After bulk loads | `SELECT title FROM project_docs WHERE embedding IS NULL;` |

---

## 4&nbsp;&nbsp;Environment Quick Ref
```bash
OPENAI_API_KEY="sk‑…"
DATABASE_URL="postgresql://user:pass@host:5432/db"
# Prefer plain 'postgresql://' over 'postgresql+asyncpg://'
```

---

## 5&nbsp;&nbsp;Document Lifecycle
1. **Prep** markdown / txt in `Docs/Docs_15_Master_Plan/`.  
2. **Single insert:**  
   ```bash
   python vector_db_insert_architectural_docs.py --file=<doc>
   ```  
3. **Bulk insert:** use `bulk_load_documents(dir, batch=10)` (see planned script).  
4. **Re‑embed** on model upgrade:  
   ```sql
   UPDATE project_docs
   SET embedding = ai.openai_embed_production('text-embedding-ada-002', content)::vector
   WHERE title='updated.md';
   ```

---

## 6&nbsp;&nbsp;Search Usage
```sql
SELECT * FROM search_docs('Layer 4 service patterns');     -- default 0.7 threshold
SELECT * FROM search_docs('naming conventions', 0.5);      -- relaxed threshold
```
Returns **title, snippet (1 000 chars), similarity** (0‑1 scale).

---

## 7&nbsp;&nbsp;Troubleshooting Cheatsheet
| Symptom | Likely Cause | Fast Fix |
|---------|--------------|----------|
| `Similarity: nan` | Un‑normalized embeddings | Re‑run fix script (already applied). |
| `pg_net` errors | Extension missing | `CREATE EXTENSION pg_net;` |
| No results | Threshold too high or null embeddings | Lower threshold / run null‑scan query. |
| API fails | Key revoked or quota hit | Rotate key; monitor status.openai.com. |

---

## 8&nbsp;&nbsp;Roadmap
- **Immediate:** REST endpoints `/api/v3/vector/*`, pattern‑matching script.  
- **Mid‑Term:** Auto‑watcher for new docs; hybrid (keyword + vector) search.  
- **Long‑Term:** Analytics dashboard, cross‑system doc sync, large‑scale tuning (IVFFlat index, pooling).

---

## 9&nbsp;&nbsp;Key Scripts
| Script | Purpose | Status |
|--------|---------|--------|
| `vector_db_insert_architectural_docs.py` | Load / update docs | ✅ Prod‑ready |
| `scripts/vector_db_simple_test.py` | Smoke‑test search | ✅ Updated 2025‑06‑02 |
| `scripts/vector_db_bulk_loader.py` | Batch loader | 📝 Planned |
| `scripts/vector_db_pattern_application.py` | Apply arch patterns | 📝 Planned |

---

## 10&nbsp;&nbsp;Change Log (compact)
| Date | Ver | Note |
|------|-----|------|
| 06‑01 | 1.0 | Initial doc |
| 06‑01 | 1.1 | Split completed vs ongoing tasks |
| 06‑02 | 1.2 | Added OpenAI prod integration |
| 06‑03 | 1.3 | Condensed & bug‑fix update |

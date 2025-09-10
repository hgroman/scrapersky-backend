# Executive summary

Goal: **verify and document** what’s happening so it can be administered, enhanced, maintained, and extended. From the logs, your “single search” flow (WF1) is working as designed (Google Maps search → results stored). **Separately, background schedulers are auto-picking up newly stored places and running “Deep Scans” (Google Place Details).** When a Deep Scan finds a website, a **Domain Scheduler** enqueues that domain for metadata extraction and then for **sitemap analysis**.
This auto-queueing appears to be **enabled by default** in your background batch (“sitemap_scheduler”) even though WF1’s canonical doc says WF1 itself does not trigger a background job. That’s the gap to verify and formally document. &#x20;

---

## Detailed timeline (UTC) with IDs

### A. WF1: User search & storage (UI → Router → Services → DB)

- **18:21:16.711** — Places search job created & started
  Job: `eed90132-9d73-43f1-b255-f124c254de19` • Tenant: `550e8400-e29b-41d4-a716-446655440000` • User: `56adcb98-d218-40ad-8a1c-997c54d83154`
- **18:21:17.453** — Search result: **10 places** for `'lawyer'` in `mansfield, pa`.
- **18:21:17.521** — Storage service: **5 existing** will be updated.
- **18:21:18.046** — Storage service: **Successfully stored 10 places (0 failed)**.
- **18:21:18.115** — Router completes job: `{success: True, places_count: 10, job_id: eed90132-9d73-43f1-b255-f124c254de19}`.

> WF1 reference: UI calls `POST /api/v3/localminer-discoveryscan/search/places` → router delegates to `PlacesSearchService` → results persisted by `places_storage_service` into **`places_staging`** with status `New`. (Doc: _WF-01 Single Search Discovery_.)&#x20;

### B. Background schedulers (minute cadence)

Jobs running every minute via APScheduler:

- **process_pending_jobs** → **`sitemap_scheduler`** (“Sitemaps, DeepScans, DomainExtractions” batch)
- **process_pending_domains** → **`domain_scheduler`**
- **process_pending_domain_sitemap_submissions**
- **process_pending_sitemap_imports**
- **process_page_curation_queue**

### C. Auto Deep Scan pickup (triggered by background, not by WF1)

- **18:22:04.941** — `sitemap_scheduler`: **Found 5 places queued for deep scan.**
  (Indicates new place records were **auto-marked** `deep_scan_status=queued` or equivalent after WF1 storage.)
- **18:22:05.011 → 18:22:08.682** — **Deep Scans executed** by `places_deep_service` for these Place IDs (examples shown):

  - `ChIJMX9f1z3Wz4kRHCEq2ihDOLM` → _Lawrence Mansfield Law Office_ (no website)
    Saved/updated ID: `18e5e673-b3e1-4c68-b139-2b7f34f641ac` (Success at **18:22:06.488–.489**)
  - `ChIJm5EQkynXz4kRjs8p2DcR83o` → _Kim Marie Staron LLC_ (**website: [https://attykimmariestaron.com](https://attykimmariestaron.com)**)
    Saved/updated ID: `e66c6c93-ad96-4aab-9bb0-7b760a24503d` (Success at **18:22:07.210**)
  - `ChIJa6vBSZXWz4kR66P09hTY0OE` → _Scheib Law Offices_ (no website)
    Saved/updated ID: `106279f6-9137-4b78-8162-48dbf7b23ab0` (Success at **18:22:08.535**)
  - `ChIJIRZuISjgz4kRM2QV1DTkeWQ` → _Brann, Williams & Caldwell_ (**website: [http://www.bwcs-law.com](http://www.bwcs-law.com)**)
    (Mapped at **18:22:08.685**)

> All Deep Scans show: `PlacesDeepService initialized` • `API queries_quota: 60` • Google Place Details call • “Successfully saved/updated deep scan details…”

### D. Domains auto-queued (derived from Deep Scans that found websites)

- **18:23:04–18:23:06** — `domain_scheduler` run:

  - **18:23:06.069** — **Found 2 pending domain(s)** (the two with websites above):

    - `3ce424c1-5253-4da7-8e8a-e3ec27220458` → **attykimmariestaron.com**
    - `c3a7a3e5-001e-41a7-8b54-963c0cf36e57` → **bwcs-law\.com**

  - **18:23:06.393–.395** — **Phase 2: metadata extraction** (ScraperAPI disabled → minimal metadata).
  - **18:23:06.558 / 18:23:06.861** — Both domains **queued for sitemap analysis** (_WF4→WF5 trigger_), “Phase 3 complete: All domain results updated”.
  - **18:23:07.023** — Domain batch summary: Found 2 / Processed 2 / Successful 2 / Failed 0.

### E. “Corrected sitemap analysis batch” heartbeats

- **18:19:04 / 18:20:04 / 18:21:04 / 18:22:04 / 18:23:04** — `Domain Sitemap Submission Scheduler` starts batches with IDs:

  - `25dbb5d3-7bc0-4560-989f-de4dea6cd35d` (18:19)
  - `cebb9638-a192-4653-b231-f4203c6f2bc1` (18:20)
  - `64bb0deb-7999-4dd4-ad52-a18dcedddaa0` (18:21)
  - `36b268c6-bb28-4da8-8ab6-dfc24dcfa7f4` (18:22)
  - `967ef3a2-f4c6-4c74-bec0-064edb8941ed` (18:23)
    …each time: “📋 Found 0 domains queued for sitemap analysis / ✅ No domains require sitemap analysis” **until** the domain_scheduler actually queued two at **18:23:06** (so the 18:24 run would be the first to see them).

---

## What this means (mechanics & where this lives)

1. **WF1 (Single Search) produces `places_staging` rows, status=`New`.**
   That’s the formal handoff to WF2 (Staging Editor). WF1 itself explicitly has **no direct background job trigger** in the canonical doc.&#x20;

2. **Background batch (`sitemap_scheduler`) independently scans for places “queued for deep scan”.**
   Your logs show it **found 5** immediately after WF1 wrote 10 places. This implies a rule in storage or a post-insert hook that sets a flag (e.g., `deep_scan_status=Queued`) on some or all new places. This is **outside WF1’s documented scope** and should be documented as part of background processing (either WFx: DeepScan or as a mode of the sitemap scheduler).

3. **Deep Scan writes “place details” and, if a `website_url` is present, a domain record is created/marked pending.**
   Then **domain_scheduler** performs metadata extraction and **enqueues sitemap analysis** (WF4→WF5).

4. **Documentation canon**: The “Workflow Canon” system is meant to capture these producer→consumer handoffs, tables, and files in a standardized way (cheat sheet, comparison tables, workflow YAMLs, dependency traces). Use it to add the **Deep Scan** and **Domain** workflows and their handoffs (from `places_staging` → deep scan queue → domain queue → sitemap submission).&#x20;

---

## Why auto-deep-scan is probably happening

- Either **storage code** (e.g., `places_storage_service`) or a **DB default/trigger** sets a flag (e.g., `deep_scan_status='Queued'`) for newly inserted place rows.
- The **`sitemap_scheduler`** batch then looks for those queued rows each minute and runs Deep Scans.
- This matches “Found N places queued for deep scan” followed immediately by Deep Scan calls and saves.

> This **contradicts WF1’s “no background job triggered by this flow” note** and should be reconciled in docs as a cross-workflow handoff (WF1 → DeepScan workflow) or behind a feature flag.&#x20;

---

## Verification & documentation checklist (actionable)

### 1) Database verification (read-only SQL)

> Adjust names to your actual models; these reflect likely structures.

- **Confirm WF1 inserts**

  ```sql
  -- last 15 minutes
  SELECT id, google_place_id, name, status, tenant_id, created_at
  FROM places_staging
  WHERE created_at >= NOW() - INTERVAL '15 minutes'
    AND tenant_id = '550e8400-e29b-41d4-a716-446655440000'
  ORDER BY created_at DESC;
  ```

- **Find how Deep Scan is queued** (look for a status/flag)

  ```sql
  SELECT id, google_place_id, deep_scan_status, deep_scan_queued_at
  FROM places_staging
  WHERE created_at >= NOW() - INTERVAL '15 minutes';
  ```

- **Confirm Deep Scan details persistence**
  (table name may be `place_deep_details` or similar—check model used by `places_deep_service`)

  ```sql
  SELECT id, google_place_id, website_url, reviews_count, updated_at
  FROM place_deep_details
  WHERE google_place_id IN ('ChIJMX9f1z3Wz4kRHCEq2ihDOLM','ChIJm5EQkynXz4kRjs8p2DcR83o',
                            'ChIJa6vBSZXWz4kR66P09hTY0OE','ChIJIRZuISjgz4kRM2QV1DTkeWQ');
  ```

- **Confirm domain queue**

  ```sql
  SELECT id, domain, status, queued_reason, created_at
  FROM domains
  WHERE domain IN ('attykimmariestaron.com','bwcs-law.com')
  ORDER BY created_at DESC;
  ```

- **Confirm sitemap submission queue**

  ```sql
  SELECT id, domain_id, status, batch_id, created_at
  FROM domain_sitemap_submissions
  WHERE created_at >= NOW() - INTERVAL '30 minutes';
  ```

### 2) Code tracing (files & log anchors)

- **WF1**: confirm no background call in the **router** or **PlacesSearchService** beyond storage

  - `src/routers/google_maps_api.py` (POST `/search/places`)
  - `src/services/places/places_search_service.py`
  - `src/services/places/places_storage_service.py`
  - Verify **no call** to deep-scan services here; only persist to `places_staging` with `status=New`. (WF1 doc)&#x20;

- **Deep Scan queueing mechanism** (find who sets “queued”)

  - Grep for log text: **“Found X places queued for deep scan”** → `src/services/sitemap_scheduler.py` (or similar)
  - In same scheduler, locate the **query** that selects queued places and the **status field name** (e.g., `deep_scan_status` or `scan_state`).
  - In **`places_storage_service`**, look for any line that sets that status on insert/update (or inspect DB triggers/migrations).

- **Deep Scan execution**

  - `src/services/places/places_deep_service.py` (calls Google Place Details & persists).
  - Identify the **model/table** used to save deep details (ID values observed: `18e5e673-…`, `e66c6c93-…`, `106279f6-…`). Document those fields.

- **Domain scheduler**

  - `src/services/domain_scheduler.py` — phases, statuses, and **creation of domain records** from place details with `website_url`.
  - Confirm **WF4→WF5 trigger** (“queued for sitemap analysis”) path.

- **Sitemap submission**

  - `src/services/domain_sitemap_submission_scheduler.py` — batches named “🔍 Starting CORRECTED sitemap analysis batch …”.
  - Confirm it consumes **queued domains** from domain_scheduler.

- **Scheduler registration**

  - `src/scheduler_instance.py` — verify jobs, intervals, and function pointers:

    - `process_pending_jobs` → sitemap/deepscan/domain extraction batch
    - `process_pending_domains`
    - `process_pending_domain_sitemap_submissions`
    - `process_pending_sitemap_imports`
    - `process_page_curation_queue`

- **Auth boundary**

  - Router logs show “Using **JWT validation only (RBAC removed)** for tenant …”. Confirm design (WF1 notes: user identity, not tenant isolation, in router).&#x20;

### 3) Configuration & flags to confirm

- `.env` / `settings.py` for any toggles like:

  - `ENABLE_AUTO_DEEP_SCAN=true` (or similar)
  - `SITEMAP_SCHEDULER_ENABLED=true`
  - `JOB_SERVICE_ENABLED` (logs show “JobService is not initialized…”)

- Verify **Google Maps API key** placement (WF1 config guidance).&#x20;

### 4) Logging & test steps

- Tail logs and trigger a tiny search; you should see the same sequence:

  1. **WF1**: search stored (job id, places_count)
  2. Next minute: `sitemap_scheduler` → “Found N places queued for deep scan”
  3. Deep Scan → “Successfully saved/updated deep scan details … (ID: …)”
  4. Next minutes: `domain_scheduler` → “Found M pending domain(s)” → “queued for sitemap analysis (WF4→WF5 trigger)”
  5. Next run: `Domain Sitemap Submission Scheduler` consumes them.

---

## Documentation to add/update (using the Workflow Canon)

- Create/Update canonical YAMLs and linear steps for:

  - **WF-DeepScan**: **Producer** = `places_staging` rows with `deep_scan_status=Queued` (or equivalent). **Consumer** = Deep Scan service. Output = deep details table + (if website) **domains** table.
  - **WF-DomainMetadata**: Producer = domains with `status=Pending`. Consumer = domain metadata extractor. Output = updated domain rows, enqueue **WF5 Sitemap Submission**.
  - **WF5 Sitemap Submission**: consumes queued domains and submits/monitors sitemap jobs.

Leverage the Canon’s workflow templates & comparison tables to keep these consistent and traceable across UI→API→Services→Models, including producer→consumer handoffs and interface tables.&#x20;

---

## Notable anomaly to log a ticket for

- **17:14:05.998** — `places_storage_service` error:
  `PlacesService.get_by_id() takes 2 positional arguments but 3 were given` (place `ChIJyX1hDUpI0IkR_Prz-yEVG84`).
  → Action: confirm function signature & call site; add unit test; check if any data loss occurred for that one record.

---

## Open questions (for the backend to confirm)

1. **Where exactly is `deep_scan_status` (or equivalent) set to `Queued`?** (storage layer vs DB trigger vs scheduler pass-through)
2. **Is auto-deep-scan intended to be universal** for all new places, or governed by a **feature flag** / user selection?
3. **What table & model store “deep scan details”?** (use the model that produced IDs `18e5e673-…`, `e66c6c93-…`, `106279f6-…`)
4. **What’s the precise schema for domain and sitemap queues** (status enums, batch ids, retry policy)?
5. **Doc alignment:** Update WF1 docs to reference the background linkage, or move the auto-queue logic into a distinct workflow doc with explicit producer→consumer semantics (recommended). &#x20;

---

If you want, I can turn this into a draft canonical YAML for **WF-DeepScan** + a linear-steps doc so your team has a ready-to-review “official” spec.

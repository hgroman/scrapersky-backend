# Work Order: Proactive Domain Existence Check for Local Businesses

**Document ID:** 17-WORK-ORDER-PROACTIVE-DOMAIN-CHECK
**Status:** Proposed Feature Enhancement
**Created:** April 2025
**Author:** Gemini Assistant & User
**Related Patterns/Work Orders:**

- `02-CURATION-DRIVEN-BACKGROUND-PROCESSING-PATTERN.md`
- `03-Work-Order-Local_Business-Row-Select-to-Domain-Table.md`
- `04-Work-Order-Implementation-Details-Local_Business-Domain-Table.md`
- `06-Note-2-Future-Self-Completion-of-Business-2-Domain.md`
- `21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md` (From AI Guides)

## 1. Objective

To implement a background service that proactively checks `local_businesses` records with a `website_url` against the `domains` table. If a corresponding domain already exists, the `local_businesses` record should be flagged, providing valuable information to users during the curation process and potentially streamlining background processing.

## 2. Background & Rationale

Currently, duplicate domain detection happens reactively within the `LocalBusinessToDomainService` _after_ a user sets a `LocalBusiness` status to `Selected`. While this prevents database duplicates, it doesn't inform the user beforehand that a business's domain might already be known to the system.

Implementing a proactive check offers several benefits:

- **Informed Curation:** Users viewing the `local_businesses` data grid could see an indicator (e.g., a flag or different status) showing that the domain is already in the `domains` table. This might influence their decision to select, ignore, or investigate the business further.
- **Improved User Experience:** Provides more context upfront, reducing potential confusion about why a seemingly valid business doesn't result in a _new_ domain entry later.
- **Potential Optimization:** While the existing worker check is still necessary, knowing a domain exists beforehand might allow for future optimizations (though not the primary goal here).

This feature is considered an enhancement and is separate from the initial implementation of the user-triggered curation flow defined in `03-...md` and `04-...md`.

## 3. Requirements

### 3.1 Database Schema Changes

- **`local_businesses` Table:**
  - Add a new boolean column: `is_domain_known BOOLEAN NULL DEFAULT FALSE`.
  - Add an index on this new column: `CREATE INDEX IF NOT EXISTS idx_local_businesses_is_domain_known ON public.local_businesses (is_domain_known);`

### 3.2 Model Changes

- **`src/models/local_business.py`:**
  - Add the corresponding field to the `LocalBusiness` SQLAlchemy model: `is_domain_known: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)` (Adjust type hint/default as needed).

### 3.3 New Background Service/Job

- **Scheduling:** Implement a new scheduled job using APScheduler, following the pattern in `src/services/sitemap_scheduler.py` and `21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md`.
  - The job should run periodically (e.g., daily, hourly - make configurable via environment variables like `PROACTIVE_DOMAIN_CHECK_INTERVAL_MINUTES`).
  - It should process records in batches (configurable batch size `PROACTIVE_DOMAIN_CHECK_BATCH_SIZE`).
- **Target Record Selection:** The job should query the `local_businesses` table for records that meet criteria like:
  - `website_url IS NOT NULL` AND `website_url != ''`
  - `is_domain_known = FALSE` (or `IS NULL`) - Only check records not already flagged.
  - Optionally, filter by `status` (e.g., only check `'New'` records) or `domain_extraction_status` if needed, but checking all unflagged records might be simpler.
  - Use appropriate locking (`with_for_update(skip_locked=True)`) if modifying records directly within the query loop.
- **Processing Logic (Per Record):**
  1.  Extract the domain name from `website_url`. Reuse or adapt the domain extraction logic from `LocalBusinessToDomainService`. Handle potential extraction errors gracefully (log and skip record?).
  2.  Query the `domains` table to check if a record with the extracted `domain` exists.
  3.  If a matching `domain` record **is found**:
      - Update the corresponding `local_businesses` record, setting `is_domain_known = TRUE`.
      - Log this finding (e.g., `INFO: Marked business [ID] as is_domain_known=True based on existing domain [domain_name]`).
  4.  If no matching `domain` record **is found**:
      - Optionally, update `is_domain_known = FALSE` explicitly if it was previously `NULL`.
      - Log this finding (e.g., `DEBUG: Domain for business [ID] not found in domains table. is_domain_known remains False.`).
- **Error Handling:** Implement robust error handling for database operations, domain extraction, etc. Log errors clearly.
- **Logging:** Add comprehensive logging for job start/end, batch processing, records checked, domains found/not found, updates made, and any errors encountered.

### 3.4 Configuration

- Introduce new environment variables for schedule interval and batch size (e.g., `PROACTIVE_DOMAIN_CHECK_INTERVAL_MINUTES`, `PROACTIVE_DOMAIN_CHECK_BATCH_SIZE`). Provide sensible defaults.

## 4. Dependency Tree & Related Tables

- **Primary Tables Involved:**
  - `local_businesses` (Read, Update)
  - `domains` (Read-only)
- **Schema Modifications:**
  - `local_businesses`: Addition of `is_domain_known` column and index.
- **Code Dependencies:**
  - `src/models/local_business.py` (Model update)
  - `src/models/domain.py` (Used for querying)
  - `src/services/sitemap_scheduler.py` (Pattern for new job structure)
  - Domain extraction utility/logic (Potentially from `src/services/business_to_domain_service.py` or a shared utility)
  - `src/db/session.py` (For obtaining DB sessions)

```mermaid
graph TD
    subgraph BackgroundJob["Proactive Domain Check Job"]
        direction LR
        BJ_Start[Start Job] --> BJ_QueryLB(Query local_businesses where website_url IS NOT NULL AND is_domain_known=FALSE)
        BJ_QueryLB -- Records Found --> BJ_Loop(Loop Through Batch)
        BJ_Loop --> BJ_Extract(Extract Domain from website_url)
        BJ_Extract -- Success --> BJ_QueryD(Query domains table for extracted_domain)
        BJ_QueryD -- Domain Found --> BJ_UpdateLB(Update local_businesses SET is_domain_known=TRUE)
        BJ_QueryD -- Domain Not Found --> BJ_LogNotFound(Log Not Found / No Update)
        BJ_Extract -- Error --> BJ_LogError(Log Extraction Error)
        BJ_UpdateLB --> BJ_NextRec(Next Record or End Batch)
        BJ_LogNotFound --> BJ_NextRec
        BJ_LogError --> BJ_NextRec
        BJ_NextRec --> BJ_Loop
        BJ_Loop -- End Batch --> BJ_End(End Job)
        BJ_QueryLB -- No Records --> BJ_End
    end

    subgraph Data
        DB_LB[local_businesses Table\n- website_url (read)\n- is_domain_known (read/write)\n- id (read)]
        DB_D[domains Table\n- domain (read)]
    end

    subgraph Models
       M_LB[LocalBusiness Model\n- Add is_domain_known field]
       M_D[Domain Model]
    end

    subgraph Config
        Conf[Environment Variables\n- Interval\n- Batch Size]
    end

    BackgroundJob --> DB_LB
    BackgroundJob --> DB_D
    BackgroundJob --> M_LB
    BackgroundJob --> M_D
    BackgroundJob --> Conf
```

## 5. Success Definition

- A new background job is created and runs reliably according to its configured schedule.
- The job correctly identifies `local_businesses` records whose `website_url` corresponds to a domain already existing in the `domains` table.
- The `is_domain_known` flag in the `local_businesses` table is accurately updated to `TRUE` for these identified records.
- The job handles records with no `website_url`, domain extraction failures, and domains not found in the `domains` table gracefully without error.
- Logging provides clear visibility into the job's execution and findings.
- The implementation adheres to project standards (ORM usage, session management, logging conventions).

## 6. Implementation Sequence (Suggested)

1.  **Schema Change:** Apply the SQL `ALTER TABLE` command to add the `is_domain_known` column and its index to the `local_businesses` table.
2.  **Model Update:** Update the `src/models/local_business.py` file to include the `is_domain_known` field.
3.  **Service Logic:** Create a new function or class (e.g., in a new file `src/services/proactive_domain_checker.py`) containing the core logic: fetch business, extract domain, check domain table, update business flag. Ensure proper use of asynchronous sessions.
4.  **Scheduler Integration:**
    - Add the new environment variables for configuration.
    - In `src/services/sitemap_scheduler.py` (or potentially a dedicated scheduler file if preferred), define a new asynchronous function for the job (e.g., `process_proactive_domain_checks`).
    - This function should implement the batching, looping, and invocation of the service logic created in step 3.
    - Register this new job function with the APScheduler instance in `main.py` or wherever the scheduler is initialized.
5.  **Testing:** Create unit/integration tests for the new service logic and potentially an end-to-end test simulating the scheduler run.
6.  **Documentation:** Update relevant documentation (e.g., README, potentially AI Guides if patterns change) if necessary.

---

**(End of Proposed Work Order)**

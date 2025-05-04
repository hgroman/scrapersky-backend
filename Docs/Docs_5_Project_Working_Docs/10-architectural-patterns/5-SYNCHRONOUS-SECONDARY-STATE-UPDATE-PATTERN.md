# Architectural Pattern: Synchronous Secondary State Update

**Version:** 1.0
**Date:** 2024-07-27
**Related Patterns:** `02-CURATION-DRIVEN-BACKGROUND-PROCESSING-PATTERN.md`

## 1. Problem Statement

In many systems, updating a primary status field via an API (e.g., setting a curation status like "Selected") should logically trigger an immediate, related state change in a secondary field (e.g., setting a processing status like "Queued"). However, this secondary update might be conditional (e.g., only queue if not already processing).

How can we implement this secondary state update reliably within the same API transaction as the primary update, ensuring atomicity and providing immediate feedback, without relying on a separate background process or polling mechanism just for this simple, direct state transition?

## 2. Solution: Conditional Logic within API Handler Transaction

The solution is to embed the conditional logic for the secondary state update directly within the service method handling the primary API request, ensuring both updates occur within a single atomic database transaction.

1.  **API Endpoint:** Define an API endpoint (typically `PUT` or `PATCH`) that accepts the primary status update.
2.  **Service Method:** The corresponding service method receives the primary update request (e.g., new status, list of IDs).
3.  **Transaction Boundary:** The service method **must** operate within a clear transaction boundary (e.g., using `async with session.begin():` in SQLAlchemy).
4.  **Primary Update:** Perform the primary status update using ORM methods (e.g., `sqlalchemy.update()`).
5.  **Conditional Check:** _Within the same transaction_, check if the conditions for the secondary update are met. This typically involves:
    - Checking the value of the _incoming_ primary status.
    - Potentially fetching or checking the _current_ value of the secondary status field for the affected records (if the update depends on the current state, e.g., "don't queue if already processing").
6.  **Secondary Update:** If the conditions are met, perform the secondary status update using ORM methods.
7.  **API Response:** Design the API response to provide clear feedback on both updates, potentially including counts of records affected by the primary update versus the secondary update (e.g., `updated_count`, `queued_count`).

## 3. Concrete Example: Sitemap Curation Batch Status Update

- **Reference:** Feature `23 - Site Maps New Tab`, specifically `PUT /api/v3/sitemap-files/status`.
- **Problem:** When a user sets the `deep_scrape_curation_status` of one or more `SitemapFile` records to `Selected` via the API, the system should ideally also set their `deep_scrape_process_status` to `Queued` to signal readiness for background processing. However, if a sitemap is _already_ being processed (`deep_scrape_process_status == Processing`), it should not be re-queued.
- **Solution Implemented:**
  - The `PUT /api/v3/sitemap-files/status` endpoint accepts a list of `sitemap_file_ids` and the target `deep_scrape_curation_status`.
  - The service method `SitemapFilesService.update_curation_status_batch` operates within `async with session.begin():`.
  - It first performs the primary update: setting `deep_scrape_curation_status` for all specified IDs.
  - **Conditional Logic:** It then checks if the `new_curation_status` provided in the request is specifically `SitemapDeepCurationStatusEnum.Selected`.
  - **Secondary Update:** If the primary status is `Selected`, it performs a _second_ `update()` statement _within the same transaction_. This statement updates `deep_scrape_process_status` to `SitemapDeepProcessStatusEnum.Queued` **only for those records** where the `id` is in the list AND the current `deep_scrape_process_status` is **not** equal to `SitemapDeepProcessStatusEnum.Processing`.
  - The service uses `RETURNING` clauses or separate counts to determine how many records had their curation status updated (`updated_count`) and how many were actually queued (`queued_count`).
  - The API response includes both `updated_count` and `queued_count`, allowing the frontend to provide precise feedback (e.g., "5 updated, 4 queued (1 already processing)").

## 4. Rationale & Benefits

- **Atomicity:** Ensures that the primary status update and the conditional secondary update either both succeed or both fail together, maintaining data consistency.
- **Immediacy:** The secondary state change happens directly as part of the API call, reducing the latency compared to waiting for a background poller to detect the primary change.
- **Clear Feedback:** Allows the API to return immediate, precise feedback on the outcome of both the primary and secondary updates.
- **Simplicity (for direct transitions):** Avoids the overhead of invoking a separate background task or relying on complex event queueing systems for simple, deterministic state transitions.

## 5. Considerations

- **Transaction Scope:** Keep the logic within the transaction focused. Avoid performing complex, long-running operations (like external API calls) inside the database transaction handling the state updates.
- **Conditional Complexity:** This pattern is best suited for relatively straightforward conditional logic. Very complex rules might be better handled by a dedicated state machine or background process.
- **Performance:** If checking the current secondary status requires querying many records before the second update, consider performance implications and ensure appropriate database indices exist.
- **API Response Design:** Clearly document the meaning of different counts or status flags returned by the API.

## 6. Relationship to Other Patterns

- **`02-CURATION-DRIVEN-BACKGROUND-PROCESSING-PATTERN.md`:** This pattern details a common _technique_ for implementing the initial state transition (e.g., User Action -> Queued) described within the broader Pattern 02 workflow. It provides a synchronous alternative to relying solely on background workers polling for status changes to initiate processing.

# Job Table Architecture Assessment (Google Maps Deep Scan)

## Context

During the implementation of the Google Maps Deep Scan feature (`places_deep_scan`), a review was conducted to determine if the existing `jobs` table architecture was suitable for managing this new type of multi-stage job. The key concerns were:

1.  **Multi-Stage Nature:** The deep scan relies on results from a previous `places_search` (discovery) job.
2.  **Input "Seed":** Unlike previous `sitemap` jobs seeded by a domain, the deep scan is seeded by the ID of the preceding discovery job.
3.  **Multipurpose Table:** Whether the `jobs` table should host distinctly different job types like sitemap scraping and multi-stage API enrichment.

## Investigation

The following tables were inspected using the `scripts/db/inspect_table.py` script:

1.  **`jobs` Table:**

    - **Schema:** Contains `id` (UUID), `tenant_id` (UUID), `status` (Enum), `job_type` (String), `params` (JSONB), `result_data` (JSONB), `progress` (Float), timestamps (`created_at`, `started_at`, `completed_at`), `error_message` (String).
    - **Existing Types:** Already handles various types (`sitemap`, `places_search`, `batch_domain_page_scraper`, etc.).
    - **Analysis:** The `job_type` column allows differentiation. The `params` JSONB column is flexible enough to store the necessary `discovery_job_id` to link the deep scan job to its source discovery job. Status, progress, results, and error handling columns are suitable.

2.  **`places_staging` Table (`Place` Model):**
    - **Schema:** Contains `place_id` (Text, PK), `tenant_id` (UUID), `search_job_id` (UUID, FK to `jobs.id`), `processed` (Boolean, default False), `last_deep_scanned_at` (Timestamp), `status` (Text), and other place details.
    - **Analysis:** The `search_job_id` correctly links staged places to their discovery job. The `processed` flag provides a clear mechanism for the deep scan job to identify which places need processing and to mark them as complete, preventing reprocessing.

## Conclusion

The existing `jobs` table architecture **is suitable** for managing the `places_deep_scan` jobs.

- The table is designed to be multipurpose, distinguished by `job_type`.
- The `params` field adequately handles the different input "seed" (the `discovery_job_id`).
- The `places_staging` table, with its `search_job_id` linkage and `processed` flag, effectively supports the multi-stage workflow by allowing the deep scan job to query and update the status of individual places identified in the discovery phase.

No modifications to the `jobs` or `places_staging` table schemas are required to support the Google Maps Deep Scan feature as designed. Future complex, multi-stage jobs can likely leverage this same pattern.

Here’s a formal backend verification brief you can hand over to your engineering team. It’s structured for **administration, enhancement, maintenance, and extension** of the deep-scan pipeline.

---

# Verification Brief: Deep Scan Job Reporting

**Executive Summary**
The deep scan job reporting pipeline was previously incomplete, showing partial lifecycle information and unclear success attribution. After recent corrections, logs now provide a complete chain of evidence for each place processed:

1. Job initiation (with `place_id` and `tenant_id`)
2. Job creation (unique `job_id`)
3. Database persistence (unique `details_id`)
4. Job completion (success/failure outcome)
5. Scheduler acknowledgment (per-place success + batch totals)

**Goal:** Verify each step across code and database layers, document the flow, and ensure future administrators can enhance, maintain, and extend this process without ambiguity.

---

## Step-by-Step Breakdown

### 1. Job Initiation

- **Log Example:**

  ```
  2025-09-10 19:31:19,640 - src.services.places.places_deep_service - INFO - Processing single deep scan for place_id: ChIJrSHr2CnfxIkRyohgkTJFUvI, tenant_id: 550e8400-e29b-41d4-a716-446655440000
  ```

- **Data Points:**

  - `place_id` uniquely identifies Google Maps entity
  - `tenant_id` ties to customer scope

**Verification:** Confirm `places_deep_service` receives correct parameters from `sitemap_scheduler`.

---

### 2. Job Creation

- **Log Example:**

  ```
  2025-09-10 19:31:19,806 - ... - INFO - Created deep scan job 2edd036a-d70f-4198-a08e-04d722a82554 for place_id: ChIJrSHr2CnfxIkRyohgkTJFUvI
  ```

- **Data Points:**

  - `job_id` UUID generated per scan

**Verification:** Check jobs table (or task queue) contains this UUID with `status=Pending` and references `place_id`.

---

### 3. Database Persistence

- **Log Example:**

  ```
  2025-09-10 19:31:22,428 - ... - INFO - Successfully saved/updated deep scan details for place_id: ... (ID: c8b63e24-eacc-42a6-87df-1a83788946ad)
  ```

- **Data Points:**

  - `details_id` = record in places_deep_scan_results (or equivalent table)
  - Should reference both `place_id` and `tenant_id`

**Verification:** Query deep scan results table for `details_id` and confirm data persisted at logged time.

---

### 4. Job Completion

- **Log Example:**

  ```
  2025-09-10 19:31:22,691 - ... - INFO - Deep scan job 2edd036a-d70f-4198-a08e-04d722a82554 completed successfully
  ```

- **Data Points:**

  - `job_id` transitions to `Completed` state
  - Exit code = Success

**Verification:** Confirm job record in DB or queue updated to `Completed` with timestamps.

---

### 5. Scheduler Acknowledgment

- **Log Example:**

  ```
  2025-09-10 19:31:22,692 - src.services.sitemap_scheduler - INFO - Deep Scan: Success for Place ID: ChIJrSHr2CnfxIkRyohgkTJFUvI
  ```

- **Batch Summary:**

  ```
  2025-09-10 19:31:41,965 - ... - DEBUG - Deep Scans: Processed=20, Successful=20
  ```

- **Data Points:**

  - Scheduler logs now explicitly confirm per-place success
  - Aggregate counters reconcile with number of jobs

**Verification:** Cross-check count of job completions against batch summary totals.

---

## Sample Verified Records (from logs)

| Timestamp           | place_id                    | job_id                               | details_id                           | Status    |
| ------------------- | --------------------------- | ------------------------------------ | ------------------------------------ | --------- |
| 2025-09-10 19:31:19 | ChIJrSHr2CnfxIkRyohgkTJFUvI | 2edd036a-d70f-4198-a08e-04d722a82554 | c8b63e24-eacc-42a6-87df-1a83788946ad | Completed |
| 2025-09-10 19:31:22 | ChIJ7Q2tKtfexIkRT2a4IOt9D2M | 5963cd46-7e86-4154-8b6e-190a6d44193d | f595e3a3-76c2-421b-abeb-32e51dced8d2 | Completed |
| 2025-09-10 19:31:24 | ChIJRf0LVMHexIkRBezdIczoCkA | 85b69932-bff1-4098-b79c-56dee64d23e0 | 65aa2de1-3770-4481-b533-120eb9ca8a13 | Completed |
| 2025-09-10 19:31:26 | ChIJg-bbh5TZxIkRbOOjP6dOwpg | 0248228b-24ea-4c3d-94fc-0d3d1507f25b | 9489c68b-13c3-4b3a-9c7a-15e94194feec | Completed |
| 2025-09-10 19:31:28 | ChIJn9y5DSrfxIkRbLk-SNlk9EI | ae91f02f-08b5-49cd-ba44-3ad2a228af4b | d5f245e0-a90c-4c41-b161-0cfc370d36e1 | Completed |
| 2025-09-10 19:31:29 | ChIJPX5xsGggxYkRTt0o2T6Iihs | 085ef36a-f2e1-4a75-96bc-ebc90dc193ff | 6543350c-f6d5-4f5e-8fc1-914a3f068e7f | Completed |
| 2025-09-10 19:31:31 | ChIJn9y5DSrfxIkRoYEe9cGZdV0 | 757d7d30-eab8-4c0e-adf3-c4fecf92549a | fab980a8-39cd-4eda-9502-e70b003a77e2 | Completed |
| 2025-09-10 19:31:33 | ChIJn9y5DSrfxIkR7Cs4SCpS7ug | 74f1be95-716c-4631-b0ec-26ea2a268b0e | 47267e91-09ce-4654-9747-2f11909f50eb | Completed |
| 2025-09-10 19:31:35 | ChIJn9y5DSrfxIkRBIfs5gYpnjA | 3d9a8048-863c-4338-8b89-62970a83697a | 6d2ca7ed-2c0d-4984-82d3-ffec5a93fa70 | Completed |

---

## Verification Tasks for Backend Team

1. **Code Path Review**

   - Trace calls from `sitemap_scheduler` → `places_deep_service`.
   - Verify creation of job objects and persistence logic.
   - Confirm error handling paths update job state to `Failed`.

2. **Database Review**

   - Validate `jobs` table entries exist for each `job_id`.
   - Validate `deep_scan_results` entries exist for each `details_id`.
   - Ensure referential integrity with `place_id` and `tenant_id`.

3. **Scheduler Consistency**

   - Confirm aggregate counters (`Processed` and `Successful`) reconcile with completed jobs in DB.
   - Test with artificial failures to confirm error paths are logged and counted.

4. **Documentation Requirement**

   - Document schema for jobs and results tables.
   - Document code modules:

     - `src.services.places.places_deep_service`
     - `src.services.sitemap_scheduler`

   - Add runbook for verifying success/failure for any given `place_id`.

---

✅ **Conclusion:** The reporting fix is confirmed. Each job now has traceable identifiers across logs, DB, and scheduler. The backend team should verify with DB queries and code path reviews, then finalize documentation so this pipeline is fully supportable.

---

Do you want me to also prepare a **database query cheat sheet** (Postgres SQL snippets) that your backend can run directly to verify job_ids and details_ids from the logs?

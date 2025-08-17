## WF7 Testing Guide: From Trigger to Table

This document outlines the step-by-step process to test the WF7 "Extractor" workflow, from triggering the process via its API endpoint to verifying its output in the database.

---

### **1. Prerequisites**

Before you begin testing, ensure the following are in place:

*   **Running ScraperSky Backend:** Your application must be running and accessible (e.g., on Render.com or locally).
*   **Valid JWT Token:** You will need an active JWT token for authentication. This token should have the necessary permissions to interact with the `/api/v2/pages/status` endpoint.
*   **Existing `Page` Record:** You must have at least one `Page` record in your database. This `Page` record should have a valid `url` field, as the `PageCurationService` will attempt to crawl it. You will need its `id` (UUID).
*   **Database Access:** You will need a way to query your PostgreSQL database (e.g., `psql` client, Supabase Studio, DBeaver, or any other preferred tool).

---

### **2. Step-by-Step Testing Protocol**

#### **Step 2.1: Trigger WF7 via API (Queue a Page)**

This step uses the V2 API endpoint to mark a `Page` as "Selected" for curation, which automatically queues it for background processing.

*   **Endpoint:** `PUT /api/v2/pages/status`
*   **Authentication:** `Authorization: Bearer <YOUR_JWT_TOKEN>` header.
*   **Content-Type:** `application/json`
*   **Action:** Send a `PUT` request with the `id` of an existing `Page` record and set its status to `"Selected"`.

**Example `curl` Command (replace placeholders):**

```bash
curl -X PUT 'https://<YOUR_RENDER_URL>/api/v2/pages/status' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer <YOUR_JWT_TOKEN>' \
-d '{
  "page_ids": [
    "<A_REAL_PAGE_ID_FROM_YOUR_DB>"
  ],
  "status": "Selected"
}'
```

*   **Expected API Response:**
    *   **Status Code:** `200 OK`
    *   **Body:** `{"updated_count": 1, "queued_count": 1}` (or more if you provided multiple IDs).

---

#### **Step 2.2: Monitor Background Processing**

Once the API call is successful, the `Page` record's `page_processing_status` will be `Queued`. The `page_curation_scheduler` will then pick it up.

1.  **Check Application Logs:**
    *   Monitor the logs of your running ScraperSky backend (e.g., `docker-compose logs -f scrapersky` if local, or your Render.com logs).
    *   Look for log messages from `page_curation_scheduler.py` and `page_curation_service.py`. You should see messages indicating:
        *   "Starting page curation queue processing cycle."
        *   "Starting curation for page_id: <your_page_id>"
        *   Messages related to `DomainContentExtractor` (crawling the URL).
        *   "Successfully created and added placeholder contact for page <your_page_id>"
        *   "Finished page curation queue processing cycle."

2.  **Query the `pages` Table (Database):**
    *   Immediately after the API call, query the `pages` table for your `page_id`:
        ```sql
        SELECT id, url, page_curation_status, page_processing_status, page_processing_error, updated_at
        FROM pages
        WHERE id = '<A_REAL_PAGE_ID_FROM_YOUR_DB>';
        ```
    *   **Expected Status Progression:**
        *   Initially, `page_curation_status` should be `Selected`, and `page_processing_status` should be `Queued`.
        *   After the scheduler picks it up, `page_processing_status` should change to `Processing`.
        *   Upon completion (success or error), `page_processing_status` should change to `Complete` or `Error`.

---

#### **Step 2.3: Verify Output in `contacts` Table**

If the `PageCurationService` successfully processed the page, it will have created a new `Contact` record.

1.  **Query the `contacts` Table (Database):**
    *   After the scheduler logs indicate successful processing (or the `pages` table shows `Complete` status), query the `contacts` table:
        ```sql
        SELECT id, page_id, name, email, phone_number, created_at
        FROM contacts
        WHERE page_id = '<A_REAL_PAGE_ID_FROM_YOUR_DB>';
        ```
    *   **Expected Output:** You should see a new row with `page_id` matching your test page, and the placeholder contact details (`Placeholder Name`, `placeholder@example.com`, `123-456-7890`).

---

### **3. Troubleshooting Tips**

*   **API Call Fails (non-200 response):**
    *   Check your JWT token for validity and expiration.
    *   Verify the `page_ids` are correct UUIDs and exist in the database.
    *   Ensure the `status` enum value is correctly spelled and capitalized (`"Selected"`).
    *   Check the backend logs for any immediate errors from the router.

*   **Page Stuck in `Queued` or `Processing`:**
    *   Verify the `page_curation_scheduler` is running and registered in `main.py`.
    *   Check the scheduler logs for any errors during its processing cycle.
    *   Ensure the `PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES` in `settings.py` is set to a reasonable value (e.g., 1 or 5 minutes).
    *   Check for any errors from the `PageCurationService` or `DomainContentExtractor` in the logs.

*   **No Contact Record Created:**
    *   Confirm the `page_processing_status` for the page is `Complete` (not `Error`).
    *   Review the `PageCurationService` logs for any errors during the contact creation step.
    *   Ensure the `DomainContentExtractor` successfully retrieved content (check logs for warnings about no content).

---

This guide provides a comprehensive approach to testing WF7. By following these steps, you can confirm the successful operation of the workflow.
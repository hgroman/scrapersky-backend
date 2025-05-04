# BATCH DOMAIN SCANNER HTML INTEGRATION WORK ORDER

**Document ID:** 07-43-BATCH-DOMAIN-SCANNER-HTML-INTEGRATION-WORK-ORDER
**Date:** 2025-03-27
**Author:** System Engineer
**Status:** Draft

## 1. Overview

The ScraperSky backend has robust batch page scraper API endpoints (`/api/v3/batch_page_scraper/*`) designed specifically for batch processing of multiple domains. However, the current HTML interface for batch domain scanning (`batch-domain-scanner.html`) does not properly utilize these batch endpoints, instead making individual scan requests for each domain. This work order details the steps required to enhance the HTML interface to leverage the batch API functionality properly, ensuring that users can submit batch jobs and view results efficiently through the web interface.

## 2. Current State Analysis

### 2.1 API Endpoints

| Endpoint                                             | Method | Purpose                        | Status      |
| ---------------------------------------------------- | ------ | ------------------------------ | ----------- |
| `/api/v3/batch_page_scraper/scan`                    | POST   | Scan a single domain           | Implemented |
| `/api/v3/batch_page_scraper/status/{job_id}`         | GET    | Get status of a single job     | Implemented |
| `/api/v3/batch_page_scraper/batch`                   | POST   | Create a batch of domain scans | Implemented |
| `/api/v3/batch_page_scraper/batch/{batch_id}/status` | GET    | Get status of a batch job      | Implemented |

### 2.2 HTML Interface Issues (`batch-domain-scanner.html`)

1. **Inefficient API Usage**: Currently processes domains individually using `/scan` endpoint instead of using the batch endpoint.
2. **Status Tracking**: Polls individual job statuses instead of using the batch status endpoint.
3. **Result Viewing**: Limited result viewing functionality compared to the single domain scanner.
4. **Error Handling**: Basic error handling for API responses.

### 2.3 Reference Implementation

The single domain scanner (`single-domain-scanner.html`) has well-developed functionality for:

- Submitting scan requests
- Polling for status updates
- Displaying detailed results

While it uses different API endpoints (`/api/v3/modernized_page_scraper/*`), its result viewing patterns and UI components can be adapted for the batch context.

## 3. Implementation Requirements

### 3.1 Batch Submission

Replace the current domain-by-domain submission with a single batch request:

```javascript
async function submitBatch(
  domains,
  tenantId,
  maxPages = 100,
  maxConcurrent = 5
) {
  try {
    const response = await fetch("/api/v3/batch_page_scraper/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer scraper_sky_2024",
        "X-Tenant-ID": tenantId,
      },
      body: JSON.stringify({
        domains: domains,
        max_pages: maxPages,
        max_concurrent_jobs: maxConcurrent,
        tenant_id: tenantId,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail?.message || "Failed to create batch");
    }

    return data; // Contains batch_id and status_url
  } catch (error) {
    console.error("Error creating batch:", error);
    throw error;
  }
}
```

### 3.2 Batch Status Polling

Implement polling for the batch status endpoint:

```javascript
async function pollBatchStatus(batchId, tenantId) {
  try {
    const response = await fetch(
      `/api/v3/batch_page_scraper/batch/${batchId}/status`,
      {
        headers: {
          Authorization: "Bearer scraper_sky_2024",
          "X-Tenant-ID": tenantId,
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail?.message || "Failed to get batch status");
    }

    return data;
  } catch (error) {
    console.error("Error polling batch status:", error);
    throw error;
  }
}
```

### 3.3 Results Display

Enhance the results table to show:

- Overall batch progress
- Individual domain statuses
- Details view for completed domains (adapting the visualization pattern from single-domain-scanner.html)

### 3.4 Error Handling

Improve error handling to:

- Display structured error messages from the API
- Handle common failure scenarios
- Provide clear user feedback

## 4. Implementation Plan

### 4.1 Phase 1: Batch Submission

1. Update domain import and validation functions (keeping existing code)
2. Implement batch submission to replace individual scan calls
3. Add progress initialization based on batch size

### 4.2 Phase 2: Status Tracking

1. Implement batch status polling
2. Update UI to show overall batch progress
3. Map batch domain statuses to the results table

### 4.3 Phase 3: Results Display

1. Adapt the result viewing pattern from single-domain-scanner.html
2. Implement details view for completed domains
3. Add export functionality for batch results

### 4.4 Phase 4: Testing and Refinement

1. Test with various domain inputs
2. Test error scenarios
3. Optimize performance for large batches

## 5. Code Changes

### 5.1 Replace Domain Processing Loop

```javascript
// Current implementation processes each domain individually
async function processBatch() {
  const batch = domains.slice(currentIndex, currentIndex + batchSize);
  currentIndex += batchSize;

  const promises = batch.map((domain) => scanDomain(domain, tenantId));
  await Promise.all(promises);

  if (currentIndex < domains.length) {
    processBatch();
  }
}
```

Replace with:

```javascript
// New implementation submits all domains as a batch
async function processBatch() {
  try {
    const batchResponse = await submitBatch(
      domains,
      tenantId,
      maxPages,
      maxConcurrentJobs
    );
    const batchId = batchResponse.batch_id;

    // Initialize batch status tracking
    initializeBatchStatus(batchId, domains.length);

    // Start polling for batch status
    pollBatchStatus(batchId, tenantId);
  } catch (error) {
    displayError(`Failed to submit batch: ${error.message}`);
  }
}
```

### 5.2 Update Results Table

```javascript
function updateResultsTable(batchStatus) {
  const tbody = document.getElementById("resultsTable");
  const domainStatuses = batchStatus.domain_statuses || {};

  // Clear existing rows if this is first update
  if (tbody.getAttribute("data-batch-id") !== batchStatus.batch_id) {
    tbody.innerHTML = "";
    tbody.setAttribute("data-batch-id", batchStatus.batch_id);
  }

  // Update progress indicators
  document.getElementById("progressBar").style.width = `${
    batchStatus.progress * 100
  }%`;
  document.getElementById("progressText").textContent = `${Math.round(
    batchStatus.progress * 100
  )}%`;

  // Create or update rows for each domain
  Object.entries(domainStatuses).forEach(([domain, status]) => {
    let row = document.querySelector(`tr[data-domain="${domain}"]`);

    if (!row) {
      row = document.createElement("tr");
      row.setAttribute("data-domain", domain);
      tbody.appendChild(row);
    }

    const statusBadge = getStatusBadge(status.status);
    const viewButton =
      status.status === "completed"
        ? `<button class="btn btn-sm btn-outline-primary view-details" data-domain="${domain}" data-job-id="${status.job_id}">View Details</button>`
        : "-";

    row.innerHTML = `
      <td>${domain}</td>
      <td>${statusBadge}</td>
      <td>${status.job_id || "-"}</td>
      <td>${viewButton}</td>
    `;
  });

  // Attach event listeners to view buttons
  attachViewDetailsListeners();
}
```

### 5.3 Add Result Viewing Functionality

Adapt the result viewing pattern from single-domain-scanner.html:

```javascript
// View domain details (adapted from single-domain-scanner.html)
async function viewDomainDetails(jobId) {
  try {
    const response = await fetch(`/api/v3/batch_page_scraper/status/${jobId}`, {
      headers: {
        Authorization: "Bearer scraper_sky_2024",
        "X-Tenant-ID": tenantId,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail?.message || "Failed to get job details");
    }

    // Display the job details in the details section
    document.getElementById("domainDetails").textContent = JSON.stringify(
      data,
      null,
      2
    );
  } catch (error) {
    console.error("Error fetching job details:", error);
    document.getElementById(
      "domainDetails"
    ).textContent = `Error: ${error.message}`;
  }
}

// Attach event listeners to view buttons
function attachViewDetailsListeners() {
  document.querySelectorAll(".view-details").forEach((button) => {
    button.addEventListener("click", function () {
      const jobId = this.getAttribute("data-job-id");
      if (jobId) {
        viewDomainDetails(jobId);
      }
    });
  });
}
```

## 6. Future Enhancements

The following features should be considered for future development:

1. **Batch Configuration**: Allow users to configure advanced batch parameters
2. **Results Export**: Add functionality to export batch results in CSV/JSON
3. **Batch Management**: Interface for viewing historical batches
4. **Real-time Updates**: Implement WebSockets for real-time status updates

## 7. Success Criteria

The integration will be considered successful when:

1. Users can import domains via CSV or text input
2. Domains are submitted as a batch using the `/api/v3/batch_page_scraper/batch` endpoint
3. Batch progress is displayed accurately
4. Individual domain results can be viewed using the pattern adapted from the single domain scanner
5. Errors are handled gracefully with clear user feedback

## 8. References

1. API Documentation: `/api/v3/batch_page_scraper/*`
2. Result Viewing Pattern: `/static/single-domain-scanner.html`
3. Batch Scraper Dependency Map: [07-50-ScraperSky Batch Scraper Dependency Map.md](/project-docs/07-database-connection-audit/07-50-ScraperSky Batch Scraper Dependency Map.md)
4. Architecture Framework: [07-51-ScraperSky Architectural Audit & Design Framework.md](/project-docs/07-database-connection-audit/07-51-ScraperSky Architectural Audit & Design Framework.md)

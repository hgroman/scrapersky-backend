# Contact Endpoint Implementation Guide & Post-Mortem

## 1. Post-Mortem

The initial goal was to create a fully-featured CRUD endpoint for the `contacts` table. The implementation process involved a rigorous research and verification phase where the initial work order was found to be inconsistent with the actual requirements and existing codebase.

Key steps in the process included:
- **Correcting the Work Order:** The work order was iteratively updated to reflect the true requirements, such as the need for full CRUD functionality instead of just batch operations.
- **Evidence-Based Updates:** All corrections to the work order were supported by direct evidence from the codebase or user commands.
- **Debugging the Environment:** The Docker build process was debugged and corrected to include missing development dependencies and fix syntax errors.
- **Final Implementation:** The final code was written according to the bulletproofed work order, following established project patterns.

## 2. Front-End Implementation Guide

This guide details how to interact with the new API for managing contacts.

**Base URL:** `/api/v3/contacts`

**Authentication:** All endpoints are protected. You must include a valid JWT in the request header:
`Authorization: Bearer <YOUR_JWT_TOKEN>`

---

### Endpoints

#### 1. List Contacts

- **Endpoint:** `GET /`
- **Description:** Retrieves a paginated list of contacts. Supports filtering and sorting.
- **Query Parameters:**
  - `limit: int` (default: 100)
  - `offset: int` (default: 0)
  - `contact_curation_status: string` (e.g., "New", "Queued")
  - `contact_processing_status: string` (e.g., "Complete")
  - `hubspot_sync_status: string`
  - `email_type: string` (e.g., "CORPORATE", "FREE")
  - `domain_id: string` (UUID)
  - `page_id: string` (UUID)
  - `email_contains: string`
  - `name_contains: string`
  - `has_gmail: boolean`
- **Success Response:** `200 OK` with a list of `ContactRead` objects.

#### 2. Create Contact

- **Endpoint:** `POST /`
- **Description:** Creates a single new contact record.
- **Request Body:** `ContactCreate` object.
- **Success Response:** `201 CREATED` with the newly created `ContactRead` object.

#### 3. Get Single Contact

- **Endpoint:** `GET /{contact_id}`
- **Description:** Retrieves a single contact by its ID.
- **Path Parameter:** `contact_id: string` (UUID)
- **Success Response:** `200 OK` with a `ContactRead` object.
- **Error Response:** `404 Not Found`

#### 4. Update Contact

- **Endpoint:** `PUT /{contact_id}`
- **Description:** Updates a single contact. All fields in the body are optional (partial update).
- **Path Parameter:** `contact_id: string` (UUID)
- **Request Body:** `ContactUpdate` object.
- **Success Response:** `200 OK` with the updated `ContactRead` object.

#### 5. Delete Contact

- **Endpoint:** `DELETE /{contact_id}`
- **Description:** Deletes a single contact.
- **Path Parameter:** `contact_id: string` (UUID)
- **Success Response:** `204 No Content`

#### 6. Batch Update by ID

- **Endpoint:** `PUT /status`
- **Description:** Updates the `contact_curation_status` for a specific list of contacts.
- **Request Body:** `ContactCurationBatchStatusUpdateRequest` object.
- **Success Response:** `200 OK` with a `ContactCurationBatchUpdateResponse` object.

#### 7. Batch Update by Filter ("Select All")

- **Endpoint:** `PUT /status/filtered`
- **Description:** Updates the `contact_curation_status` for all contacts that match a given set of filters.
- **Request Body:** `ContactCurationFilteredUpdateRequest` object.
- **Success Response:** `200 OK` with a `ContactCurationBatchUpdateResponse` object.

---

### TypeScript Interfaces (Data Schemas)

Here are the TypeScript interfaces corresponding to the API schemas.

```typescript
// Enums (as string literals)
export type ContactCurationStatus = "New" | "Queued" | "Processing" | "Complete" | "Error" | "Skipped";
export type ContactEmailTypeEnum = "SERVICE" | "CORPORATE" | "FREE" | "UNKNOWN";
export type ContactProcessingStatus = "Queued" | "Processing" | "Complete" | "Error";
export type HubSpotSyncStatus = "New" | "Queued" | "Processing" | "Complete" | "Error" | "Skipped";
export type HubSpotProcessingStatus = "Queued" | "Processing" | "Complete" | "Error";

// Main interface for displaying a contact
export interface ContactRead {
    id: string; // UUID
    created_at: string; // ISO DateTime
    updated_at: string; // ISO DateTime
    email: string;
    email_type?: ContactEmailTypeEnum;
    has_gmail?: boolean;
    context?: string;
    source_url?: string;
    name?: string;
    phone_number?: string;
    domain_id: string; // UUID
    page_id: string; // UUID
    source_job_id?: string; // UUID
    contact_curation_status: ContactCurationStatus;
    contact_processing_status?: ContactProcessingStatus;
    contact_processing_error?: string;
    hubspot_sync_status: HubSpotSyncStatus;
    hubspot_processing_status?: HubSpotProcessingStatus;
    hubspot_processing_error?: string;
}

// For creating a new contact
export interface ContactCreate {
    email: string;
    email_type?: ContactEmailTypeEnum;
    has_gmail?: boolean;
    context?: string;
    source_url?: string;
    name?: string;
    phone_number?: string;
    domain_id: string; // UUID
    page_id: string; // UUID
    source_job_id?: string; // UUID
}

// For updating a contact (all fields optional)
export interface ContactUpdate {
    email?: string;
    email_type?: ContactEmailTypeEnum;
    has_gmail?: boolean;
    context?: string;
    source_url?: string;
    name?: string;
    phone_number?: string;
    contact_curation_status?: ContactCurationStatus;
    contact_processing_status?: ContactProcessingStatus;
    contact_processing_error?: string;
    hubspot_sync_status?: HubSpotSyncStatus;
    hubspot_processing_status?: HubSpotProcessingStatus;
    hubspot_processing_error?: string;
}

// For batch updating by a list of IDs
export interface ContactCurationBatchStatusUpdateRequest {
    contact_ids: string[]; // List of UUIDs
    status: ContactCurationStatus;
}

// For batch updating by a filter
export interface ContactCurationFilteredUpdateRequest {
    status: ContactCurationStatus;
    // Filter fields (all optional)
    contact_curation_status?: ContactCurationStatus;
    contact_processing_status?: ContactProcessingStatus;
    hubspot_sync_status?: HubSpotSyncStatus;
    email_type?: ContactEmailTypeEnum;
    domain_id?: string; // UUID
    page_id?: string; // UUID
    email_contains?: string;
    name_contains?: string;
    has_gmail?: boolean;
}

// Response from batch update operations
export interface ContactCurationBatchUpdateResponse {
    updated_count: number;
    queued_count: number;
    hubspot_queued_count: number;
}
```

# Architectural Pattern: Frontend Lookup for Backend Identifiers

**Version:** 1.0
**Date:** 2023-10-27

## 1. Problem Statement

Often, user interfaces require users to filter or select items based on human-readable names (e.g., a domain name, a category name), but the corresponding backend API endpoint requires a technical identifier (e.g., a UUID like `domain_id`) for efficient and precise database operations. Directly exposing UUIDs in the UI is poor user experience, and having the primary backend endpoint perform name-to-ID translation adds complexity and potential ambiguity.

## 2. Solution: Frontend-Driven Lookup and ID Mapping

The preferred solution is to decouple the user selection from the backend API call using a frontend-driven lookup mechanism:

1.  **UI Interaction:** The user interacts with a UI element designed for selecting the human-readable entity (e.g., a text input with type-ahead/autocomplete, a dropdown).
2.  **Frontend Lookup:** As the user interacts (e.g., types in the input), the frontend JavaScript calls a **separate, dedicated lookup API endpoint**. This endpoint is designed specifically to search for the entity by its human-readable attribute (e.g., `name_contains`, `label_like`) and returns a list of matching entities, including both their human-readable names **and** their technical identifiers (UUIDs).
3.  **User Selection:** The user selects the desired item from the suggestions provided by the lookup.
4.  **ID Storage:** The frontend JavaScript stores the technical identifier (UUID) associated with the user's selection.
5.  **Primary API Call:** When the user triggers the main action (e.g., applies filters, saves a form), the frontend JavaScript sends the **stored technical identifier (UUID)** to the primary backend API endpoint, which is designed to accept this ID directly.

## 3. Concrete Example: Sitemap Curation Domain Filter (Ref: `23.5`)

- **Problem:** The "Sitemap Curation" tab needs to allow users to filter sitemap files by domain. Users know domain names (e.g., "example.com"), but the `GET /api/v3/sitemap-files/` endpoint requires the `domain_id` (UUID) for efficient filtering.
- **Solution Implemented:**
  - The UI provides a text input field labeled "Domain" with type-ahead functionality.
  - As the user types, the frontend calls `GET /api/v3/domains/?name_contains=<user_input>` (assuming this endpoint exists).
  - This lookup endpoint returns matching domain names and their UUIDs (e.g., `[{ "domain": "example.com", "id": "UUID_HERE" }]`).
  - The user selects "example.com" from the suggestions.
  - The frontend stores `"UUID_HERE"`.
  - When the user clicks "Apply Filters", the frontend calls `GET /api/v3/sitemap-files/?domain_id=UUID_HERE&...`.
  - The `GET /api/v3/sitemap-files/` endpoint receives the precise `domain_id` and performs its filtering logic cleanly.

## 4. Rationale & Benefits

- **Decoupling:** Separates the user interaction concern (finding the right item by name) from the backend operation concern (filtering/acting by ID).
- **Clean Backend Endpoints:** Primary endpoints remain simple and efficient, dealing directly with specific IDs.
- **Improved User Experience:** Provides modern UI interactions like type-ahead, hiding technical details (UUIDs) from the user.
- **Reusability:** The lookup endpoint (`GET /api/v3/domains/`) can potentially be reused by other parts of the application.
- **Reduced Ambiguity:** Avoids issues with partial name matches or multiple results being handled within the primary endpoint's logic.

## 5. Considerations

- **Lookup Endpoint Requirement:** This pattern necessitates the existence (or creation) of a dedicated API endpoint for performing the name-based lookup and returning associated IDs. This endpoint should support appropriate filtering (e.g., `name_contains`, `startswith`) and pagination if necessary.
- **Frontend Complexity:** Adds complexity to the frontend JavaScript to handle the type-ahead logic, API call, and storing the selected ID. Frameworks or libraries can often simplify this (e.g., Select2, Autocomplete components).

# Google Maps API Frontend Integration

This document provides technical details for integrating with the Google Maps API endpoints in the ScraperSky backend.

## Base URL

```
http://localhost:8000
```

Replace with your actual deployment URL in production.

## Authentication

All endpoints require a Bearer token for authentication:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Search Places

Initiates a search for places using the Google Maps API. This is an asynchronous operation that returns a job ID.

**Endpoint:** `/api/v3/google_maps_api/search`
**Method:** POST
**Content-Type:** application/json

**Request Body:**

```json
{
  "business_type": "restaurant", // Type of business to search for
  "location": "Burlington, Vermont", // Location to search in
  "radius_km": 10 // Search radius in kilometers (optional, default: 10)
}
```

**Response:**

```json
{
  "job_id": "82b72d9f-bf8d-4360-8ce9-468e33c22c7d",
  "status": "pending",
  "status_url": "/api/v3/google_maps_api/status/82b72d9f-bf8d-4360-8ce9-468e33c22c7d"
}
```

The `status_url` field provides the path to check the job status.

### 2. Check Search Status

Checks the status of a previously initiated search job.

**Endpoint:** `/api/v3/google_maps_api/status/{job_id}`
**Method:** GET

**URL Parameters:**

- `job_id`: The ID of the job to check status for

**Response:**

```json
{
  "job_id": "82b72d9f-bf8d-4360-8ce9-468e33c22c7d",
  "status": "completed", // Can be "pending", "processing", "completed", or "failed"
  "progress": 1.0, // Progress indicator from 0.0 to 1.0
  "created_at": "2025-03-20T04:22:28.839768",
  "updated_at": "2025-03-20T04:22:30.176687",
  "error": null, // Error message if status is "failed"
  "search_query": "restaurant",
  "search_location": "Burlington, Vermont",
  "user_id": "dev-admin-id",
  "user_name": "Unknown User",
  "total_places": 20, // Total places found in the search
  "stored_places": 20 // Number of places successfully stored
}
```

### 3. Get Staging Places

Retrieves places from the staging table, which stores the results of previous searches.

**Endpoint:** `/api/v3/google_maps_api/staging`
**Method:** GET

**Query Parameters:**

- `tenant_id`: (optional) Filter by tenant ID
- `status`: (optional) Filter by status ("new", "approved", "rejected", etc.)
- `limit`: (optional) Maximum number of results to return (default: 100, max: 1000)
- `offset`: (optional) Pagination offset (default: 0)

**Response:**

```json
{
  "places": [
    {
      "id": "123",
      "place_id": "ChIJZ_YISduAhYARCEq5Bul0bHA",
      "name": "Restaurant Name",
      "formatted_address": "123 Main St, Burlington, VT 12345, USA",
      "business_type": "restaurant",
      "latitude": 44.4759,
      "longitude": -73.2121,
      "vicinity": "123 Main St",
      "rating": 4.5,
      "user_ratings_total": 123,
      "price_level": 2,
      "status": "new",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
      "search_query": "restaurant",
      "search_location": "Burlington, Vermont",
      "search_time": "2025-03-20T04:22:29.123456",
      "created_at": "2025-03-20T04:22:29.123456",
      "updated_at": "2025-03-20T04:22:29.123456"
    }
    // Additional place objects...
  ],
  "total_count": 20,
  "limit": 100,
  "offset": 0
}
```

### 4. Update Place Status

Updates the status of a place in the staging table.

**Endpoint:** `/api/v3/google_maps_api/update-status`
**Method:** POST

**Query Parameters:**

- `place_id`: The Google Place ID to update
- `status`: The new status (e.g., "approved", "rejected")

**Response:**

```json
{
  "id": "123",
  "place_id": "ChIJZ_YISduAhYARCEq5Bul0bHA",
  "name": "Restaurant Name",
  "status": "approved"
  // Other place fields...
}
```

### 5. Batch Update Status

Updates the status of multiple places in a single request.

**Endpoint:** `/api/v3/google_maps_api/batch-update-status`
**Method:** POST
**Content-Type:** application/json

**Request Body:**

```json
{
  "status_updates": [
    {
      "place_id": "ChIJZ_YISduAhYARCEq5Bul0bHA",
      "status": "approved"
    },
    {
      "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
      "status": "rejected"
    }
  ]
}
```

**Response:**

```json
{
  "success": 2,
  "failed": 0,
  "errors": []
}
```

## Frontend Integration Example

### React Example with Fetch API

```tsx
import { useState, useEffect } from "react";

// Define types
interface PlacesSearchRequest {
  business_type: string;
  location: string;
  radius_km?: number;
}

interface PlacesSearchResponse {
  job_id: string;
  status: string;
  status_url: string;
}

interface PlaceStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  error: string | null;
  total_places: number;
  stored_places: number;
}

interface Place {
  id: string;
  place_id: string;
  name: string;
  formatted_address?: string;
  business_type?: string;
  latitude?: number;
  longitude?: number;
  vicinity?: string;
  rating?: number;
  user_ratings_total?: number;
  price_level?: number;
  status: string;
}

const GoogleMapsSearch = () => {
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<PlaceStatusResponse | null>(null);
  const [places, setPlaces] = useState<Place[]>([]);
  const [searchParams, setSearchParams] = useState<PlacesSearchRequest>({
    business_type: "",
    location: "",
    radius_km: 10,
  });

  // Function to start a search
  const startSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v3/google_maps_api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data: PlacesSearchResponse = await response.json();
      setJobId(data.job_id);

      // Start polling for status
      pollJobStatus(data.job_id);
    } catch (error) {
      console.error("Error starting search:", error);
    }
  };

  // Function to poll job status
  const pollJobStatus = async (id: string) => {
    try {
      const response = await fetch(`/api/v3/google_maps_api/status/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Status check failed");
      }

      const status: PlaceStatusResponse = await response.json();
      setJobStatus(status);

      // If job is still running, poll again after a delay
      if (status.status === "pending" || status.status === "processing") {
        setTimeout(() => pollJobStatus(id), 2000);
      } else {
        // Job completed or failed, fetch results
        if (status.status === "completed") {
          fetchResults();
        }
        setLoading(false);
      }
    } catch (error) {
      console.error("Error checking status:", error);
      setLoading(false);
    }
  };

  // Function to fetch search results
  const fetchResults = async () => {
    try {
      const response = await fetch("/api/v3/google_maps_api/staging", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch results");
      }

      const data = await response.json();
      setPlaces(data.places);
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  };

  return (
    <div>
      <h1>Google Maps Places Search</h1>

      {/* Search Form */}
      <div>
        <input
          type="text"
          placeholder="Business Type (e.g., restaurant)"
          value={searchParams.business_type}
          onChange={(e) =>
            setSearchParams({ ...searchParams, business_type: e.target.value })
          }
        />
        <input
          type="text"
          placeholder="Location (e.g., Burlington, Vermont)"
          value={searchParams.location}
          onChange={(e) =>
            setSearchParams({ ...searchParams, location: e.target.value })
          }
        />
        <input
          type="number"
          placeholder="Radius in km"
          value={searchParams.radius_km}
          onChange={(e) =>
            setSearchParams({
              ...searchParams,
              radius_km: parseInt(e.target.value),
            })
          }
        />
        <button onClick={startSearch} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Status Display */}
      {jobStatus && (
        <div>
          <h2>Search Status</h2>
          <p>Status: {jobStatus.status}</p>
          <p>Progress: {jobStatus.progress * 100}%</p>
          {jobStatus.error && <p>Error: {jobStatus.error}</p>}
          {jobStatus.status === "completed" && (
            <p>
              Found {jobStatus.total_places} places, stored{" "}
              {jobStatus.stored_places}
            </p>
          )}
        </div>
      )}

      {/* Results Display */}
      {places.length > 0 && (
        <div>
          <h2>Search Results</h2>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Address</th>
                <th>Rating</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {places.map((place) => (
                <tr key={place.place_id}>
                  <td>{place.name}</td>
                  <td>{place.formatted_address || place.vicinity || "N/A"}</td>
                  <td>
                    {place.rating
                      ? `${place.rating} (${place.user_ratings_total})`
                      : "N/A"}
                  </td>
                  <td>{place.status}</td>
                  <td>
                    <button
                      onClick={() =>
                        updatePlaceStatus(place.place_id, "approved")
                      }
                    >
                      Approve
                    </button>
                    <button
                      onClick={() =>
                        updatePlaceStatus(place.place_id, "rejected")
                      }
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  // Function to update place status
  async function updatePlaceStatus(placeId: string, newStatus: string) {
    try {
      const response = await fetch(
        `/api/v3/google_maps_api/update-status?place_id=${placeId}&status=${newStatus}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      // Refresh the list
      fetchResults();
    } catch (error) {
      console.error("Error updating status:", error);
    }
  }
};

export default GoogleMapsSearch;
```

## Error Handling

The API follows standard HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User doesn't have required permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error responses have this format:

```json
{
  "detail": "Error message"
}
```

## Rate Limiting

The Google Maps API service is subject to rate limiting. The backend implements appropriate rate limiting to avoid hitting Google's API limits. If you need to perform a large number of searches, consider using batch operations.

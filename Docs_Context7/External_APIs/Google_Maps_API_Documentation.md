# Google Maps API Documentation

## Overview & Installation

Google Maps Platform provides a comprehensive suite of APIs and SDKs for building location-aware applications. It offers mapping services, places data, routing, geocoding, and navigation capabilities for web and mobile applications.

### Key Features
- **Maps**: Interactive maps with customizable markers, overlays, and controls
- **Places**: Access to millions of place details worldwide with search and autocomplete
- **Routes**: Directions, distance calculations, and route optimization
- **Geocoding**: Convert addresses to coordinates and vice versa
- **Street View**: Panoramic street-level imagery
- **Real-time Data**: Traffic conditions, business hours, and place ratings

### Core APIs
- **Maps JavaScript API**: Interactive web maps
- **Places API**: Place search, details, and autocomplete
- **Geocoding API**: Address-to-coordinate conversion
- **Directions API**: Route calculations
- **Distance Matrix API**: Travel times and distances
- **Geolocation API**: User location detection
- **Maps Static API**: Static map images

## Installation & Setup

### 1. Google Cloud Platform Setup
```bash
# Create a Google Cloud Platform account and project
# Enable the required APIs in the Google Cloud Console
```

### 2. API Key Generation
1. Go to Google Cloud Console
2. Navigate to APIs & Services > Credentials
3. Create an API Key
4. Restrict the key to specific APIs and origins for security

### 3. Client Library Installation

**Python (googlemaps):**
```bash
pip install googlemaps
```

**JavaScript:**
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places"></script>
```

**Node.js:**
```bash
npm install @googlemaps/google-maps-services-js
```

## Core Concepts & Architecture

### API Architecture
Google Maps Platform uses RESTful APIs with JSON responses for web services and JavaScript APIs for interactive maps.

### Authentication
All requests require an API key passed as a query parameter:
```
https://maps.googleapis.com/maps/api/geocode/json?address=Seattle&key=YOUR_API_KEY
```

### Rate Limits and Quotas
- Different APIs have different quotas
- Rate limiting is applied per project
- Monitor usage in Google Cloud Console

## Common Usage Patterns

### 1. Python Client Setup
```python
import googlemaps
from datetime import datetime

# Initialize the client
gmaps = googlemaps.Client(key='YOUR_API_KEY')

# Basic geocoding
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
print(geocode_result[0]['geometry']['location'])
```

### 2. Places Search
```python
# Text search for places
places_result = gmaps.places(
    query='restaurants near Seattle',
    type='restaurant',
    language='en'
)

for place in places_result['results']:
    print(f"Name: {place['name']}")
    print(f"Rating: {place.get('rating', 'N/A')}")
    print(f"Address: {place['formatted_address']}")
```

### 3. Place Details
```python
# Get detailed information about a place
place_id = 'ChIJN1t_tDeuEmsRUsoyG83frY4'  # Example place ID
place_details = gmaps.place(
    place_id=place_id,
    fields=['name', 'rating', 'formatted_phone_number', 'website', 'opening_hours']
)

details = place_details['result']
print(f"Name: {details['name']}")
print(f"Phone: {details.get('formatted_phone_number', 'N/A')}")
print(f"Website: {details.get('website', 'N/A')}")
```

### 4. Nearby Search
```python
# Search for places near a location
nearby_search = gmaps.places_nearby(
    location=(37.7749, -122.4194),  # San Francisco coordinates
    radius=1000,  # 1km radius
    type='restaurant',
    keyword='pizza'
)

for place in nearby_search['results']:
    print(f"Name: {place['name']}")
    print(f"Price Level: {place.get('price_level', 'N/A')}")
```

### 5. Directions and Routes
```python
# Get directions between two points
directions_result = gmaps.directions(
    origin='Sydney Town Hall',
    destination='Parramatta, NSW',
    mode='driving',
    departure_time=datetime.now()
)

if directions_result:
    route = directions_result[0]
    leg = route['legs'][0]
    print(f"Distance: {leg['distance']['text']}")
    print(f"Duration: {leg['duration']['text']}")
```

### 6. Distance Matrix
```python
# Calculate distances between multiple origins and destinations
matrix = gmaps.distance_matrix(
    origins=['Seattle, WA', 'Portland, OR'],
    destinations=['San Francisco, CA', 'Los Angeles, CA'],
    mode='driving',
    units='metric'
)

for i, origin in enumerate(matrix['origin_addresses']):
    for j, destination in enumerate(matrix['destination_addresses']):
        element = matrix['rows'][i]['elements'][j]
        if element['status'] == 'OK':
            print(f"{origin} to {destination}: {element['distance']['text']}")
```

### 7. JavaScript Maps Integration
```html
<!DOCTYPE html>
<html>
<head>
    <title>Google Maps Example</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places"></script>
</head>
<body>
    <div id="map" style="width: 100%; height: 400px;"></div>
    
    <script>
        function initMap() {
            // Create map
            const map = new google.maps.Map(document.getElementById('map'), {
                zoom: 13,
                center: { lat: 37.7749, lng: -122.4194 } // San Francisco
            });
            
            // Add marker
            const marker = new google.maps.Marker({
                position: { lat: 37.7749, lng: -122.4194 },
                map: map,
                title: 'San Francisco'
            });
            
            // Places service
            const service = new google.maps.places.PlacesService(map);
        }
        
        // Initialize map when page loads
        window.onload = initMap;
    </script>
</body>
</html>
```

## Best Practices & Security

### 1. API Key Security
```python
import os
from google.oauth2 import service_account

# Use environment variables
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# For server-side applications, consider service account authentication
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json'
)
```

### 2. Error Handling
```python
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout

try:
    gmaps = googlemaps.Client(key=API_KEY)
    result = gmaps.geocode('Invalid Address')
    
    if not result:
        print("No results found")
    
except ApiError as e:
    print(f"API Error: {e}")
except TransportError as e:
    print(f"Transport Error: {e}")
except Timeout as e:
    print(f"Timeout Error: {e}")
```

### 3. Rate Limiting and Caching
```python
import time
from functools import lru_cache

class RateLimitedGoogleMaps:
    def __init__(self, api_key, requests_per_second=10):
        self.client = googlemaps.Client(key=api_key)
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
    
    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()
    
    @lru_cache(maxsize=1000)
    def geocode_cached(self, address):
        self._rate_limit()
        return self.client.geocode(address)
```

### 4. API Key Restrictions
```python
# Set up API key restrictions in Google Cloud Console:
# - Application restrictions (HTTP referrers, IP addresses)
# - API restrictions (limit to specific APIs)
# - Quota restrictions (daily limits)
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import googlemaps
import os

app = FastAPI()
gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

class PlaceSearchRequest(BaseModel):
    query: str
    location: str = None
    radius: int = 5000

@app.post("/places/search")
async def search_places(request: PlaceSearchRequest):
    try:
        if request.location:
            # Geocode the location first
            geocode_result = gmaps.geocode(request.location)
            if not geocode_result:
                raise HTTPException(status_code=400, detail="Invalid location")
            
            location = geocode_result[0]['geometry']['location']
            
            # Search nearby
            results = gmaps.places_nearby(
                location=(location['lat'], location['lng']),
                radius=request.radius,
                keyword=request.query
            )
        else:
            # Text search
            results = gmaps.places(query=request.query)
        
        return {
            "status": "success",
            "results": results['results'][:10],  # Limit to 10 results
            "next_page_token": results.get('next_page_token')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Async Operations
```python
import asyncio
import aiohttp
import json

class AsyncGoogleMaps:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://maps.googleapis.com/maps/api'
    
    async def geocode(self, address):
        url = f"{self.base_url}/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['results']
    
    async def places_search(self, query):
        url = f"{self.base_url}/place/textsearch/json"
        params = {
            'query': query,
            'key': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['results']

# Usage
async def main():
    gmaps = AsyncGoogleMaps(API_KEY)
    
    # Concurrent requests
    tasks = [
        gmaps.geocode('Seattle, WA'),
        gmaps.places_search('restaurants in Seattle')
    ]
    
    results = await asyncio.gather(*tasks)
    geocode_results, places_results = results
```

## Troubleshooting & FAQs

### Common Issues

1. **API Key Errors**
   ```python
   # Check API key is valid and has correct permissions
   # Verify the key is not restricted for your IP/domain
   ```

2. **Quota Exceeded**
   ```python
   # Monitor usage in Google Cloud Console
   # Implement exponential backoff for rate limiting
   import time
   import random
   
   def exponential_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except Exception as e:
               if 'quota' in str(e).lower() and attempt < max_retries - 1:
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   time.sleep(wait_time)
               else:
                   raise
   ```

3. **No Results Found**
   ```python
   # Check if the query is too specific
   # Try broader search terms
   # Verify the location exists
   ```

### Performance Optimization

1. **Batch Requests**
   ```python
   # Use places_nearby instead of multiple individual requests
   # Combine multiple addresses in distance_matrix calls
   ```

2. **Caching Strategy**
   ```python
   import redis
   import json
   import hashlib
   
   class CachedGoogleMaps:
       def __init__(self, api_key, redis_client):
           self.client = googlemaps.Client(key=api_key)
           self.redis = redis_client
           self.cache_ttl = 3600  # 1 hour
       
       def _cache_key(self, method, params):
           key_data = f"{method}:{json.dumps(params, sort_keys=True)}"
           return hashlib.md5(key_data.encode()).hexdigest()
       
       def geocode_cached(self, address):
           cache_key = self._cache_key('geocode', {'address': address})
           
           # Try cache first
           cached = self.redis.get(cache_key)
           if cached:
               return json.loads(cached)
           
           # Make API call
           result = self.client.geocode(address)
           
           # Cache result
           self.redis.setex(cache_key, self.cache_ttl, json.dumps(result))
           return result
   ```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Python Library**: `googlemaps==4.10.0`
- **Services Used**: Places API for location-based business discovery
- **Integration**: Used in places search services for local business curation

### Configuration
```python
# Environment variables required
GOOGLE_MAPS_API_KEY=your-api-key-here

# Client initialization in ScraperSky
import googlemaps
import os

class GoogleMapsService:
    def __init__(self):
        self.client = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))
    
    async def search_places_by_location(self, query: str, location: str, radius: int = 5000):
        """Search for places near a specific location"""
        try:
            # First geocode the location
            geocode_result = self.client.geocode(location)
            if not geocode_result:
                return None
            
            coords = geocode_result[0]['geometry']['location']
            
            # Search for places
            places = self.client.places_nearby(
                location=(coords['lat'], coords['lng']),
                radius=radius,
                keyword=query,
                type='establishment'
            )
            
            return places['results']
            
        except Exception as e:
            logger.error(f"Google Maps API error: {e}")
            return None
```

### Use Cases in ScraperSky
1. **Local Business Discovery**: Find businesses by location and type
2. **Address Validation**: Verify and standardize business addresses
3. **Geocoding**: Convert addresses to coordinates for mapping
4. **Place Details**: Retrieve comprehensive business information

This documentation provides comprehensive guidance for working with Google Maps API in the ScraperSky project context, emphasizing Python integration and best practices for location-based services.
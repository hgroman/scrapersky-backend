Google Places API Integration and Web Scraping Hybrid Plan
Executive Summary
This plan outlines a hybrid approach to gathering business data by combining the Google Places API for core business information with targeted web scraping for supplemental data. The approach reduces legal risks while maximizing data collection capabilities. The implementation is divided among three specialized AI assistants with clearly defined roles and responsibilities.
Roles and Responsibilities
Role 1: Infrastructure & GCP Setup Specialist
Responsibility: Configure Google Cloud Platform, set up API access, manage credentials, and establish authentication.
Role 2: Architecture & Module Design Specialist
Responsibility: Design the system architecture, define data models, and create the core components that will be integrated into the FastAPI application.
Role 3: IDE & Implementation Specialist
Responsibility: Write, test, and refine the actual code within the IDE (fork of VSCode), ensuring all components work together seamlessly.
Implementation Plan
Phase 1: Infrastructure Setup (Role 1)
1.1 Google Cloud Platform Setup
Copy1. Create/Configure Google Cloud Project

- Log in to GCP Console (https://console.cloud.google.com/)
- Create new project or select existing project
- Note Project ID (required for .env)

2. Enable Required APIs

   - Places API
   - Maps JavaScript API
   - Geocoding API
   - Places SDK for Android/iOS (if mobile integration needed)

3. Create API Credentials

   - Create API Key with appropriate restrictions:
     - IP address restrictions
     - HTTP referrer restrictions
     - API restrictions (limit to only needed APIs)
   - Note API Key (required for .env)

4. Set Up Billing

   - Link billing account
   - Set up budget alerts to avoid unexpected charges
   - Note: $200 free monthly credit available

5. Configure Quotas

   - Request quota increases if needed (default: 100 queries per 100 seconds)
   - Set up monitoring for quota usage

6. Service Account Setup (for server-side auth)

   - Create service account with minimal permissions
   - Generate and download JSON key
   - Store key securely (required for .env)

7. Configure Environment Variables

   - Create .env file template with:
     GOOGLE_CLOUD_PROJECT_ID=your-project-id
     GOOGLE_MAPS_API_KEY=your-api-key
     GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-file.json
     1.2 Authorization & Security Configuration
     Copy1. Set up OAuth 2.0 (if needed for user authentication)
   - Configure OAuth consent screen
   - Create OAuth client ID
   - Download OAuth client credentials

8. Configure CORS settings in GCP

   - Add allowed origins for API requests

9. Implement Key Rotation Strategy
   - Document process for regular key rotation
   - Set up alerting for API key usage anomalies
     Phase 2: Architecture Design (Role 2)
     2.1 Data Models
     pythonCopy# models.py additions
     from pydantic import BaseModel, Field, HttpUrl
     from typing import List, Dict, Optional, Any
     from datetime import datetime
     from enum import Enum

class BusinessType(str, Enum):
MEDICAL = "medical"
DENTAL = "dental"
OPHTHALMOLOGY = "ophthalmology"
PEDIATRICS = "pediatrics" # Add more as needed

class PlacesAPIRequest(BaseModel):
"""Model for Google Places API search requests"""
location: str # e.g., "Houston, TX" or coordinates
business_type: BusinessType
radius_meters: int = Field(default=5000, ge=1, le=50000)
max_results: int = Field(default=20, ge=1, le=60)
tenant_id: str = Field(default="default")

class BusinessData(BaseModel):
"""Core business data model"""
place_id: str
name: str
formatted_address: str
location: Dict[str, float] # lat/lng
business_type: BusinessType
phone_number: Optional[str] = None
website: Optional[HttpUrl] = None
rating: Optional[float] = None
user_ratings_total: Optional[int] = None
price_level: Optional[int] = None
tenant_id: str

    # Enriched data (from web scraping)
    email: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    team_members: Optional[List[Dict[str, Any]]] = None

    # Metadata
    fetched_via_api: bool = True
    api_fetch_date: datetime = Field(default_factory=datetime.utcnow)
    scrape_date: Optional[datetime] = None

class PlacesJobStatus(BaseModel):
"""Job status tracking model"""
job_id: str
status: str # "pending", "running", "completed", "failed"
tenant_id: str
query_params: PlacesAPIRequest
started_at: datetime = Field(default_factory=datetime.utcnow)
completed_at: Optional[datetime] = None
businesses_found: int = 0
businesses_processed: int = 0
businesses_enriched: int = 0
error: Optional[str] = None
2.2 Module Structure
Copysrc/
├── routers/
│ └── places_data.py # API endpoint router
├── services/
│ ├── google_places.py # Google Places API integration
│ ├── web_scraper.py # Website scraping for supplemental data
│ └── data_enrichment.py # Business data enrichment
├── db/
│ └── business_repository.py # Database operations
├── utils/
│ ├── rate_limiter.py # API rate limiting utilities
│ └── selectors.py # Web scraping selectors with versioning
└── models.py # Data models
2.3 Database Schema Design
sqlCopy-- Create businesses table
CREATE TABLE IF NOT EXISTS businesses (
id SERIAL PRIMARY KEY,
place_id TEXT UNIQUE NOT NULL,
name TEXT NOT NULL,
formatted_address TEXT NOT NULL,
business_type TEXT NOT NULL,
latitude FLOAT,
longitude FLOAT,
phone_number TEXT,
website TEXT,
rating FLOAT,
user_ratings_total INTEGER,
price_level INTEGER,

    -- Enriched data
    email TEXT,
    social_links JSONB,
    team_members JSONB,

    -- Metadata
    tenant_id TEXT NOT NULL,
    fetched_via_api BOOLEAN NOT NULL DEFAULT TRUE,
    api_fetch_date TIMESTAMP WITH TIME ZONE NOT NULL,
    scrape_date TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Create timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

-- Create indexes
CREATE INDEX idx_business_tenant ON businesses(tenant_id);
CREATE INDEX idx_business_location ON businesses USING gist (
ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);
CREATE INDEX idx_business_type ON businesses(business_type);
Phase 3: Implementation (Role 3)
3.1 Google Places API Integration
pythonCopy# services/google_places.py
import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models import PlacesAPIRequest, BusinessData

class GooglePlacesService:
"""Service for interacting with Google Places API"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_places(self, request: PlacesAPIRequest) -> List[Dict[str, Any]]:
        """Search for places using the Places API Text Search"""
        url = f"{self.base_url}/textsearch/json"

        params = {
            "query": f"{request.business_type} in {request.location}",
            "radius": request.radius_meters,
            "key": self.api_key
        }

        all_results = []

        try:
            # First page
            async with self.session.get(url, params=params) as response:
                data = await response.json()

                if data.get("status") != "OK":
                    logging.error(f"Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    return []

                all_results.extend(data.get("results", []))

                # Handle pagination if needed
                next_page_token = data.get("next_page_token")

                # Note: Google requires a delay before using the next_page_token
                while next_page_token and len(all_results) < request.max_results:
                    # Wait for token to become valid
                    await asyncio.sleep(2)

                    # Fetch next page
                    next_params = {
                        "pagetoken": next_page_token,
                        "key": self.api_key
                    }

                    async with self.session.get(url, params=next_params) as next_response:
                        next_data = await next_response.json()

                        if next_data.get("status") != "OK":
                            break

                        all_results.extend(next_data.get("results", []))
                        next_page_token = next_data.get("next_page_token")

            # Limit to max_results
            return all_results[:request.max_results]

        except Exception as e:
            logging.error(f"Error searching places: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific place"""
        url = f"{self.base_url}/details/json"

        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,geometry,rating,user_ratings_total,price_level,opening_hours",
            "key": self.api_key
        }

        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()

                if data.get("status") != "OK":
                    logging.error(f"Place Details API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    return None

                return data.get("result")

        except Exception as e:
            logging.error(f"Error getting place details: {str(e)}")
            raise

    def parse_business_data(self, place_data: Dict[str, Any], tenant_id: str, business_type: str) -> BusinessData:
        """Parse raw API data into BusinessData model"""
        return BusinessData(
            place_id=place_data.get("place_id"),
            name=place_data.get("name"),
            formatted_address=place_data.get("formatted_address", place_data.get("vicinity", "")),
            location={
                "lat": place_data.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place_data.get("geometry", {}).get("location", {}).get("lng")
            },
            business_type=business_type,
            phone_number=place_data.get("formatted_phone_number"),
            website=place_data.get("website"),
            rating=place_data.get("rating"),
            user_ratings_total=place_data.get("user_ratings_total"),
            price_level=place_data.get("price_level"),
            tenant_id=tenant_id,
            fetched_via_api=True
        )

3.2 Web Scraper for Supplemental Data
pythonCopy# services/web_scraper.py
import re
import logging
import random
import asyncio
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from ..utils.selectors import SelectorVersions

class WebScraperService:
"""Service for scraping supplemental data from business websites"""

    def __init__(self):
        self.session = None
        self.selectors = SelectorVersions.get_current_selectors()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_random_headers(self):
        """Generate random headers to avoid detection"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    async def scrape_website(self, url: str) -> Optional[str]:
        """Scrape content from a website with retry logic"""
        if not url:
            return None

        # Standardize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        try:
            # Random delay to avoid detection
            await asyncio.sleep(random.uniform(1, 3))

            async with self.session.get(
                url,
                headers=self._get_random_headers(),
                timeout=15,
                allow_redirects=True
            ) as response:
                if response.status != 200:
                    logging.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None

                return await response.text()

        except Exception as e:
            logging.warning(f"Error scraping {url}: {str(e)}")
            return None

    async def extract_email(self, html: str) -> List[str]:
        """Extract email addresses from HTML content"""
        if not html:
            return []

        # Email regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, html)

        # Filter out common false positives
        filtered_emails = [
            email for email in emails
            if not any(fake in email.lower() for fake in ['example', '@example', '.example', 'user@', 'name@', 'email@', '@test'])
        ]

        return list(set(filtered_emails))  # Deduplicate

    async def extract_social_links(self, html: str) -> Dict[str, str]:
        """Extract social media links from HTML content"""
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        social_links = {}

        # Social media patterns
        social_patterns = {
            'facebook': r'facebook\.com/([^/"\s]+)',
            'twitter': r'twitter\.com/([^/"\s]+)',
            'linkedin': r'linkedin\.com/(?:company|in)/([^/"\s]+)',
            'instagram': r'instagram\.com/([^/"\s]+)',
            'youtube': r'youtube\.com/(?:user|channel|c)/([^/"\s]+)'
        }

        # Extract from href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                match = re.search(pattern, href)
                if match:
                    social_links[platform] = href

        return social_links

    async def enrich_business_data(self, website_url: str) -> Dict[str, any]:
        """Scrape supplemental data from a business website"""
        if not website_url:
            return {}

        html = await self.scrape_website(website_url)
        if not html:
            return {}

        enrichment = {}

        # Extract emails
        emails = await self.extract_email(html)
        if emails:
            enrichment['email'] = emails[0]  # Use first found email

        # Extract social links
        social_links = await self.extract_social_links(html)
        if social_links:
            enrichment['social_links'] = social_links

        return enrichment

3.3 Database Repository
pythonCopy# db/business_repository.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..db.sb_connection import db
from ..models import BusinessData

class BusinessRepository:
"""Repository for business data operations"""

    @staticmethod
    async def upsert_business(business: BusinessData) -> Dict[str, Any]:
        """Insert or update business data"""
        # Convert nested dictionaries to JSON strings
        business_dict = business.model_dump()

        if isinstance(business_dict.get('location'), dict):
            business_dict['latitude'] = business_dict['location'].get('lat')
            business_dict['longitude'] = business_dict['location'].get('lng')
            del business_dict['location']

        if isinstance(business_dict.get('social_links'), dict):
            business_dict['social_links'] = json.dumps(business_dict['social_links'])

        if isinstance(business_dict.get('team_members'), list):
            business_dict['team_members'] = json.dumps(business_dict['team_members'])

        query = """
            INSERT INTO businesses (
                place_id,
                name,
                formatted_address,
                business_type,
                latitude,
                longitude,
                phone_number,
                website,
                rating,
                user_ratings_total,
                price_level,
                email,
                social_links,
                team_members,
                tenant_id,
                fetched_via_api,
                api_fetch_date,
                scrape_date
            ) VALUES (
                %(place_id)s,
                %(name)s,
                %(formatted_address)s,
                %(business_type)s,
                %(latitude)s,
                %(longitude)s,
                %(phone_number)s,
                %(website)s,
                %(rating)s,
                %(user_ratings_total)s,
                %(price_level)s,
                %(email)s,
                %(social_links)s,
                %(team_members)s,
                %(tenant_id)s,
                %(fetched_via_api)s,
                %(api_fetch_date)s,
                %(scrape_date)s
            )
            ON CONFLICT (place_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                formatted_address = EXCLUDED.formatted_address,
                business_type = EXCLUDED.business_type,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                phone_number = EXCLUDED.phone_number,
                website = EXCLUDED.website,
                rating = EXCLUDED.rating,
                user_ratings_total = EXCLUDED.user_ratings_total,
                price_level = EXCLUDED.price_level,
                email = COALESCE(EXCLUDED.email, businesses.email),
                social_links = COALESCE(EXCLUDED.social_links, businesses.social_links),
                team_members = COALESCE(EXCLUDED.team_members, businesses.team_members),
                tenant_id = EXCLUDED.tenant_id,
                fetched_via_api = EXCLUDED.fetched_via_api,
                api_fetch_date = EXCLUDED.api_fetch_date,
                scrape_date = EXCLUDED.scrape_date,
                last_updated = NOW()
            RETURNING *;
        """

        with db.get_cursor() as cur:
            try:
                cur.execute(query, business_dict)
                return cur.fetchone()
            except Exception as e:
                logging.error(f"Error upserting business: {str(e)}")
                raise

    @staticmethod
    async def batch_upsert_businesses(businesses: List[BusinessData]) -> int:
        """Batch upsert multiple businesses for better performance"""
        if not businesses:
            return 0

        successful_inserts = 0

        # Process in batches of 50
        batch_size = 50
        for i in range(0, len(businesses), batch_size):
            batch = businesses[i:i+batch_size]

            try:
                # Prepare batch of business data
                batch_data = []
                for business in batch:
                    business_dict = business.model_dump()

                    if isinstance(business_dict.get('location'), dict):
                        business_dict['latitude'] = business_dict['location'].get('lat')
                        business_dict['longitude'] = business_dict['location'].get('lng')
                        del business_dict['location']

                    if isinstance(business_dict.get('social_links'), dict):
                        business_dict['social_links'] = json.dumps(business_dict['social_links'])

                    if isinstance(business_dict.get('team_members'), list):
                        business_dict['team_members'] = json.dumps(business_dict['team_members'])

                    batch_data.append(business_dict)

                # Use copy_records_to_table for bulk insert
                with db.get_connection() as conn:
                    cursor = conn.cursor()

                    # Build the columns string and values placeholders
                    columns = list(batch_data[0].keys())
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join([f"%({col})s" for col in columns])

                    # Build the ON CONFLICT clause
                    update_cols = [col for col in columns if col != 'place_id']
                    update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])

                    query = f"""
                        INSERT INTO businesses ({columns_str})
                        VALUES ({placeholders})
                        ON CONFLICT (place_id)
                        DO UPDATE SET {update_str}, last_updated = NOW();
                    """

                    # Execute batch query
                    cursor.executemany(query, batch_data)
                    conn.commit()

                    successful_inserts += len(batch)

            except Exception as e:
                logging.error(f"Error in batch upsert: {str(e)}")
                # Continue with next batch instead of failing the entire operation

        return successful_inserts

    @staticmethod
    async def get_businesses_by_tenant(tenant_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get businesses for a specific tenant with pagination"""
        query = """
            SELECT * FROM businesses
            WHERE tenant_id = %(tenant_id)s
            ORDER BY api_fetch_date DESC
            LIMIT %(limit)s OFFSET %(offset)s;
        """

        with db.get_cursor() as cur:
            try:
                cur.execute(query, {
                    "tenant_id": tenant_id,
                    "limit": limit,
                    "offset": offset
                })
                return cur.fetchall()
            except Exception as e:
                logging.error(f"Error getting businesses by tenant: {str(e)}")
                raise

3.4 Places API Router
pythonCopy# routers/places_data.py
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from ..models import PlacesAPIRequest, PlacesJobStatus, BusinessData
from ..services.google_places import GooglePlacesService
from ..services.web_scraper import WebScraperService
from ..db.business_repository import BusinessRepository

# Setup router

router = APIRouter(prefix="/api/v1", tags=["places-data"])

# In-memory job storage (replace with Redis in production)

\_job_statuses: Dict[str, PlacesJobStatus] = {}

async def process_places_job(job_id: str, request: PlacesAPIRequest):
"""Process places data job in background"""
status = \_job_statuses[job_id]
status.status = "running"

    try:
        # Initialize services
        async with GooglePlacesService() as places_service:
            # 1. Fetch places from Google Places API
            places_results = await places_service.search_places(request)

            # Update status
            status.businesses_found = len(places_results)

            # 2. Process each place
            businesses: List[BusinessData] = []

            for place_result in places_results:
                try:
                    # Get place details (more comprehensive data)
                    place_id = place_result.get("place_id")
                    place_details = await places_service.get_place_details(place_id)

                    # Use details if available, otherwise use search result
                    place_data = place_details or place_result

                    # Parse business data
                    business = places_service.parse_business_data(
                        place_data,
                        request.tenant_id,
                        request.business_type
                    )

                    businesses.append(business)
                    status.businesses_processed += 1

                except Exception as e:
                    logging.error(f"Error processing place {place_result.get('name', 'Unknown')}: {str(e)}")
                    # Continue with next place

            # 3. Save businesses to database (batch operation)
            await BusinessRepository.batch_upsert_businesses(businesses)

            # 4. Enrich data with web scraping (only for businesses with websites)
            async with WebScraperService() as scraper:
                for business in businesses:
                    if business.website:
                        try:
                            # Scrape additional data
                            enrichment = await scraper.enrich_business_data(str(business.website))

                            if enrichment:
                                # Update business with enriched data
                                for key, value in enrichment.items():
                                    setattr(business, key, value)

                                business.scrape_date = datetime.utcnow()

                                # Update in database
                                await BusinessRepository.upsert_business(business)
                                status.businesses_enriched += 1

                        except Exception as e:
                            logging.error(f"Error enriching business {business.name}: {str(e)}")
                            # Continue with next business

        # Mark job as completed
        status.status = "completed"
        status.completed_at = datetime.utcnow()

    except Exception as e:
        # Mark job as failed
        status.status = "failed"
        status.error = str(e)
        status.completed_at = datetime.utcnow()
        logging.error(f"Job {job_id} failed: {str(e)}")

@router.post("/places", response_model=Dict[str, Any])
async def search_places(request: PlacesAPIRequest, background_tasks: BackgroundTasks):
"""
Search for businesses using Google Places API and enrich with web scraping.
""" # Generate job ID
job_id = str(uuid.uuid4())

    # Initialize job status
    _job_statuses[job_id] = PlacesJobStatus(
        job_id=job_id,
        status="pending",
        tenant_id=request.tenant_id,
        query_params=request
    )

    # Start background processing
    background_tasks.add_task(process_places_job, job_id, request)

    # Return job info
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Processing request for {request.business_type} in {request.location}",
        "status_url": f"/api/v1/places/status/{job_id}"
    }

@router.get("/places/status/{job_id}")
async def get_job_status(job_id: str):
"""Get the status of a places data job"""
if job_id not in \_job_statuses:
raise HTTPException(404, detail="Job not found")

    return _job_statuses[job_id]

@router.get("/places/businesses")
async def get_businesses(
tenant_id: str = Query(..., description="Tenant ID"),
limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
offset: int = Query(0, ge=0, description="Pagination offset")
):
"""Get businesses for a tenant with pagination"""
try:
businesses = await BusinessRepository.get_businesses_by_tenant(
tenant_id=tenant_id,
limit=limit,
offset=offset
)

        return {
            "businesses": businesses,
            "count": len(businesses),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

3.5 Selector Versioning Utility
pythonCopy# utils/selectors.py
from typing import Dict, Any

class SelectorVersions:
"""Manages HTML selectors with versioning for web scraping resilience"""

    CURRENT_VERSION = "2025-02-v1"

    @classmethod
    def get_current_selectors(cls) -> Dict[str, str]:
        """Get current version of selectors"""
        return cls.get_selectors().get(cls.CURRENT_VERSION, {})

    @classmethod
    def get_selectors(cls) -> Dict[str, Dict[str, str]]:
        """Get all versions of selectors"""
        return {
            # Current version
            "2025-02-v1": {
                # Contact selectors
                "contact_email": ".contact-email, .email, [itemprop='email']",
                "contact_form": "form.contact-form, form.wpcf7-form",
                "contactRetryClaude hit the max length for a message and has paused its response. You can write Continue to keep the chat going.HGcontinueEditutils/selectors.py (continued)

pythonCopy "contact_form": "form.contact-form, form.wpcf7-form",
"contact_section": ".contact-us, .contact-info, #contact",

                # Social media selectors
                "social_links": ".social-media, .social-links, .social-icons",
                "facebook_link": "a[href*='facebook.com']",
                "twitter_link": "a[href*='twitter.com'], a[href*='x.com']",
                "linkedin_link": "a[href*='linkedin.com']",
                "instagram_link": "a[href*='instagram.com']",

                # Team member selectors
                "team_section": ".team, .our-team, .staff, .physicians, .doctors",
                "team_member": ".team-member, .staff-member, .doctor, .physician",
                "member_name": ".name, .member-name, h3, h4",
                "member_title": ".title, .position, .role, .specialty",
                "member_bio": ".bio, .description, .about, p"
            },

            # Previous version (fallback)
            "2025-01-v2": {
                # Contact selectors
                "contact_email": ".email, .mail, [data-type='email']",
                "contact_form": "#contact-form, .contact-form",
                "contact_section": "#contact, .contact",

                # Social media selectors
                "social_links": ".social, .social-media",
                "facebook_link": ".facebook, a[href*='fb.com']",
                "twitter_link": ".twitter, a[href*='twitter.com']",
                "linkedin_link": ".linkedin, a[href*='linkedin.com']",
                "instagram_link": ".instagram, a[href*='instagram.com']",

                # Team member selectors
                "team_section": "#team, .team",
                "team_member": ".member, .person",
                "member_name": ".name, h3",
                "member_title": ".job-title, .position",
                "member_bio": ".biography, .description"
            }
        }

    @classmethod
    def try_all_versions(cls, html_parser, selector_key):
        """Try all versions of a selector until one works"""
        selectors = cls.get_selectors()

        for version, selectors_dict in selectors.items():
            if selector_key in selectors_dict:
                result = html_parser.select(selectors_dict[selector_key])
                if result:
                    return result

        return []

3.6 Rate Limiter Utility
pythonCopy# utils/rate_limiter.py
import time
import asyncio
import logging
from typing import Dict, Callable, Any, Optional
from functools import wraps

class APIRateLimiter:
"""Rate limiter for API calls"""

    def __init__(self, calls: int, period: int):
        """
        Initialize rate limiter

        Args:
            calls: Number of allowed calls
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.timestamps = []

    async def wait(self):
        """Wait if needed to respect rate limits"""
        now = time.time()

        # Remove timestamps older than the period
        self.timestamps = [ts for ts in self.timestamps if now - ts <= self.period]

        # If we've reached the limit, wait
        if len(self.timestamps) >= self.calls:
            oldest = self.timestamps[0]
            sleep_time = self.period - (now - oldest) + 0.1  # Add small buffer

            if sleep_time > 0:
                logging.debug(f"Rate limit reached, waiting for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                now = time.time()  # Update current time after sleep

        # Add current timestamp
        self.timestamps.append(now)

class RateLimiterRegistry:
"""Registry of rate limiters for different services"""

    _limiters: Dict[str, APIRateLimiter] = {}

    @classmethod
    def get_limiter(cls, service_name: str) -> APIRateLimiter:
        """Get or create rate limiter for a service"""
        if service_name not in cls._limiters:
            # Default rate limits based on service
            if service_name == "google_places":
                # Google Places API: 100 QPS per user, but we use more conservative limit
                cls._limiters[service_name] = APIRateLimiter(calls=50, period=60)
            elif service_name == "web_scraper":
                # Web scraper: Be conservative to avoid detection
                cls._limiters[service_name] = APIRateLimiter(calls=10, period=60)
            else:
                # Default rate limit
                cls._limiters[service_name] = APIRateLimiter(calls=20, period=60)

        return cls._limiters[service_name]

def rate_limited(service_name: str):
"""Decorator to apply rate limiting to a function"""
def decorator(func: Callable):
@wraps(func)
async def wrapper(*args, \*\*kwargs):
limiter = RateLimiterRegistry.get_limiter(service_name)
await limiter.wait()
return await func(*args, \*\*kwargs)
return wrapper
return decorator
Phase 4: Registration and Configuration
4.1 Register Router in FastAPI App
pythonCopy# In your main.py or equivalent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers

from src.routers import places_data

app = FastAPI(
title="ScraperSky",
description="A FastAPI-based service for gathering business information."
)

# CORS settings

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # Update for production
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Include routers

app.include_router(places_data.router)
4.2 Environment Variables Setup
Copy# .env file template

# Google Cloud Platform

GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_MAPS_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-file.json

# Supabase

SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-key
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_DB_PASSWORD=your-supabase-db-password

# Application Settings

LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0
MAX_WORKERS=4
Cost Analysis & Resource Optimization
Google Places API Costs

Places API Search

Price: $17 per 1,000 requests
Monthly Usage Estimate (50,000 businesses): 10,000 search requests ($170)

Place Details API

Price: $34 per 1,000 requests
Monthly Usage Estimate (50,000 businesses): 50,000 detail requests ($1,700)

Total Monthly Cost Estimate

$1,870 (before any free credits)
Optimization: Use the $200 monthly credit to reduce cost to ~$1,670

Optimization Strategies

Limit Place Details Requests

Only fetch details for businesses matching specific criteria
Cache results to avoid refetching the same business data

Batch Processing

Group businesses by region and process in batches
Schedule scraping during off-peak hours
Use incremental updates rather than full rescans

Quota Management

Monitor API usage closely
Implement circuit breakers to stop processing if nearing quota limits
Distribute requests evenly throughout the day

Role-Specific Tasks and Implementation Strategy
Role 1: Infrastructure & GCP Setup Specialist
Key Responsibilities:

Configure Google Cloud Project with proper API access
Set up authentication and security measures
Manage quotas and billing alerts
Generate and store credentials securely

Implementation Steps:

Create GCP project and enable required APIs
Generate API credentials with appropriate restrictions
Set up service account for server-to-server authentication
Configure environment variables for credentials
Set up monitoring and alerting for API usage
Document the setup process for the team

Key Deliverables:

Configured GCP project with enabled APIs
API key with appropriate restrictions
Service account JSON key
.env file with required credentials
Documentation of the setup process

Role 2: Architecture & Module Design Specialist
Key Responsibilities:

Design the overall system architecture
Define data models and database schema
Plan the module structure and interactions
Design for scalability and maintainability

Implementation Steps:

Create Pydantic models for all data structures
Design database schema with proper indexing
Define module structure and interfaces
Create architectural diagrams for the team
Plan for error handling and recovery
Design monitoring and logging strategy

Key Deliverables:

Data models in models.py
Database schema SQL definitions
Module structure documentation
Component interaction diagrams
API endpoint specifications
Error handling guidelines

Role 3: IDE & Implementation Specialist
Key Responsibilities:

Implement the actual code in VSCode fork
Write clean, maintainable, and well-documented code
Implement error handling and logging
Test and debug the implementation
Optimize for performance and resource usage

Implementation Steps:

Set up project structure with proper imports
Implement services for Google Places API and web scraping
Create database repository with efficient operations
Implement FastAPI router with proper endpoint definitions
Add comprehensive error handling and logging
Optimize critical code paths for performance
Write tests to verify functionality

Key Deliverables:

Fully implemented Python code modules
Unit and integration tests
Performance optimization recommendations
Documentation of implementation details
Troubleshooting guide for common issues

Testing and Validation Strategy
Unit Testing
pythonCopy# tests/test_google_places.py
import pytest
from unittest.mock import patch, MagicMock
import json
import os
from src.services.google_places import GooglePlacesService
from src.models import PlacesAPIRequest, BusinessType

@pytest.mark.asyncio
async def test_search_places(): # Mock the aiohttp ClientSession
with patch('aiohttp.ClientSession.get') as mock_get: # Mock the HTTP response
mock_response = MagicMock()
mock_response.status = 200
mock_response.json.return_value = {
"status": "OK",
"results": [
{
"place_id": "test_place_id",
"name": "Test Business",
"vicinity": "123 Test St, Houston, TX",
"geometry": {
"location": {
"lat": 29.7604,
"lng": -95.3698
}
},
"rating": 4.5
}
]
}
mock_get.return_value.**aenter**.return_value = mock_response

        # Test the service
        service = GooglePlacesService()
        service.session = MagicMock()  # Mock the session
        service.api_key = "test_api_key"

        request = PlacesAPIRequest(
            location="Houston, TX",
            business_type=BusinessType.MEDICAL,
            radius_meters=5000,
            max_results=10
        )

        results = await service.search_places(request)

        # Assertions
        assert len(results) == 1
        assert results[0]["place_id"] == "test_place_id"
        assert results[0]["name"] == "Test Business"

Integration Testing
pythonCopy# tests/test_integration.py
import pytest
import os
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_places_search_endpoint():
response = client.post(
"/api/v1/places",
json={
"location": "Houston, TX",
"business_type": "medical",
"radius_meters": 5000,
"max_results": 10,
"tenant_id": "test_tenant"
}
)

    # Assert response structure
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "started"

Deployment and Scaling Considerations
Deployment Options

Docker Container

Containerize the application for consistency
Use Docker Compose for local development
Suitable for various deployment targets

Kubernetes (for large-scale)

Deploy as Kubernetes pods for scaling
Use Horizontal Pod Autoscaler for demand management
Implement resource quotas and limits

Serverless (AWS Lambda or Cloud Functions)

For smaller deployments or cost optimization
Split functionality into separate functions
Consider cold start impact on performance

Scaling Strategies

Vertical Scaling

Increase resources (CPU/memory) for the application server
Suitable for moderate workloads

Horizontal Scaling

Add more application instances behind a load balancer
Stateless design enables easy scaling
Requires distributed job tracking (Redis)

Task Distribution

Use message queues (RabbitMQ, SQS) for job distribution
Worker pool for processing tasks
Helps manage rate limits and resource utilization

Monitoring and Maintenance
Monitoring

API Usage Monitoring

Track Google Places API usage with Prometheus metrics
Set up alerts for approaching quota limits
Monitor costs with GCP billing alerts

Application Monitoring

Track request rates, latencies, and error rates
Monitor database performance
Set up alerting for critical errors

Log Management

Structured logging with correlation IDs
Log aggregation with ELK stack or similar
Retention policies for compliance

Maintenance

Regular Updates

Update web scraping selectors when structures change
Monitor for Google Places API changes
Dependencies security updates

Database Maintenance

Regular backups
Index optimization
Data archiving strategy

Code Quality

Automated testing in CI/CD pipeline
Code reviews for all changes
Performance profiling and optimization

Role Coordination and Communication
Shared Resources

Documentation Repository

Architecture diagrams
API specifications
Setup guides
Troubleshooting information

Shared Environment

Development environment configuration
Test datasets
Mock API responses
Database schema definitions

Project Management

Task tracking
Milestone definitions
Dependencies mapping
Regular sync meetings

Communication Channels

Regular Sync Meetings

Weekly team sync
Cross-role knowledge sharing
Progress updates and roadblocks

Documentation Updates

Maintain living documentation
Update as implementation evolves
Document key decisions and trade-offs

Code Reviews

Cross-role code reviews
Knowledge sharing
Consistency enforcement

Conclusion
This hybrid plan leverages the benefits of both the Google Places API and targeted web scraping to build a robust system for gathering business data. By using the Google Places API for core business information and supplementing with web scraping for additional details, we minimize legal risks while maximizing data collection capabilities.
The implementation is divided among three specialized AI assistants, each with clearly defined roles and responsibilities. This division of labor ensures that each aspect of the system receives the attention it deserves, from infrastructure setup to architecture design to code implementation.
The plan provides a complete roadmap from initial setup to deployment and maintenance, with detailed implementation guidance for each component. By following this plan, you'll be able to build a scalable, maintainable system that meets your requirements for scraping 50,000 sites per month while staying within reasonable cost constraints.

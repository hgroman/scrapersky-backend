# Data Schema (The Database Truth)

**Generated:** 2025-11-22
**Source:** Supabase `information_schema`
**Status:** Verified

---

## WF1: Places (`places`)
*Raw Google Maps Data*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `google_place_id` | text | NO | Unique Google ID |
| `name` | text | NO | |
| `address` | text | YES | |
| `phone` | text | YES | |
| `website` | text | YES | |
| `rating` | numeric | YES | |
| `user_ratings_total` | integer | YES | |
| `types` | jsonb | YES | Google categories |
| `status` | text | YES | Curation Status |
| `deep_scan_status` | text | YES | Processing Status |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |

---

## WF3: Local Businesses (`local_businesses`)
*Processed Business Entities*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `place_id` | uuid | NO | FK -> places.id |
| `name` | text | NO | |
| `website_url` | text | YES | |
| `domain_extraction_status` | text | YES | Processing Status |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |

---

## WF4: Domains (`domains`)
*Unique Web Domains*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `domain` | text | NO | Unique |
| `sitemap_curation_status` | text | YES | Curation Status |
| `sitemap_analysis_status` | text | YES | Processing Status |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |

---

## WF5: Sitemap Files (`sitemap_files`)
*Discovered Sitemaps*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `domain_id` | uuid | NO | FK -> domains.id |
| `sitemap_url` | text | NO | |
| `sitemap_type` | text | YES | |
| `url_count` | integer | YES | |
| `deep_scrape_curation_status` | text | YES | Curation Status |
| `sitemap_import_status` | text | YES | Processing Status |
| `created_at` | timestamptz | YES | |
| `updated_at` | timestamptz | YES | |

---

## WF7: Pages (`pages`)
*Individual URLs*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `domain_id` | uuid | NO | FK -> domains.id |
| `url` | text | NO | |
| `page_type` | text | YES | Honeybee Category |
| `page_curation_status` | text | YES | Curation Status |
| `page_processing_status` | text | YES | Processing Status |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |

---

## WF7: Contacts (`contacts`)
*Extracted People/Emails*

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | PK |
| `domain_id` | uuid | NO | FK -> domains.id |
| `page_id` | uuid | NO | FK -> pages.id |
| `email` | text | NO | |
| `contact_curation_status` | text | NO | Curation Status |
| `contact_processing_status` | text | YES | Processing Status |
| `hubspot_sync_status` | text | NO | Sync Status |
| `brevo_sync_status` | text | NO | Sync Status |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |

# WF6 Database Table Specifications
# Layer-by-Layer Database Testing Requirements

## Overview

This document provides comprehensive database table specifications for each layer in the WF6 testing framework, ensuring complete data validation and integrity testing across the ScraperSky Layer Architecture.

## Layer 1 (L1): Data Sentinel - Database Tables

### Primary Tables

#### `sitemap_files` Table
**Guardian Persona**: Layer 1 Data Sentinel  
**Purpose**: Input table for WF6 workflow - stores sitemap file metadata and processing status

```sql
CREATE TABLE sitemap_files (
    -- Primary Keys & Identity
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL DEFAULT '550e8400-e29b-41d4-a716-446655440000'::uuid,
    
    -- Foreign Keys
    domain_id UUID NOT NULL REFERENCES domains(id),
    user_id UUID,
    created_by UUID,
    updated_by UUID,
    job_id UUID,
    
    -- Core Fields
    url TEXT NOT NULL,
    sitemap_type TEXT NOT NULL,
    discovery_method TEXT,
    
    -- Metadata Fields
    page_count INTEGER,
    url_count INTEGER DEFAULT 0,
    size_bytes INTEGER,
    response_time_ms INTEGER,
    priority INTEGER DEFAULT 5,
    status_code INTEGER,
    
    -- Status & Processing
    status sitemap_file_status_enum NOT NULL DEFAULT 'Pending'::sitemap_file_status_enum,
    sitemap_import_status sitemap_import_process_status_enum,
    sitemap_import_error TEXT,
    deep_scrape_curation_status "SitemapCurationStatusEnum" DEFAULT 'New'::"SitemapCurationStatusEnum",
    
    -- Content Analysis
    is_gzipped BOOLEAN,
    has_lastmod BOOLEAN,
    has_priority BOOLEAN,
    has_changefreq BOOLEAN,
    generator TEXT,
    
    -- Timestamps
    last_modified TIMESTAMP WITH TIME ZONE,
    process_after TIMESTAMP WITH TIME ZONE,
    last_processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    -- User Fields
    user_name TEXT,
    notes TEXT,
    tags JSONB,
    lead_source TEXT,
    is_active BOOLEAN DEFAULT true
);
```

**Test Validation Points**:
- UUID generation and uniqueness
- Foreign key constraints to `domains` table
- Enum value validation for status fields
- Default value assignment
- Timestamp field behavior
- JSONB field handling
- Index performance on frequently queried fields

#### `pages` Table
**Guardian Persona**: Layer 1 Data Sentinel  
**Purpose**: Output table for WF6 workflow - stores URLs extracted from sitemap files

```sql
CREATE TABLE pages (
    -- Primary Keys & Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    
    -- Foreign Keys
    domain_id UUID NOT NULL REFERENCES domains(id),
    sitemap_file_id UUID REFERENCES sitemap_files(id),
    
    -- Core Fields
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    h1 TEXT,
    canonical_url TEXT,
    meta_robots TEXT,
    
    -- Content Analysis
    has_schema_markup BOOLEAN DEFAULT false,
    schema_types TEXT[],
    has_contact_form BOOLEAN DEFAULT false,
    has_comments BOOLEAN DEFAULT false,
    word_count INTEGER,
    
    -- Link Analysis
    inbound_links TEXT[],
    outbound_links TEXT[],
    
    -- Metadata
    page_type TEXT,
    lead_source TEXT,
    additional_json JSONB DEFAULT '{}'::jsonb,
    
    -- Status & Processing
    page_curation_status page_curation_status NOT NULL DEFAULT 'New'::page_curation_status,
    page_processing_status page_processing_status,
    page_processing_error TEXT,
    
    -- Timestamps
    last_modified TIMESTAMP WITH TIME ZONE,
    last_scan TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Test Validation Points**:
- Foreign key relationship to `sitemap_files`
- URL field validation and uniqueness constraints
- Array field handling (schema_types, inbound_links, outbound_links)
- JSONB field validation
- Status enum validation
- Cascade behavior on sitemap_file deletion

#### `domains` Table (Supporting)
**Guardian Persona**: Layer 1 Data Sentinel  
**Purpose**: Parent table providing domain context for sitemap files

```sql
CREATE TABLE domains (
    -- Primary Keys & Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    
    -- Core Fields
    domain CHARACTER VARYING NOT NULL,
    status CHARACTER VARYING NOT NULL DEFAULT 'active'::text,
    is_active BOOLEAN DEFAULT true,
    
    -- Technical Details
    has_ssl BOOLEAN,
    ssl_expiry_date TIMESTAMP WITH TIME ZONE,
    ssl_issuer TEXT,
    ssl_version TEXT,
    server_type TEXT,
    ip_address TEXT,
    hosting_provider TEXT,
    country_code TEXT,
    server_response_time INTEGER,
    hosting_location TEXT,
    cdn_provider TEXT,
    
    -- Content & SEO
    robots_txt TEXT,
    has_sitemap BOOLEAN,
    page_count INTEGER,
    content_language TEXT[],
    
    -- Processing Status Fields
    content_scrape_status task_status DEFAULT 'Queued'::task_status,
    content_scrape_at TIMESTAMP WITH TIME ZONE,
    content_scrape_error TEXT,
    
    page_scrape_status task_status DEFAULT 'Queued'::task_status,
    page_scrape_at TIMESTAMP WITH TIME ZONE,
    page_scrape_error TEXT,
    
    sitemap_monitor_status task_status DEFAULT 'Queued'::task_status,
    sitemap_monitor_at TIMESTAMP WITH TIME ZONE,
    sitemap_monitor_error TEXT,
    
    sitemap_curation_status "SitemapCurationStatusEnum" DEFAULT 'New'::"SitemapCurationStatusEnum",
    sitemap_analysis_status "SitemapAnalysisStatusEnum" DEFAULT 'pending'::"SitemapAnalysisStatusEnum",
    sitemap_analysis_error TEXT,
    
    -- HubSpot Integration
    hubspot_sync_status hubspot_sync_status NOT NULL DEFAULT 'New'::hubspot_sync_status,
    hubspot_processing_status hubspot_processing_status,
    hubspot_processing_error TEXT,
    
    -- Security & Technical Analysis
    security_headers JSONB,
    dns_records JSONB,
    
    -- Metadata
    lead_source TEXT,
    last_modified TIMESTAMP WITH TIME ZONE
);
```

**Test Validation Points**:
- Domain name validation and uniqueness
- Status enum validation across multiple status fields
- JSONB field validation (security_headers, dns_records)
- Array field handling (content_language)
- Default value assignment for status fields

### Enum Types

#### `sitemap_import_process_status_enum`
```sql
CREATE TYPE sitemap_import_process_status_enum AS ENUM (
    'Queued',
    'Processing', 
    'Complete',
    'Error'
);
```

#### `page_curation_status`
```sql
CREATE TYPE page_curation_status AS ENUM (
    'New',
    'Selected',
    'Rejected'
);
```

#### `task_status`
```sql
CREATE TYPE task_status AS ENUM (
    'Queued',
    'Processing',
    'Complete',
    'Error'
);
```

## Layer Testing Database Validation Requirements

### Layer 1 (L1) Tests - Data Integrity
- **Table Structure Validation**: Verify all columns, types, and constraints
- **Foreign Key Integrity**: Test cascade behavior and referential integrity
- **Enum Value Validation**: Ensure all enum values are present and functional
- **Index Performance**: Validate query performance on indexed columns
- **Default Value Assignment**: Test default value behavior on INSERT
- **Timestamp Behavior**: Verify created_at/updated_at automatic updates

### Layer 3 (L3) Tests - API Data Flow
- **CRUD Operations**: Test data persistence through API endpoints
- **Input Validation**: Verify API input validation matches database constraints
- **Transaction Integrity**: Test rollback behavior on API errors
- **Batch Operations**: Validate bulk updates maintain data integrity

### Layer 4 (L4) Tests - Business Logic Data Processing
- **Status Transitions**: Test valid status progression through business logic
- **Data Transformation**: Verify service layer data processing accuracy
- **Error Handling**: Test data consistency during error scenarios
- **Concurrent Processing**: Validate data integrity under concurrent operations

## Test Data Templates

### Minimal Valid Records
```sql
-- Test Domain
INSERT INTO domains (id, domain, status, tenant_id) 
VALUES ('test-domain-uuid', 'test-example.com', 'active', 'test-tenant-uuid');

-- Test Sitemap File
INSERT INTO sitemap_files (id, domain_id, url, sitemap_type, discovery_method, tenant_id)
VALUES ('test-sitemap-uuid', 'test-domain-uuid', 'https://test-example.com/sitemap.xml', 'Standard', 'test', 'test-tenant-uuid');

-- Test Page
INSERT INTO pages (id, domain_id, sitemap_file_id, url, tenant_id)
VALUES ('test-page-uuid', 'test-domain-uuid', 'test-sitemap-uuid', 'https://test-example.com/', 'test-tenant-uuid');
```

### Status Transition Test Data
```sql
-- Queued Sitemap File
UPDATE sitemap_files 
SET sitemap_import_status = 'Queued' 
WHERE id = 'test-sitemap-uuid';

-- Processing Sitemap File
UPDATE sitemap_files 
SET sitemap_import_status = 'Processing' 
WHERE id = 'test-sitemap-uuid';

-- Completed Sitemap File with Pages
UPDATE sitemap_files 
SET sitemap_import_status = 'Complete', url_count = 5 
WHERE id = 'test-sitemap-uuid';
```

## Cleanup Procedures

### Layer-Aware Cleanup Order
```sql
-- 1. Clean child records first (Layer 1 dependency order)
DELETE FROM pages WHERE sitemap_file_id IN (
    SELECT id FROM sitemap_files WHERE discovery_method = 'test'
);

-- 2. Clean parent records
DELETE FROM sitemap_files WHERE discovery_method = 'test';

-- 3. Clean supporting records
DELETE FROM domains WHERE domain LIKE 'test-%';
```

## Performance Benchmarks

### Expected Query Performance
- **Sitemap File Lookup by ID**: < 1ms
- **Pages by Sitemap File ID**: < 5ms for 1000 pages
- **Status-based Filtering**: < 10ms for 10,000 records
- **Bulk Status Updates**: < 100ms for 100 records

### Index Requirements
```sql
-- Performance-critical indexes for WF6
CREATE INDEX idx_sitemap_files_status ON sitemap_files(sitemap_import_status);
CREATE INDEX idx_sitemap_files_domain ON sitemap_files(domain_id);
CREATE INDEX idx_pages_sitemap_file ON pages(sitemap_file_id);
CREATE INDEX idx_pages_domain ON pages(domain_id);
```

This comprehensive database specification ensures complete data validation testing across all layers of the WF6 workflow.

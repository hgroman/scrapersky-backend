-- Rename PascalCase Enums to snake_case
-- CORRECTED: Database has lowercase names without quotes (not PascalCase with quotes)
-- Pre-flight check confirmed: domainextractionstatusenum and sitemapcurationstatusenum exist
ALTER TYPE domainextractionstatusenum RENAME TO domain_extraction_status_enum;
ALTER TYPE sitemapcurationstatusenum RENAME TO sitemap_curation_status_enum;

-- Add Foreign Key Constraints for tenant_id
-- local_businesses
ALTER TABLE local_businesses 
    ADD CONSTRAINT fk_local_businesses_tenant 
    FOREIGN KEY (tenant_id) 
    REFERENCES tenants(id);

-- places_staging
ALTER TABLE places_staging 
    ADD CONSTRAINT fk_places_staging_tenant 
    FOREIGN KEY (tenant_id) 
    REFERENCES tenants(id);

-- sitemap_files
ALTER TABLE sitemap_files 
    ADD CONSTRAINT fk_sitemap_files_tenant 
    FOREIGN KEY (tenant_id) 
    REFERENCES tenants(id);

-- sitemap_urls
ALTER TABLE sitemap_urls 
    ADD CONSTRAINT fk_sitemap_urls_tenant 
    FOREIGN KEY (tenant_id) 
    REFERENCES tenants(id);

-- Add recommended indexes for WF8 Contacts CRUD endpoint performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_curation_status ON contacts(contact_curation_status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_email_type ON contacts(email_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_domain_id ON contacts(domain_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_has_gmail ON contacts(has_gmail);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_email_gin ON contacts USING gin(email gin_trgm_ops);

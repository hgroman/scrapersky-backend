-- Update orphaned file
UPDATE file_audit
SET notes = 'Part of Page Curation Workflow. Initial content extraction service. See Knowledge Base: Docs/Docs_10_Final_Audit/Knowledge_Base/Page-Curation-Workflow.md. JIRA: SCRAPERSKY-123',
    jira_ticket = 'SCRAPERSKY-123'
WHERE file_path = 'src/services/domain_content_service.py';

-- Update phantom files
UPDATE file_audit
SET notes = 'Part of Page Curation Workflow. Planned service for content processing. See Knowledge Base: Docs/Docs_10_Final_Audit/Knowledge_Base/Page-Curation-Workflow.md. JIRA: SCRAPERSKY-124',
    jira_ticket = 'SCRAPERSKY-124'
WHERE file_path = 'src/services/page_curation_service.py';

UPDATE file_audit
SET notes = 'Part of Page Curation Workflow. Planned scheduler for background processing. See Knowledge Base: Docs/Docs_10_Final_Audit/Knowledge_Base/Page-Curation-Workflow.md. JIRA: SCRAPERSKY-125',
    jira_ticket = 'SCRAPERSKY-125'
WHERE file_path = 'src/services/page_curation_scheduler.py';

-- Update phantom files with JIRA ticket references
UPDATE file_audit
SET notes = 'Part of Page Curation Workflow. Planned service for content processing. See JIRA: SCRAPERSKY-124',
    jira_ticket = 'SCRAPERSKY-124'
WHERE file_path = 'src/services/page_curation_service.py';

UPDATE file_audit
SET notes = 'Part of Page Curation Workflow. Planned scheduler for background processing. See JIRA: SCRAPERSKY-125',
    jira_ticket = 'SCRAPERSKY-125'
WHERE file_path = 'src/services/page_curation_scheduler.py';

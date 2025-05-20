-- Add orphan file to file_audit table
INSERT INTO file_audit (
    file_path,
    file_number,
    layer_number,
    status,
    workflows,
    notes,
    jira_ticket
) VALUES (
    'src/services/domain_content_service.py',
    (SELECT COALESCE(MAX(file_number), 0) + 1 FROM file_audit WHERE layer_number = 4),
    4,
    'NOVEL',
    ARRAY['WF4'],
    'Part of Page Curation Workflow. Initial content extraction service. See Knowledge Base: Docs/Docs_10_Final_Audit/Knowledge_Base/Page-Curation-Workflow.md',
    'SCRAPERSKY-123'
) ON CONFLICT (file_path) DO UPDATE SET
    notes = EXCLUDED.notes,
    jira_ticket = EXCLUDED.jira_ticket;

-- =============================================
-- ScraperSky File Audit System - Standard Queries
-- =============================================
-- Created: 2025-05-19
-- Author: David Shepherd
-- Description: Standard queries for the file_audit table

-- ======================
-- 1. Layer-Based Reports
-- ======================

-- 1.1 Count files by layer
SELECT layer_number, layer_name, COUNT(*) AS file_count
FROM file_audit
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- 1.2 Technical debt by layer
SELECT
  layer_number,
  layer_name,
  COUNT(*) AS total_files,
  COUNT(CASE WHEN has_technical_debt = true THEN 1 END) AS files_with_debt,
  ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) AS debt_percentage
FROM file_audit
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- 1.3 Audit progress by layer
SELECT
  layer_number,
  layer_name,
  COUNT(*) AS total_files,
  COUNT(CASE WHEN audit_status = 'NOT_STARTED' THEN 1 END) AS not_started,
  COUNT(CASE WHEN audit_status = 'IN_PROGRESS' THEN 1 END) AS in_progress,
  COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END) AS completed,
  ROUND(COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) AS completion_percentage
FROM file_audit
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- 1.4 Files in a specific layer
SELECT
  file_number,
  file_path,
  file_name,
  status,
  workflows,
  has_technical_debt,
  audit_status
FROM file_audit
WHERE layer_number = 1 -- Change to desired layer number (1-7)
ORDER BY file_number;


-- =======================
-- 2. Workflow-Based Reports
-- =======================

-- 2.1 Count files by workflow
SELECT
  unnest(workflows) AS workflow,
  COUNT(*) AS file_count
FROM file_audit
GROUP BY workflow
ORDER BY workflow;

-- 2.2 Files in a specific workflow
SELECT
  file_number,
  file_path,
  layer_number,
  layer_name,
  status,
  has_technical_debt,
  audit_status
FROM file_audit
WHERE 'WF1' = ANY(workflows) -- Change to desired workflow (WF1-WF7 or SYSTEM)
ORDER BY layer_number, file_number;

-- 2.3 Files shared between multiple workflows
SELECT
  file_number,
  file_path,
  layer_number,
  layer_name,
  status,
  workflows,
  array_length(workflows, 1) AS workflow_count
FROM file_audit
WHERE status = 'SHARED'
ORDER BY array_length(workflows, 1) DESC, layer_number, file_number;

-- 2.4 Workflows with the most files
SELECT
  workflow,
  COUNT(*) as file_count
FROM (
  SELECT unnest(workflows) as workflow
  FROM file_audit
) as workflow_files
GROUP BY workflow
ORDER BY file_count DESC;


-- =======================
-- 3. Technical Debt Reports
-- =======================

-- 3.1 All files with technical debt
SELECT
  file_number,
  file_path,
  layer_number,
  layer_name,
  status,
  workflows,
  technical_debt,
  jira_tickets
FROM file_audit
WHERE has_technical_debt = true
ORDER BY layer_number, file_number;

-- 3.2 Technical debt summary
SELECT
  COUNT(*) as total_files,
  COUNT(CASE WHEN has_technical_debt = true THEN 1 END) as debt_files,
  ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as debt_percentage
FROM file_audit;

-- 3.3 Files with specific technical debt issues
SELECT
  file_number,
  file_path,
  layer_number,
  layer_name,
  technical_debt
FROM file_audit
WHERE technical_debt ILIKE '%raw sql%' -- Change to search for specific issues
ORDER BY layer_number, file_number;

-- 3.4 Files with linked Jira tickets
SELECT
  file_number,
  file_path,
  jira_tickets,
  technical_debt
FROM file_audit
WHERE jira_tickets IS NOT NULL AND array_length(jira_tickets, 1) > 0
ORDER BY file_number;


-- =======================
-- 4. Status-Based Reports
-- =======================

-- 4.1 Count files by status type
SELECT status, COUNT(*) AS file_count
FROM file_audit
GROUP BY status
ORDER BY status;

-- 4.2 Audit progress summary
SELECT
  audit_status,
  COUNT(*) as file_count,
  ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM file_audit)::numeric * 100, 2) as percentage
FROM file_audit
GROUP BY audit_status
ORDER BY
  CASE
    WHEN audit_status = 'COMPLETED' THEN 1
    WHEN audit_status = 'IN_PROGRESS' THEN 2
    WHEN audit_status = 'NOT_STARTED' THEN 3
    ELSE 4
  END;


-- =======================
-- 5. Combined Analysis Reports
-- =======================

-- 5.1 Status and technical debt by workflow
SELECT
  workflow,
  COUNT(*) as total_files,
  COUNT(CASE WHEN has_technical_debt = true THEN 1 END) as debt_files,
  ROUND(COUNT(CASE WHEN has_technical_debt = true THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as debt_percentage,
  COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END) as completed_files,
  ROUND(COUNT(CASE WHEN audit_status = 'COMPLETED' THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as completion_percentage
FROM (
  SELECT
    file_number,
    has_technical_debt,
    audit_status,
    unnest(workflows) as workflow
  FROM file_audit
) as workflow_files
GROUP BY workflow
ORDER BY workflow;

-- 5.2 Layer and status distribution
SELECT
  layer_number,
  layer_name,
  COUNT(CASE WHEN status = 'NOVEL' THEN 1 END) as novel_files,
  COUNT(CASE WHEN status = 'SHARED' THEN 1 END) as shared_files,
  COUNT(CASE WHEN status = 'SYSTEM' THEN 1 END) as system_files,
  COUNT(*) as total_files
FROM file_audit
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- 5.3 File number availability by layer
WITH numbers AS (
  SELECT generate_series(1, 999) AS num
),
layer1_used AS (
  SELECT
    SUBSTRING(file_number, 2, 3)::int AS used_num
  FROM file_audit
  WHERE layer_number = 1
)
SELECT
  LPAD(num::text, 3, '0') AS available_number,
  CONCAT('0', LPAD(num::text, 3, '0')) AS available_file_number
FROM numbers
WHERE num NOT IN (SELECT used_num FROM layer1_used)
  AND num <= 999
ORDER BY num
LIMIT 10; -- Shows first 10 available numbers for Layer 1
-- Change the layer_number = 1 and the CONCAT('0', ...) prefix for other layers


-- =======================
-- 6. Orphan Detection Queries
-- =======================

-- 6.1 Get potential file path patterns for orphan detection
SELECT
  regexp_replace(file_path, '[^/]+\.py$', '', 'g') AS directory_path,
  COUNT(*) AS file_count
FROM file_audit
GROUP BY directory_path
ORDER BY file_count DESC;

-- =======================
-- 7. Update Queries
-- =======================

-- 7.1 Mark a file as having technical debt
UPDATE file_audit
SET
  has_technical_debt = true,
  technical_debt = 'Description of the technical debt issue',
  jira_tickets = ARRAY['SCRSKY-123'],
  updated_at = NOW()
WHERE file_number = '0001'; -- Replace with target file number

-- 7.2 Update audit status for a file
UPDATE file_audit
SET
  audit_status = 'IN_PROGRESS', -- Options: 'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED'
  updated_at = NOW()
WHERE file_number = '0001'; -- Replace with target file number

-- 7.3 Mark a completed audit
UPDATE file_audit
SET
  audit_status = 'COMPLETED',
  audit_date = NOW(),
  audited_by = 'David Shepherd',
  notes = 'File fully complies with architectural standards',
  updated_at = NOW()
WHERE file_number = '0001'; -- Replace with target file number

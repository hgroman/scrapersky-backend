-- Migration to create approved_scan_directories table for controlled document vectorization
-- This creates a table to track which directories should be scanned for documents

-- Create approved directories table if it doesn't exist
CREATE TABLE IF NOT EXISTS approved_scan_directories (
  id SERIAL PRIMARY KEY,
  directory_path TEXT NOT NULL UNIQUE,
  description TEXT,
  active BOOLEAN DEFAULT true,
  approved_by TEXT,
  approved_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_approved_scan_directories_path ON approved_scan_directories(directory_path);

-- Create document candidates view
CREATE OR REPLACE VIEW document_candidates AS
SELECT
  f.path AS file_path,
  f.name AS filename,
  a.directory_path AS approved_directory,
  a.active AS directory_active,
  CASE WHEN f.name LIKE 'v\_%' THEN true ELSE false END AS is_marked
FROM 
  approved_scan_directories a
CROSS JOIN LATERAL (
  SELECT * FROM pg_ls_dir(a.directory_path) AS name
) AS dirs
CROSS JOIN LATERAL (
  SELECT 
    a.directory_path || '/' || dirs.name AS path,
    dirs.name AS name
  WHERE
    dirs.name LIKE '%.md'
) AS f
WHERE
  a.active = true;

-- Function to get vectorization candidates in a specific directory
CREATE OR REPLACE FUNCTION get_vectorization_candidates(dir_path TEXT)
RETURNS TABLE (
  file_path TEXT,
  filename TEXT,
  is_marked BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    dc.file_path,
    dc.filename,
    dc.is_marked
  FROM
    document_candidates dc
  WHERE
    dc.approved_directory = dir_path
  ORDER BY
    dc.is_marked, dc.filename;
END;
$$ LANGUAGE plpgsql;

-- Function to get all approved directories with document counts
CREATE OR REPLACE FUNCTION get_directory_stats()
RETURNS TABLE (
  directory_path TEXT,
  description TEXT,
  active BOOLEAN,
  total_documents INT,
  marked_documents INT,
  pending_documents INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    a.directory_path,
    a.description,
    a.active,
    COUNT(DISTINCT dc.file_path)::INT AS total_documents,
    COUNT(DISTINCT CASE WHEN dc.is_marked THEN dc.file_path ELSE NULL END)::INT AS marked_documents,
    COUNT(DISTINCT CASE WHEN NOT dc.is_marked THEN dc.file_path ELSE NULL END)::INT AS pending_documents
  FROM
    approved_scan_directories a
  LEFT JOIN
    document_candidates dc ON a.directory_path = dc.approved_directory
  GROUP BY
    a.directory_path, a.description, a.active
  ORDER BY
    a.directory_path;
END;
$$ LANGUAGE plpgsql;

-- Add initial approved directories
INSERT INTO approved_scan_directories (directory_path, description, approved_by)
VALUES 
  ('Docs/Docs_6_Architecture_and_Status', 'Architecture documentation and system status', 'system_init'),
  ('Docs/Docs_18_Vector_Operations', 'Full vector operations directory', 'system_init'),
  ('Docs/Docs_18_Vector_Operations/Documentation', 'Vector database documentation', 'system_init'),
  ('Docs/Docs_1_AI_GUIDES', 'AI guides and reference documentation', 'system_init')
ON CONFLICT (directory_path) DO NOTHING;

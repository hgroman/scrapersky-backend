-- ============================================
-- V7 MIGRATION TRACKING DATABASE INFRASTRUCTURE
-- ============================================
-- Directive: AD_005_V7_Database_Infrastructure
-- Created: 2025-08-07
-- Author: V7 Conductor Persona (per Architectural Directive)
-- Status: PENDING APPROVAL - DO NOT EXECUTE WITHOUT AUTHORIZATION
-- ============================================

-- GUARDIAN'S PARADOX SAFEGUARD:
-- These scripts are documented but NOT to be executed without explicit approval.
-- Database modifications are irreversible. Code can be reverted, databases cannot.

-- ============================================
-- SECTION 1: MASTER WORKFLOW TRACKING TABLE
-- ============================================
-- Purpose: Track the 7 phases of V7 migration with approval gates
CREATE TABLE IF NOT EXISTS v7_migration_workflow (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase_number INTEGER NOT NULL,
    phase_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    lead_persona VARCHAR(100) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    approval_status VARCHAR(50),
    approved_by VARCHAR(100),
    approval_notes TEXT,
    deliverables JSONB,
    blockers JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT phase_status_check CHECK (status IN (
        'not_started', 'in_progress', 'review', 'approved',
        'completed', 'blocked', 'rolled_back'
    ))
);

-- Initial phase data insertion
INSERT INTO v7_migration_workflow (phase_number, phase_name, lead_persona) VALUES
(1, 'Assessment', 'The Architect'),
(2, 'Design', 'Layer Guardians'),
(3, 'Review', 'Workflow Personas'),
(4, 'Database', 'DB Team + Architect'),
(5, 'Implementation', 'Dev Team'),
(6, 'Validation', 'Test Sentinel'),
(7, 'Retirement', 'The Architect')
ON CONFLICT DO NOTHING;

-- ============================================
-- SECTION 2: ENHANCED FILE AUDIT FOR V7
-- ============================================
-- Purpose: Extend existing file_audit table with V7-specific tracking
-- Note: Using ALTER TABLE to preserve existing data
ALTER TABLE file_audit
ADD COLUMN IF NOT EXISTS v7_workflow_status VARCHAR(50) DEFAULT 'pending_assessment',
ADD COLUMN IF NOT EXISTS v7_target_name VARCHAR(500),  -- New WF*_V7_L*_* name
ADD COLUMN IF NOT EXISTS v7_database_enums JSONB,      -- Which ENUMs it uses
ADD COLUMN IF NOT EXISTS v7_enum_mappings JSONB,       -- Old ENUM -> V7 ENUM mapping
ADD COLUMN IF NOT EXISTS v7_dependencies TEXT[],       -- What files depend on this
ADD COLUMN IF NOT EXISTS v7_dependents TEXT[],         -- What this depends on
ADD COLUMN IF NOT EXISTS v7_impact_score INTEGER,      -- 1-10 risk score
ADD COLUMN IF NOT EXISTS v7_review_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS v7_reviewed_by VARCHAR(100)[],
ADD COLUMN IF NOT EXISTS v7_implementation_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS v7_test_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS v7_retirement_date DATE;

-- Add constraint for v7_workflow_status values
ALTER TABLE file_audit
ADD CONSTRAINT v7_workflow_status_check CHECK (
    v7_workflow_status IN (
        'pending_assessment', 'assessed', 'designed', 'approved',
        'implementing', 'testing', 'migrated', 'retired'
    )
);

-- ============================================
-- SECTION 3: ENUM MAPPING AND CONSOLIDATION
-- ============================================
-- Purpose: Track ENUM consolidation to eliminate 45+ duplicates
CREATE TABLE IF NOT EXISTS v7_enum_migrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_enum_name VARCHAR(100) NOT NULL,
    current_enum_values TEXT[] NOT NULL,
    v7_enum_name VARCHAR(100) NOT NULL,
    v7_enum_values TEXT[] NOT NULL,
    consolidates_with VARCHAR(100)[],  -- Other ENUMs being merged
    affected_tables VARCHAR(100)[] NOT NULL,
    affected_columns JSONB NOT NULL,  -- {table: [columns]}
    migration_script TEXT,
    rollback_script TEXT,
    status VARCHAR(50) DEFAULT 'proposed',
    risk_level VARCHAR(20),
    approved_by VARCHAR(100),
    implemented_at TIMESTAMP,
    validated_at TIMESTAMP,
    retired_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT status_check CHECK (status IN (
        'proposed', 'approved', 'implemented',
        'validated', 'retired', 'rolled_back'
    )),
    CONSTRAINT risk_level_check CHECK (risk_level IN (
        'low', 'medium', 'high', 'critical'
    ))
);

-- Document known ENUM duplications for consolidation
INSERT INTO v7_enum_migrations (
    current_enum_name, 
    current_enum_values,
    v7_enum_name,
    v7_enum_values,
    consolidates_with,
    affected_tables,
    affected_columns,
    risk_level,
    status
) VALUES 
(
    'contact_curation_status',
    ARRAY['Complete', 'Error', 'New', 'Processing', 'Queued', 'Skipped'],
    'v7_contact_status',
    ARRAY['complete', 'error', 'new', 'processing', 'queued', 'skipped'],
    ARRAY['contactcurationstatus'],
    ARRAY['contacts'],
    '{"contacts": ["curation_status"]}'::jsonb,
    'high',
    'proposed'
),
(
    'contactcurationstatus',
    ARRAY['Complete', 'Error', 'New', 'Processing', 'Queued', 'Skipped'],
    'v7_contact_status',
    ARRAY['complete', 'error', 'new', 'processing', 'queued', 'skipped'],
    ARRAY['contact_curation_status'],
    ARRAY['contacts'],
    '{"contacts": ["status"]}'::jsonb,
    'high',
    'proposed'
)
ON CONFLICT DO NOTHING;

-- ============================================
-- SECTION 4: GLOBAL IMPACT TRACKING
-- ============================================
-- Purpose: Track cross-layer impacts of V7 changes
CREATE TABLE IF NOT EXISTS v7_global_impacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    change_type VARCHAR(50) NOT NULL,  -- 'enum', 'file', 'api', 'schema'
    change_detail JSONB NOT NULL,
    affected_workflows VARCHAR(10)[] NOT NULL,  -- ['WF1', 'WF2', etc]
    affected_layers INTEGER[] NOT NULL,  -- [1, 2, 3, etc]
    impact_description TEXT NOT NULL,
    risk_assessment VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'critical'
    mitigation_strategy TEXT,
    reviewed_by_personas VARCHAR(100)[],
    approval_status VARCHAR(50) DEFAULT 'pending',
    implementation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT change_type_check CHECK (change_type IN (
        'enum', 'file', 'api', 'schema', 'config', 'dependency'
    )),
    CONSTRAINT risk_check CHECK (risk_assessment IN (
        'low', 'medium', 'high', 'critical'
    )),
    CONSTRAINT approval_check CHECK (approval_status IN (
        'pending', 'reviewing', 'approved', 'rejected', 'implemented'
    ))
);

-- ============================================
-- SECTION 5: SUB-WORKFLOW PROGRESS TRACKING
-- ============================================
-- Purpose: Granular task tracking within each phase
CREATE TABLE IF NOT EXISTS v7_subworkflow_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_phase INTEGER NOT NULL,
    task_number INTEGER NOT NULL,
    task_name VARCHAR(200) NOT NULL,
    responsible_persona VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    dart_task_id VARCHAR(100),
    dart_task_url TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    blockers TEXT[],
    dependencies UUID[],  -- Other tasks that must complete first
    deliverable_urls TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_phase, task_number),
    CONSTRAINT task_status_check CHECK (status IN (
        'pending', 'in_progress', 'blocked', 'review',
        'completed', 'cancelled', 'deferred'
    )),
    FOREIGN KEY (parent_phase) REFERENCES v7_migration_workflow(phase_number)
);

-- ============================================
-- SECTION 6: V7 TEST RESULTS TRACKING
-- ============================================
-- Purpose: Track test results for V7 components
CREATE TABLE IF NOT EXISTS v7_test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_type VARCHAR(50) NOT NULL,  -- 'unit', 'integration', 'system', 'performance'
    component_tested VARCHAR(500) NOT NULL,
    v7_file_path VARCHAR(500),
    test_status VARCHAR(20) NOT NULL,  -- 'pass', 'fail', 'skip'
    error_details TEXT,
    performance_metrics JSONB,
    backwards_compatible BOOLEAN,
    tested_by VARCHAR(100),
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retest_required BOOLEAN DEFAULT FALSE,
    notes TEXT,
    CONSTRAINT test_type_check CHECK (test_type IN (
        'unit', 'integration', 'system', 'performance', 'regression', 'smoke'
    )),
    CONSTRAINT test_status_check CHECK (test_status IN (
        'pass', 'fail', 'skip', 'error', 'timeout'
    ))
);

-- ============================================
-- SECTION 7: PERFORMANCE INDEXES
-- ============================================
-- Purpose: Optimize query performance for monitoring
CREATE INDEX IF NOT EXISTS idx_v7_workflow_status ON v7_migration_workflow(status);
CREATE INDEX IF NOT EXISTS idx_file_audit_v7_status ON file_audit(v7_workflow_status);
CREATE INDEX IF NOT EXISTS idx_enum_migrations_status ON v7_enum_migrations(status);
CREATE INDEX IF NOT EXISTS idx_global_impacts_risk ON v7_global_impacts(risk_assessment);
CREATE INDEX IF NOT EXISTS idx_subworkflow_status ON v7_subworkflow_tasks(status);
CREATE INDEX IF NOT EXISTS idx_test_results_status ON v7_test_results(test_status);

-- ============================================
-- SECTION 8: MONITORING VIEWS
-- ============================================
-- Purpose: Provide easy-to-query dashboard views
CREATE OR REPLACE VIEW v7_migration_dashboard AS
SELECT
    mw.phase_number,
    mw.phase_name,
    mw.status as phase_status,
    mw.lead_persona,
    COUNT(DISTINCT st.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN st.status = 'completed' THEN st.id END) as completed_tasks,
    COUNT(DISTINCT fa.id) FILTER (WHERE fa.v7_workflow_status = 'migrated') as migrated_files,
    COUNT(DISTINCT em.id) FILTER (WHERE em.status = 'implemented') as enum_migrations,
    MAX(gi.risk_assessment) as highest_risk
FROM v7_migration_workflow mw
LEFT JOIN v7_subworkflow_tasks st ON mw.phase_number = st.parent_phase
LEFT JOIN file_audit fa ON fa.v7_workflow_status IS NOT NULL
LEFT JOIN v7_enum_migrations em ON em.status != 'proposed'
LEFT JOIN v7_global_impacts gi ON gi.approval_status = 'approved'
GROUP BY mw.phase_number, mw.phase_name, mw.status, mw.lead_persona
ORDER BY mw.phase_number;

-- View for ENUM consolidation status
CREATE OR REPLACE VIEW v7_enum_consolidation_status AS
SELECT 
    v7_enum_name,
    COUNT(*) as enums_to_consolidate,
    array_agg(current_enum_name) as source_enums,
    status,
    risk_level,
    COUNT(DISTINCT unnest(affected_tables)) as affected_table_count
FROM v7_enum_migrations
GROUP BY v7_enum_name, status, risk_level
ORDER BY risk_level DESC, v7_enum_name;

-- View for file migration readiness
CREATE OR REPLACE VIEW v7_file_migration_readiness AS
SELECT 
    layer_number,
    layer_name,
    COUNT(*) as total_files,
    COUNT(*) FILTER (WHERE v7_workflow_status = 'pending_assessment') as pending,
    COUNT(*) FILTER (WHERE v7_workflow_status = 'assessed') as assessed,
    COUNT(*) FILTER (WHERE v7_workflow_status = 'designed') as designed,
    COUNT(*) FILTER (WHERE v7_workflow_status = 'migrated') as migrated,
    AVG(v7_impact_score) as avg_impact_score
FROM file_audit
WHERE file_path LIKE '%WF%'
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- ============================================
-- SECTION 9: ROLLBACK SCRIPTS
-- ============================================
-- Purpose: Emergency rollback capability (Guardian's Paradox requirement)

-- Rollback script (DO NOT EXECUTE unless emergency rollback needed)
/*
-- ROLLBACK: Remove V7 columns from file_audit
ALTER TABLE file_audit
DROP COLUMN IF EXISTS v7_workflow_status,
DROP COLUMN IF EXISTS v7_target_name,
DROP COLUMN IF EXISTS v7_database_enums,
DROP COLUMN IF EXISTS v7_enum_mappings,
DROP COLUMN IF EXISTS v7_dependencies,
DROP COLUMN IF EXISTS v7_dependents,
DROP COLUMN IF EXISTS v7_impact_score,
DROP COLUMN IF EXISTS v7_review_status,
DROP COLUMN IF EXISTS v7_reviewed_by,
DROP COLUMN IF EXISTS v7_implementation_status,
DROP COLUMN IF EXISTS v7_test_status,
DROP COLUMN IF EXISTS v7_retirement_date;

-- ROLLBACK: Drop V7 tables
DROP VIEW IF EXISTS v7_migration_dashboard CASCADE;
DROP VIEW IF EXISTS v7_enum_consolidation_status CASCADE;
DROP VIEW IF EXISTS v7_file_migration_readiness CASCADE;
DROP TABLE IF EXISTS v7_test_results CASCADE;
DROP TABLE IF EXISTS v7_subworkflow_tasks CASCADE;
DROP TABLE IF EXISTS v7_global_impacts CASCADE;
DROP TABLE IF EXISTS v7_enum_migrations CASCADE;
DROP TABLE IF EXISTS v7_migration_workflow CASCADE;
*/

-- ============================================
-- END OF V7 DATABASE INFRASTRUCTURE SCRIPT
-- ============================================
-- REMINDER: DO NOT EXECUTE WITHOUT EXPLICIT APPROVAL FROM THE ARCHITECT
-- This script is for documentation and review purposes only
# ARCHITECTURAL DIRECTIVE 005: V7 DATABASE INFRASTRUCTURE CREATION

**TO:** Claude (Designated AI Agent for Database Operations)
**FROM:** The Architect
**DATE:** 2025-08-06
**SUBJECT: MANDATORY CREATION OF V7 MIGRATION DATABASE INFRASTRUCTURE**

---

### ARTICLE 1: MANDATE & PURPOSE

1.1. The V7 Perfect Migration is a critical, system-wide initiative designed to rectify architectural inconsistencies, consolidate naming conventions, and align code with database reality, all while adhering to the principles of the Guardian's Paradox.

1.2. A foundational component of this migration is a robust, auditable database infrastructure for tracking progress, changes, and impacts. This infrastructure will serve as the single source of truth for the entire V7 journey.

1.3. Your mission is to meticulously design and document the SQL scripts for creating these essential tracking tables, and to outline the workflow for their management.

---

### ARTICLE 2: PRIMARY DIRECTIVES

2.1. You are hereby directed to **design and document the SQL scripts** for the creation of the V7 migration tracking tables as specified in Article 3.

2.2. You are to **create the `DATABASE_WORKFLOW.md` document** within the `Docs/V7_Migration/04_Database_Phase/` directory, detailing the process for managing these database components as specified in Article 4.

2.3. **Precision is Paramount:** The SQL scripts must exactly match the schema provided in Article 3. Any deviation will result in rejection.

2.4. **No Execution Without Approval:** You are to design and document the scripts. **DO NOT execute these SQL scripts against the Supabase database without explicit approval from The Architect.**

---

### ARTICLE 3: V7 DATABASE SCHEMA REFERENCE

Your SQL scripts must create the following tables and enhancements:

```sql
-- ============================================
-- V7 MIGRATION TRACKING DATABASE ENHANCEMENTS
-- ============================================

-- 1. Master Workflow Tracking Table
CREATE TABLE v7_migration_workflow (
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

-- 2. Enhanced File Audit for V7 Tracking
ALTER TABLE file_audit
ADD COLUMN v7_workflow_status VARCHAR(50) DEFAULT 'pending_assessment',
ADD COLUMN v7_target_name VARCHAR(500),  -- New WF*_V7_L*_* name
ADD COLUMN v7_database_enums JSONB,      -- Which ENUMs it uses
ADD COLUMN v7_enum_mappings JSONB,       -- Old ENUM -> V7 ENUM mapping
ADD COLUMN v7_dependencies TEXT[],       -- What files depend on this
ADD COLUMN v7_dependents TEXT[],         -- What this depends on
ADD COLUMN v7_impact_score INTEGER,      -- 1-10 risk score
ADD COLUMN v7_review_status VARCHAR(50),
ADD COLUMN v7_reviewed_by VARCHAR(100)[],
ADD COLUMN v7_implementation_status VARCHAR(50),
ADD COLUMN v7_test_status VARCHAR(50),
ADD COLUMN v7_retirement_date DATE;

-- 3. ENUM Mapping and Consolidation Table
CREATE TABLE v7_enum_migrations (
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
    ))
);

-- 4. Global Impact Tracking Table
CREATE TABLE v7_global_impacts (
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Sub-Workflow Progress Tracking
CREATE TABLE v7_subworkflow_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_phase INTEGER REFERENCES v7_migration_workflow(phase_number),
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
    UNIQUE(parent_phase, task_number)
);

-- 6. V7 Test Results Tracking
CREATE TABLE v7_test_results (
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
    notes TEXT
);

-- 7. Create indexes for performance
CREATE INDEX idx_v7_workflow_status ON v7_migration_workflow(status);
CREATE INDEX idx_file_audit_v7_status ON file_audit(v7_workflow_status);
CREATE INDEX idx_enum_migrations_status ON v7_enum_migrations(status);
CREATE INDEX idx_global_impacts_risk ON v7_global_impacts(risk_assessment);
CREATE INDEX idx_subworkflow_status ON v7_subworkflow_tasks(status);
CREATE INDEX idx_test_results_status ON v7_test_results(test_status);

-- 8. Create views for easy monitoring
CREATE VIEW v7_migration_dashboard AS
SELECT
    mw.phase_number,
    mw.phase_name,
    mw.status as phase_status,
    mw.lead_persona,
    COUNT(DISTINCT st.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN st.status = 'completed' THEN st.id END) as
completed_tasks,
    COUNT(DISTINCT CASE WHEN fa.v7_workflow_status = 'completed' THEN fa.id END) as
migrated_files,
    COUNT(DISTINCT em.id) as enum_migrations,
    MAX(gi.risk_assessment) as highest_risk
FROM v7_migration_workflow mw
LEFT JOIN v7_subworkflow_tasks st ON mw.phase_number = st.parent_phase
LEFT JOIN file_audit fa ON fa.v7_workflow_status IS NOT NULL
LEFT JOIN v7_enum_migrations em ON em.status != 'proposed'
LEFT JOIN v7_global_impacts gi ON gi.approval_status = 'approved'
GROUP BY mw.phase_number, mw.phase_name, mw.status, mw.lead_persona
ORDER BY mw.phase_number;
```

---

### ARTICLE 4: DOCUMENTATION REQUIREMENTS

You must create the `DATABASE_WORKFLOW.md` document at `Docs/V7_Migration/04_Database_Phase/DATABASE_WORKFLOW.md`. This document must detail:

4.1. **Purpose:** The role of the database phase in the V7 migration.
4.2. **Task Breakdown:** A step-by-step guide for database creation, data migration, and rollback procedures.
4.3. **Responsible Personas:** Clearly identify which personas are responsible for each task within this phase.
4.4. **Verification Steps:** How to verify the successful creation and population of the V7 tracking tables.
4.5. **Error Handling:** Protocols for addressing issues during database operations.
4.6. **SQL Script References:** Explicitly reference the SQL scripts you will create as part of this directive.

---

### ARTICLE 5: JUDGEMENT & REPORTING PROTOCOL

5.1. Upon completion of this directive, you will file a single, formal report in your designated DART Journal.
5.2. The report shall be titled: `COMPLETION OF AD_005: V7 DATABASE INFRASTRUCTURE - [DATE]`.
5.3. Your report must confirm:
    *   The successful creation and documentation of the SQL scripts.
    *   The successful creation of the `DATABASE_WORKFLOW.md` document.
    *   Your readiness to execute the SQL scripts upon approval from The Architect.

---

*This directive is issued under the full authority of the Architect. Precision and adherence to the Guardian's Paradox safeguards are paramount.*
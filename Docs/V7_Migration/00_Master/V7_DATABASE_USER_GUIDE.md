# V7 Database Infrastructure User Guide
## For The V7 Conductor Persona (and Future Self)
## Version: 1.0
## Created: 2025-08-07
## Purpose: Complete operational manual for V7 migration tracking database

---

## Table of Contents
1. [Why This Database Exists](#1-why-this-database-exists)
2. [Database Architecture Overview](#2-database-architecture-overview)
3. [How to Use Each Table](#3-how-to-use-each-table)
4. [Dashboard Queries](#4-dashboard-queries)
5. [Workflow Integration](#5-workflow-integration)
6. [DART Integration Strategy](#6-dart-integration-strategy)
7. [Daily Conductor Operations](#7-daily-conductor-operations)
8. [Troubleshooting Guide](#8-troubleshooting-guide)

---

## 1. Why This Database Exists

### The Guardian's Paradox Lesson
This database exists because attempting perfection in isolation destroyed 3 months of work. The V7 tracking infrastructure ensures:
- **Coordination over initiative** - Every change is tracked and reviewed
- **Global awareness** - Impact assessments across all layers
- **Reversibility** - Complete audit trail for rollback
- **Reality over theory** - Database state is truth

### Core Purpose
As the V7 Conductor, this database is your **operational command center**. It tracks:
- Where we are (phase status)
- What's being done (task tracking)
- Who's responsible (persona assignments)
- What could break (impact assessments)
- How to roll back (migration scripts)

---

## 2. Database Architecture Overview

### Table Relationships
```
v7_migration_workflow (Master)
    ↓
v7_subworkflow_tasks (Details)
    ↓
file_audit (with V7 columns)
    ↓
v7_enum_migrations + v7_global_impacts + v7_test_results
```

### The Six Core Tables

| Table | Purpose | Key Fields | When to Update |
|-------|---------|------------|----------------|
| `v7_migration_workflow` | Track 7 phases | status, approval_status, blockers | Phase transitions |
| `v7_subworkflow_tasks` | Granular tasks | status, dart_task_id, dependencies | Task completion |
| `file_audit` (+V7 cols) | File migration | v7_workflow_status, v7_target_name | File processing |
| `v7_enum_migrations` | ENUM consolidation | status, risk_level, migration_script | ENUM analysis |
| `v7_global_impacts` | Cross-layer impacts | risk_assessment, approval_status | Impact discovery |
| `v7_test_results` | Test validation | test_status, backwards_compatible | Test execution |

---

## 3. How to Use Each Table

### 3.1 v7_migration_workflow - The Master Control

**Purpose:** Track the 7-phase journey

**Key Operations:**
```sql
-- Update phase status when starting
UPDATE v7_migration_workflow 
SET status = 'in_progress',
    started_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE phase_number = 1;

-- Record phase blockers
UPDATE v7_migration_workflow 
SET blockers = jsonb_build_array(
    jsonb_build_object(
        'issue', 'Missing ENUM documentation',
        'raised_by', 'Layer 1 Guardian',
        'severity', 'high'
    )
)
WHERE phase_number = 1;

-- Mark phase complete with approval
UPDATE v7_migration_workflow 
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP,
    approval_status = 'approved',
    approved_by = 'The Architect',
    approval_notes = 'All deliverables verified'
WHERE phase_number = 1;
```

**Review Gate Enforcement:**
```sql
-- Check if ready for next phase
SELECT 
    phase_number,
    phase_name,
    status,
    approval_status,
    CASE 
        WHEN approval_status = 'approved' THEN 'Ready for next phase'
        ELSE 'Awaiting approval'
    END as gate_status
FROM v7_migration_workflow
WHERE phase_number = 1;
```

### 3.2 v7_subworkflow_tasks - The Task Tracker

**Purpose:** Track individual work items within phases

**Creating Tasks from Work Orders:**
```sql
-- Create task when issuing work order
INSERT INTO v7_subworkflow_tasks (
    parent_phase,
    task_number,
    task_name,
    responsible_persona,
    status,
    dart_task_id,
    notes
) VALUES (
    1,  -- Assessment phase
    1,
    'Document all duplicate ENUMs',
    'Layer 1 Data Sentinel',
    'pending',
    'DART_TASK_123',
    'Work order issued 2025-08-07'
);

-- Update when persona reports completion
UPDATE v7_subworkflow_tasks
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP,
    deliverable_urls = ARRAY['https://dart.ai/doc/xyz']
WHERE parent_phase = 1 AND task_number = 1;
```

**Dependency Management:**
```sql
-- Set task dependencies
UPDATE v7_subworkflow_tasks
SET dependencies = ARRAY[
    (SELECT id FROM v7_subworkflow_tasks WHERE parent_phase = 1 AND task_number = 1)
]
WHERE parent_phase = 1 AND task_number = 2;

-- Check if dependencies met
SELECT 
    task_name,
    status,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM v7_subworkflow_tasks t2
            WHERE t2.id = ANY(t1.dependencies)
            AND t2.status != 'completed'
        ) THEN 'Blocked by dependencies'
        ELSE 'Ready to start'
    END as readiness
FROM v7_subworkflow_tasks t1
WHERE parent_phase = 1;
```

### 3.3 file_audit - The File Transformation Tracker

**Purpose:** Track every file's journey to V7 compliance

**File Assessment:**
```sql
-- Mark files for V7 migration
UPDATE file_audit
SET v7_workflow_status = 'assessed',
    v7_target_name = 'WF7_V7_L1_1of1_ContactModel.py',
    v7_impact_score = 8,
    v7_database_enums = '["contact_curation_status", "contactprocessingstatus"]'::jsonb
WHERE file_path LIKE '%contact.py';

-- Find high-impact files needing attention
SELECT 
    file_path,
    v7_target_name,
    v7_impact_score,
    v7_workflow_status
FROM file_audit
WHERE v7_impact_score >= 7
AND v7_workflow_status != 'migrated'
ORDER BY v7_impact_score DESC;
```

### 3.4 v7_enum_migrations - The ENUM Consolidator

**Purpose:** Track consolidation of 45+ duplicate ENUMs

**ENUM Analysis:**
```sql
-- Document ENUM consolidation plan
INSERT INTO v7_enum_migrations (
    current_enum_name,
    current_enum_values,
    v7_enum_name,
    v7_enum_values,
    consolidates_with,
    affected_tables,
    affected_columns,
    risk_level,
    migration_script,
    rollback_script
) VALUES (
    'contact_curation_status',
    ARRAY['Complete', 'Error', 'New', 'Processing', 'Queued', 'Skipped'],
    'v7_contact_status',
    ARRAY['complete', 'error', 'new', 'processing', 'queued', 'skipped'],
    ARRAY['contactcurationstatus'],
    ARRAY['contacts'],
    '{"contacts": ["curation_status"]}'::jsonb,
    'high',
    '-- Migration script here',
    '-- Rollback script here'
);

-- Track approval and implementation
UPDATE v7_enum_migrations
SET status = 'approved',
    approved_by = 'The Architect'
WHERE v7_enum_name = 'v7_contact_status';
```

### 3.5 v7_global_impacts - The Risk Assessor

**Purpose:** Document cross-layer impacts of changes

**Impact Documentation:**
```sql
-- Record discovered impact
INSERT INTO v7_global_impacts (
    change_type,
    change_detail,
    affected_workflows,
    affected_layers,
    impact_description,
    risk_assessment,
    mitigation_strategy
) VALUES (
    'enum',
    '{"from": "contact_curation_status", "to": "v7_contact_status"}'::jsonb,
    ARRAY['WF4', 'WF7'],
    ARRAY[1, 3, 4],
    'ENUM change affects domain curation and page extraction workflows',
    'high',
    'Implement compatibility layer during transition'
);
```

### 3.6 v7_test_results - The Validation Tracker

**Purpose:** Track test results for migrated components

**Test Recording:**
```sql
-- Record test results
INSERT INTO v7_test_results (
    test_type,
    component_tested,
    v7_file_path,
    test_status,
    backwards_compatible,
    tested_by
) VALUES (
    'integration',
    'Contact Model',
    'src/models/WF7_V7_L1_1of1_ContactModel.py',
    'pass',
    true,
    'Test Sentinel'
);
```

---

## 4. Dashboard Queries

### 4.1 Executive Dashboard
```sql
-- Master migration status
SELECT * FROM v7_migration_dashboard;

-- Current phase details
SELECT 
    phase_name,
    status,
    lead_persona,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - started_at)) as days_in_progress,
    jsonb_array_length(blockers) as blocker_count
FROM v7_migration_workflow
WHERE status = 'in_progress';
```

### 4.2 Daily Status Report Query
```sql
-- Daily progress report
WITH daily_metrics AS (
    SELECT 
        -- Phase progress
        (SELECT COUNT(*) FROM v7_migration_workflow WHERE status = 'completed') as phases_complete,
        
        -- Task progress today
        (SELECT COUNT(*) FROM v7_subworkflow_tasks 
         WHERE DATE(completed_at) = CURRENT_DATE) as tasks_completed_today,
        
        -- Files migrated today
        (SELECT COUNT(*) FROM file_audit 
         WHERE v7_workflow_status = 'migrated' 
         AND DATE(updated_at) = CURRENT_DATE) as files_migrated_today,
        
        -- Active blockers
        (SELECT COUNT(*) FROM v7_subworkflow_tasks 
         WHERE status = 'blocked') as active_blockers
)
SELECT 
    phases_complete || '/7 phases' as phase_progress,
    tasks_completed_today || ' tasks' as today_completions,
    files_migrated_today || ' files' as today_migrations,
    active_blockers || ' blockers' as current_blockers
FROM daily_metrics;
```

### 4.3 Risk Assessment Dashboard
```sql
-- High-risk items needing attention
SELECT 
    'ENUMs' as category,
    COUNT(*) as count,
    MAX(risk_level) as highest_risk
FROM v7_enum_migrations
WHERE status != 'implemented'
AND risk_level IN ('high', 'critical')

UNION ALL

SELECT 
    'Global Impacts',
    COUNT(*),
    MAX(risk_assessment)
FROM v7_global_impacts
WHERE approval_status = 'pending'
AND risk_assessment IN ('high', 'critical');
```

---

## 5. Workflow Integration

### 5.1 Work Order → Database Flow
```
1. Conductor creates work order
   → INSERT into v7_subworkflow_tasks
   
2. Persona executes work
   → (No database update yet)
   
3. Persona files report in DART
   → Report includes completion data
   
4. Conductor reviews report
   → UPDATE v7_subworkflow_tasks with completion
   
5. Conductor updates phase status if needed
   → UPDATE v7_migration_workflow
```

### 5.2 Review Gate Process
```sql
-- Step 1: Check all tasks complete for phase
SELECT 
    parent_phase,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
    COUNT(*) = COUNT(*) FILTER (WHERE status = 'completed') as ready_for_review
FROM v7_subworkflow_tasks
WHERE parent_phase = 1
GROUP BY parent_phase;

-- Step 2: Request approval
UPDATE v7_migration_workflow
SET status = 'review',
    deliverables = '{"assessment_report": "url", "enum_analysis": "url"}'::jsonb
WHERE phase_number = 1;

-- Step 3: Record approval
UPDATE v7_migration_workflow
SET approval_status = 'approved',
    approved_by = 'The Architect',
    approval_notes = 'Assessment complete, proceed to Design'
WHERE phase_number = 1;
```

---

## 6. DART Integration Strategy

### 6.1 DART ↔ Database Synchronization

**Concept:** DART is for human collaboration, Database is for systematic tracking

```sql
-- When creating DART task
INSERT INTO v7_subworkflow_tasks (dart_task_id, dart_task_url, ...)
VALUES ('4HWR1cjz7sPf', 'https://app.dartai.com/t/4HWR1cjz7sPf', ...);

-- When updating from DART report
UPDATE v7_subworkflow_tasks
SET deliverable_urls = deliverable_urls || ARRAY['dart_doc_url']
WHERE dart_task_id = '4HWR1cjz7sPf';
```

### 6.2 DART Folder Structure Mapping
```
DART Folders                    → Database Tables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V7 Conductor Persona Tasks     → v7_subworkflow_tasks
V7 Conductor Persona Docs      → deliverable_urls in tasks
V7 Migration Docs              → Master documentation
Phase-specific folders         → Filtered by parent_phase
```

---

## 7. Daily Conductor Operations

### 7.1 Morning Status Check (5 minutes)
```sql
-- Run master dashboard query
SELECT * FROM v7_migration_dashboard;

-- Check for overnight blockers
SELECT * FROM v7_subworkflow_tasks 
WHERE status = 'blocked' 
OR (status = 'in_progress' AND started_at < CURRENT_DATE - INTERVAL '2 days');

-- Review pending approvals
SELECT phase_name, status, approval_status 
FROM v7_migration_workflow 
WHERE status = 'review';
```

### 7.2 Issuing Work Orders (per task)
1. Create work order document
2. Insert task into `v7_subworkflow_tasks`
3. Note DART task ID in database
4. Set status = 'pending'

### 7.3 Processing Reports (per report)
1. Read report from DART docs folder
2. Extract completion data
3. Update `v7_subworkflow_tasks`
4. Check if phase complete
5. Update phase status if needed

### 7.4 Evening Wrap-up (10 minutes)
```sql
-- Generate daily summary
WITH today_summary AS (
    SELECT 
        'Completed' as category,
        COUNT(*) as count
    FROM v7_subworkflow_tasks
    WHERE DATE(completed_at) = CURRENT_DATE
    
    UNION ALL
    
    SELECT 
        'Started',
        COUNT(*)
    FROM v7_subworkflow_tasks
    WHERE DATE(started_at) = CURRENT_DATE
    AND status = 'in_progress'
    
    UNION ALL
    
    SELECT 
        'Blocked',
        COUNT(*)
    FROM v7_subworkflow_tasks
    WHERE status = 'blocked'
)
SELECT * FROM today_summary;

-- Update phase timestamps
UPDATE v7_migration_workflow
SET updated_at = CURRENT_TIMESTAMP
WHERE phase_number IN (
    SELECT DISTINCT parent_phase 
    FROM v7_subworkflow_tasks 
    WHERE DATE(updated_at) = CURRENT_DATE
);
```

---

## 8. Troubleshooting Guide

### 8.1 Common Issues and Solutions

| Issue | Solution | Prevention |
|-------|----------|------------|
| Duplicate task numbers | Use UNIQUE constraint | Always check max(task_number) first |
| Missing dependencies | Check dependency IDs exist | Validate before INSERT |
| Orphaned tasks | Set parent_phase correctly | Use foreign key constraint |
| Status conflicts | Use transaction blocks | Update atomically |

### 8.2 Emergency Rollback Procedures
```sql
-- If phase needs rollback
UPDATE v7_migration_workflow
SET status = 'rolled_back',
    blockers = blockers || jsonb_build_object(
        'rollback_reason', 'Critical issue discovered',
        'rollback_date', CURRENT_TIMESTAMP
    )
WHERE phase_number = ?;

-- Reset associated tasks
UPDATE v7_subworkflow_tasks
SET status = 'cancelled',
    notes = notes || ' - Rolled back on ' || CURRENT_DATE
WHERE parent_phase = ?;
```

### 8.3 Data Integrity Checks
```sql
-- Check for orphaned tasks
SELECT * FROM v7_subworkflow_tasks
WHERE parent_phase NOT IN (
    SELECT phase_number FROM v7_migration_workflow
);

-- Check for missing DART links
SELECT * FROM v7_subworkflow_tasks
WHERE status = 'completed'
AND dart_task_id IS NULL;

-- Check for stale in-progress tasks
SELECT * FROM v7_subworkflow_tasks
WHERE status = 'in_progress'
AND started_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
```

---

## 9. Quick Reference Card

### Essential Queries for Daily Use
```sql
-- What's happening now?
SELECT * FROM v7_migration_dashboard;

-- What needs attention?
SELECT * FROM v7_subworkflow_tasks WHERE status IN ('blocked', 'in_progress');

-- What's complete today?
SELECT * FROM v7_subworkflow_tasks WHERE DATE(completed_at) = CURRENT_DATE;

-- What's the next phase?
SELECT * FROM v7_migration_workflow WHERE status = 'not_started' ORDER BY phase_number LIMIT 1;
```

### Status Values Reference
```yaml
v7_migration_workflow.status:
  - not_started
  - in_progress
  - review
  - approved
  - completed
  - blocked
  - rolled_back

v7_subworkflow_tasks.status:
  - pending
  - in_progress
  - blocked
  - review
  - completed
  - cancelled
  - deferred

file_audit.v7_workflow_status:
  - pending_assessment
  - assessed
  - designed
  - approved
  - implementing
  - testing
  - migrated
  - retired
```

---

## 10. Future Enhancements (Draft Ideas)

### 10.1 Automated DART Sync
- Webhook from DART on task completion
- Automatic status updates
- Two-way synchronization

### 10.2 Performance Metrics
- Time per task tracking
- Velocity calculations
- Burndown charts

### 10.3 Predictive Analytics
- Estimated completion dates
- Risk probability scoring
- Resource allocation optimization

---

## Remember, Future Self:

1. **This database is your memory** - Trust it over recollection
2. **Every action must be tracked** - No shadow work
3. **Reports are your inputs** - Process them systematically
4. **The dashboard is your truth** - Check it religiously
5. **Guardian's Paradox is your teacher** - Coordination prevents catastrophe

---

**Created by:** V7 Conductor Persona (for V7 Conductor Persona)
**Last Updated:** 2025-08-07
**Status:** Living Document - Update as you learn

*"The database remembers what humans forget. Trust the data, not the narrative."*
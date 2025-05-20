# ScraperSky File Audit System (Supabase Implementation)

## Purpose and Overview

Create a Supabase database that comprehensively tracks every file in our system with unique identifiers, appropriate classification, and audit status. This system will help us maintain architectural integrity, track technical debt, and ensure complete coverage in our audit process.

## Database Design

### Main Table: file_audit

```
file_audit
- id (auto-generated primary key)
- file_number (unique sequential identifier, e.g., 0042)
- file_path (complete path from project root)
- file_name (extracted from path)
- canonical_name (format: [FILE_NUM]-[WORKFLOW]-[LAYER]-[STATUS]-filename)
- layer (Layer 1-7, as documented in our architecture)
- status ('NOVEL', 'SHARED', 'SYSTEM', 'ORPHANED')
- workflows (array of workflow IDs: WF1, WF2, etc.)
- audit_status ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')
- audit_date (when audit was completed)
- audited_by (person who performed the audit)
- technical_debt (description of any technical debt)
- technical_debt_severity ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
- jira_tickets (array of related JIRA tickets)
- compliance_status ('COMPLIANT', 'NON_COMPLIANT', 'PARTIALLY_COMPLIANT')
- notes (any additional information)
```

### Guidelines Table: guidelines

```
guidelines
- id (auto-generated primary key)
- guideline_id (e.g., 'ORM-01', 'LAYER3-API-02')
- title (short title of the guideline)
- description (full description)
- layer (which layer this primarily applies to)
- file_path (path to the guideline document)
- severity ('MANDATORY', 'RECOMMENDED', 'OPTIONAL')
```

### File-Guideline Mapping: file_guidelines

```
file_guidelines
- id (auto-generated primary key)
- file_id (reference to file_audit)
- guideline_id (reference to guidelines)
- compliance_status ('COMPLIANT', 'NON_COMPLIANT', 'PARTIALLY_COMPLIANT')
- notes (compliance-specific notes)
```

## Implementation Strategy

### 1. Data Population

We'll leverage our existing comprehensive documentation to populate the database:

1. **File Inventory**: Use "ScraperSky Files by Layer and Workflow.md" as the source of truth for:
   - Layer classification (Layer 1-7)
   - Status classification ([NOVEL]/[SHARED])
   - Workflow mappings (WF1-WF7)
   - Technical debt and associated Jira tickets

2. **Sequential Numbering**: Assign unique file numbers (0001, 0042, etc.) to each file, following a logical pattern:
   - Numbers 0001-0999: Layer 1 files
   - Numbers 1000-1999: Layer 2 files
   - And so on for consistent reference

3. **Canonical Names**: Generate structured names following the pattern:
   `[FILE_NUM]-[WORKFLOW]-[LAYER]-[STATUS]-filename`
   Examples:
   - 0042-WF2-L3-NOV-places_staging.py
   - 0143-WF1-4-L1-SHR-place.py

4. **Guidelines Import**: Extract core architectural guidelines from:
   - Docs/Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md
   - Docs/Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md
   - Other key guideline documents

### 2. Key Database Operations

1. **File Lookup** - Find files using various criteria:
   - By layer and status
   - By workflow involvement
   - By technical debt severity
   - By compliance status
   - By audit completion status

2. **Audit Tracking** - Log and monitor the audit process:
   - Track completed vs. pending audits
   - Record who performed audits and when
   - Track technical debt remediation
   - Monitor compliance improvements

3. **Compliance Assessment** - Evaluate architectural compliance:
   - Track compliance with specific guidelines
   - Generate reports on non-compliant areas
   - Link to technical debt and remediation plans

4. **Orphan Detection** - Identify files not properly tracked:
   - Compare database registry against actual codebase
   - Flag unregistered files for classification

## Sample Queries and Reports

1. **Audit Progress**:
   ```
   Show me all files where audit_status = 'NOT_STARTED', grouped by layer
   ```

2. **Technical Debt Assessment**:
   ```
   Show all files with technical_debt_severity = 'HIGH' OR technical_debt_severity = 'CRITICAL',
   with jira_tickets, sorted by severity
   ```

3. **Layer Composition**:
   ```
   Count files by status (NOVEL, SHARED, SYSTEM) for each layer
   ```

4. **Workflow Analysis**:
   ```
   For Workflow 2 (WF2), show all files, their layer, status, and any technical debt
   ```

5. **Compliance Reports**:
   ```
   Show all files that are NON_COMPLIANT with guideline 'ORM-01'
   ```

## Basic Dashboard Views

1. **Audit Progress**: Track completion percentage by layer
2. **Technical Debt**: Distribution of debt by severity and layer
3. **Compliance Status**: Overview of compliance by guideline
4. **File Distribution**: Breakdown of files by layer and status

## Development Steps

1. Create the database schema with proper relationships
2. Import existing file classification data from documentation
3. Assign unique file numbers and generate canonical names
4. Create basic queries and reports
5. Set up simple dashboard for progress tracking

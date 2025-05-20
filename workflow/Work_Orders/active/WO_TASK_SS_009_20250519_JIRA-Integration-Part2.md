# Work Order: JIRA Integration Part 2 (Bidirectional Sync, Field Mapping, and Automation)

**Work Order ID:** TASK_SS_009
**Task ID:** TASK_SS_009
**Date Created:** 2025-05-19
**Priority:** High
**Status:** Queued
**Assigned To:** AI Assistant & Henry Groman

## Background

The first phase of JIRA integration established one-way connectivity from Supabase to JIRA, allowing for the creation of JIRA issues from file_audit data. The next phase will complete the integration by enabling bidirectional sync, advanced field mapping, automation, and improved developer tooling.

## Objectives

1. Implement bidirectional synchronization between Supabase and JIRA
2. Map all relevant file_audit fields to JIRA custom fields
3. Automate and schedule sync jobs
4. Enhance error handling, reporting, and notifications
5. Provide robust CLI tools and comprehensive documentation
6. Address linter/type safety issues in the codebase

## Requirements

### Technical Requirements

- Develop logic for JIRA → Supabase sync (update file_audit when JIRA tickets are resolved/updated)
- Map file_audit fields (e.g., file_path, file_number, technical_debt) to JIRA custom fields
- Implement automation (scheduled jobs, manual triggers)
- Add enhanced error handling and notification (e.g., email, Slack, JIRA comments)
- Provide CLI options for different sync modes
- Fix linter/type safety issues

### Documentation Requirements

- Update tools/README.md with comprehensive usage, setup, and troubleshooting instructions
- Document field mappings and sync logic
- Provide examples and best practices for future developers

## Deliverables

- Updated `tools/jira_sync.py` with bidirectional sync and field mapping
- Automated/scheduled sync job (script, cron, or CI/CD)
- Enhanced CLI and error reporting
- Updated `tools/README.md` with full documentation
- Journal entry summarizing progress and lessons learned

## Related Artifacts

- **Task:** TASK_SS_009
- **tools/jira_sync.py**
- **tools/README.md**

## Acceptance Criteria

1. Bidirectional sync is operational and reliable
2. All relevant fields are mapped between Supabase and JIRA
3. Sync jobs can be automated and/or triggered manually
4. Errors are logged and reported to stakeholders
5. Documentation is clear, comprehensive, and up to date
6. Codebase passes linter/type checks

## Status

**Queued** (awaiting prioritization and resource allocation)

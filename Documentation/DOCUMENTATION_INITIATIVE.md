# Documentation Initiative - "Code is Truth"

**Started:** 2025-11-19  
**Status:** 🟡 In Progress  
**Philosophy:** Code headers are the source of truth. External guides explain usage and maintenance.

---

## The Pattern

### Three-Tier Documentation System

```
┌─────────────────────────────────────────────────────┐
│  TIER 1: CODE HEADERS (Source of Truth)             │
│  Location: Router/Service file headers              │
│  Audience: Developers                                │
│  Content: Technical specs, fields, workflow, cmds   │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌───────────────────┐         ┌───────────────────┐
│  TIER 2: USER     │         │  TIER 3: OPS      │
│  GUIDES           │         │  GUIDES           │
│  Location:        │         │  Location:        │
│  Docs/Guides/     │         │  Docs/Operations/ │
│  Audience: Users  │         │  Audience: Admins │
│  Content: How-to  │         │  Content: Maintain│
└───────────────────┘         └───────────────────┘
```

### Why This Works

1. **No Documentation Drift** - Code headers update with code
2. **Single Source of Truth** - Developers see specs immediately
3. **Layered Access** - Users get guides, admins get runbooks
4. **Always In Sync** - External docs reference code headers

---

## Implementation Checklist

### ✅ Completed (1/8)

#### n8n Enrichment Return Pipeline (WO-021)
- ✅ Enhanced router header (`src/routers/v3/n8n_webhook_router.py`)
  - All 15 fields documented
  - Workflow, examples, maintenance commands
- ✅ User guide (`Documentation/Guides/n8n_enrichment_user_guide.md`)
  - What it does, how to use, troubleshooting
- ✅ Maintenance guide (`Documentation/Operations/n8n_enrichment_maintenance.md`)
  - Monitoring, troubleshooting, maintenance tasks

**Commit:** `be90ff0`

---

### 🔲 Pending (7/8)

#### 1. Brevo CRM Integration (WO-015)
**Files to enhance:**
- [ ] `src/routers/v3/contacts_router.py` (or dedicated brevo router)
- [ ] `src/services/crm/brevo_sync_service.py` header

**Guides to create:**
- [ ] `Documentation/Guides/brevo_crm_user_guide.md`
  - How to sync contacts to Brevo
  - Understanding sync status
  - Best practices
- [ ] `Documentation/Operations/brevo_crm_maintenance.md`
  - Configuration
  - Monitoring sync success rate
  - Troubleshooting failed syncs
  - Retry logic management

**Key Info to Document:**
- Dual-status pattern (sync_status + processing_status)
- Retry logic (5→10→20 min exponential backoff)
- Batch size (10 contacts per cycle)
- Scheduler interval (1 min dev, 5 min prod)

---

#### 2. HubSpot CRM Integration (WO-016)
**Files to enhance:**
- [ ] `src/services/crm/hubspot_sync_service.py` header

**Guides to create:**
- [ ] `Documentation/Guides/hubspot_crm_user_guide.md`
- [ ] `Documentation/Operations/hubspot_crm_maintenance.md`

**Key Info to Document:**
- Same dual-status pattern as Brevo
- HubSpot-specific field mappings
- Date format requirements (text field compatibility)
- Performance (~3 seconds per contact)

---

#### 3. DeBounce Email Validation - Service (WO-017)
**Files to enhance:**
- [ ] `src/services/email_validation/debounce_service.py` header

**Guides to create:**
- [ ] `Documentation/Guides/email_validation_user_guide.md`
  - What email validation does
  - Understanding validation results (valid, invalid, disposable, catch_all)
  - Confidence scores (0-100)
  - When to validate contacts
- [ ] `Documentation/Operations/email_validation_maintenance.md`
  - DeBounce API configuration
  - Monitoring validation success rate
  - Cost tracking
  - Handling disposable email domains

**Key Info to Document:**
- 8 validation result fields
- Validation results: valid, invalid, disposable, catch_all, unknown
- Score interpretation (0-100)
- Auto-CRM queue logic (valid emails → CRM)

---

#### 4. DeBounce Email Validation - API Endpoints (WO-018)
**Files to enhance:**
- [ ] `src/routers/v3/contacts_validation_router.py` header

**Guides to create:**
- [ ] `Documentation/Guides/email_validation_api_guide.md`
  - Using the 4 validation endpoints
  - Polling for status updates
  - Batch validation strategies

**Key Info to Document:**
- 4 endpoints: validate, validate/all, validation-status, validation-summary
- Request/response formats
- Polling strategy (2-second intervals)
- Batch size limits (100 contacts)

---

#### 5. n8n Webhook Integration - Outbound (WO-020)
**Files to enhance:**
- [ ] `src/services/crm/n8n_sync_service.py` header
- [ ] `src/services/crm/n8n_sync_scheduler.py` header

**Guides to create:**
- [ ] `Documentation/Guides/n8n_webhook_user_guide.md`
  - How to send contacts to n8n
  - Understanding webhook status
  - Fire-and-forget pattern
- [ ] `Documentation/Operations/n8n_webhook_maintenance.md`
  - Webhook URL configuration
  - Bearer token setup
  - Monitoring webhook success
  - Troubleshooting webhook failures

**Key Info to Document:**
- Fire-and-forget pattern (webhook accepts = complete)
- Webhook URL and optional Bearer token
- 30-second timeout
- Retry logic with exponential backoff

---

#### 6. Direct Submission Endpoints (WO-009, WO-010, WO-011)
**Files to enhance:**
- [ ] `src/routers/v3/pages_direct_submission_router.py` header
- [ ] `src/routers/v3/domains_direct_submission_router.py` header
- [ ] `src/routers/v3/sitemaps_direct_submission_router.py` header

**Guides to create:**
- [ ] `Documentation/Guides/direct_submission_user_guide.md`
  - When to use direct submission vs normal workflow
  - Submitting pages, domains, sitemaps directly
  - Understanding bypass workflows
- [ ] `Documentation/Operations/direct_submission_maintenance.md`
  - Monitoring direct submissions
  - Duplicate detection logic
  - Domain normalization

**Key Info to Document:**
- 3 endpoints: pages, domains, sitemaps
- Workflow bypass (which stages are skipped)
- Duplicate detection
- Auto-queue for processing
- NULL foreign key support

---

#### 7. CSV Import System (WO-012)
**Files to enhance:**
- [ ] `src/routers/v3/pages_csv_import_router.py` header
- [ ] `src/routers/v3/domains_csv_import_router.py` header
- [ ] `src/routers/v3/sitemaps_csv_import_router.py` header

**Guides to create:**
- [ ] `Documentation/Guides/csv_import_user_guide.md`
  - CSV file format requirements
  - Bulk importing contacts, domains, sitemaps
  - Handling import errors
  - Best practices for large files
- [ ] `Documentation/Operations/csv_import_maintenance.md`
  - File upload limits
  - Parsing performance
  - Error handling per row
  - Monitoring import success rate

**Key Info to Document:**
- 3 endpoints: pages, domains, sitemaps
- CSV format requirements
- Batch processing
- Duplicate detection
- Error reporting per row

---

#### 8. Multi-Scheduler Split (WO-004)
**Files to enhance:**
- [ ] `src/services/WF2_deep_scan_scheduler.py` header
- [ ] `src/services/WF3_domain_extraction_scheduler.py` header

**Guides to create:**
- [ ] `Documentation/Operations/scheduler_architecture.md`
  - Why schedulers were split
  - Independent tuning (intervals, batch sizes)
  - Fault isolation benefits
  - Monitoring individual schedulers

**Key Info to Document:**
- Deep Scan scheduler (WF2): 5 min interval, 10 contacts
- Domain Extraction scheduler (WF3): 2 min interval, 20 domains
- Row-level locking for race condition prevention
- SDK pattern usage

---

## Header Template

Use this template for all router/service headers:

```python
"""
WO-XXX: [Feature Name]

WHAT THIS DOES:
[One-line description]

ENDPOINT/PURPOSE:
[API endpoint or service purpose]

AUTHENTICATION:
[Auth requirements if applicable]

KEY FIELDS/DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List all database fields, parameters, or key data structures]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW:
1. [Step 1]
2. [Step 2]
3. [Step 3]

EXAMPLE REQUEST/USAGE:
[Code example or usage pattern]

RELATED FILES:
• [Related file 1]
• [Related file 2]
• Docs: Documentation/Guides/[feature]_user_guide.md
• Docs: Documentation/Operations/[feature]_maintenance.md

MAINTENANCE:
• [Key command 1]
• [Key command 2]
• [Key command 3]

IMPLEMENTED: [Date] (Commit [hash])
"""
```

---

## User Guide Template

```markdown
# [Feature Name] - User Guide

**Feature:** [Name]
**Status:** ✅ Production Ready
**Last Updated:** YYYY-MM-DD

---

## What is [Feature]?

[Non-technical explanation]

---

## How It Works

[Visual workflow diagram]

---

## Using [Feature]

### Step 1: [Action]
[Instructions]

### Step 2: [Action]
[Instructions]

---

## Understanding Results

[How to interpret output]

---

## Troubleshooting

### Issue: [Common Problem]
**Solutions:**
1. [Solution 1]
2. [Solution 2]

---

## Best Practices

[Tips for success]

---

## FAQ

### [Question]?
[Answer]

---

## Related Documentation

- **Technical Details:** See router header in `src/...`
- **Maintenance Guide:** `Documentation/Operations/...`
```

---

## Maintenance Guide Template

```markdown
# [Feature Name] - Maintenance Guide

**Feature:** [Name]
**Status:** ✅ Production
**Audience:** DevOps, System Administrators
**Last Updated:** YYYY-MM-DD

---

## System Overview

[Architecture diagram]

---

## Configuration

### Environment Variables
[List all env vars]

---

## Monitoring

### Health Checks
[Commands to verify system health]

### Key Metrics
[What to monitor]

---

## Troubleshooting

### Issue: [Problem]
**Diagnosis:**
[How to diagnose]

**Solutions:**
[How to fix]

---

## Maintenance Tasks

### Daily
[Daily checks]

### Weekly
[Weekly tasks]

### Monthly
[Monthly reviews]

---

## Emergency Procedures

[How to handle critical issues]

---

## Related Documentation

- **User Guide:** `Documentation/Guides/...`
- **Technical Details:** Router header in `src/...`
```

---

## Progress Tracking

**Completion:** 1/8 features (12.5%)

**Estimated Time per Feature:**
- Enhanced header: 30 minutes
- User guide: 1-2 hours
- Maintenance guide: 2-3 hours
- **Total per feature:** 3.5-5.5 hours

**Total Remaining:** ~25-40 hours for all 7 features

---

## Benefits

### For Users
- ✅ Clear, non-technical guides
- ✅ Step-by-step instructions
- ✅ Troubleshooting help
- ✅ Best practices

### For Administrators
- ✅ Comprehensive maintenance guides
- ✅ Monitoring procedures
- ✅ Emergency procedures
- ✅ Performance optimization

### For Developers
- ✅ Technical specs in code (always current)
- ✅ No documentation drift
- ✅ Quick reference in headers
- ✅ Related files clearly linked

### For the Project
- ✅ Single source of truth (code)
- ✅ Layered documentation (users/admins/devs)
- ✅ Sustainable (code updates = doc updates)
- ✅ Professional presentation

---

## Next Steps

1. **Prioritize by usage:**
   - Start with most-used features (Brevo, HubSpot, Email Validation)
   - Then direct submission and CSV import
   - Finally scheduler architecture

2. **Batch creation:**
   - Do all headers first (quick wins)
   - Then all user guides
   - Finally all maintenance guides

3. **Review and iterate:**
   - Get user feedback on guides
   - Refine templates based on what works
   - Update as features evolve

---

**Remember:** Code is truth. Guides explain usage. This pattern scales.

**Last Updated:** 2025-11-19

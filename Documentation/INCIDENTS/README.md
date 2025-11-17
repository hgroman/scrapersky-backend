# Incident Database
**Purpose:** Searchable history of all major incidents  
**Last Updated:** November 17, 2025

---

## How to Use

This directory contains detailed post-mortems of significant incidents. Each incident is documented with:
- Symptoms (what we saw)
- Root cause (the actual bug)
- Why it was hidden (what masked it)
- Investigation process
- The fix (with commit reference)
- Lessons learned
- Related incidents

**When debugging:** Search this directory for similar symptoms or error messages.

---

## Incidents by Date

### 2025-11-17
1. **[sitemap-jobs-not-processing](./2025-11-17-sitemap-jobs-not-processing.md)** - CRITICAL
   - Jobs created but never processed
   - Root cause: Missing background task trigger
   - Fixed in: Commit 9f091f6

2. **[authentication-failure](./2025-11-17-authentication-failure.md)** - HIGH
   - "invalid authentication submitted" errors
   - Root cause: Dev token restricted to development
   - Fixed in: Commits 8604a37, d9e4fc2, 1ffa371

3. **[http-service-calls](./2025-11-17-http-service-calls.md)** - MEDIUM
   - Anti-pattern: HTTP calls between services
   - Root cause: Legacy pattern
   - Fixed in: Commit 1ffa371

### 2025-09-09
4. **[scheduler-disabled](./2025-09-09-scheduler-disabled.md)** - CRITICAL
   - Sitemap job processor disabled without replacement
   - Root cause: Incomplete refactoring
   - Impact: 2+ months of silent failures

---

## Incidents by Severity

### Critical
- 2025-11-17: sitemap-jobs-not-processing
- 2025-09-09: scheduler-disabled

### High
- 2025-11-17: authentication-failure

### Medium
- 2025-11-17: http-service-calls

---

## Incidents by Workflow

### WF4 (Domain Curation)
- 2025-11-17: sitemap-jobs-not-processing
- 2025-11-17: authentication-failure
- 2025-11-17: http-service-calls

### WF5 (Sitemap Import)
- 2025-11-17: sitemap-jobs-not-processing (downstream impact)
- 2025-09-09: scheduler-disabled

### WF7 (Page Curation)
- 2025-11-17: sitemap-jobs-not-processing (downstream impact)

---

## Common Patterns

### Silent Failures
- 2025-11-17: sitemap-jobs-not-processing
- 2025-09-09: scheduler-disabled

**Lesson:** Always add monitoring for expected state transitions

### Authentication Issues
- 2025-11-17: authentication-failure

**Lesson:** Separate development and production authentication

### Service Communication
- 2025-11-17: http-service-calls

**Lesson:** Use direct service calls, not HTTP

---

## How to Add New Incidents

1. Copy the template from any existing incident
2. Name file: `YYYY-MM-DD-short-description.md`
3. Fill in all sections
4. Link to related incidents
5. Reference commit hashes
6. Update this README

---

## Template

```markdown
# INCIDENT-YYYY-MM-DD-SHORT-NAME

## Metadata
- **Date:** YYYY-MM-DD HH:MM
- **Severity:** Critical/High/Medium/Low
- **Duration:** X hours
- **Workflows Affected:** WFX, WFY
- **Status:** Resolved/Ongoing

## Symptoms
What we saw

## Root Cause
The actual bug

## Why Hidden
What masked it

## Investigation
How we found it

## The Fix
Commit + code change

## Verification
How we confirmed fix

## Lessons Learned
What we learned

## Related Incidents
Links to other incidents

## Prevention
How to prevent recurrence
```

---

## Search Tips

**By symptom:**
```bash
grep -r "stuck in pending" Documentation/INCIDENTS/
```

**By error message:**
```bash
grep -r "invalid authentication" Documentation/INCIDENTS/
```

**By commit:**
```bash
grep -r "9f091f6" Documentation/INCIDENTS/
```

**By workflow:**
```bash
grep -r "WF4" Documentation/INCIDENTS/
```

---

**For more context, see:**
- [PATTERNS.md](../Context_Reconstruction/PATTERNS.md) - Patterns that prevent incidents
- [DECISIONS/](../DECISIONS/) - Why things are the way they are
- [WO-004_HOTFIX_POSTMORTEM.md](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md) - Detailed Nov 17 timeline

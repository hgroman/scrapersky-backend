# Work Order: WO-026 - WF7 to WF8 Contact Migration

**Status:** PENDING
**Priority:** HIGH
**Created:** 2025-11-22
**Estimated Effort:** 4-6 hours

---

## 1. Background & Problem Statement

### The Issue
Contact-related functionality was incorrectly grouped under WF7 (The Extractor) when it should have its own dedicated workflow. WF7 was originally designed for **Page Curation** - scraping pages, batch processing, and extracting data from web pages.

Over time, contact enrichment features (DeBounce validation, CRM sync to HubSpot/Brevo/n8n, email scanning) were added with `wf7_` prefixes, contaminating the workflow boundary.

### The Correction
- **WF7: The Extractor** - Should contain ONLY page curation functionality
- **WF8: The Connector** - Should contain ALL contact enrichment functionality

This aligns with the existing documentation in `Docs/Docs_49_Contacts_CRUD/` which already references WF8 for contacts.

---

## 2. Scope of Changes

### 2.1 Files to REMAIN in WF7 (Page Curation) - NO CHANGES

| Layer | File | Purpose |
|-------|------|---------|
| L3 Router | `wf7_page_batch_scraper_router.py` | Batch page scraping |
| L3 Router | `wf7_page_csv_import_router.py` | CSV page import |
| L3 Router | `wf7_page_direct_submission_router.py` | Direct page submission |
| L3 Router | `wf7_page_modernized_scraper_router.py` | Modernized scraper |
| L3 Router | `wf7_pages_router.py` | Page CRUD operations |
| L4 Service | `wf7_page_curation_service.py` | Page curation logic |
| L4 Service | `wf7_page_curation_scheduler.py` | Background page processing |
| L4 Service | `wf7_processing_service.py` | Page processing |
| L1 Model | `wf7_page.py` | Page data model |
| L2 Schema | `wf7_page_direct_submission_schemas.py` | Page schemas |

### 2.2 Files to MIGRATE from WF7 → WF8 (Contact Enrichment)

#### Routers (Layer 3)
| Current Name | New Name |
|--------------|----------|
| `wf7_contacts_router.py` | `wf8_contacts_router.py` |
| `wf7_contacts_validation_router.py` | `wf8_contacts_validation_router.py` |
| `wf7_email_scanner_router.py` | `wf8_email_scanner_router.py` |
| `wf7_n8n_webhook_router.py` | `wf8_n8n_webhook_router.py` |

#### Background Schedulers (Layer 4)
| Current Name | New Name |
|--------------|----------|
| `wf7_crm_brevo_sync_scheduler.py` | `wf8_crm_brevo_sync_scheduler.py` |
| `wf7_crm_debounce_scheduler.py` | `wf8_crm_debounce_scheduler.py` |
| `wf7_crm_hubspot_sync_scheduler.py` | `wf8_crm_hubspot_sync_scheduler.py` |
| `wf7_crm_n8n_sync_scheduler.py` | `wf8_crm_n8n_sync_scheduler.py` |

#### CRM Services (Layer 4)
| Current Name | New Name |
|--------------|----------|
| `wf7_brevo_sync_service.py` | `wf8_brevo_sync_service.py` |
| `wf7_hubspot_sync_service.py` | `wf8_hubspot_sync_service.py` |
| `wf7_n8n_sync_service.py` | `wf8_n8n_sync_service.py` |
| `wf7_n8n_enrichment_service.py` | `wf8_n8n_enrichment_service.py` |

#### Email Validation Services (Layer 4)
| Current Name | New Name |
|--------------|----------|
| `wf7_debounce_service.py` | `wf8_debounce_service.py` |
| `wf7_validation_api_service.py` | `wf8_validation_api_service.py` |

#### Models (Layer 1)
| Current Name | New Name |
|--------------|----------|
| `wf7_contact.py` | `wf8_contact.py` |

#### Schemas (Layer 2)
| Current Name | New Name |
|--------------|----------|
| `wf7_contact_schemas.py` | `wf8_contact_schemas.py` |
| `wf7_contact_validation_schemas.py` | `wf8_contact_validation_schemas.py` |
| `wf7_email_scan_schemas.py` | `wf8_email_scan_schemas.py` |

---

## 3. Migration Checklist

### Phase 1: Preparation
- [ ] Create backup branch: `git checkout -b backup/pre-wf8-migration`
- [ ] Document all current import relationships
- [ ] Verify no active deployments in progress

### Phase 2: File Renames (use `git mv` to preserve history)
- [ ] Rename all routers (4 files)
- [ ] Rename all background schedulers (4 files)
- [ ] Rename all CRM services (4 files)
- [ ] Rename all email validation services (2 files)
- [ ] Rename model file (1 file)
- [ ] Rename schema files (3 files)
- [ ] Delete `__pycache__` directories with old names

### Phase 3: Import Updates
- [ ] Update `src/routers/__init__.py`
- [ ] Update `src/main.py` router registrations
- [ ] Update all internal imports within renamed files
- [ ] Update cross-references from other files importing these modules
- [ ] Update any configuration files referencing old names

### Phase 4: Verification
- [ ] Run `ruff check .` - no errors
- [ ] Run `ruff format .` - formatted
- [ ] Start application locally - no import errors
- [ ] Test each migrated endpoint manually
- [ ] Run full test suite

### Phase 5: Documentation
- [ ] Create WF8 workflow canon artifacts (CANONICAL.yaml, dependency trace)
- [ ] Update WF7 documentation to remove contact references
- [ ] Update any README files referencing old paths
- [ ] Add entry to CHANGELOG

### Phase 6: Deployment
- [ ] Commit with descriptive message
- [ ] Push to main
- [ ] Verify Render deployment succeeds
- [ ] Smoke test production endpoints

---

## 4. Import Dependency Map

Files that import from the modules being renamed (must be updated):

```
# These files likely import from wf7_contact* modules:
src/main.py
src/routers/__init__.py
src/services/background/*.py (cross-scheduler imports)
```

Run this command to find all imports:
```bash
grep -r "from.*wf7_contact\|from.*wf7_crm\|from.*wf7_debounce\|from.*wf7_n8n\|from.*wf7_email\|from.*wf7_validation" src/
```

---

## 5. Rollback Plan

If migration fails:
1. `git checkout main`
2. `git reset --hard HEAD~1` (if already committed)
3. Redeploy previous version on Render

---

## 6. Success Criteria

- [ ] All `wf7_contact*`, `wf7_crm*`, `wf7_debounce*`, `wf7_n8n*`, `wf7_email*` files renamed to `wf8_*`
- [ ] Application starts without import errors
- [ ] All contact-related endpoints functional
- [ ] All CRM sync schedulers running
- [ ] No references to old file names in codebase (except git history)
- [ ] WF8 workflow documentation created

---

## 7. Files Summary

**Total files to rename:** 18 files

| Category | Count |
|----------|-------|
| Routers | 4 |
| Background Schedulers | 4 |
| CRM Services | 4 |
| Email Validation Services | 2 |
| Models | 1 |
| Schemas | 3 |

---

## 8. Related Documentation

- `Docs/Docs_49_Contacts_CRUD/` - Existing WF8 documentation
- `Docs/Docs_7_Workflow_Canon/` - Workflow canon templates
- `Documentation/Work_Orders/WO-025_COPILOT_SEMANTIC_SEARCH.md` - Related work order

---

## 9. Notes

This migration is a **naming/organizational change only**. No business logic should be modified. The goal is to correct the workflow boundary violation and establish proper separation of concerns.

After this migration:
- **WF7** = Page Curation (The Extractor)
- **WF8** = Contact Enrichment (The Connector)
- **WF9** = Knowledge Management (The Librarian) - Co-Pilot semantic search

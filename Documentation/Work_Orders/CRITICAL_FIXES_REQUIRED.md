# CRITICAL FIXES REQUIRED: WO-009 and WO-011

**Status:** 🔴 BLOCKING - Must fix before implementation  
**Date:** November 17, 2025  
**Severity:** HIGH (will cause database constraint violations)

---

## Ground Truth from Code Verification

### Issue 1: tenant_id is REQUIRED (nullable=False)

**File:** `src/models/domain.py`  
**Line:** 117-123

```python
tenant_id = Column(
    PGUUID,
    ForeignKey("tenants.id"),
    nullable=False,  # ← REQUIRED
    index=True,
    default=lambda: uuid.UUID(DEFAULT_TENANT_ID),
)
```

**DEFAULT_TENANT_ID:** `"550e8400-e29b-41d4-a716-446655440000"`  
**Location:** `src/models/tenant.py:16`

**Impact:** Domain creation will FAIL without tenant_id

---

### Issue 2: sitemap_type is REQUIRED (nullable=False)

**File:** `src/models/sitemap.py`  
**Line:** 106

```python
sitemap_type = Column(Text, nullable=False)  # ← REQUIRED
```

**Common Values:** "INDEX", "STANDARD", "IMAGE", "VIDEO", "NEWS"  
**Default for direct submission:** "STANDARD"

**Impact:** SitemapFile creation will FAIL without sitemap_type

---

## Required Fixes

### Fix 1: WO-009 Domain Creation (Lines 437-447)

**Current (BROKEN):**
```python
domain = Domain(
    id=uuid.uuid4(),
    domain=domain_name,
    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
    sitemap_curation_status=SitemapCurationStatusEnum.New,
    sitemap_analysis_status=None,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Fixed (CORRECT):**
```python
from src.models.tenant import DEFAULT_TENANT_ID

domain = Domain(
    id=uuid.uuid4(),
    domain=domain_name,
    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # ← REQUIRED
    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
    sitemap_curation_status=SitemapCurationStatusEnum.New,
    sitemap_analysis_status=None,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Additional Import Required:**
```python
# At top of file
from src.models.tenant import DEFAULT_TENANT_ID
```

---

### Fix 2: WO-011 Domain Creation (Lines 462-470)

**Current (BROKEN):**
```python
domain = Domain(
    id=uuid.uuid4(),
    domain=domain_name,
    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
    sitemap_curation_status=SitemapCurationStatusEnum.New,
    sitemap_analysis_status=None,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Fixed (CORRECT):**
```python
from src.models.tenant import DEFAULT_TENANT_ID

domain = Domain(
    id=uuid.uuid4(),
    domain=domain_name,
    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # ← REQUIRED
    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
    sitemap_curation_status=SitemapCurationStatusEnum.New,
    sitemap_analysis_status=None,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Additional Import Required:**
```python
# At top of file
from src.models.tenant import DEFAULT_TENANT_ID
```

---

### Fix 3: WO-011 SitemapFile Creation (Line 496)

**Current (BROKEN):**
```python
sitemap_file = SitemapFile(
    id=uuid.uuid4(),
    url=url_str,
    
    # Foreign key
    domain_id=domain.id,  # REQUIRED (nullable=False per SYSTEM_MAP.md)
    
    # DUAL-STATUS PATTERN (CRITICAL)
    deep_scrape_curation_status=(
        SitemapImportCurationStatusEnum.Selected if request.auto_import
        else SitemapImportCurationStatusEnum.New
    ),
    sitemap_import_status=(
        SitemapImportProcessStatusEnum.Queued if request.auto_import
        else None
    ),
    
    # Metadata (NULL initially, populated after import)
    url_count=None,
    last_modified=None,
    file_size=None,
    sitemap_type=None,  # ← WRONG - nullable=False
```

**Fixed (CORRECT):**
```python
sitemap_file = SitemapFile(
    id=uuid.uuid4(),
    url=url_str,
    
    # Foreign key
    domain_id=domain.id,  # REQUIRED (nullable=False per SYSTEM_MAP.md)
    
    # REQUIRED field
    sitemap_type="STANDARD",  # ← REQUIRED (nullable=False) - default for direct submission
    
    # DUAL-STATUS PATTERN (CRITICAL)
    deep_scrape_curation_status=(
        SitemapImportCurationStatusEnum.Selected if request.auto_import
        else SitemapImportCurationStatusEnum.New
    ),
    sitemap_import_status=(
        SitemapImportProcessStatusEnum.Queued if request.auto_import
        else None
    ),
    
    # Metadata (NULL initially, populated after import)
    url_count=None,
    last_modified=None,
    file_size=None,
```

---

## Summary of Changes

### WO-009 Changes
1. **Add import:** `from src.models.tenant import DEFAULT_TENANT_ID`
2. **Line 437-447:** Add `tenant_id=uuid.UUID(DEFAULT_TENANT_ID)` to Domain creation

### WO-011 Changes
1. **Add import:** `from src.models.tenant import DEFAULT_TENANT_ID`
2. **Line 462-470:** Add `tenant_id=uuid.UUID(DEFAULT_TENANT_ID)` to Domain creation
3. **Line 496:** Change `sitemap_type=None` to `sitemap_type="STANDARD"`

---

## Testing Verification

### Test 1: Verify Domain Creation
```python
# After creating domain, verify tenant_id is set
assert domain.tenant_id == uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
```

### Test 2: Verify SitemapFile Creation
```python
# After creating sitemap_file, verify sitemap_type is set
assert sitemap_file.sitemap_type == "STANDARD"
```

### Test 3: Database Constraint Check
```sql
-- Verify domain has tenant_id
SELECT id, domain, tenant_id FROM domains WHERE domain = 'example.com';

-- Verify sitemap has sitemap_type
SELECT id, url, sitemap_type FROM sitemap_files WHERE url LIKE '%sitemap.xml';
```

---

## Impact Assessment

**Without these fixes:**
- ❌ Domain creation will fail with: `IntegrityError: null value in column "tenant_id" violates not-null constraint`
- ❌ SitemapFile creation will fail with: `IntegrityError: null value in column "sitemap_type" violates not-null constraint`
- ❌ 100% failure rate for direct submissions

**With these fixes:**
- ✅ Domain creation succeeds with default tenant
- ✅ SitemapFile creation succeeds with "STANDARD" type
- ✅ Direct submissions work as intended

---

## Update SYSTEM_MAP.md

Add to "Critical Model Constraints" section:

```markdown
### Domain Model (`src/models/domain.py`)

**CRITICAL CONSTRAINT:**
```python
# Line 117-123
tenant_id = Column(
    PGUUID,
    ForeignKey("tenants.id"),
    nullable=False,  # ← NOT NULL
    index=True,
    default=lambda: uuid.UUID(DEFAULT_TENANT_ID),
)
```

**Impact:** All Domain records MUST have a tenant_id. Use DEFAULT_TENANT_ID for direct submissions.

**DEFAULT_TENANT_ID:** `"550e8400-e29b-41d4-a716-446655440000"` (from `src/models/tenant.py`)

---

### SitemapFile Model (`src/models/sitemap.py`)

**CRITICAL CONSTRAINT:**
```python
# Line 106
sitemap_type = Column(Text, nullable=False)  # ← NOT NULL
```

**Impact:** All SitemapFile records MUST have a sitemap_type. Use "STANDARD" for direct submissions.

**Valid Values:** "INDEX", "STANDARD", "IMAGE", "VIDEO", "NEWS"
```

---

## Action Required

**For Online AI:**
1. Apply Fix 1 to WO-009 (add tenant_id)
2. Apply Fix 2 to WO-011 (add tenant_id)
3. Apply Fix 3 to WO-011 (set sitemap_type="STANDARD")
4. Add import statement to both WOs
5. Update testing sections to verify these fields

**For Local AI:**
1. Update SYSTEM_MAP.md with tenant_id and sitemap_type constraints
2. Review and approve corrected work orders

---

**Status After Fixes:** ✅ READY FOR IMPLEMENTATION  
**Risk Level:** LOW (all constraints satisfied)

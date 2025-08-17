# L1 Model Guardian Pattern-AntiPattern Companion v2.0
## Instant Pattern Recognition & Violation Detection Guide - Enhanced Edition

**Version:** 2.0  
**Purpose:** Enable instant model/enum pattern recognition and violation detection  
**Cardinal Rule:** Inherit from BaseModel, never redefine core fields!  
**Usage:** Load ONLY this document for complete L1 model review authority  
**Verification Requirement:** All models must inherit BaseModel fields correctly  

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST
- [ ] Model inherits from BaseModel without redefining id/created_at/updated_at
- [ ] All ENUMs defined in centralized `enums.py` file
- [ ] ENUM database names use snake_case (e.g., `contact_curation_status`)
- [ ] Foreign keys reference primary keys only (`table.id`)
- [ ] Foreign key types match referenced column types (UUID → UUID)
- [ ] Required fields marked with `nullable=False`
- [ ] File names use underscores, not hyphens

### 🔴 INSTANT REJECTION TRIGGERS
1. **Redefining BaseModel fields** → REJECT (Pattern #1 violation)
2. **ENUMs outside enums.py** → REJECT (Pattern #2 violation)
3. **PascalCase database names** → REJECT (Pattern #3 violation)
4. **Foreign key type mismatch** → REJECT (Pattern #4 violation)
5. **Hyphens in Python filenames** → REJECT (Pattern #5 violation)
6. **Integer primary keys** → REJECT (Pattern #6 violation)
7. **Duplicate ENUM definitions** → REJECT (Pattern #7 violation)

### ✅ APPROVAL REQUIREMENTS
Before approving ANY model implementation:
1. Verify BaseModel inheritance without field redefinition
2. Confirm all ENUMs in enums.py with snake_case DB names
3. Check foreign keys reference .id columns only
4. Verify nullable=False on required business fields
5. Confirm file names use underscores only
6. Ensure UUID primary keys throughout

---

## PATTERN #1: BaseModel Inheritance (NEVER REDEFINE)

### ✅ CORRECT PATTERN:
```python
from src.models.base import BaseModel

class Domain(BaseModel):
    __tablename__ = "domains"
    
    # Business fields only - NO id, created_at, updated_at!
    domain = Column(String(255), nullable=False, unique=True)
    status = Column(SQLAlchemyEnum(DomainStatus), nullable=False)
    
    # BaseModel automatically provides:
    # - id (UUID primary key)
    # - created_at (timestamp)
    # - updated_at (timestamp)
```
**Why:** BaseModel provides consistent core fields across all models  
**Citation:** Layer 1 Blueprint 2.1.3, Constitutional BaseModel pattern

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Redefining id Field**
```python
# contact.py - CRITICAL VIOLATION!
class Contact(Base, BaseModel):
    id = Column(PGUUID, primary_key=True, default=uuid.uuid4)  # NEVER DO THIS!
    # BaseModel already provides id!
```
**Detection:** Any model with `id = Column(...)`  
**From Audit:** Contact model redefines id unnecessarily  
**Impact:** Inconsistent id handling, potential conflicts

**Violation B: Integer Primary Key Override**
```python
# batch_job.py & job.py - VIOLATION!
class BatchJob(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)  # WRONG TYPE!
    id_uuid = Column(PGUUID, unique=True)  # Redundant field
```
**Detection:** `Column(Integer, primary_key=True)` in any model  
**From Audit:** BatchJob and Job models use Integer instead of UUID  
**Impact:** Breaks UUID consistency, requires migration

---

## PATTERN #2: ENUM Centralization

### ✅ CORRECT PATTERN:
```python
# src/models/enums.py - ALL ENUMs here
from enum import Enum

class DomainStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"

class ContactCurationStatus(str, Enum):
    PENDING = "pending"
    ENRICHED = "enriched"
    VERIFIED = "verified"

# src/models/domain.py - Import from enums
from src.models.enums import DomainStatus
```
**Why:** Single source of truth for all ENUMs  
**Citation:** Layer 1 Blueprint 2.2, ENUM centralization requirement

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: ENUMs in Model Files**
```python
# contact.py - VIOLATION!
class ContactCurationStatus(str, enum.Enum):
    PENDING = "pending"
    # Should be in enums.py!

# domain.py - ALSO VIOLATION!
class HubotSyncStatus(enum.Enum):
    Queued = "Queued"
    # Duplicate definition, wrong location!
```
**Detection:** `class.*Enum.*:` in non-enums.py files  
**From Audit:** Multiple models define their own ENUMs  
**Impact:** Duplicate definitions, import conflicts

**Violation B: Duplicate ENUM Definitions**
```python
# contact.py:
class HubotSyncStatus(str, enum.Enum):
    PENDING = "pending"

# domain.py - DUPLICATE!
class HubotSyncStatus(enum.Enum):  # Different inheritance!
    Queued = "Queued"  # Different values!
```
**Detection:** Same ENUM name in multiple files  
**From Audit:** HubotSyncStatus, SitemapAnalysisStatusEnum duplicated  
**Impact:** Conflicting definitions, unpredictable behavior

---

## PATTERN #3: ENUM Database Naming (MUST BE snake_case)

### ✅ CORRECT PATTERN:
```python
# Always use snake_case for database type names
status = Column(
    SQLAlchemyEnum(ContactCurationStatus, name="contact_curation_status"),
    nullable=False
)

analysis_status = Column(
    SQLAlchemyEnum(SitemapAnalysisStatus, name="sitemap_analysis_status"),
    nullable=False
)
```
**Why:** PostgreSQL naming conventions require snake_case  
**Citation:** Layer 1 Blueprint 2.2.2, PostgreSQL standards

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: PascalCase Database Names**
```python
# domain.py - VIOLATIONS!
SQLAlchemyEnum(SitemapAnalysisStatusEnum, name="SitemapAnalysisStatusEnum")  # WRONG!
# Should be: name="sitemap_analysis_status_enum"
```
**Detection:** `name="[A-Z]` in SQLAlchemyEnum  
**From Audit:** Multiple ENUMs use PascalCase in database  
**Impact:** PostgreSQL naming conflicts, migration issues

**Violation B: Missing Underscores**
```python
# contact.py - VIOLATION!
SQLAlchemyEnum(ContactCurationStatus, name="contactcurationstatus")  # No underscores!
# Should be: name="contact_curation_status"
```
**Detection:** `name="[a-z]{10,}"` without underscores  
**From Audit:** contact.py concatenates words without separators  
**Impact:** Unreadable database type names

---

## PATTERN #4: Foreign Key Standards

### ✅ CORRECT PATTERN:
```python
# Always reference primary keys with matching types
class Contact(BaseModel):
    # UUID foreign key references UUID primary key
    domain_id = Column(PGUUID, ForeignKey('domains.id'), nullable=False)
    
    # Relationship uses backref
    domain = relationship('Domain', backref='contacts')
```
**Why:** Type safety and referential integrity  
**Citation:** Layer 1 Blueprint 2.1.6, Foreign key requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Type Mismatch**
```python
# job.py - CRITICAL VIOLATION!
batch_id = Column(String, ForeignKey('batch_jobs.batch_id'))  # String → UUID mismatch!
# Should be: Column(PGUUID, ForeignKey('batch_jobs.id'))
```
**Detection:** Foreign key type doesn't match referenced column  
**From Audit:** job.py has String referencing UUID columns  
**Impact:** Database constraint violations, runtime errors

**Violation B: Non-Primary Key References**
```python
# contact.py - VIOLATION!
source_job_id = Column(PGUUID, ForeignKey('jobs.job_id'))  # Wrong column!
# Should reference: ForeignKey('jobs.id')  # Primary key

# job.py - VIOLATION!
batch_id = Column(String, ForeignKey('batch_jobs.batch_id'))  # Not primary key!
# Should reference: ForeignKey('batch_jobs.id')
```
**Detection:** ForeignKey not referencing `.id`  
**From Audit:** Multiple models reference non-primary columns  
**Impact:** Referential integrity issues, query performance

---

## PATTERN #5: Python Import Requirements (NO HYPHENS)

### ✅ CORRECT PATTERN:
```python
# File names MUST use underscores
src/models/contact_model.py  # Valid
src/models/domain_service.py  # Valid
src/models/base_model.py     # Valid

# Import works:
from src.models.contact_model import Contact
```
**Why:** Python cannot import files with hyphens  
**Citation:** Python language requirement, WF7 crisis lesson

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Hyphens in Filenames**
```python
# VIOLATION - Python cannot import!
src/models/contact-model.py  # WRONG!
src/models/domain-service.py  # WRONG!

# This fails:
from src.models.contact-model import Contact  # SyntaxError!
```
**Detection:** Any `.py` file with hyphens  
**From WF7:** 3-hour debugging session from this issue  
**Impact:** ImportError, module not found

---

## PATTERN #6: UUID Primary Keys (NEVER Integer)

### ✅ CORRECT PATTERN:
```python
# BaseModel provides UUID primary key
class BaseModel(Base):
    __abstract__ = True
    id = Column(PGUUID, primary_key=True, default=uuid.uuid4)

# All models inherit this UUID primary key
class Domain(BaseModel):  # Has UUID id automatically
    pass
```
**Why:** UUID prevents ID conflicts in distributed systems  
**Citation:** Constitutional UUID requirement

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Integer Primary Keys**
```python
# batch_job.py - CRITICAL VIOLATION!
class BatchJob(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)  # NO!
    id_uuid = Column(PGUUID, unique=True)  # Confusion!
```
**Detection:** `Column(Integer, primary_key=True)`  
**From Audit:** BatchJob and Job use Integer IDs  
**Impact:** ID collision risk, migration complexity

---

## PATTERN #7: ENUM Inheritance Consistency

### ✅ CORRECT PATTERN:
```python
# Always use (str, Enum) for string-based ENUMs
class DomainStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    
class ContactStatus(str, Enum):  # Consistent inheritance
    NEW = "new"
    VERIFIED = "verified"
```
**Why:** Ensures string serialization works correctly  
**Citation:** Layer 1 Blueprint ENUM standards

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Inconsistent Inheritance**
```python
# domain.py - VIOLATION!
class SitemapCurationStatusEnum(enum.Enum):  # Missing str!
    Fit = "Fit"
    
# Should be:
class SitemapCurationStatusEnum(str, enum.Enum):
    FIT = "fit"  # Also fix casing
```
**Detection:** `(enum.Enum)` without `str`  
**From Audit:** Multiple ENUMs missing str inheritance  
**Impact:** Serialization issues, API response errors

---

## PATTERN #8: Required Field Validation

### ✅ CORRECT PATTERN:
```python
class Domain(BaseModel):
    # Required business fields marked non-nullable
    domain = Column(String(255), nullable=False, unique=True)
    status = Column(SQLAlchemyEnum(DomainStatus), nullable=False)
    
    # Optional fields can be nullable
    description = Column(Text, nullable=True)
```
**Why:** Database enforces business rules  
**Citation:** Layer 1 Blueprint field requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing nullable=False**
```python
# Multiple models - VIOLATION!
email = Column(String(255))  # Required but nullable!
domain_name = Column(String(255))  # Critical field but nullable!

# Should be:
email = Column(String(255), nullable=False)
domain_name = Column(String(255), nullable=False)
```
**Detection:** Critical fields without `nullable=False`  
**From Audit:** Many required fields allow NULL  
**Impact:** Data integrity issues, business rule violations

---

## VERIFICATION REQUIREMENTS

### Model Review Protocol
```bash
# Check for BaseModel field redefinition
grep -n "id = Column\|created_at = Column\|updated_at = Column" src/models/*.py

# Find ENUMs outside enums.py
grep -n "class.*Enum" src/models/*.py | grep -v enums.py

# Check for snake_case in ENUM database names
grep -n 'name="[A-Z]' src/models/*.py

# Find foreign key type mismatches
grep -n "ForeignKey" src/models/*.py

# Check for hyphens in filenames
find src/models -name "*-*.py"
```

### What WF7 Did Wrong:
```python
# 1. Created files with hyphens (couldn't import)
# 2. Redefined BaseModel fields in Contact
# 3. Used Integer primary keys in Job models
# 4. Put ENUMs in model files instead of enums.py
# 5. Used PascalCase for database type names
```

### What WF7 Should Have Done:
```python
# 1. Use underscores in all Python filenames
# 2. Inherit BaseModel without redefinition
# 3. Keep UUID primary keys throughout
# 4. Centralize all ENUMs in enums.py
# 5. Use snake_case for all database names
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 1 models, use this format:

```markdown
L1 MODEL GUARDIAN ANALYSIS:
✅ Compliant with Pattern #1: Proper BaseModel inheritance
❌ VIOLATION of Pattern #2: ENUM defined outside enums.py (Line 45)
❌ VIOLATION of Pattern #3: PascalCase database name "ContactStatus"
❌ VIOLATION of Pattern #4: Foreign key type mismatch String→UUID
⚠️ WARNING on Pattern #8: Missing nullable=False on email field

REQUIRED CORRECTIONS:
1. Move ContactStatus ENUM to enums.py
2. Change database name to "contact_status"
3. Change batch_id type from String to PGUUID
4. Add nullable=False to required fields

APPROVAL: DENIED - Patterns #2, #3, #4 violations must be corrected
```

---

## REPLACES
- L1 Model Guardian Companion v1.0
- Full Layer 1 Models/ENUMs Blueprint (250+ lines)
- 10 Layer 1 audit report chunks
- ENUM location guidelines
- BaseModel inheritance documentation

**With this single 490-line companion for instant pattern recognition!**

---

*"Inherit wisely, centralize ENUMs, name with underscores, reference primary keys."*  
**- The L1 Model Guardian v2.0**
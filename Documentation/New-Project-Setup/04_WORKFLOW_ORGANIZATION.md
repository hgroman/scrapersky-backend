# Workflow-Based Organization

**Document:** 04_WORKFLOW_ORGANIZATION.md  
**Phase:** Code Organization  
**Time Required:** 30 minutes  
**Prerequisites:** [03_BACKEND_ARCHITECTURE.md](./03_BACKEND_ARCHITECTURE.md) completed

---

## Overview

ScraperSky uses workflow-based naming for ALL code artifacts. This makes data flow immediately obvious and simplifies debugging.

---

## Naming Convention

### Pattern

```
wf{N}_{entity}_{artifact_type}.py
```

**Examples:**
- `wf1_place_staging_router.py` - WF1 router for place staging
- `wf3_local_business_model.py` - WF3 model for local businesses
- `wf4_domain_service.py` - WF4 service for domains
- `wf5_sitemap_file_router.py` - WF5 router for sitemap files
- `wf7_page_curation_service.py` - WF7 service for page curation

### Workflow Numbers

Define your workflows first:

```
WF1: User Registration & Onboarding
WF2: Data Collection
WF3: Data Processing
WF4: Data Enrichment
WF5: Data Export
WF7: Analytics & Reporting
```

**Note:** You can skip numbers (ScraperSky skips WF6)

---

## File Organization

### Routers

```
src/routers/
├── wf1_user_registration_router.py
├── wf2_data_collection_router.py
├── wf3_data_processing_router.py
└── wf4_data_enrichment_router.py
```

### Models

```
src/models/
├── base.py
├── enums.py
├── wf1_user.py
├── wf2_data_source.py
├── wf3_processed_data.py
└── wf4_enriched_data.py
```

### Services

```
src/services/
├── wf1_user_registration_service.py
├── wf2_data_collection_service.py
├── wf3_data_processing_service.py
└── wf4_data_enrichment_service.py
```

### Schemas

```
src/schemas/
├── wf1_user_schemas.py
├── wf2_data_source_schemas.py
├── wf3_processed_data_schemas.py
└── wf4_enriched_data_schemas.py
```

---

## Enum Organization

### Centralized Enums

**File:** `src/models/enums.py`

```python
"""
Centralized Enum Definitions

ALL enums MUST be defined here to prevent duplication.
"""

from enum import Enum

# WF1: User Registration
class UserStatus(str, Enum):
    Active = "Active"
    Inactive = "Inactive"
    Suspended = "Suspended"

# WF2: Data Collection
class CollectionStatus(str, Enum):
    Pending = "Pending"
    InProgress = "InProgress"
    Complete = "Complete"
    Failed = "Failed"

# WF3: Data Processing
class ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**Key Rules:**
1. ALL enums in one file
2. Group by workflow
3. Comment which workflow each enum belongs to
4. Never duplicate enum definitions

---

## Model Example

```python
"""
User Model (Workflow 1)

Handles user registration and authentication.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDMixin, TimestampMixin
from src.models.enums import UserStatus

class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for WF1: User Registration.
    
    Table: users
    Workflow: WF1 (User Registration & Onboarding)
    """
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=UserStatus.Active.value)
```

---

## Router Example

```python
"""
User Registration Router (Workflow 1)

Handles user registration and onboarding endpoints.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/users",
    tags=["WF1: User Registration"],
)

@router.post("/register")
async def register_user(...):
    """Register new user (WF1)."""
    pass
```

---

## Benefits

### 1. Immediate Context

```python
# Traditional naming
from routers.users import router

# Workflow naming
from routers.wf1_user_registration_router import router
```

You immediately know this is WF1 (User Registration).

### 2. Easy Debugging

```
ERROR in wf3_data_processing_service.py line 45
```

You know exactly which workflow failed.

### 3. Clear Dependencies

```
WF1 (Registration) → WF2 (Collection) → WF3 (Processing)
```

File names show the data flow.

---

## Migration from Traditional Naming

### Step 1: Document Workflows

Create `Documentation/WORKFLOWS.md`:

```markdown
# Application Workflows

## WF1: User Registration
- Handles user signup, verification, onboarding
- Models: User, UserProfile
- Status: Active, Inactive, Suspended

## WF2: Data Collection
- Collects data from external sources
- Models: DataSource, CollectionJob
- Status: Pending, InProgress, Complete, Failed
```

### Step 2: Rename Files

```bash
# Old
mv src/routers/users.py src/routers/wf1_user_registration_router.py
mv src/models/user.py src/models/wf1_user.py
mv src/services/user_service.py src/services/wf1_user_registration_service.py
```

### Step 3: Update Imports

```python
# Old
from routers.users import router

# New
from routers.wf1_user_registration_router import router
```

---

## Verification Checklist

- [ ] Workflows documented
- [ ] All routers renamed with wf{N}_ prefix
- [ ] All models renamed with wf{N}_ prefix
- [ ] All services renamed with wf{N}_ prefix
- [ ] All schemas renamed with wf{N}_ prefix
- [ ] All enums centralized in enums.py
- [ ] Imports updated throughout codebase
- [ ] Application runs without import errors

---

## Next Steps

✅ **Completed:** Workflow-based organization

**Next:** [05_DEPLOYMENT.md](./05_DEPLOYMENT.md) - Deploy to Render and Vercel

---

**Status:** ✅ Workflow organization complete  
**Next:** Deployment configuration

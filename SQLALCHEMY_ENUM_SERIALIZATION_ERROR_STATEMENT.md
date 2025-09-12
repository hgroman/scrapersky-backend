# SQLAlchemy PostgreSQL Enum Serialization Error Statement

**Date**: September 12, 2025  
**Error Type**: Database Enum Value Serialization  
**System**: FastAPI + SQLAlchemy + PostgreSQL + AsyncPG  

## **Critical Error**

```
sqlalchemy.exc.DBAPIError: (sqlalchemy.dialects.postgresql.asyncpg.Error) 
<class 'asyncpg.exceptions.InvalidTextRepresentationError'>: 
invalid input value for enum page_type_enum: "UNKNOWN"
```

## **Problem Statement**

SQLAlchemy is serializing Python `PageTypeEnum` objects incorrectly when inserting into PostgreSQL database:
- **Expected**: `"unknown"` (enum.value)
- **Actual**: `"UNKNOWN"` (enum.name)  
- **Database**: Rejects `"UNKNOWN"` as invalid enum value

## **System Configuration**

### **Database Schema**
```sql
-- PostgreSQL enum type
CREATE TYPE page_type_enum AS ENUM (
    'contact_root', 'career_contact', 'about_root', 'services_root', 
    'menu_root', 'pricing_root', 'team_root', 'legal_root', 
    'wp_prospect', 'unknown'
);
```

### **Python Enum Definition**
```python
# src/models/enums.py
class PageTypeEnum(str, Enum):
    """Page types identified by Honeybee categorization system"""
    CONTACT_ROOT = "contact_root"
    CAREER_CONTACT = "career_contact"
    ABOUT_ROOT = "about_root"
    SERVICES_ROOT = "services_root"
    MENU_ROOT = "menu_root"
    PRICING_ROOT = "pricing_root"
    TEAM_ROOT = "team_root"
    LEGAL_ROOT = "legal_root"
    WP_PROSPECT = "wp_prospect"
    UNKNOWN = "unknown"  # ← This should serialize as "unknown", not "UNKNOWN"
```

### **SQLAlchemy Model Definition**
```python
# src/models/page.py
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

class Page(Base, BaseModel):
    page_type: Column[Optional[PageTypeEnum]] = Column(
        PgEnum(PageTypeEnum, name="page_type_enum", create_type=False),
        nullable=True,
        index=True,
    )
```

## **Data Flow & Error Location**

### **1. Enum Creation (Correct)**
```python
from src.utils.honeybee_categorizer import HoneybeeCategorizer
hb = HoneybeeCategorizer()
result = hb.categorize('https://example.com/unknown-page')
# result["category"] = PageTypeEnum.UNKNOWN (enum object)
# result["category"].value = "unknown" (correct string)
# result["category"].name = "UNKNOWN" (incorrect string)
```

### **2. Page Object Creation (Issue Location)**
```python
# src/services/sitemap_import_service.py:167
page_data = {
    "page_type": hb["category"],  # PageTypeEnum.UNKNOWN object
    # ... other fields
}
page = Page(**page_data)  # ← ERROR OCCURS HERE
session.add_all([page])   # SQLAlchemy serializes enum incorrectly
```

### **3. Database Insertion (Failure Point)**
```sql
-- What SQLAlchemy generates (WRONG):
INSERT INTO pages (page_type, ...) VALUES ('UNKNOWN', ...);
-- Database error: 'UNKNOWN' is not a valid enum value

-- What should be generated (CORRECT):
INSERT INTO pages (page_type, ...) VALUES ('unknown', ...);
```

## **Investigation Results**

### **Enum Behavior Verification**
```python
from src.models.enums import PageTypeEnum

enum_obj = PageTypeEnum.UNKNOWN
print(f"enum_obj.value: {enum_obj.value}")        # "unknown" ✓
print(f"enum_obj.name: {enum_obj.name}")          # "UNKNOWN" ✗
print(f"str(enum_obj): {str(enum_obj)}")          # "PageTypeEnum.UNKNOWN" ✗
print(f"repr(enum_obj): {repr(enum_obj)}")        # "<PageTypeEnum.UNKNOWN: 'unknown'>" ✓
```

### **SQLAlchemy PgEnum Configuration**
```python
PgEnum(PageTypeEnum, name="page_type_enum", create_type=False)
# create_type=False: Don't create enum type (already exists in DB)
# Expects enum objects to serialize as their .value strings
```

## **Failed Attempts**

1. **✗ Store enum.value strings**: Breaks SQLAlchemy type expectations
2. **✗ JSONB serialization fix**: Only fixed honeybee_json field, not page_type column
3. **✗ Datetime parser fix**: Unrelated issue
4. **✗ Multiple reactive patches**: Addressed symptoms, not root cause

## **Core Question**

**Why is SQLAlchemy's PgEnum serializing `PageTypeEnum.UNKNOWN` as `"UNKNOWN"` instead of `"unknown"`?**

Possible causes:
- AsyncPG driver enum serialization bug
- SQLAlchemy PgEnum configuration issue  
- Python str Enum inheritance problem
- Connection/session configuration issue
- Type conversion middleware interfering

## **System Environment**
- **Python**: 3.11
- **SQLAlchemy**: AsyncPG dialect
- **Database**: PostgreSQL (Supabase)
- **Connection**: Async sessions via Supavisor pooler
- **Framework**: FastAPI

## **Reproduction Steps**
1. Create `PageTypeEnum.UNKNOWN` object
2. Pass to `Page(page_type=enum_obj)` constructor  
3. Add to SQLAlchemy session
4. Attempt database flush/commit
5. Error occurs during SQL generation/execution

## **Required Solution**
Identify and fix the SQLAlchemy enum serialization configuration so that:
- `PageTypeEnum.UNKNOWN` → `"unknown"` (database enum value)
- `PageTypeEnum.CONTACT_ROOT` → `"contact_root"` (database enum value)
- All enum objects serialize to their `.value` strings, not `.name` strings

**This is a systematic SQLAlchemy enum serialization issue, not an application logic bug.**
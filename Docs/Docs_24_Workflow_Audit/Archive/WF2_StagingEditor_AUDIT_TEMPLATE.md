# WF2 - Staging Editor Audit

**Audit Date**: {YYYY-MM-DD}
**Auditor**: Cascade AI
**Status**: DRAFT

---

## 1. Executive Summary
* High-level findings here.

---

## 2. Canonical Definition (The "Should Be")

_Source: `v_5_REFERENCE_IMPLEMENTATION_WF2.yaml`_

### Models & Tables

| Model | File Path | Required Table Name |
|---|---|---|
| `Place` | `src/models/place.py` | `places` |
| `LocalBusiness` | `src/models/local_business.py`| `local_businesses` |

### Enums

| Enum | Required Values |
|---|---|
| `PlaceStatusEnum` | `[New, Selected, Rejected, Processed]` |
| `DeepScanStatusEnum`| `[None, Queued, InProgress, Complete, Error]` |
| `PlaceStagingStatusEnum`| `[New, Selected, Rejected]` |

### Handoffs

*   **Consumes from WF1:** Reads records from the `places` table where `status` is `New`.
*   **Produces for WF3:** Creates records in the `local_businesses` table with `status` as `Selected`.

---

## 3. Live System Evidence (The "Is")

_This section contains commands to inspect the live system. The output of these commands provides the evidence for the analysis._

### 3.1 Database Inspection

#### 3.1.1 List All Tables

```bash
# This command lists all tables in the database.
python3 -c "from sqlalchemy import inspect, create_engine; from src.config.settings import Settings; settings = Settings(); engine = create_engine(settings.database_url); inspector = inspect(engine); print('\n'.join(inspector.get_table_names()))"
```

#### 3.1.2 Inspect `places_staging` Table

_Note: The canonical workflow specifies the `places` table, but we are inspecting `places_staging` based on previous findings._

```bash
# Get schema for places_staging
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config.settings import Settings
settings = Settings()
engine = create_engine(settings.database_url)
inspector = inspect(engine)
table_name = 'places_staging'
print(f'\n=== Schema for {table_name} ===')
for column in inspector.get_columns(table_name):
    print(f\"- {column['name']}: {column['type']}\")
"

# Get indexes for places_staging
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config.settings import Settings
settings = Settings()
engine = create_engine(settings.database_url)
inspector = inspect(engine)
table_name = 'places_staging'
print(f'\n=== Indexes for {table_name} ===')
for index in inspector.get_indexes(table_name):
    print(f\"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})\")
"
```

#### 3.1.3 Inspect `local_businesses` Table

```bash
# Get schema for local_businesses
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config.settings import Settings
settings = Settings()
engine = create_engine(settings.database_url)
inspector = inspect(engine)
table_name = 'local_businesses'
print(f'\n=== Schema for {table_name} ===')
for column in inspector.get_columns(table_name):
    print(f\"- {column['name']}: {column['type']}\")
"

# Get indexes for local_businesses
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config.settings import Settings
settings = Settings()
engine = create_engine(settings.database_url)
inspector = inspect(engine)
table_name = 'local_businesses'
print(f'\n=== Indexes for {table_name} ===')
for index in inspector.get_indexes(table_name):
    print(f\"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})\")
"
```

### 3.2 Code Implementation Audit

```bash
# Find the implemented table names in the models
grep -r '__tablename__' src/models/
```

---

## 4. Discrepancy Analysis
* Table comparing Canonical vs. Actual.
* Analysis of where things differ.

---

## 5. Remediation Plan
* Checklist of required fixes.
* Short and long term actions.

---

## 6. Sign-Off
* Auditor, Reviewer, Approver table.

# Workflow Audit: {WORKFLOW_ID} - {WORKFLOW_NAME}

## 0. Pre-Audit Setup

### 0.1 Ingest Required Documentation

Before beginning the audit, execute these CLI commands to ingest all required documentation:

```bash
# 1. Ingest architectural standards
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md"
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md"
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md"

# 2. Ingest workflow-specific documentation
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "{WORKFLOW_ID}-{WORKFLOW_NAME}_CANONICAL.yaml"

# 3. Ingest common knowledge base
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "common_knowledge_base.md"
```

### 0.2 Query Workflow Context

```bash
# Get workflow definition and standards
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "{WORKFLOW_ID} {WORKFLOW_NAME} workflow definition and standards"

# Find related components
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "{WORKFLOW_ID} {WORKFLOW_NAME} related models, services, and routers"
```

## 1. Executive Summary

[Audit overview and high-level findings]

## 2. Vector Database Analysis

### 2.1 Workflow Context
```bash
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py \
  "{WORKFLOW_ID} {WORKFLOW_NAME} workflow context and architecture"
```

### 2.2 Cross-Workflow Comparison
```bash
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py \
  "Compare {WORKFLOW_ID} with other workflows for consistency"
```

## 3. Database Verification

### 3.1 Table Verification

#### 3.1.1 List All Tables
```bash
python3 -c "from sqlalchemy import inspect; from src.session import engine; inspector = inspect(engine); print('\n'.join(inspector.get_table_names()))"
```

#### 3.1.2 Get Table Schema
```bash
# Replace {table_name} with actual table name (e.g., places_staging)
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# Get columns for a specific table
table_name = 'places_staging'  # Change this to the table you want to inspect
print(f'\n=== {table_name} ===')
for column in inspector.get_columns(table_name):
    print(f"{column['name']}: {column['type']}")
    
# Get foreign keys
print('\nForeign Keys:')
for fk in inspector.get_foreign_keys(table_name):
    print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
"
```

#### 3.1.3 Check Table Indexes
```bash
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# Get indexes for a specific table
table_name = 'places_staging'  # Change this to the table you want to inspect
print(f'\n=== Indexes for {table_name} ===')
for index in inspector.get_indexes(table_name):
    print(f"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})")
"
```

## 4. Database Schema Analysis

### 4.1 places_staging Table

#### 4.1.1 Schema Verification
```bash
# Get detailed schema for places_staging
python3 -c "
from sqlalchemy import inspect, create_engine
from src.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

table_name = 'places_staging'
print(f'=== {table_name} Schema ===')
print('\nColumns:')
for column in inspector.get_columns(table_name):
    print(f"- {column['name']}: {column['type']} (nullable: {column['nullable']}, default: {column.get('default', None)})")

print('\nIndexes:')
for index in inspector.get_indexes(table_name):
    print(f"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})")

print('\nForeign Keys:')
for fk in inspector.get_foreign_keys(table_name):
    print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
"
```

#### 4.1.2 Common Queries

```bash
# Check row count
python3 -c "
from sqlalchemy import text
from src.session import async_session
import asyncio

async def get_row_count():
    async with async_session() as session:
        result = await session.execute(text('SELECT COUNT(*) FROM places_staging'))
        count = result.scalar()
        print(f'Total rows in places_staging: {count}')

asyncio.run(get_row_count())
"

# Check status distribution
python3 -c "
from sqlalchemy import text
from src.session import async_session
import asyncio

async def get_status_distribution():
    async with async_session() as session:
        result = await session.execute(text('''
            SELECT status, COUNT(*) as count 
            FROM places_staging 
            GROUP BY status
            ORDER BY count DESC
        '''))
        print('Status Distribution:')
        for row in result:
            print(f"- {row.status}: {row.count}")

asyncio.run(get_status_distribution())
"
```

## 5. Code Implementation Audit

### 4.1 Model Verification
```bash
# Search for model implementations
find src/models -name "*.py" -exec grep -l "class .*Base" {} \;
```

## 5. Documentation Review

### 5.1 Workflow Documentation
```bash
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py \
  "{WORKFLOW_ID} {WORKFLOW_NAME} documentation standards and requirements"
```

## 6. Findings and Recommendations

[Document findings using evidence from CLI queries]

## 7. Verification Steps

[CLI commands to verify fixes]

## 8. References

1. **Architectural Standards**
   - `v_CONVENTIONS_AND_PATTERNS_GUIDE-*.md`
   - `common_knowledge_base.md`
   - `layer_7_guardian_vision_boot_sequence.md`

2. **Workflow Documentation**
   - `{WORKFLOW_ID}-{WORKFLOW_NAME}_CANONICAL.yaml`
   - Related model and service implementations

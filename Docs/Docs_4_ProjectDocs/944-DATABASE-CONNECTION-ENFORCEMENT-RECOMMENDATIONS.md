# Database Connection Enforcement Recommendations

**Date:** 2025-03-25  
**Author:** Cascade AI  
**Status:** Draft  
**Priority:** High

## Executive Summary

This document outlines concrete recommendations for enforcing the ONE AND ONLY ONE acceptable method for database connections in the ScraperSky backend. These recommendations address the root causes of non-compliance identified during the database connection audit and provide actionable steps to prevent future violations.

## Problem Statement

Despite clear architectural mandates and standardization efforts, non-compliant database connection patterns have persisted in the codebase. The audit has revealed several root causes:

1. **Multiple Implementation Patterns**: Different approaches to database connections coexist in the same codebase
2. **Special Case Thinking**: Developers creating custom connection handling for background tasks and error scenarios
3. **Lack of Automated Enforcement**: No systematic way to detect and prevent non-compliant code
4. **Incomplete Documentation**: Edge cases not explicitly addressed in existing documentation
5. **Technical Debt Accumulation**: Non-compliant patterns becoming entrenched over time

## Recommendations

### 1. Automated Enforcement

#### 1.1 Custom Database Connection Linter

Develop a Python script that can be integrated into the CI/CD pipeline to detect non-compliant database connection patterns.

```python
# Example implementation concept
import ast
import os

class DatabaseConnectionLinter(ast.NodeVisitor):
    def __init__(self):
        self.violations = []
        
    def visit_Call(self, node):
        # Check for direct session creation
        if isinstance(node.func, ast.Name) and node.func.id == 'async_session_factory':
            self.violations.append((node.lineno, "Direct session creation using async_session_factory"))
        
        # Check for other non-compliant patterns
        # ...
        
        self.generic_visit(node)

def lint_file(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
        linter = DatabaseConnectionLinter()
        linter.visit(tree)
        return linter.violations

def lint_directory(directory):
    violations = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_violations = lint_file(file_path)
                if file_violations:
                    violations[file_path] = file_violations
    return violations
```

#### 1.2 Pre-commit Hook Integration

Add a pre-commit hook that runs the database connection linter before allowing commits:

```yaml
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: database-connection-linter
      name: Database Connection Linter
      entry: python scripts/linters/db_connection_linter.py
      language: python
      types: [python]
      pass_filenames: true
```

#### 1.3 CI/CD Pipeline Integration

Add a step in the CI/CD pipeline to run the database connection linter on all Python files:

```yaml
# Example GitHub Actions workflow step
- name: Run Database Connection Linter
  run: python scripts/linters/db_connection_linter.py --directory src
```

### 2. Comprehensive Documentation

#### 2.1 Connection Pattern Reference Guide

Create a comprehensive reference guide that explicitly addresses all common scenarios:

```markdown
# Database Connection Pattern Reference Guide

## General Rule
Always use FastAPI dependency injection with get_session_dependency.

## Specific Scenarios

### API Endpoints
```python
@router.get("/endpoint")
async def endpoint(session: AsyncSession = Depends(get_session_dependency)):
    # Use session here
```

### Background Tasks
```python
async def background_task():
    from ...session.async_session import get_session
    
    async with get_session() as session:
        # Use session here
```

### Error Handling
```python
try:
    # Operation that might fail
except Exception:
    # Handle error WITHOUT creating a new session
```

### Testing
```python
# Test with dependency override
app.dependency_overrides[get_session_dependency] = lambda: test_session
```
```

#### 2.2 Code Templates Repository

Create a repository of approved code templates for common database connection scenarios:

```markdown
# Approved Database Connection Templates

## Template 1: FastAPI Endpoint with Session Dependency
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...session.async_session import get_session_dependency

@router.get("/resource")
async def get_resource(
    resource_id: int,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Use session here
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    return result.scalars().first()
```

## Template 2: Background Task with Session Context Manager
```python
from ...session.async_session import get_session

async def process_in_background(data_id: int):
    async with get_session() as session:
        # Use session here
        result = await session.execute(
            select(Data).where(Data.id == data_id)
        )
        data = result.scalars().first()
        
        # Process data
        
        # Changes are automatically committed when context manager exits
```
```

### 3. Developer Education

#### 3.1 Onboarding Documentation

Update onboarding documentation to emphasize database connection standards:

```markdown
# Developer Onboarding: Database Connections

## The ONE Rule
There is ONE AND ONLY ONE acceptable method for database connections:
FastAPI dependency injection using get_session_dependency.

## Why This Matters
- Ensures proper connection pooling
- Prevents "Tenant or user not found" errors
- Maintains compatibility with Supabase and Render.com
- Follows architectural mandate to remove tenant filtering

## How to Comply
1. Never create sessions directly
2. Always use dependency injection or the get_session context manager
3. Follow the approved templates in our code templates repository
4. Run the database connection linter locally before committing
```

#### 3.2 Knowledge Sharing Sessions

Schedule regular knowledge sharing sessions to reinforce standards:

- Monthly code review sessions focusing on database connections
- Quarterly architecture review meetings
- "Database Connection Patterns" training for new team members

### 4. Continuous Monitoring

#### 4.1 Regular Codebase Audits

Implement a schedule for regular codebase audits:

- Weekly automated scans using the database connection linter
- Monthly manual reviews of high-risk files
- Quarterly comprehensive audits of the entire codebase

#### 4.2 Compliance Dashboard

Develop a simple dashboard to track compliance metrics:

- Number of non-compliant files
- Percentage of codebase in compliance
- Trend over time
- Files with the most violations

## Implementation Timeline

| Phase | Action | Timeline | Owner |
|-------|--------|----------|-------|
| 1 | Complete current audit | In progress | Current team |
| 2 | Develop database connection linter | 1 week | TBD |
| 3 | Create comprehensive documentation | 2 weeks | TBD |
| 4 | Integrate with CI/CD pipeline | 1 week | TBD |
| 5 | Conduct knowledge sharing session | 1 day | TBD |
| 6 | Implement continuous monitoring | Ongoing | TBD |

## Conclusion

By implementing these recommendations, we can ensure that the ONE AND ONLY ONE acceptable method for database connections is consistently followed throughout the codebase. This will eliminate the "Tenant or user not found" errors, improve compatibility with our infrastructure, and maintain architectural integrity.

## Appendix: Common Non-Compliant Patterns to Avoid

1. **Direct Session Creation**
   ```python
   # WRONG
   session = async_session_factory()
   ```

2. **Manual Transaction Management**
   ```python
   # WRONG
   await session.begin()
   try:
       # Do work
       await session.commit()
   except:
       await session.rollback()
   ```

3. **Tenant Filtering in Database Operations**
   ```python
   # WRONG
   query = query.filter(Model.tenant_id == tenant_id)
   ```

4. **JWT Claims in Database Connection Parameters**
   ```python
   # WRONG
   connection_params["options"] = f"-c role={role}"
   ```
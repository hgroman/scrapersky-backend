# RBAC Removal Context Guide for AI Assistance

## Project Overview

ScraperSky Backend is a FastAPI-based web scraping and data management application that is undergoing modernization to simplify its authentication system. The complex Role-Based Access Control (RBAC) system is being removed while preserving JWT authentication and tenant isolation.

## Key Documents

1. **Implementation Plan**: `/Docs3-_ContentMap/33-RBAC-Removal-Implementation-Plan.md`
2. **Progress Tracking**: `/Docs3-_ContentMap/34-RBAC-Removal-Implementation-Results.md`

## Key Architecture Elements

- **JWT Authentication**: `/src/auth/jwt_auth.py` contains the core JWT functionality
- **Database Sessions**: `/src/db/session.py` manages async SQLAlchemy sessions
- **Models Structure**: `/src/models/__init__.py` shows models with RBAC imports commented out
- **RBAC Models**: `/src/models/rbac.py` contains models that should be preserved but not used
- **Main Application**: `/src/main.py` has RBAC routers already removed
- **Router Imports**: `/src/routers/__init__.py` has RBAC router imports commented out
- **Auth Service**: `/src/auth/auth_service.py` still has RBAC dependencies that need cleaning

## Implementation Approach

1. **Preserve model definitions** for future reintegration
2. **Comment out imports** rather than deleting files
3. **Add documentation** to clarify preserved components
4. **Remove or comment out active RBAC code** in auth, services, and routers

## Work Session Structure

For each work session:

1. Focus on completing **one specific step** from the implementation plan (numbered 1-14)
2. Update the progress tracking document as you complete tasks:
   - Update the table with status, date (YYYY-MM-DD), and who completed it
   - Add detailed notes in the respective implementation section
3. Test each change to ensure the application still works
4. Document any issues or unexpected challenges
5. Avoid scope creep by strictly following the outlined plan

### Documentation Standard

When documenting changes in `34-RBAC-Removal-Implementation-Results.md`:

```markdown
#### [Component Name] - Step #[X]
- **Status**: Completed
- **Date**: YYYY-MM-DD
- **Completed By**: [AI Session ID or Name]
- **Changes**:
  - [List specific changes made]
  - [Include file paths and code snippets]
- **Verification**:
  - [How the change was tested]
  - [Results of testing]
- **Issues**:
  - [Any issues encountered]
  - [How they were resolved]
```

Always include a timestamp and step number with each update.

## Starting a New Session

When starting a new session, use this prompt:

```
I'm implementing the RBAC removal plan for ScraperSky Backend. Please help me with Step #[X]: [component name] from Phase [Y].

For context, review these documents:
1. Implementation plan: `/Docs3-_ContentMap/33-RBAC-Removal-Implementation-Plan.md`
2. Progress tracking: `/Docs3-_ContentMap/34-RBAC-Removal-Implementation-Results.md`
3. Context guide: `/Docs3-_ContentMap/35-RBAC-Removal-Context-Guide.md`

Key points about the project:
- We're removing RBAC functionality while preserving JWT authentication
- We're keeping the RBAC model definitions for future reintegration
- For this step, we need to update [specific files] by [specific actions]

Please follow this workflow:
1. Review the relevant files to understand the current state
2. Propose specific changes to implement this step
3. After implementation, document the changes in the results file using the documentation standard
4. Include a timestamp and step number with all updates
5. Update the progress tracking table with status, date, and your session ID

Avoid scope creep by focusing ONLY on this specific step.
```

## Critical Guidelines

1. **Preserve Model Files**: Keep model definitions while commenting out their use
2. **Maintain JWT Auth**: Ensure JWT authentication continues to work
3. **Document for Future**: Add clear comments for future RBAC reintegration
4. **Focused Changes**: Make minimal, focused changes to avoid unintended side effects
5. **Test Everything**: Verify application continues to run after changes

## Key File Paths

| Component | File Path |
|-----------|-----------|
| Auth Service | `/src/auth/auth_service.py` |
| JWT Auth | `/src/auth/jwt_auth.py` |
| Dependencies | `/src/auth/dependencies.py` |
| RBAC Models | `/src/models/rbac.py` |
| Models Init | `/src/models/__init__.py` |
| Tenant Model | `/src/models/tenant.py` |
| Profile Model | `/src/models/profile.py` |
| Sidebar Model | `/src/models/sidebar.py` |
| Services Init | `/src/services/__init__.py` |
| Main App | `/src/main.py` |
| Routers Init | `/src/routers/__init__.py` |

Use this guide to provide essential context to a new AI assistant quickly, focusing the session on specific implementation tasks while maintaining the broader context of the RBAC removal strategy.

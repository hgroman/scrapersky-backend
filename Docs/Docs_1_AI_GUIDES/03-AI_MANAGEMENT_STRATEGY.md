# AI MANAGEMENT STRATEGY

This document outlines a practical strategy for managing AI assistants when working on the ScraperSky project, with a focus on creating specialized sessions, preventing scope creep, and ensuring consistency.

## 1. SPECIALIZED AI ROLES

Create dedicated AI sessions for specific domains:

### Database Expert

```markdown
You are now a Database Expert specialized in SQLAlchemy and PostgreSQL. Your role is to help with database operations in the ScraperSky backend. You have deep expertise in:
- SQLAlchemy ORM and Core
- Async database operations
- Transaction management
- PostgreSQL features
- Data modeling and migrations

Your task is to focus ONLY on database-related code. DO NOT attempt to work on other aspects of the application.

You follow these golden rules:
1. Services never create or manage transactions - they are transaction-aware
2. Routers own transaction boundaries
3. Background tasks create their own sessions and manage their own transactions
4. All database operations use SQLAlchemy ORM models and their helper methods
5. UUID handling must be consistent with type checking
```

### Auth & Security Expert

```markdown
You are now an Auth & Security Expert specialized in FastAPI authentication systems. Your role is to help with authentication, authorization, and security in the ScraperSky backend. You have deep expertise in:
- JWT authentication
- Role-based access control
- Multi-tenancy isolation
- API security best practices
- Feature flagging systems

Your task is to focus ONLY on authentication and security-related code. DO NOT attempt to work on other aspects of the application.

You follow these golden rules:
1. Auth is handled through dependencies
2. Tenant isolation is enforced at all levels
3. Permissions are checked consistently using established patterns
4. Feature flags are tied to tenant subscriptions
5. Security is never compromised for convenience
```

### API & Router Expert

```markdown
You are now an API & Router Expert specialized in FastAPI. Your role is to help with API endpoints and router implementation in the ScraperSky backend. You have deep expertise in:
- FastAPI routing and dependencies
- API design patterns
- Request validation and response formatting
- Background task management
- Error handling

Your task is to focus ONLY on API endpoints and routers. DO NOT attempt to work on other aspects of the application.

You follow these golden rules:
1. Routers own transaction boundaries with explicit begin/commit
2. Business logic is delegated to services
3. Background tasks are added AFTER transaction commits
4. Routes include appropriate auth and permission checks
5. Error handling follows established patterns
```

### Service Logic Expert

```markdown
You are now a Service Logic Expert specialized in business logic implementation. Your role is to help with service layer implementation in the ScraperSky backend. You have deep expertise in:
- Domain-driven design
- Service pattern implementation
- Async Python
- Transaction-aware service design
- Background task processing

Your task is to focus ONLY on service layer code. DO NOT attempt to work on other aspects of the application.

You follow these golden rules:
1. Services don't create or manage transactions (they're transaction-aware)
2. Services receive sessions from routers or background tasks
3. Background tasks create their own sessions and transactions
4. Business logic stays in the service layer, not routers or models
5. Errors must propagate for proper transaction handling
```

## 2. SESSION INITIALIZATION

Start each AI session with these steps:

1. **Define the Role**
   - Choose the appropriate specialized role from above
   - Provide the role description at the start

2. **Set Context**
   - Provide the module-specific prompt from `01-MODULE_SPECIFIC_PROMPTS.md`
   - Include the current implementation code you're working on

3. **Define Task Boundaries**
   - Be explicit about what you want the AI to help with
   - Set clear constraints about what should NOT be changed

4. **Provide Reference Material**
   - Link to specific guidance from the architecture reference
   - Include relevant patterns from other modules as examples

Example initialization:

```
You are now a Database Expert for the ScraperSky project.

I'm working on the sitemap_processing_service.py module. This module follows these strict database patterns:
[paste relevant section from MODULE_SPECIFIC_PROMPTS]

Here's the current implementation:
[paste code]

My specific task is to fix the database insertion in the _process_domain method.

Please adhere strictly to these constraints:
[paste constraints]

For reference, here's how we implement this pattern in other services:
[paste example implementation]
```

## 3. TASK ISOLATION STRATEGY

### Single-Purpose Sessions

1. Create a new AI session for each module or task
2. End the session once the task is complete
3. Don't let scope creep extend beyond the initial task

### Controlled Handoffs

If you need to work across modules:

1. Complete work on one module
2. Document what was done and interfaces established
3. Start a new session with the next module
4. Provide the documentation to maintain consistency

### Progress Tracking

Create a task log document that records:

1. Module/file modified
2. Changes made
3. AI session used
4. Tests to verify changes

## 4. SCOPE CREEP PREVENTION

### Warning Signs of Scope Creep

Watch for:
- "While we're at it..."
- "You should also fix..."
- "This other module also needs..."
- "The entire architecture should..."

### Countermeasures

1. **Explicit Task Boundaries**
   ```
   Your task is ONLY to fix the database insertion in _process_domain.
   DO NOT modify any other methods or files.
   ```

2. **Single Responsibility Focus**
   ```
   Assume all other components are working correctly.
   Focus ONLY on making this specific function work.
   ```

3. **Rejection Statements**
   When AI suggests scope creep:
   ```
   Please stay focused on the current task. We'll address other issues in separate sessions.
   ```

4. **Change Limits**
   ```
   I only want changes to these specific lines of code.
   Do not modify anything else, even if you think it's an improvement.
   ```

## 5. SESSION MANAGEMENT WORKFLOW

### Starting a Session

1. Identify the module/file to work on
2. Choose the appropriate specialized AI role
3. Prepare the module-specific prompt
4. Initialize the session

### During the Session

1. Keep the AI focused on the specific task
2. Reject scope creep suggestions
3. Verify understanding by asking AI to explain its approach
4. Test changes incrementally

### Ending a Session

1. Document what was changed
2. Document any interfaces or patterns established
3. Create tests to verify changes
4. Close the session

## 6. TROUBLESHOOTING AI ISSUES

### When AI Gets Confused

1. Ask AI to explain its understanding of the task
2. Correct any misunderstandings explicitly
3. Provide more specific examples if needed
4. Reset the session if necessary

### When AI Introduces Inconsistencies

1. Point out the specific inconsistency
2. Reference the established pattern it should follow
3. Provide a clear example of the correct approach
4. Ask AI to revise based on the correct pattern

### When AI Generates Errors

1. Share the error message
2. Ask AI to debug without changing the overall approach
3. Provide context about the environment or dependencies
4. Focus on fixing the specific error, not rewriting the solution
# MODULE-SPECIFIC AI PROMPTS

These prompt templates should be used when working with AI on specific modules of the ScraperSky project. Copy the appropriate template based on the module you're working on, fill in the specifics, and use it to start your AI session.

## DATABASE MODULE PROMPT

```markdown
# DATABASE MODULE PROMPT

## CONTEXT
I'm working on the database module of ScraperSky. This module follows these strict patterns:
- Sessions are created by routers or background tasks, NEVER by services
- Services use provided sessions without creating transactions
- All DB operations use SQLAlchemy ORM models with helper methods
- Transaction boundaries are owned by routers, services are transaction-aware

## ⚠️ CRITICAL CONNECTION REQUIREMENTS ⚠️
- MUST use Supavisor connection pooling ONLY
- Direct psycopg2/asyncpg connections are STRICTLY PROHIBITED
- Connection string format MUST be Supavisor-compatible:
  `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
- Connection pool MUST be properly configured:
  - pool_pre_ping=True
  - pool_size=5 (minimum)
  - max_overflow=10 (recommended)

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- NO DIRECT SQL statements unless absolutely necessary
- NO SESSION creation in service methods (except background tasks)
- ALWAYS use existing model helper methods (create_new, etc.)
- FOLLOW transaction pattern: routers own transactions, services are transaction-aware
- NO NESTED TRANSACTIONS
- PROPER UUID handling with type checking and conversion
- TENANT ISOLATION must be maintained
- ABSOLUTELY NO direct psycopg2/asyncpg imports or usage
- NEVER manually construct connection strings
- USE ONLY get_db_session() or async_session_factory() for obtaining sessions
```

## AUTH MODULE PROMPT

```markdown
# AUTH MODULE PROMPT

## CONTEXT
I'm working on the authentication module of ScraperSky. This module follows these strict patterns:
- JWT authentication with Supabase integration
- Role-based access control (RBAC) with tenant isolation
- Feature flagging tied to tenant subscriptions
- Middleware for tenant isolation and auth verification

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- MAINTAIN compatibility with existing auth flow
- ENSURE proper tenant isolation
- NO changes to core auth patterns
- FOLLOW established permission checking pattern
- ALL routes must use get_current_user dependency
- SECURITY must be maintained throughout
```

## API ROUTER PROMPT

```markdown
# API ROUTER PROMPT

## CONTEXT
I'm working on an API router module of ScraperSky. The routers follow these strict patterns:
- Each router owns its transaction boundaries
- Authentication is handled via dependencies
- All business logic is delegated to services
- Routers handle request validation and response formatting
- Background tasks are spawned after transaction completion

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- FOLLOW the pattern: validate → begin transaction → call service → commit/rollback → format response
- ROUTER methods should be thin (5-15 lines max)
- ALL business logic belongs in services, not routers
- BACKGROUND tasks must be added AFTER transaction is committed
- ERROR handling must follow established patterns
- ROUTES must include appropriate auth and permission checks
```

## SERVICE MODULE PROMPT

```markdown
# SERVICE MODULE PROMPT

## CONTEXT
I'm working on a service module of ScraperSky. The services follow these strict patterns:
- Services don't create or manage transactions (they're transaction-aware)
- Services receive sessions from routers or background tasks
- Services implement business logic and call other services
- Database operations use models and their helper methods
- Background tasks create their own sessions and transactions

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- NEVER create or manage transactions in regular service methods
- ALWAYS use the provided session parameter
- TRANSACTION management for background tasks only
- ERROR handling must propagate errors for proper transaction handling
- DELEGATE database operations to model helper methods
- NO direct SQL usage - use SQLAlchemy ORM consistently
```

## MODEL MODULE PROMPT

```markdown
# MODEL MODULE PROMPT

## CONTEXT
I'm working on a model module of ScraperSky. The models follow these strict patterns:
- SQLAlchemy ORM models map to database tables
- Models provide helper methods for common operations
- Models inherit from Base and BaseModel
- UUID primary keys are standard
- Models include tenant_id for multi-tenancy

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- FOLLOW SQLAlchemy ORM patterns
- HELPER methods must handle transaction awareness
- ENSURE proper tenant isolation in all operations
- MAINTAIN UUID handling consistency
- NO business logic in models - only database operations
- PROPER handling of relationships and foreign keys
```

## BACKGROUND TASK PROMPT

```markdown
# BACKGROUND TASK PROMPT

## CONTEXT
I'm working on a background task in ScraperSky. Background tasks follow these strict patterns:
- Tasks create their own database sessions and manage transactions
- Tasks handle proper error recovery
- Tasks ensure session cleanup in all cases
- Tasks update job status and handle state persistence

## SPECIFIC MODULE
Today we're working on: [module_name.py]

## CURRENT IMPLEMENTATION
[Paste relevant part of current code]

## TASK
[Describe your specific task]

## CONSTRAINTS
- ALWAYS create a dedicated session for background tasks
- MANAGE transaction boundaries with explicit begin/commit/rollback
- ENSURE proper session cleanup in all cases (try/finally)
- ERROR recovery must use separate error sessions
- STATE management must handle both memory and database persistence
- FOLLOW established transaction management pattern
```
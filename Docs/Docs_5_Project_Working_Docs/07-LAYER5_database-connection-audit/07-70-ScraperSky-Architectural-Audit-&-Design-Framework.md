# ScraperSky Architectural Audit & Design Framework

## 1. Layered Architecture Overview

The ScraperSky backend is built on a clear layered architecture that enforces separation of concerns and provides a foundation for both implementation and audit processes. Each layer has distinct responsibilities and maintains specific boundaries.

```
┌───────────────────────────────────┐
│ Layer 1: Auth Layer               │
│ - Authentication & Authorization  │
│ - User Context Management         │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 2: API/Router Layer         │
│ - HTTP Endpoints                  │
│ - Request Validation              │
│ - Transaction Boundaries          │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 3: Service Layer            │
│ - Business Logic                  │
│ - Transaction Awareness           │
│ - Orchestration                   │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 4: Domain-Specific Layer    │
│ - External Integrations           │
│ - Domain Logic                    │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 5: Data Access Layer        │
│ - Database Interactions           │
│ - Model Definitions               │
└───────────────────────────────────┘
```

### Separation of Concerns

Each layer has a clear and distinct responsibility within the system. This separation ensures:

- **Maintainability**: Changes to one layer minimally impact other layers
- **Testability**: Layers can be tested in isolation
- **Scalability**: Each layer can be scaled independently as needed
- **Security**: Authentication and authorization are managed at dedicated boundaries

### Flow of Responsibility

Data and control flow through the layers in a consistent manner:

1. Auth Layer establishes identity and permissions
2. API/Router Layer handles HTTP concerns and initiates transactions
3. Service Layer orchestrates business operations
4. Domain-Specific Layer manages integration and specialized logic
5. Data Access Layer interacts with persistent storage

**Reference**: See [17-CORE_ARCHITECTURAL_PRINCIPLES.md](/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md) for detailed architectural principles.

## 2. Layer 1: Auth Layer

The Auth Layer serves as the gatekeeper for all API operations, establishing identity and enforcing access controls.

### Authentication Boundary Principles

- JWT authentication occurs exclusively at this layer
- Token validation follows OAuth 2.0 standards
- No authentication logic should exist in other layers
- Clear separation between authentication and authorization

### JWT Implementation Standards

- JWTs must include standard claims (iss, sub, exp, iat)
- Tenant ID must be embedded in token claims
- Tokens must be validated on every request
- Token refresh follows secure patterns

### User Context Management

- User context is extracted from validated tokens
- Context is propagated to inner layers via dependency injection
- No direct token access in layers beyond auth
- Clear identity propagation through services

### Tenant Isolation Approach

- Multi-tenancy enforced through JWT claims
- Tenant ID required for all data operations
- Cross-tenant access strictly prohibited
- Tenant context maintained throughout request lifecycle

### Audit Checkpoints

| Checkpoint        | Verification Method | Compliance Criteria                        |
| ----------------- | ------------------- | ------------------------------------------ |
| Token Validation  | Code Review         | All requests pass through token validation |
| ID Propagation    | Code Review         | User/tenant ID available to all operations |
| Security Controls | Penetration Testing | No bypass of authentication possible       |
| Tenant Isolation  | Data Analysis       | No cross-tenant data access                |

**Implementation Pattern**:

```python
# In auth layer
async def get_current_user_context(token: str = Depends(oauth2_scheme)) -> UserContext:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if user_id is None or tenant_id is None:
        raise InvalidCredentialsException()
    return UserContext(user_id=UUID(user_id), tenant_id=UUID(tenant_id))

# In router
@router.get("/resource")
async def get_resource(user_context: UserContext = Depends(get_current_user_context)):
    # Use validated user_context
```

**Reference**: See [Authentication Boundary](/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#authentication-boundary) in core principles.

## 3. Layer 2: API/Router Layer

The API/Router Layer defines the HTTP interface and manages request lifecycles.

### Transaction Boundary Ownership

- Routers initiate and complete all database transactions
- Transaction boundaries never cross service boundaries
- Consistent use of transaction management patterns
- Clear error handling that respects transaction boundaries

### Request Validation Standards

- All request validation occurs at the router level
- Standard validation errors returned for malformed requests
- Comprehensive input sanitization
- Consistent parameter type handling (especially UUIDs)

### Error Response Handling

- Standard HTTP status codes used appropriately
- Error responses follow consistent JSON format
- Detailed error messages for client debugging
- Security-sensitive information never leaked in errors

### Background Task Initiation

- Background tasks initiated from routers, not services
- Clear separation between sync and async operations
- Background tasks properly handled for error reporting
- Tasks properly associated with tenant context

### Audit Checkpoints

| Checkpoint                 | Verification Method | Compliance Criteria                                  |
| -------------------------- | ------------------- | ---------------------------------------------------- |
| Transaction Management     | Code Review         | All DB operations within router-defined transactions |
| API Standardization        | Automated Testing   | Endpoints follow naming and response conventions     |
| Error Handling             | Unit Testing        | All error paths return standardized responses        |
| Background Task Management | Code Review         | Background tasks initiated correctly with context    |

**Implementation Pattern**:

```python
@router.post("/resource")
async def create_resource(
    request: CreateResourceRequest,
    db: AsyncSession = Depends(get_session),
    user_context: UserContext = Depends(get_current_user_context)
):
    try:
        # Start transaction
        async with db.begin():
            result = await resource_service.create_resource(
                db=db,
                data=request.model_dump(),
                tenant_id=user_context.tenant_id
            )
        # Transaction auto-commits here

        # Background task outside transaction
        background_tasks.add_task(
            notify_creation,
            resource_id=result.id,
            tenant_id=user_context.tenant_id
        )

        return SuccessResponse(data=result)
    except ValidationError as e:
        return ErrorResponse(status_code=400, message=str(e))
    except ResourceExistsError as e:
        return ErrorResponse(status_code=409, message=str(e))
    except Exception as e:
        logger.error(f"Error creating resource: {e}")
        return ErrorResponse(status_code=500, message="Internal server error")
```

**Reference**: See [API Standardization](/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#api-standardization) for detailed guidelines.

## 4. Layer 3: Service Layer

The Service Layer implements core business logic and orchestrates operations across domains.

### Business Logic Implementation

- Services implement pure business logic
- No direct HTTP or transport concerns
- Focus on use cases and business rules
- Coordination between multiple domains as needed

### Transaction Awareness (Not Management)

- Services are transaction-aware but do not manage transactions
- No explicit commits or rollbacks in service layer
- Service methods receive active session objects
- Services can use nested transactions when necessary

### Background Processing Patterns

- Background task logic implemented in services
- Clear separation from synchronous operations
- Proper error handling and retry logic
- Dedicated sessions for background operations

### Cross-Cutting Concerns

- Consistent logging patterns throughout services
- Error handling focuses on domain-specific exceptions
- Services manage cross-domain coordination
- Resource cleanup handled properly

### Audit Checkpoints

| Checkpoint                | Verification Method | Compliance Criteria                       |
| ------------------------- | ------------------- | ----------------------------------------- |
| No Transaction Management | Code Review         | No transaction begin/commit in services   |
| Session Handling          | Code Review         | Sessions passed to services, not created  |
| Error Propagation         | Unit Tests          | Domain exceptions propagated to router    |
| Business Logic Isolation  | Architecture Review | Pure business logic with no HTTP concerns |

**Implementation Pattern**:

```python
# Service layer implementation
async def create_resource(
    db: AsyncSession,
    data: Dict[str, Any],
    tenant_id: UUID
) -> ResourceModel:
    # Validate business rules
    if await resource_exists(db, data["name"], tenant_id):
        raise ResourceExistsError(f"Resource with name {data['name']} already exists")

    # Create the resource
    resource = ResourceModel(
        id=uuid4(),
        tenant_id=tenant_id,
        name=data["name"],
        properties=data["properties"],
        created_at=datetime.utcnow()
    )

    # Persist within transaction managed by router
    db.add(resource)

    # Additional business logic
    await update_related_resources(db, resource.id, data["related_ids"])

    return resource
```

**Reference**: See [Code Organization](/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#code-organization) for principles.

## 5. Layer 4: Domain-Specific Layer

The Domain-Specific Layer handles specialized functionality and external integrations.

### Domain Logic Isolation

- Domain-specific logic kept separate from general business logic
- Clear boundaries around specialized functionality
- Domain models reflect real-world concepts
- High cohesion within domain boundaries

### External Integration Standards

- Standardized approach to external service integration
- Consistent error handling for external services
- Retry mechanisms for transient failures
- Circuit breaking for persistent failures

### Metadata Processing Patterns

- Consistent approach to metadata extraction
- Standardized handling of external data formats
- Validation of external data before processing
- Transformation to internal data models

### Audit Checkpoints

| Checkpoint               | Verification Method | Compliance Criteria                             |
| ------------------------ | ------------------- | ----------------------------------------------- |
| Separation from Database | Code Review         | No direct database access from integration code |
| Testability              | Unit Test Coverage  | Integration points mockable and testable        |
| Configuration Management | Config Review       | External service config properly isolated       |
| Error Handling           | Code Review         | Proper handling of external service failures    |

**Implementation Pattern**:

```python
# External integration client
class GoogleMapsClient:
    def __init__(self, api_key: str, base_url: str = "https://maps.googleapis.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = ClientSession()

    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": self.api_key,
            "fields": "name,formatted_address,geometry,place_id"
        }

        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()

                if response.status != 200:
                    logger.error(f"Google Maps API error: {data.get('error_message')}")
                    raise ExternalServiceError(f"Failed to get place details: {data.get('error_message')}")

                if data.get("status") != "OK":
                    logger.error(f"Google Maps API error: {data.get('status')}")
                    raise ExternalServiceError(f"Failed to get place details: {data.get('status')}")

                return data["result"]
        except ClientError as e:
            logger.error(f"HTTP error when calling Google Maps API: {str(e)}")
            raise ExternalServiceError(f"Failed to connect to Google Maps API: {str(e)}")
```

**Reference**: See [07-49-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md](/project-docs/07-database-connection-audit/07-49-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md) for exemplar implementation.

## 6. Layer 5: Data Access Layer

The Data Access Layer manages all interactions with persistent storage.

### Model Definition Standards

- Models follow SQLAlchemy ORM patterns
- Clear definition of table relationships
- Consistent naming conventions
- Proper column type definitions

### UUID Standardization

- All IDs implement proper UUIDs
- Consistent use of PostgreSQL UUID types
- No string representation of UUIDs in database
- UUID generation follows standardized patterns

### Relationship Management

- Relationships clearly defined in models
- Foreign key constraints properly implemented
- Cascade behavior explicitly defined
- Indexes created for performance

### Session Factory Pattern

- Consistent use of session factory pattern
- No global session objects
- Sessions properly scoped to requests
- Connection pooling properly configured

### Audit Checkpoints

| Checkpoint               | Verification Method | Compliance Criteria                              |
| ------------------------ | ------------------- | ------------------------------------------------ |
| UUID Standards           | Schema Review       | All ID columns use UUID types                    |
| Timestamp Implementation | Schema Review       | Created/updated timestamps present on all models |
| Schema Consistency       | Database Audit      | Naming conventions followed consistently         |
| Session Management       | Code Review         | No leaked sessions or global session objects     |

**Implementation Pattern**:

```python
# Model definition
class ResourceModel(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    properties = relationship("ResourceProperty", back_populates="resource", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_resource_tenant_name"),
    )
```

**Reference**: See [UUID Standardization](/Docs/Docs_1_AI_GUIDES/16-UUID_STANDARDIZATION_GUIDE.md) and [19-DEVELOPMENT_USER_UUID_STANDARDIZATION.md](/Docs/Docs_1_AI_GUIDES/19-DEVELOPMENT_USER_UUID_STANDARDIZATION.md) for additional details.

## 7. Cross-Layer Standards

Standards that apply across all layers of the architecture.

### Error Handling Across Layers

- Each layer has appropriate error types
- Errors translated at layer boundaries
- Consistent logging of errors
- Clear distinction between system and business errors

### Logging Standards

- Consistent logging format across layers
- Appropriate log levels for different events
- Context information included in log entries
- Correlation IDs for request tracking

### Configuration Management

- Environment-based configuration
- Secrets management
- Feature flags implementation
- Configuration validation at startup

### Testing Requirements

- Unit tests for all layers
- Integration tests for key flows
- Test coverage requirements
- Mocking standards for external dependencies

## 8. Dependency Maps

Reference implementations that demonstrate the architecture in practice.

### Google Maps API (Gold Standard)

The Google Maps API implementation serves as the gold standard for architectural compliance. It demonstrates clean separation of concerns, proper transaction management, and adherence to all architectural principles.

See [07-49-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md](/project-docs/07-database-connection-audit/07-49-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md) for detailed documentation and [07-50-ScraperSky Batch Scraper Dependency Map.md](/project-docs/07-database-connection-audit/07-50-ScraperSky Batch Scraper Dependency Map.md) for visual representation.

### Batch Scraper

A complex multi-stage processing system that demonstrates background processing patterns and transaction boundaries.

```
┌───────────────────────────────────┐
│ Layer 1: Auth Layer               │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 2: API/Router Layer         │
│ src/routers/batch_page_scraper.py │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 3: Service Layer            │
│ src/services/batch/               │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 4: Domain-Specific Layer    │
│ src/scrapers/                     │
└───────────────────┬───────────────┘
                    ▼
┌───────────────────────────────────┐
│ Layer 5: Data Access Layer        │
│ src/models/batch_*.py             │
└───────────────────────────────────┘
```

See [07-50-ScraperSky Batch Scraper Dependency Map.md](/project-docs/07-database-connection-audit/07-50-ScraperSky Batch Scraper Dependency Map.md) for detailed documentation.

### Single Domain Scanner

Implementation for scanning individual domains with proper error handling and reporting.

### Sitemap Scanner

Implementation for processing and scanning website sitemaps at scale.

### Supporting Tools

Tools and utilities that support the core architecture.

## 9. Implementation Verification

Guidelines for verifying architectural compliance.

### Anti-Pattern Detection

Common anti-patterns to watch for:

- Router-level session management across service calls
- Services that manage their own transactions
- Direct database access from domain-specific integrations
- Authentication logic outside the auth layer
- String-based UUIDs in database operations

### Auditor Checklist

| Category         | Checklist Item                         | Verification Method |
| ---------------- | -------------------------------------- | ------------------- |
| Layer Boundaries | Services don't access HTTP context     | Code Review         |
| Layer Boundaries | Routers own all transactions           | Code Review         |
| Layer Boundaries | External integrations isolated from DB | Code Review         |
| Layer Boundaries | Auth logic only in auth layer          | Code Review         |
| Standardization  | All UUIDs use proper types             | Schema Review       |
| Standardization  | API endpoints follow naming convention | API Review          |
| Standardization  | Error responses consistent             | API Testing         |
| Performance      | Appropriate indexing                   | Schema Review       |
| Performance      | N+1 query prevention                   | Query Analysis      |
| Security         | No sensitive data in logs              | Log Review          |
| Security         | Proper tenant isolation                | Code Review         |

### Traceability Matrix

The traceability matrix maps architectural principles to implementation components:

| Architectural Principle | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Layer 5 |
| ----------------------- | ------- | ------- | ------- | ------- | ------- |
| API Standardization     |         | ✓       |         |         |         |
| Connection Management   |         |         |         |         | ✓       |
| Transaction Boundaries  |         | ✓       |         |         |         |
| UUID Standardization    |         |         |         |         | ✓       |
| Authentication Boundary | ✓       |         |         |         |         |
| Error Handling          | ✓       | ✓       | ✓       | ✓       | ✓       |
| Background Task Pattern |         | ✓       | ✓       |         |         |
| Code Organization       |         | ✓       | ✓       | ✓       | ✓       |

### Exemplar Implementations

Reference implementations that demonstrate best practices:

1. **Google Maps API** - Gold standard for overall architecture
2. **Batch Processor** - Example of background processing
3. **User Management** - Example of proper UUID handling
4. **Tenant Management** - Example of multi-tenancy implementation

**Reference**: See [Exemplar Implementations](/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#exemplar-implementations) in core principles.

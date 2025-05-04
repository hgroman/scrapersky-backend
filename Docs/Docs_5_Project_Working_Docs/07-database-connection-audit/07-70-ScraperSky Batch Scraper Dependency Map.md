# ScraperSky Batch Scraper Dependency Map

**Document ID:** 07-60-ScraperSky Batch Scraper Dependency Map
**Date:** 2025-04-01
**Status:** Active
**Priority:** High
**Related Documents:**

- 07-54-BATCH-SCRAPER-COMPLETION-WORK-ORDER
- 07-47-BATCH-PROCESSING-ARCHITECTURE-RECOMMENDATIONS

## Architecture Overview

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
│  ├── types.py                     │
│  │   └── Shared types & interfaces│
│  ├── batch_functions.py           │
│  │   └── Core batch operations    │
│  └── batch_processor_service.py   │
│      └── High-level service logic │
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

## Module Structure

### 1. Types Module (`types.py`)

- Centralized type definitions
- Shared interfaces for batch operations
- Constants for status and options
- Eliminates circular dependencies

Key Components:

- `BatchOptions`: Configuration options
- `BatchStatus`: Status tracking
- `DomainResult`: Individual domain results
- `BatchResult`: Overall batch results
- Status constants and type aliases

### 2. Batch Functions (`batch_functions.py`)

- Core batch processing operations
- Transaction-aware functions
- Proper session management
- Error handling and logging

Key Functions:

- `create_batch`: Create new batch job
- `get_batch_status`: Retrieve batch status
- `process_batch_with_own_session`: Background processing

### 3. Batch Processor Service (`batch_processor_service.py`)

- High-level business logic
- Coordination between components
- Background task management
- Status tracking and updates

## Data Flow

### 1. Request Flow

```
Client Request
   ↓
Router (Transaction Boundary)
   ↓
Batch Functions (Transaction Aware)
   ↓
Domain Processing
   ↓
Data Access
```

### 2. Background Processing

```
Background Task
   ↓
Own Session Management
   ↓
Batch Status Updates
   ↓
Domain Processing
   ↓
Results Storage
```

## Transaction Management

### 1. Router Layer

- Owns transaction boundaries
- Manages commit/rollback
- Handles request validation

### 2. Service Layer

- Transaction-aware
- Accepts sessions
- No transaction management

### 3. Background Tasks

- Own session creation
- Independent transaction scope
- Status updates via separate session

## Error Handling

### 1. System Errors

- Logged with context
- Proper error propagation
- Status updates on failure

### 2. Business Errors

- Domain-specific handling
- User-friendly messages
- Status tracking

## Monitoring

### 1. Task Status

- Real-time updates
- Progress tracking
- Error reporting

### 2. Performance Metrics

- Processing time
- Success rates
- Resource usage

## Dependencies

### External Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- Redis (planned)

### Internal Dependencies

- Page Scraper Service
- Domain Processor
- Database Models
- Session Management

## Security Considerations

### 1. Authentication

- JWT validation at router level
- No tenant isolation in database
- API key validation

### 2. Authorization

- Role-based access control
- Feature flag checks
- Permission validation

## Testing Strategy

### 1. Unit Tests

- Individual component testing
- Mock database interactions
- Error handling verification

### 2. Integration Tests

- Layer interaction testing
- Transaction boundary verification
- Authentication flow testing

### 3. End-to-End Tests

- Complete batch processing flow
- Error recovery scenarios
- Status update verification

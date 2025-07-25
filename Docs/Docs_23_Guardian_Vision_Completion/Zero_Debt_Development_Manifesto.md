# The Zero Technical Debt Manifesto

**Version:** 1.0
**Date:** 2025-06-30

> **Our goal is not to have *fewer* incidents. Our goal is to have *zero* incidents. We are proud to announce [ 0 ] days without incurring architectural debt. Let's keep the counter rising.**

## 1. Our Philosophy

Technical debt is not a necessary evil; it is a failure of process, discipline, and collective ownership. This manifesto codifies the lessons learned from the Guardian Vision Boot Sequence into a set of non-negotiable principles for all SeptaGram Personas. 

Our architecture is defined by seven distinct layers. The integrity of the entire system depends on the integrity of each layer. This document empowers each Guardian to protect their domain.

## 2. The Guardrails: Principles for Each Layer

These are the guardrails that emerged from fixing our most critical anti-patterns. They are not suggestions; they are the standard of work for ScraperSky.

### L1 Guardian: Models & ENUMs
- **Your Domain**: `src/models/`, SQLAlchemy ORM classes, Alembic migrations.
- **Your Guardrail**: **Jurisdictional Purity.** The `models` directory is for database schema definitions ONLY. Pydantic schemas, business logic, or utility functions are forbidden. All ENUMs, without exception, live in `src/models/enums.py`. You are the gatekeeper of the database's structure.

### L2 Guardian: Schemas
- **Your Domain**: `src/schemas/`, Pydantic API models.
- **Your Guardrail**: **Sanctity of the Contract.** Your schemas are the public API contract. They must be self-contained and import only from L1 (Models/ENUMs) or standard libraries. They must never contain business logic. You ensure that what we promise our API consumers is what they receive.

### L3 Guardian: Routers
- **Your Domain**: `src/routers/`, FastAPI endpoints, transaction boundaries.
- **Your Guardrail**: **Lean Endpoints.** Routers are traffic controllers, not workshops. A router's only job is to receive a request, delegate the work to an L4 Service, and return the response. All business logic, database interaction, and complex orchestration belongs in a service. If your endpoint is more than a few lines long, you are violating this principle.

### L4 Guardian: Services
- **Your Domain**: `src/services/`, `src/session/`, business logic, schedulers, external API clients.
- **Your Guardrail**: **Centralized Logic.** You are the heart of the application. All business processes, database sessions, and interactions with the outside world are managed here. You must never expose raw database models to the routers; always use L2 schemas for communication. You are responsible for orchestrating the work.

### L5 Guardian: Configuration
- **Your Domain**: `.env`, `src/config/`, `requirements.txt`.
- **Your Guardrail**: **Single Source of Truth.** All configuration—credentials, environment variables, feature flags, and external dependencies—is managed through your layer. The `settings` object is the only permissible way to access configuration. The `requirements.txt` file is the definitive manifest of our environment. Direct calls to `os.getenv` or ad-hoc package installations are a critical failure.

### L6 Guardian: UI Components
- **Your Domain**: JavaScript modules, UI components, DOM.
- **Your Guardrail**: **Decoupled Presentation.** The UI is a consumer of the API, not an extension of the backend. It must interact with the backend exclusively through the documented L3 endpoints. It should have no knowledge of the backend's internal structure, database, or business logic.

### L7 Guardian: Testing
- **Your Domain**: `src/tests/`, fixtures, mocking, test isolation.
- **Your Guardrail**: **Isolate and Verify.** Every test must be atomic and isolated, targeting a specific piece of functionality within a single layer. Use mocking and fixtures to isolate your layer from others. A test that crosses multiple layers is an integration test, and must be clearly marked as such. Your job is to validate the contract of each function, not the entire system in one go.

## 3. Our Pledge

By contributing to this codebase, we pledge to uphold these principles. We agree to be guardians of our respective layers, to hold our peers accountable, and to take pride in a system that is stable, predictable, and free of architectural debt.

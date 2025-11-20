# Validation Plan: Standardization Refactoring

This document outlines the step-by-step process to validate the recent "Constitutional Architecture" refactoring before merging and deploying.

**Objective**: Ensure that Schema Extraction (Refactors 1 & 2) and ORM Standardization (Refactor 3) are implemented correctly and do not break the application.

## Prerequisites
- Local Docker environment is available.
- Python environment with `pytest` installed.

## Context & Background
**Who are you?** You are the "Quality Assurance & Deployment Agent". Your role is to validate the work of the previous "Refactoring Agent".

**What changed?**
1.  **Schema Extraction**: Inline Pydantic models were moved from `src/routers/local_businesses.py` and `src/routers/places_staging.py` to `src/schemas/`.
2.  **ORM Standardization**: `src/services/sitemap_scheduler.py` was refactored to use SQLAlchemy ORM objects instead of raw `update()` statements.
3.  **Architecture**: A new `ARCHITECTURE.md` file was created to formalize these patterns.

**Why are we doing this?**
To enforce a "Constitutional Architecture" where routers own sessions, schemas are centralized, and the ORM is used exclusively.

**Your Mission**:
Execute the steps below to prove these changes work, then clean up the test artifacts and deploy.

---

## Phase 1: Isolated Verification (Code Logic)

Run the verification scripts created during the refactoring. These scripts test the specific changes in isolation using mocked environment variables.

### Step 1: Verify Local Businesses Schema Extraction
**Goal**: Confirm `src/routers/local_businesses.py` correctly imports schemas from `src/schemas/local_business_schemas.py`.

```bash
PYTHONPATH=. pytest tests/verification_local_businesses.py
```
- [ ] **Pass**: Tests pass without `ImportError` or `AttributeError`.

### Step 2: Verify Places Staging Schema Extraction
**Goal**: Confirm `src/routers/places_staging.py` correctly imports schemas from `src/schemas/places_staging_schemas.py`.

```bash
PYTHONPATH=. pytest tests/verification_places_staging.py
```
- [ ] **Pass**: Tests pass without `ImportError` or `AttributeError`.

### Step 3: Verify Sitemap Scheduler ORM Usage
**Goal**: Confirm `src/services/sitemap_scheduler.py` uses ORM object updates instead of raw SQL `update()`.

```bash
PYTHONPATH=. pytest tests/verification_sitemap_scheduler.py
```
- [ ] **Pass**: Tests pass, confirming the mock job object was updated via attributes.

---

## Phase 2: Integration Smoke Test (Docker)

Since refactoring involved moving classes between files, the biggest risk is a runtime `ImportError` that static analysis might miss. We will spin up the application to ensure it starts correctly.

### Step 4: Start Application in Docker
```bash
docker compose up --build -d
```

### Step 5: Verify Startup Logs
Check the logs to ensure the application started without crashing due to import errors.
```bash
docker compose logs -f scrapersky | grep "Application startup complete"
```
- [ ] **Pass**: Log shows "Application startup complete" (or similar success message) and NO stack traces regarding `ImportError` or `ModuleNotFoundError`.

### Step 6: Basic Health Check (Optional but Recommended)
If the app is running on localhost:8000:
```bash
curl http://localhost:8000/health  # Or appropriate health endpoint
```
- [ ] **Pass**: Returns 200 OK.

---

## Phase 3: Cleanup & Handover

Once Phase 1 and 2 are successful, the code is safe to merge.

### Step 7: Remove Verification Scripts
The verification scripts were temporary artifacts.
```bash
rm tests/verification_local_businesses.py
rm tests/verification_places_staging.py
rm tests/verification_sitemap_scheduler.py
```

### Step 8: Commit to Git
```bash
git add src/routers/local_businesses.py src/schemas/local_business_schemas.py
git add src/routers/places_staging.py src/schemas/places_staging_schemas.py
git add src/services/sitemap_scheduler.py
git add ARCHITECTURE.md
git commit -m "refactor: Standardize schemas and ORM usage per Architecture Constitution"
```

### Step 9: Deployment Verification
- Push to the branch connected to Render.
- Monitor Render dashboard for successful build and deploy.

# Comprehensive Plan for Sunday's ScraperSky Modernization Work

Based on the project structure and documentation I've reviewed, here's a detailed plan for Sunday's work that will bring your AI-assisted IDE up to speed:

## Context for Sunday's Work

"The ScraperSky backend modernization project has been underway for several weeks. We've successfully migrated the database layer from direct SQL to SQLAlchemy ORM and fixed critical issues with Supabase's Supavisor connection pooler.

Our original modernization plan called for standardizing around 7 key services:

- Core services: auth_service, db_service, error_service
- Extended services: validation_service, job_manager_service, batch_processor_service, user_context_service

While we've made good progress on the database layer, the service standardization is inconsistent. Looking at the project structure, services are scattered across different directories:

- Some in `/src/services/` (root)
- Some in `/src/services/core/`
- Some in `/src/services/batch/`
- Some in `/src/services/error/`
- Some in `/src/services/job/`
- Some in `/src/services/validation/`
- Even more in `/src/services/new/`

We need to bring order to this chaos and align with our original architectural vision.

## Sunday's Work Plan

1. **Service Inventory & Assessment (1 hour)**

   - Create a complete inventory of all 7 planned services
   - For each service, document:
     - Current location/implementation
     - Whether it uses SQLAlchemy or direct SQL
     - Which routes are currently using it
     - Dependencies on other services

2. **Service Architecture Decision (30 min)**

   - Based on the inventory, recommend a consistent organizational structure:
     - Either all services in the root services directory
     - Or logically grouped in subdirectories

3. **Service Migration Plan (2 hours)**

   - Create a sequential plan for migrating/standardizing the services
   - Start with the 3 core services (auth, db, error)
   - For each service:
     - Determine the final location/structure
     - Update imports in dependent files
     - Ensure SQLAlchemy is used consistently
     - Update any references in routes

4. **Sitemap Scraper Service Usage Analysis (2 hours)**

   - Analyze sitemap_scraper.py to identify:
     - Which services it's currently using
     - Any direct database access that bypasses services
     - Inconsistent service usage patterns
     - Create concrete examples of how it should be refactored

5. **Service Implementation Templates (1 hour)**

   - Create standardized templates for service implementation
   - Document expected interfaces and methods
   - Show examples of proper service usage from routes

6. **Documentation (1.5 hours)**
   - Document the finalized service architecture
   - Create a service interaction diagram
   - Update any existing documentation on service usage

The goal is a clear, consistent service architecture that supports the modernized SQLAlchemy database layer, starting with proper service usage in the sitemap_scraper.py route."

This plan provides clear context about the current state, acknowledges the architectural inconsistency, and outlines specific, actionable steps to bring order to the service layer while building on the successful database migration work.

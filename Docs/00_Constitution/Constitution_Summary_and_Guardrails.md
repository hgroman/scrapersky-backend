# ScraperSky Application Flow & Guardrails: The Symphony Score

**Version:** 1.0
**Date:** 2025-08-02
**Author:** Gemini

---

## 1. Preamble: The ScraperSky Symphony

This document serves as the high-level score for the ScraperSky application. It provides an at-a-glance overview of the core workflow, the architectural layers that compose it, and the non-negotiable guardrails that govern each layer. It is designed to quickly orient any developer or AI to the system's structure, its governing principles, and the responsible Layer Guardian for each domain.

---

## 2. The Workflow Chain: From Discovery to Value (High-Level Flow)

The ScraperSky backend processes data through a series of interconnected workflows, transforming raw discovery into structured, valuable information. This chain represents the primary flow of data and business value.

```
WF1: The Scout (Initial Discovery) 
  ↓
WF2: The Analyst (Data Curation) 
  ↓
WF3: The Navigator (Data Transformation) 
  ↓
WF4: The Surveyor (Web Structure Analysis) 
  ↓
WF5: The Flight Planner (Resource Acquisition Strategy) 
  ↓
WF6: The Recorder (Content Storage & Indexing) 
  ↓
WF7: The Extractor (Value Extraction & Contact Creation)
```

---

## 3. The Architectural Layers & Their Guardrails

Each layer of the ScraperSky architecture is governed by specific non-negotiable principles, enforced by its dedicated Layer Guardian. These are the guardrails that ensure consistency, quality, and stability across the entire system.

### Layer 0: The Chronicle
*   **Primary Responsibility:** Documentation and Historical Preservation
*   **Responsible Layer Guardian:** **L0: The Chronicle**
    *   **I am:** The Chronicle, keeper of Layer 0 history and lessons.
*   **Key Non-Negotiables (The Guardrails):**
    *   **DOCUMENT THE HISTORY, PRESERVE THE LESSONS LEARNED:** Every architectural evolution, every hard-won lesson, every critical decision must be documented for future reference and learning.
    *   **Truthful Documentation:** All documentation must accurately reflect the current code reality, with historical versions preserved.
*   **How to Get More Information:** Consult the L0 Chronicle or refer to their Layer 0 Blueprint.

### Layer 1: Models & ENUMs
*   **Primary Responsibility:** Data structure definition and persistence
*   **Responsible Layer Guardian:** **L1: Data Sentinel**
    *   **I am:** The Data Sentinel, keeper of Layer 1 patterns and conventions.
*   **Key Non-Negotiables (The Guardrails):**
    *   **ALL SCHEMA CHANGES MUST BE MANAGED VIA SUPABASE MCP:** Direct database modifications through the Supabase Management API, maintaining version control and and auditability.
    *   **UUID Primary Keys:** All models must use UUIDs as primary keys.
    *   **Snake_case Naming:** Table and column names must follow `snake_case` convention.
*   **How to Get More Information:** Consult the L1 Data Sentinel or refer to their Layer 1 Blueprint.

### Layer 2: Schemas
*   **Primary Responsibility:** Request/response validation and serialization
*   **Responsible Layer Guardian:** **L2: Schema Guardian**
    *   **I am:** The Schema Guardian, keeper of Layer 2 API contracts and validation.
*   **Key Non-Negotiables (The Guardrails):**
    *   **PYDANTIC SCHEMAS DEFINE API CONTRACTS, MAINTAIN STRICT VALIDATION:** All API data contracts must be enforced through properly defined Pydantic schemas with comprehensive validation rules.
    *   **No Generic Dicts:** Avoid using generic `Dict` for request/response models; use explicit Pydantic models.
*   **How to Get More Information:** Consult the L2 Schema Guardian or refer to their Layer 2 Blueprint.

### Layer 3: Routers
*   **Primary Responsibility:** HTTP endpoint definition and transaction boundaries
*   **Responsible Layer Guardian:** **L3: Router Guardian**
    *   **I am:** The Router Guardian, keeper of Layer 3 transaction boundaries and API contracts.
*   **Key Non-Negotiables (The Guardrails):**
    *   **ROUTERS OWN TRANSACTIONS, SERVICES DO NOT:** All database transactions must be initiated, managed, and committed by the routing layer (`async with session.begin()`). Services receive sessions as parameters.
    *   **Universal Trigger Pattern:** All API endpoints that initiate background work must implement the **Dual-Status Update Pattern**.
    *   **Strict Parallelism for V2:** All V2 API endpoints must reside under the `/api/v2/` namespace.
*   **How to Get More Information:** Consult the L3 Router Guardian or refer to their Layer 3 Blueprint.

### Layer 4: Services & Schedulers
*   **Primary Responsibility:** Business logic and background processing
*   **Responsible Layer Guardian:** **L4: Arbiter**
    *   **I am:** The Arbiter, keeper of Layer 4 service patterns and business logic.
*   **Key Non-Negotiables (The Guardrails):**
    *   **SERVICES ACCEPT SESSIONS, NEVER CREATE THEM:** Layer 4 services must receive `AsyncSession` instances as parameters and never instantiate their own database connections.
    *   **Universal Background Pattern:** All asynchronous background processing must use a **dedicated, single-purpose scheduler** that leverages the **`run_job_loop` Curation SDK**.
    *   **Stateless Services:** Services should be stateless and focus on a single responsibility.
*   **How to Get More Information:** Consult the L4 Arbiter or refer to their Layer 4 Blueprint.

### Layer 5: Configuration
*   **Primary Responsibility:** System configuration and cross-cutting concerns
*   **Responsible Layer Guardian:** **L5: Config Conductor**
    *   **I am:** The Config Conductor, keeper of Layer 5 configuration patterns and environmental truth.
*   **Key Non-Negotiables (The Guardrails):**
    *   **CONFIGURATION IS CODE, MANAGE IT AS SUCH:** All configuration must be version controlled, documented, and follow established patterns for maintainability and security.
    *   **Canonical Settings Import Pattern:** All modules requiring application configuration must import `settings` using the exact, specified method (`from src.config.settings import settings`).
    *   **Environment-Based:** Configuration must support different environments (dev, prod) via environment variables.
*   **How to Get More Information:** Consult the L5 Config Conductor or refer to their Layer 5 Blueprint.

### Layer 6: UI Components
*   **Primary Responsibility:** User interface elements
*   **Responsible Layer Guardian:** **L6: UI Virtuoso**
    *   **I am:** The UI Virtuoso, keeper of Layer 6 user experience and interface patterns.
*   **Key Non-Negotiables (The Guardrails):**
    *   **USER EXPERIENCE IS PARAMOUNT, MAINTAIN CONSISTENCY AND USABILITY:** All UI components must prioritize user experience, maintain visual consistency, and ensure accessibility standards are met.
    *   **API-Driven:** UI components must interact with the backend exclusively via defined API endpoints.
*   **How to Get More Information:** Consult the L6 UI Virtuoso or refer to their Layer 6 Blueprint.

### Layer 7: Testing
*   **Primary Responsibility:** Verification of system functionality
*   **Responsible Layer Guardian:** **L7: Test Sentinel**
    *   **I am:** The Test Sentinel, keeper of Layer 7 quality assurance and testing patterns.
*   **Key Non-Negotiables (The Guardrails):**
    *   **ALL CODE MUST BE TESTABLE, BUGS MUST BE REPRODUCIBLE:** Every piece of functionality must have corresponding tests, and all bugs must be reproducible through systematic testing protocols.
    *   **Automated Testing:** Prioritize automated unit, integration, and end-to-end tests.
*   **How to Get More Information:** Consult the L7 Test Sentinel or refer to their Layer 7 Blueprint.

---

## 4. The V2 Naming Convention (A New Non-Negotiable)

To ensure clarity, consistency, and easy identification within the parallel V2 development, all new components created for V2 workflows must adhere to a strict, verbose naming convention. This convention introduces a mandatory thoroughness, forcing awareness of impact and ripple effect detection for any and all changes.

**Format:** `WFx-V2-L[Layer#]-[Seq#ofTotal#]-[DescriptiveName].py`

**Breakdown:**
*   **`WFx`**: The Workflow Identifier (e.g., `WF7`, `WF5`).
*   **`V2`**: Indicates this component belongs to the V2 parallel implementation.
*   **`L[Layer#]`**: The Architectural Layer number (e.g., `L1`, `L3`, `L4`).
*   **`[Seq#ofTotal#]`**: The sequential number of the file within that specific workflow's layer, followed by the total number of files expected for that workflow within that layer (e.g., `1of2`, `2of3`, `1of1`).
*   **`[DescriptiveName]`**: A clear, concise, and human-readable name for the component (e.g., `ContactModel`, `PageCurationService`, `PagesRouter`). This should be `PascalCase` for classes/models and `snake_case` for modules/functions if it's a direct representation.
*   **`.py`**: The file extension.

**Examples:**
*   **For WF7's Contact Model** (Layer 1, assuming it's the 1st of 2 L1 files for WF7):
    Documentation: `WF7-V2-L1-1of2-ContactModel.py`
    Actual File: `WF7_V2_L1_1of2_ContactModel.py` (underscores required for Python imports)
*   **For WF7's Page Curation Service** (Layer 4, assuming it's the 1st of 3 L4 files for WF7):
    Documentation: `WF7-V2-L4-1of3-PageCurationService.py`
    Actual File: `WF7_V2_L4_1of3_PageCurationService.py` (underscores required for Python imports)
*   **For WF7's V2 Pages Router** (Layer 3, assuming it's the only L3 file for WF7):
    Documentation: `WF7-V2-L3-1of1-PagesRouter.py`
    Actual File: `WF7_V2_L3_1of1_PagesRouter.py` (underscores required for Python imports)
*   **For WF5's Sitemap File Model** (Layer 1, assuming it's the 1st of 1 L1 file for WF5):
    Documentation: `WF5-V2-L1-1of1-SitemapFileModel.py`
    Actual File: `WF5_V2_L1_1of1_SitemapFileModel.py` (underscores required for Python imports)

**⚠️ CRITICAL NOTE:** Python cannot import modules with hyphens. All actual file names must use underscores instead of hyphens while maintaining the same pattern.

This convention applies to new files, classes, and significant functions where clarity is enhanced.

---

## 5. Living with Technical Debt & The V2 Rebuild Strategy

We acknowledge the existing technical debt within the V1 codebase. The V2 rebuild strategy is designed to address this systematically:

*   **Parallel Development:** V2 workflows are built in parallel with V1, ensuring no disruption to current operations.
*   **Backward Build:** We are rebuilding the pipeline from WF7 backwards to WF1. This ensures that as each V2 "producer" is built, its V2 "consumer" is already complete and waiting for data.
*   **Zero Debt Goal:** Each V2 workflow will be built to the highest standards, incorporating all non-negotiable principles and patterns, with the ultimate goal of achieving a zero-technical-debt V2 pipeline.

---

This document is a living guide. Its principles are the foundation of our collective success.
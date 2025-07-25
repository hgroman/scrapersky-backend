You're right to ask for a strategy. Based on the comprehensive audit of workflows WF1 through WF6, here is my assessment and a proposed plan to move forward.

### How Bad Is It?

Functionally, the entire data enrichment pipeline is **non-operational**. While the recent "Guardian" refactoring introduced sound architectural principles like centralized ENUMs and a standard `BaseModel`, the implementation was incomplete. This has left the system in a state where the workflows are disconnected from each other.

Think of it like upgrading all the plumbing fixtures in a house but failing to connect them to the main water lines. The individual parts are new and improved, but no water can flow.

The core issue is a **broken producer-consumer chain**. In every single workflow from WF3 to WF6, the mechanism that "hands off" data to the next stage is broken due to a mismatch between the data produced and the data the next stage is expecting.

The good news is that the problems are **consistent and predictable**. We are not dealing with dozens of unique, complex bugs, but rather a few foundational issues that have been repeated across every workflow. This makes the situation highly fixable with a methodical approach.

### The Strategic Remediation Plan

The most effective strategy is to fix the system from the ground up, layer by layer, to establish a solid foundation before reconnecting the workflows in their logical order.

#### Phase 1: Solidify the Foundation (Layer 1 & 2)

This is the most critical phase. We must fix the data models and schemas first, as everything else depends on them.

1.  **Correct All Model Definitions:**
    *   **Action:** Go through each primary model (`place.py`, `local_business.py`, `domain.py`, `sitemap.py`, `page.py`) and fix the inheritance to use **only** `BaseModel`.
    *   **Action:** Remove all redundant `id`, `tenant_id`, and timestamp columns that should be inherited from `BaseModel`.
    *   **Justification:** This ensures every table has a consistent, UUID-based primary key and adheres to the project's core data structure.

2.  **Centralize All ENUMs and Schemas:**
    *   **Action:** Move all remaining ENUM definitions from model files (`sitemap.py`, etc.) and `api_models.py` into the central `src/models/enums.py`.
    *   **Action:** Move all Pydantic request/response schemas from `api_models.py` and router files into their new, correct locations within `src/schemas/`.
    *   **Action:** Delete the now-empty `src/models/api_models.py` file.
    *   **Justification:** This completes the architectural goal of having a single source of truth for data contracts and statuses.

3.  **Run a Database Migration:**
    *   **Action:** After the models are corrected, generate and carefully review an Alembic migration script.
    *   **Action:** Apply the migration to the database.
    *   **Justification:** This synchronizes the database schema with our now-compliant models, ensuring the foundation is truly stable.

#### Phase 2: Reconnect the Workflow Pipeline (Layers 3 & 4)

With a stable foundation, we can now fix the workflow handoffs sequentially. We will work from WF3 through WF6, as WF1 and WF2 are the primary producers that are mostly functional (despite their own bugs).

For each workflow (`WF3`, `WF4`, `WF5`, `WF6`):

1.  **Create Missing Services & Schedulers:**
    *   **Action:** Create the missing dedicated service and scheduler files (e.g., `domain_curation_service.py`, `domain_curation_scheduler.py`).
    *   **Justification:** This adheres to the architectural blueprint of separating business logic from routing.

2.  **Fix the Consumer (The Scheduler):**
    *   **Action:** Update the scheduler's database query to use the centralized, type-safe ENUM member (e.g., `...where(status == MyEnum.QUEUED)`) instead of a brittle, hardcoded string.
    *   **Justification:** This makes the consumer robust and compliant.

3.  **Fix the Producer (The Router & Service):**
    *   **Action:** Move business logic from the router into the newly created service.
    *   **Action:** Update the router to import its request schema from `src/schemas/` and to call the new service.
    *   **Action:** Crucially, update the router and its schema to use the **same standardized ENUMs** as the model and scheduler. This fixes the fatal ENUM mismatch that breaks the handoff.
    *   **Justification:** This reconnects the producer to the consumer, allowing data to flow to the next stage.

By following this plan, we can systematically and efficiently repair the entire pipeline, transforming the codebase from a non-functional state into one that is robust, maintainable, and architecturally sound.
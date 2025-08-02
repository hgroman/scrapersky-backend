# AI Role Context Primers for ScraperSky Backend

## Purpose

This document outlines recommended "context recipes" for efficiently priming AI assistants for specific roles within the ScraperSky backend project. The goal is to provide a targeted set of existing project documents that will give the AI the most relevant context for common tasks, reducing onboarding time and ensuring its contributions align with our architectural truth, conventions, and current project state.

By providing this focused context, we aim to:

- Enhance the quality and relevance of AI-assisted development.
- Minimize the need for extensive iterative questioning to establish a baseline understanding.
- Ensure AI suggestions are grounded in documented project standards.

---

## Role-Based Context Recipes

### 1. Role: Code Development

**Objective:** To assist with new feature development, bug fixes, implementing changes based on work orders, and general coding tasks.

**Recommended Context Documents (in order of review):**

1.  **`Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`**
    - **Purpose:** Understand the target 7-layer architecture, core architectural principles (ORM-only, transaction management, API versioning, etc.), and key technologies.
2.  **`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`**
    - **Purpose:** Learn the detailed, mandatory naming and structural conventions for all code layers (models, schemas, routers, services, UI elements, tests, etc.).
3.  **`Docs/Docs_6_Architecture_and_Status/4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md`**
    - **Purpose:** Get a clear picture of the current implementation status, compliance metrics (e.g., transaction boundary compliance, API versioning gaps), known technical debt, and immediate project priorities.
4.  **`README.md`**
    - **Purpose:** Understand practical project setup, environment configuration, how to run and test the application, available tooling (like `db_inspector.py`), and the CI/tooling philosophy.

**Opening Instruction for AI:**

> "You are assisting with code development for the ScraperSky backend. Please review these documents in the order provided to understand the project's target architecture, detailed coding conventions, current implementation status, and practical development environment.
> **Important Note:** If any architectural descriptions in `README.md` (e.g., regarding multi-tenancy) directly contradict the information in the `1.0-ARCH-TRUTH-Definitive_Reference.md` or `4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md`, please prioritize the `ARCH-TRUTH` documents as the definitive source for architectural state and current plans."

---

### 2. Role: Code Cleanup & Refactoring

**Objective:** To assist with improving code quality, ensuring adherence to established standards, refactoring existing code for better clarity or efficiency, and addressing identified technical debt.

**Recommended Context Documents (in order of review):**

1.  **`Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`**
    - **Purpose:** Understand the target 7-layer architecture and the core architectural principles the codebase should adhere to.
2.  **`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`**
    - **Purpose:** Internalize the specific, mandatory naming and structural rules. This is critical for identifying deviations and refactoring code to meet standards.
3.  **`Docs/Docs_6_Architecture_and_Status/4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md`**
    - **Purpose:** Identify areas with known technical debt, low compliance metrics, and where refactoring efforts are most needed according to current project priorities.

**Opening Instruction for AI:**

> "You are assisting with code cleanup and refactoring for the ScraperSky backend. Please review these documents in the order provided to understand the project's target architecture, detailed coding conventions, and current compliance status. Your goal is to help identify areas for improvement and ensure that any proposed changes align strictly with the established standards and address known technical debt."

---

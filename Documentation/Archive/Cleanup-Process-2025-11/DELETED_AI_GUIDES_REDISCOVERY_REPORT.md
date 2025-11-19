# Report: Rediscovery and Mapping of Critical Deleted AI Guides

**Date:** November 16, 2025
**Author:** Cascade
**Status:** Complete
**Audience:** ScraperSky Documentation Consolidation Team

## 1. Executive Summary

This report documents the investigation into a set of critical AI development guides, formerly located in a directory named `Docs/Docs_1_AI_GUIDES/`, which were deleted from the repository.

The investigation confirms that the directory and its contents were intentionally deleted on **May 21, 2025 (commit `c32d565d`)** during a large-scale documentation audit.

Crucially, the investigation also confirms that the core, "hard-won principles" from these guides were **not lost**. They were preserved and integrated into various other documents, most notably into formal **Architecture Decision Records (ADRs)** and **Lessons-Learned** analyses.

This report provides a definitive map from the original deleted files to their new, decentralized locations, enabling the documentation team to verify their inclusion and consolidate them into the new canonical documentation set at `Documentation/`.

## 2. Investigation Methodology

The findings were established through a multi-step forensic analysis of the git history:
1.  Initial `git log` searches for the directory failed, indicating a non-standard deletion or renaming.
2.  An audit file (`.../Docs_Docs_1_AI_GUIDES_..._audit.md`) was used as an anchor to identify the exact commit (`c32d565d`) where the deletion occurred.
3.  The contents of the critical deleted files were retrieved from the commit *prior* to their deletion (`c32d565d~1`).
4.  Unique, core phrases from each deleted file were used to `grep` the current state of the entire repository, pinpointing the new locations of these principles.

## 3. Detailed Findings: Mapping Principles from Old to New

The following is a file-by-file analysis of the most critical deleted guides and where their content now resides.

### 3.1. SQLAlchemy & ORM Rules

#### **Original File:** `Docs/Docs_1_AI_GUIDES/01-LAYER1_ABSOLUTE_ORM_REQUIREMENT.md`
*   **Core Principle:** NEVER USE RAW SQL IN APPLICATION CODE. All database interactions must go through the SQLAlchemy ORM.
*   **Status:** **Preserved and Decentralized.** The principle is now a "war story" used to justify architectural decisions.
*   **New Locations & Evidence:**
    *   **`Docs/Docs_5_Project_Working_Docs/11-LAYER4_Background-Task-Scheduler/11.12-BACKGROUND-TASK-SCHEDULER-LESSONS-LEARNED.md`**
        > ```
        > ⚠️ CRITICAL ARCHITECTURAL PRINCIPLE ⚠️
        > ┌─────────────────────────────────────────────────────┐
        > │ NEVER USE RAW SQL IN APPLICATION CODE               │
        > └─────────────────────────────────────────────────────┘
        > ```
    *   **`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/Process/0.0_AI_Project_Primer.md`**
        > ```
        > #### 1. NEVER USE RAW SQL IN APPLICATION CODE
        > ```

---

#### **Original File:** `Docs/Docs_1_AI_GUIDES/27-LAYER1_ENUM_HANDLING_STANDARDS.md`
*   **Core Principle:** Established strict naming conventions for Enums (`PascalCaseEnum`) and rules for handling them in SQLAlchemy (`.value`).
*   **Status:** **Preserved and Evolved.** The principle was formalized into a detailed Architecture Decision Record after a catastrophic system failure.
*   **New Location & Evidence:**
    *   **`Documentation/Architecture/ADR-005-ENUM-Catastrophe.md`**
        > This ADR documents the "ENUM Catastrophe" and establishes a mandatory, backwards-compatible process for all cross-layer refactors. It explicitly contains the correct patterns for handling Enums in SQLAlchemy to avoid database errors.
        > ```python
        > # ✅ CORRECT: Always use .value for SQLAlchemy operations
        > filters.append(Contact.status == ContactStatus.New.value)  # WORKS!
        > contact.status = ContactStatus.Active.value  # WORKS!
        > ```

---

#### **Original File:** `Docs/Docs_1_AI_GUIDES/25-LAYER1_SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md`
*   **Core Principle:** Intended to define rules for SQLAlchemy model integrity.
*   **Status:** **Empty.** The investigation revealed this file contained no content and was a placeholder. No knowledge was lost.

### 3.2. Router & API Rules

#### **Original File:** `Docs/Docs_1_AI_GUIDES/15-LAYER3_API_STANDARDIZATION_GUIDE.md`
*   **Core Principle:** All APIs must use the `/api/v3/` prefix, follow standard response structures, and include authentication.
*   **Status:** **Preserved and Integrated.** The rules are now part of the canonical architectural patterns library.
*   **New Location & Evidence:**
    *   **`Docs/01_Architectural_Guidance/03_ARCHITECTURAL_PATTERNS_LIBRARY.md`**
        > This comprehensive library contains the official patterns for all layers.
        > ```python
        > # ✅ CORRECT: New code uses v3
        > router = APIRouter(prefix="/api/v3/pages")
        > ```
        > The document also specifies the "Router owns transaction" and "Auth dependency" patterns, fully capturing the intent of the original guide.

## 4. Recommendations for the Documentation Team

1.  **Acknowledge This Report:** Confirm that your team has received and reviewed these findings.

2.  **Verify and Consolidate:** Use this report as a map. Your primary action should be to ensure that the principles detailed here are adequately and clearly represented in the new, canonical `Documentation/` directory. For example:
    *   The "ABSOLUTE ORM REQUIREMENT" should be a prominent rule in `Documentation/Development/CONTRIBUTING.md`.
    *   The lessons from `ADR-005-ENUM-Catastrophe.md` should be referenced in any guide that discusses database models or migrations.
    *   The API standards from the `03_ARCHITECTURAL_PATTERNS_LIBRARY.md` should be the single source of truth for all API development.

3.  **Archive the Old `Docs`:** Once your team has fully integrated and verified this knowledge, the historical `Docs/` sub-directories (e.g., `Docs_5_Project_Working_Docs`) can be moved to a final archive location to prevent future confusion.

This investigation has successfully bridged the gap between past knowledge and the current documentation effort. By following these recommendations, the team can ensure that these hard-won principles are preserved and continue to guide the development of ScraperSky.

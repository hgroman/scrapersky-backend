# Blueprint BP-01: Standard Curation Workflow

**Version:** 1.0
**Date:** 2025-05-02
**Author:** AI Assistant (Gemini) & Hank Groman

## 1. Purpose

This document serves as the **standard blueprint** for designing, implementing, and auditing UI-driven curation workflows within the ScraperSky backend. It ensures consistency, maintainability, and adherence to established architectural principles.

**Use Cases:**

1. **Development Guide:** Provides a step-by-step template for building new curation features (e.g., adding a new status, triggering a different background process).
2. **Auditing Checklist:** Offers a framework for reviewing existing curation workflows against core principles.
3. **Onboarding Tool:** Helps new developers understand the standard pattern for data flow and responsibility separation.

This blueprint is derived from analyzing existing successful patterns (like the "Local Business Curation -> Domain Extraction" flow) and codifying the principles outlined in `Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md`.

## 1.1. Principles Checklist Legend

The checklists below use the following abbreviations, referencing sections in `Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md`:

- **API Std:** API Standardization (Section 1)
- **Conn Mgmt:** Connection Management (Section 2)
- **Txn Boundary:** Transaction Boundaries (Section 3)
- **UUID Std:** UUID Standardization (Section 4)
- **Auth Boundary:** Authentication Boundary (Section 5)
- **Error Handling:** Error Handling (Section 6)
- **Bg Task Pattern:** Background Task Pattern (Section 7)
- **Code Org:** Code Organization (Section 8)
- **ORM Req:** ORM Requirement (Implied; See `01-ABSOLUTE_ORM_REQUIREMENT.md`)
- **Enum Handling:** Enum Handling (See `27-ENUM_HANDLING_STANDARDS.md`)
- **Models:** Use of SQLAlchemy Models (Implied by ORM Req)
- **Decoupling:** Design principle ensuring separation between components.
- **Atomicity:** Ensuring operations complete fully or not at all (relevant to transactions).
- **Clear User Feedback:** UI/UX principle.

---

## 5. Using this Blueprint for Validation with AI

To support systematic validation of curation workflows, a YAML-based format is used to encode each workflow trace against this blueprint. This process is especially powerful when paired with AI agents (e.g., Cursor, GPT-based tools) capable of reasoning over code.

### 🎯 Purpose:

- Capture how a real workflow maps to BP-01 phases and principles
- Provide a structured checklist for audits
- Enable AI-based static analysis and developer onboarding

### 🔄 Lifecycle:

1. A human or AI generates the initial YAML trace for a specific workflow
2. An AI assistant reviews each phase and step:

   - Verifies that each principle marked `true` is actually upheld
   - Flags any missing or violated principles

3. Validated YAMLs are stored in:

   - `Docs/Docs_9_Workflow_Validation/`
   - Named like `WF-03-LocalBusiness-Validation.yaml`

### 🤖 AI Instructions:

If you are an AI assistant reviewing YAMLs:

- Use static analysis to confirm principle adherence
- Cross-reference the principle keys with the legend in Section 1.1
- Be explicit: mark each as `true` or `false`, and use notes to explain any `false` values

---

## 6. Appendix: YAML Validation Template

```yaml
workflow_name: Example Workflow Name
date_reviewed: YYYY-MM-DD
reviewed_by: Hank Groman

phases:
  - phase: UI Interaction
    steps:
      - step_id: 1.1
        file: static/js/example-tab.js
        action: User selects rows, clicks "Update"
        principles:
          API Std: true
          Clear User Feedback: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: ""

  - phase: API Routing
    steps:
      - step_id: 2.1
        file: src/routers/example_router.py
        action: Validates request and starts transaction
        principles:
          API Std: true
          Auth Boundary: true
          Conn Mgmt: true
          Txn Boundary: true
          Code Org: true
          UUID Std: true
          Enum Handling: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: ""

  - phase: Service Delegation & Logic
    steps:
      - step_id: 3.1
        file: src/services/example_service.py
        action: Business logic executes update
        principles:
          Auth Boundary: true
          Txn Boundary: true
          ORM Req: true
          Code Org: true
          UUID Std: true
          Enum Handling: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: ""

  - phase: Database Interaction
    steps:
      - step_id: 4.1
        file: src/services/example_service.py
        action: ORM fetch/update
        principles:
          ORM Req: true
          Models: true
          Enums: true
          UUIDs: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: ""

  - phase: Background Task Triggering
    steps:
      - step_id: 5.1
        file: src/services/example_service.py
        action: Sets `next_step_status = 'Queued'`
        principles:
          Decoupling: true
          Atomicity: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: "Status-based queuing"

  - phase: Background Task Execution
    steps:
      - step_id: 6.1
        file: src/services/example_scheduler.py
        action: Polls and processes queued records
        principles:
          Bg Task Pattern: true
          Conn Mgmt: true
          Txn Boundary: true
          ORM Req: true
          Code Org: true
          Error Handling: true
          # Example: If violated, mark false with explanation in notes
          Txn Boundary: false
        notes: ""
```

---

_This format ensures that all workflows—manual or machine-generated—can be traced, validated, and continuously aligned with the architectural blueprint._

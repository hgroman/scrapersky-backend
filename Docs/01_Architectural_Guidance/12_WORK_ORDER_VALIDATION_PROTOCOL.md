# Protocol: Work Order Validation

**Purpose:** To provide a mandatory, evidence-based validation process that all Work Orders must pass before implementation. This protocol prevents work from starting based on flawed assumptions and ensures all proposed changes are grounded in the "truth of the files."

**Philosophy:** Trust, but verify with code.

---

## The Validation Checklist

Before a Work Order can be approved for implementation, the assigned developer or AI partner MUST perform the following checks and document the results.

### 1. Prerequisite Verification

For every prerequisite or assumption listed in the Work Order, provide evidence of its current state.

*   **Action:** Use tools like `read_file`, `grep`, or database queries to verify each claim.
*   **Example (from the chat log):**
    *   **Claim:** The `page_type` Enum exists and is correctly configured.
    *   **Evidence:**
        1.  `read_file('src/models/enums.py')` to verify the Python `PageTypeEnum` definition.
        2.  `read_file('src/models/page.py')` to verify the SQLAlchemy model's column definition.
        3.  `execute_sql('SELECT unnest(enum_range(NULL::page_type_enum))')` to verify the actual values in the live database.
    *   **Deliverable:** A "Schema Verification Results" section in the Work Order's chat history, confirming alignment between all layers.

### 2. Pattern & Anti-Pattern Compliance Review

The Work Order must be explicitly checked against our established patterns.

*   **Action:**
    1.  Parse the `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_MENU.yaml`.
    2.  For each proposed code change in the Work Order, identify the corresponding building block from the YAML file.
    3.  Confirm that the proposed code is a direct application of the `template` from the building block.
    4.  Review the linked `war_stories` for any relevant anti-patterns and confirm the Work Order does not repeat them.
*   **Deliverable:** An "Architectural Compliance" section confirming that the plan adheres to specific, named patterns (e.g., `sqlalchemy_enum_column`, `value_driven_service_return`).

### 3. "Truth of the Files" Confirmation

The final implementation plan must be based on the verified state of the files, not just the Work Order's text.

*   **Action:** Before generating the final implementation steps, re-read the primary files that will be modified.
*   **Example (from the chat log):**
    *   The AI re-read `WF7_V3_L3_1of1_PagesRouter.py` and `WF7_V3_L2_1of1_PageCurationSchemas.py` to confirm the exact line numbers and existing code structure before proposing the final `replace` operations.
*   **Deliverable:** A final, actionable implementation plan that is explicitly grounded in the current content of the target files.

---

## Final Verdict

Only after all three validation steps are complete and documented in the chat log can a Work Order be moved from "Ready for Peer Review" to "Approved for Implementation."

This protocol makes verification a mandatory, evidence-based part of our workflow, ensuring we never again proceed with a plan based on a faulty premise.

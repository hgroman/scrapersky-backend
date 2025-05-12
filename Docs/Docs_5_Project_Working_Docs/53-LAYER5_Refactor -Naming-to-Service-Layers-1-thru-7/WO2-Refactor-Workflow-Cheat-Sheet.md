# Work Order: Refactor ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md

**Objective:**
Refactor the `Docs/Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md` document to improve its readability, maintainability, and utility as a "cheat sheet" by externalizing large code blocks and reducing in-document code to essential illustrative snippets.

**Source Document:**

- `Docs/Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md`

**Key Tasks:**

1.  **Identify and Categorize Code Blocks:**

    - Thoroughly review the source document and identify all substantial code blocks. These will include Python, SQL, JavaScript, and HTML examples.

2.  **Create New Directory for Code Snippets:**

    - Create a new directory: `Docs/Docs_Code_Snippets/Workflow_Templates/`
    - If this path needs adjustment for better organization within the `Docs` structure, please use a sensible alternative and note it.

3.  **Externalize Large Code Blocks:**

    - For each identified substantial code block:
      - Create a new, appropriately named file within the `Docs/Docs_Code_Snippets/Workflow_Templates/` directory.
      - Examples names:
        - `workflow_api_router_example.py` (for section 2.1.2)
        - `workflow_scheduler_example.py` (for section 3.1, including the `setup_{workflow_name}_scheduler` function)
        - `workflow_curation_service_example.py` (for section 4.1)
        - `workflow_ui_tab_example.html` (for section 4.5.1)
        - `workflow_ui_tab_example.js` (for section 4.5.2)
      - Move the complete code block from the cheat sheet into this new file.
      - Ensure all placeholders (e.g., `{workflow_name}`, `{source_table}`, etc.) are preserved in the extracted files.

4.  **Update the Original Cheat Sheet:**
    - **Replace Externalized Code:** In place of the moved code blocks, insert:
      - A concise description of what the code block does and its purpose.
      - A clear markdown link to the newly created external file.
      - Example: "For a full example of the API router implementation, see: [workflow_api_router_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_api_router_example.py)"
    - **Shrink In-Document Code:** For remaining code snippets (e.g., SQL DDL, SQLAlchemy Model additions, short configuration examples):
      - Reduce them to show only the critical lines or the essential pattern.
      - The goal is to illustrate the _concept_ or _convention_, not provide a full copy-paste block within the cheat sheet.
      - Example for SQLAlchemy model update:
        ```python
        # In src/models/{source_table}.py
        # ...
        {workflow_name}_curation_status = Column(PgEnum(...), ...)
        {workflow_name}_processing_status = Column(PgEnum(...), ...)
        # ...
        ```
    - **Preserve Core Content:** Ensure all non-code critical information remains clear and prominent. This includes:
      - The 5-phase overview and step-by-step instructions.
      - Questionnaires and definitions.
      - Critical Naming Conventions and Transaction Patterns.
      - Links to other relevant guides and architectural documents.
      - The "ENUM STANDARDIZATION MANDATE".
    - **Maintain Placeholders:** All existing `{placeholder}` values in text and remaining snippets should be preserved.

**Goals & Expected Outcome:**

- The line count of `ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md` should be significantly reduced (aim for a 50-70% reduction).
- The document should be transformed into a more focused and readable reference guide.
- The externalized code snippets should serve as complete, ready-to-adapt templates.

**Deliverables:**

1.  The updated, leaner `Docs/Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md`.
2.  The new directory (`Docs/Docs_Code_Snippets/Workflow_Templates/` or alternative) containing all the extracted code snippet files.
3.  A list of all files created and the primary file modified.

**Completion Criteria:**

- All substantial code blocks are externalized.
- The cheat sheet primarily contains conceptual guidance, illustrative snippets, and links.
- The document is significantly shorter and easier to navigate.

Please proceed with this refactoring. Let me know if any part of this Work Order is unclear.
When you are finished, please provide a summary of the changes made and list the new/modified files.

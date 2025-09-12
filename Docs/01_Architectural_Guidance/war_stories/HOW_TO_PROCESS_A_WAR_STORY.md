# Protocol: Processing a "War Story" into Institutional Knowledge

**Purpose:** This document outlines the mandatory, 5-step process for converting a significant technical incident (a "war story" or "train wreck") into a set of robust, lasting, and enforceable assets for the ScraperSky project.

**Philosophy:** A mistake is only a failure if we fail to learn from it. This process ensures that every hard-won lesson makes our system and our development practices more resilient.

---

## The "War Story Quadrant" Model

This protocol is built on a four-part model designed to address the root causes of implementation failures. A complete solution requires addressing each quadrant:

1.  **The "Why" (The War Story):** The narrative context. Why is this rule so important? What was the pain that led to its creation? This provides the institutional memory.
2.  **The "What" (The Code Template):** The machine-readable, correct code. What is the single source of truth for the implementation? This provides the battle-tested asset.
3.  **The "How" (The Developer Guide):** The human-readable instructions. How does a developer use the asset correctly? This provides clear, actionable guidance.
4.  **The "Enforcement" (The Linter Rule):** The automated guardrail. How do we make it impossible to repeat the mistake? This provides the safety net.

## The 5-Step Protocol

When a significant incident has been resolved, the following five steps MUST be completed to officially close the incident and integrate the learnings.

### Step 1: Write the War Story (The "Why")

The first step is to document the incident as a clear, concise narrative. This is not a dry technical report; it is a story designed to be memorable and educational.

*   **Action:** Create a new markdown file in the `Docs/01_Architectural_Guidance/war_stories/` directory.
*   **Naming Convention:** `WAR_STORY__{Topic}__{Date}.md` (e.g., `WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md`).
*   **Content:** The story should, at a minimum, describe:
    *   The initial goal.
    *   The "Original Sin": The subtle but critical mistake that was made.
    *   The "Train Wreck": The cascade of failures and flawed reactive fixes that resulted.
    *   The "Aha! Moment": The root cause analysis that led to the true fix.
    *   The Final Lesson: A clear summary of what was learned.

### Step 2: Codify the Building Block (The "What")

Extract the correct, reusable code pattern from the final solution and add it to the machine-readable database of patterns.

*   **Action:** Edit the `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_MENU.yaml` file.
*   **Content:** Add a new entry under the `building_blocks` section. This entry MUST contain:
    *   A clear `name` and `description`.
    *   The full, commented, copy-pasteable code in a `template` field.
    *   A `war_story_link` pointing to the file created in Step 1.
    *   A `docs_link` that will point to the guide in Step 3.

### Step 3: Create or Update the Guide (The "How")

Create or update the relevant human-readable developer guide to instruct developers on the new, mandatory pattern.

*   **Action:** Create or edit a markdown file in the `Docs/01_Architectural_Guidance/developer_guides/` directory.
*   **Content:** The guide must:
    1.  Clearly state that the new pattern is **mandatory**.
    2.  Explicitly forbid the anti-pattern that was identified in the war story.
    3.  Instruct the developer to get the code template from the `09_BUILDING_BLOCKS_MENU.yaml` file.
    4.  Provide a direct link to the war story document for context.

### Step 4: Define the Enforcement (The "Enforcement")

Define the automated check that makes the anti-pattern impossible to commit in the future.

*   **Action:** Create a new file in the `linting_rules/` directory.
*   **Naming Convention:** `scrapersky_{topic}_rule.py`.
*   **Content:** The file should contain a clear definition or pseudo-code for a custom linter rule. The rule's error message MUST be explicit and point the developer to the Developer Guide created in Step 3.

### Step 5: Update the Toolshed Index

Make the new assets discoverable.

*   **Action:** Edit the `Docs/01_Architectural_Guidance/TOOLSHED_TABLE_OF_CONTENTS.md`.
*   **Content:** Add links to the new War Story and the new/updated Developer Guide in the appropriate sections. Update the document count.

---

By following this 5-step process, we ensure that every incident, no matter how painful, results in a permanent and positive improvement to our codebase, our processes, and our collective knowledge.
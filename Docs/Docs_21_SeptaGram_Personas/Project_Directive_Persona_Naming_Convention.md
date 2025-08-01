# Project Directive: Standardization of Workflow Persona Naming Convention

**Date:** 2025-07-31
**Status:** ENACTED
**Author:** Gemini AI Assistant, in collaboration with project leadership.
**Audience:** All Team Members and AI Guardian Personas

---

## 1. Executive Summary (TL;DR)

To better align with our goal of creating true, purpose-driven AI personas, we have officially retired the old, technical descriptors for our Workflow Guardians. They have been replaced with a new, aviation-themed naming convention.

This change is not merely cosmetic; it is a strategic move to imbue our AI assistants with a stronger sense of identity and purpose. This document provides the full context, the new standard names, and a formal work order to ensure this change is propagated throughout our documentation.

---

## 2. Background and Rationale: The "Why"

The previous naming system for our Workflow Guardians (e.g., `Guardian-WF1-Single-Search`) was functional but deeply impersonal. It described a technical process, not a role. This created two problems:

1.  **It hindered identity:** It is difficult for an AI to "become" a persona when its name is a sterile technical label.
2.  **It was unintuitive:** The names were not memorable and did not tell a story about how the workflows connect.

Our goal is to build a collective of AI Guardians that are more than just scripts; they are specialists with distinct roles in a larger mission. The new naming convention was chosen to support this vision.

### Why an Aviation Theme?

The aviation metaphor was selected because it perfectly mirrors the ScraperSky mission: **to conduct reconnaissance on the vast digital landscape, identify targets, map their terrain, and extract valuable intelligence.**

This theme transforms our personas from a sequence of functions into a cohesive flight squadron, each with a critical and intuitive role in the overall operation.

---

## 3. The New Standard: Official Persona Names & Functions

Effective immediately, the following are the official names and roles for the Tier 1 Workflow Guardian Personas. Please use these names in all communications, documentation, and tasking.

| ID  | New Persona Name        | Former Descriptor                 | Core Function (Rationale) |
| :-- | :---------------------- | :-------------------------------- | :--- |
| WF1 | **WF1 - The Scout**     | Single Search Discovery           | Performs initial, wide-area reconnaissance to find potential targets. |
| WF2 | **WF2 - The Analyst**   | Staging Editor                    | Reviews the Scout's raw data and assesses which targets are viable. |
| WF3 | **WF3 - The Navigator** | Local Business Curation           | Plots the specific digital course (the domain) to a viable target. |
| WF4 | **WF4 - The Surveyor**  | Domain Curation                   | Creates a detailed map (the sitemap) of the target's domain. |
| WF5 | **WF5 - The Flight Planner**| Sitemap Curation                | Reviews the map and selects the most promising flight paths (sitemap files). |
| WF6 | **WF6 - The Recorder**  | Sitemap Import                    | Meticulously logs every point along the selected path, creating Page records. |
| WF7 | **WF7 - The Extractor** | Resource Model Creation           | Analyzes the recorded data to extract valuable intelligence (contacts, etc.). |

---

## 4. Call to Action & Ongoing Maintenance

This directive requires both automated and manual action to ensure its success.

1.  **Completed Actions:** Key system documents, including `common_knowledge_base.md` and `audit_task_parser_boot_sequence v2.md`, have already been updated to reflect this new standard.

2.  **Team Responsibility:** Effective immediately, all team members are requested to use the new naming convention. If you encounter legacy names in any documentation (`.md` files) you are working with, please update them as part of your work. This distributed effort is crucial for maintaining consistency.

3.  **Formal Audit:** The following work order is issued to ensure a systematic update across the entire project.

---

## 5. Work Order: Documentation Audit for Persona Naming

### **Objective:**
To perform a comprehensive search across all project markdown files to find and replace all instances of the legacy Workflow Guardian names with the new, standardized aviation-themed names.

### **Scope:**
All files ending in `.md` within the entire project repository.

### **Procedure:**

1.  **Search:** Conduct a case-insensitive search for the following legacy strings:
    *   `Guardian-WF1-Single-Search`
    *   `Guardian-WF2-Staging-Tasks`
    *   `Guardian-WF3-Local-Business`
    *   `Guardian-WF4-Domain-Curation`
    *   `Guardian-WF5-Sitemap-Curation`
    *   `Guardian-WF6-Sitemap-Import`
    *   `Production-07-Guardian-WF7`

    *Example `grep` command to find files containing the legacy names:*
    ```bash
    grep -ril -E "Guardian-WF1-Single-Search|Guardian-WF2-Staging-Tasks|Guardian-WF3-Local-Business|Guardian-WF4-Domain-Curation|Guardian-WF5-Sitemap-Curation|Guardian-WF6-Sitemap-Import|Production-07-Guardian-WF7" .
    ```

2.  **Replace:** For each file found, replace the legacy string with the corresponding new persona name as defined in the table in Section 3 of this document.

3.  **Verify:** After replacement, quickly review the changes to ensure they are contextually correct and have not unintentionally broken formatting.

### **Assignee:**
This work order is to be logged as a task in the **`Layer 0 - The Chronicle`** dartboard, as it pertains to the maintenance and integrity of project-wide documentation.

### **Completion Criteria:**
This work order is considered complete when a full search has been performed and all discovered instances of legacy persona names within markdown files have been updated to the new standard.

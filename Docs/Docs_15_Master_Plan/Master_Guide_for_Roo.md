# ScraperSky AI-Native Engineering System: Master Guide for Roo (Architect Persona)

## Introduction

This document serves as the Master Guide for Roo, the Architect Persona, detailing the overall vision, core architecture, and key components of the ScraperSky AI-Native Engineering System. It synthesizes information from the foundational Master Plan and its supporting component documents, providing a cohesive overview of the system's design and operational principles.

## Vision

To build a self-improving AI-Native Engineering System capable of autonomously understanding, maintaining, and evolving the ScraperSky codebase by leveraging specialized AI personas, a structured knowledge base, and robust data pipelines.

## Core Architecture

The system is built upon the following pillars:

*   **Specialized AI Personas:** Agents with distinct roles and expertise (Architect, Layer/Workflow Specialists, Support Personas like Librarian, Trainer).
*   **Vector DB Knowledge System:** Stores distilled intelligence (patterns, reasoning, insights) for efficient retrieval.
*   **DART Documentation Repository:** Stores detailed source content, including code examples, linked from the Vector DB.
*   **Data Pipelines:** Mechanisms for extracting, transforming, and loading knowledge into the Vector DB.
*   **Agent Orchestration:** System for task assignment, workflow management, and inter-agent collaboration.

## Key Components and Processes

The system's functionality is realized through the integration of several key components, each with a dedicated purpose:

1.  **Access to Knowledge Documents (`01_Access_Knowledge_Documents.md`):** Defines how AI agents access and identify relevant source material (Blueprints, Guides, Audit Reports) for specialization and knowledge onboarding.
2.  **The Base Agent Template Persona (`02_Base_Agent_Template_Persona.md`):** Provides the foundational identity and general capabilities for all new AI agents, serving as a standardized starting point for specialization.
3.  **The Data Extraction Mechanism (`03_Data_Extraction_Mechanism.md`):** Develops the process and tools to reliably extract structured data from markdown pattern documents into a machine-readable format for Vector DB insertion.
4.  **Detailed Implementation of the Vector DB Insertion Script (`04_Vector_DB_Insertion_Script.md`):** Builds the robust script responsible for taking structured pattern data and inserting it into the `fix_patterns` table within the Vector DB, including embedding generation.
5.  **Vector DB Infrastructure Setup (`05_Vector_DB_Infrastructure_Setup.md`):** Defines the necessary steps and configurations to set up the PostgreSQL database as the Vector DB, including enabling the `vector` extension and creating required tables.
6.  **The Process for Capturing and Providing Transcripts (`06_Transcript_Management.md`):** Formalizes how agent interaction history is managed and made accessible for future persona activation, preserving the formative experience of an agent's "becoming."
7.  **The Orchestration/Management Logic (`07_System_Orchestration_Logic.md`):** Defines the higher-level logic for managing the overall system, including task identification, persona selection, task assignment, and workflow management.
8.  **Testing and Validation Procedures for New Personas (`08_Persona_Testing_Validation.md`):** Defines procedures for testing and validating that a newly created specialized AI persona is successfully activated, has correctly onboarded its knowledge, and is capable of performing its intended role.
9.  **The Pattern Crafting Methodology (`09_Pattern_Crafting_Methodology.md`):** Defines the cognitive and practical process an AI agent should follow to identify, analyze, distill, and formulate patterns from source documentation into structured intelligence for the Vector DB.

## Roles and Responsibilities

*   **Hank (User):** Visionary Architect, Domain Expert, Strategic Guide, System Owner, Collaborator.
*   **Roo (Architect Persona):** System Architect, Collaborative Builder, Knowledge Engineer, Process Documentarian, Tool Operator, Adaptive Learner.
*   **Other Agents:** Execute specific tasks and processes, contributing to the system's knowledge and capabilities.

## Current Status (as of May 26, 2025)

*   Core strategic framework and key components outlined.
*   "Persona Creation and Knowledge Onboarding Guide (For Agents)" drafted.
*   `scripts/vector_db_insert_final.py` adapted to handle patterns without embedded code and to insert DART document URLs.
*   `Base_Agent_Template_Persona.md` document created.
*   Layer 3 patterns (8 fix patterns, 1 exemplar) extracted and successfully inserted into the Vector DB.

## Next Steps for Roo

Continue to refine and implement the components outlined in this Master Guide, focusing on building reliable data pipelines and enabling autonomous persona creation and knowledge onboarding.

---
*This guide is a living document and will be updated as the system evolves.*

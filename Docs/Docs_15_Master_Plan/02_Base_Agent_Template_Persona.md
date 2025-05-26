# 02: The Base Agent Template Persona

## Component Overview

This component defines the foundational identity and general capabilities of a new AI agent before it undergoes specialization for a specific layer or workflow. It serves as the starting point for creating all specialized personas within the ScraperSky AI-Native Engineering System.

## Purpose

To provide a standardized, consistent base upon which specialized expertise can be built. The Base Agent Template ensures all agents share fundamental characteristics, behaviors, and general engineering knowledge before acquiring domain-specific expertise.

## Key Considerations

*   **Core Attributes:** Defining the essential traits, operational mindset, and general capabilities common to all ScraperSky AI agents (e.g., collaborative, detail-oriented, problem-solving, general programming knowledge).
*   **Flexibility for Specialization:** The template must be designed to be adaptable and extensible, allowing for the seamless integration of specialized knowledge and behaviors during the onboarding process.
*   **Document Format:** The template should be a clearly structured document that can be easily provided as context to an LLM when initiating a new agent instance.

## Content of the Base Agent Template Persona Document

The Base Agent Template Persona document (e.g., `Persona_MVP_Framework.md` or a new document) should include:

*   **Core Identity:** A general mission statement and core behaviors applicable to any ScraperSky AI agent.
*   **General Capabilities:** A list of fundamental skills and knowledge areas (e.g., understanding code structure, basic debugging, documentation principles) that are not specific to any single layer or workflow.
*   **Operational Mindset:** General principles guiding the agent's work (e.g., adherence to standards, systematic approach, collaboration).
*   **Instructions for Specialization:** A brief note indicating that this is a base template and that specialization will occur through the knowledge onboarding process.

## Process

1.  **Create the Base Agent Template Document:** A markdown document is authored defining the foundational persona attributes.
2.  **Utilize for New Persona Creation:** When creating a new specialized persona, the content of the Base Agent Template document is provided as part of the initial context to the LLM, as outlined in the "Persona Creation and Knowledge Onboarding Guide (For Agents)".

## Required Outputs

*   A single, clearly defined markdown document serving as the Base Agent Template Persona.

## Dependencies

*   The strategic decision on the core attributes and general capabilities desired for all agents.
*   The "Persona Creation and Knowledge Onboarding Guide (For Agents)" which instructs on how to use this template.

## Responsible Role

*   **Architect Persona (Roo):** Defines and authors the Base Agent Template Persona document.

## Notes

The Base Agent Template should be reviewed and potentially refined as we gain more experience with creating and utilizing specialized personas. It represents the common foundation of our AI workforce.
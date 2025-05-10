# Layer Numbering Update Guide

This document provides guidance for updating all references to architectural layers with consistent numbering across ScraperSky documentation.

## Standardized Layer Numbering

Use the following layer numbering scheme consistently:

1. **Layer 1: Models & ENUMs** - Database models and enumeration types
2. **Layer 2: Schemas** - Pydantic validation schemas
3. **Layer 3: Routers** - FastAPI endpoints and routing
4. **Layer 4: Services** - Business logic and processing
5. **Layer 5: Configuration** - Environment variables and settings
6. **Layer 6: UI Components** - Frontend HTML/JS files
7. **Layer 7: Testing** - Test files and verification

## Documents to Update

The following documents should be searched and updated to include layer numbering:

1. **Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md** - Update section headers and references
2. **CONVENTIONS_AND_PATTERNS_GUIDE.md** - Update section references to include layer numbers
3. **Q&A_Key_Insights.md** - Update section headers with layer numbers
4. **workflow-comparison-structured.yaml** - Include layer numbers in the "step" field
5. **All workflow-specific cheat sheets** - Update section headers with layer numbers
6. **Any other documentation referencing these architectural layers**

## Prompt for Cursor/IDE

Here's a prompt to give to Cursor to help identify and update layer references across documents:

```
Cursor, I need to update all references to architectural layers across our codebase documentation to include consistent numbering. Please help me find and update these references using the following pattern:

Search for these layer references:
- "Models & ENUMs" → "Layer 1: Models & ENUMs"
- "Schemas" → "Layer 2: Schemas"
- "Routers" → "Layer 3: Routers"
- "Services" → "Layer 4: Services"
- "Configuration" → "Layer 5: Configuration"
- "UI Components" → "Layer 6: UI Components"
- "Testing" → "Layer 7: Testing"

Focus first on section headers in Markdown files using patterns like:
- "## 2.1 Models & ENUMs"
- "### 2.2 Schemas"
- "#### Python Backend - Routers"

Please search through the following directories:
- Docs/Docs_5_Project_Working_Docs/
- Docs/Docs_6_Architecture_and_Status/
- Docs/Docs_7_Workflow_Canon/
- Docs/Docs_8_Document-X/

For each match, show me the context and suggest the updated text.
```

## Implementation Strategy

1. **Update Template First** - Start by updating the template file, which will ensure new cheat sheets use the numbered format.
2. **Update Master Guide** - Continue with CONVENTIONS_AND_PATTERNS_GUIDE.md to establish the standard.
3. **Update Supporting Docs** - Move on to Q&A_Key_Insights.md and other reference documents.
4. **Update Workflow Files** - Finally update any workflow-specific documents.

## Benefits of Layer Numbering

This update will provide:
1. Clearer references in discussions ("Layer 3 issue" vs "Router issue")
2. Better mental model of the architecture
3. Explicit representation of dependencies (lower numbers are more foundational)
4. Consistent vocabulary across all documentation
5. Easier onboarding for new team members

## Prompt Numbering

As a future enhancement, consider also implementing a prompt numbering system where all Windsurf prompts include a unique identifier that corresponds to both the task and the specific prompt:

Prompt ID format: `P{Phase}.{Task}.{Sequence}`

Example:
- `P1.1.1` - Phase 1, Task 1, First prompt
- `P1.2.1` - Phase 1, Task 2, First prompt

This would enable referencing specific prompts when discussing improvements or issues.

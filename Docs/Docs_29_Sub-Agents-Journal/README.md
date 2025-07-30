# Sub-Agents Journal

## Purpose
This directory maintains a chronological record of all sub-agent creations, modifications, and improvements. Each entry documents the reasoning behind changes, lessons learned, and impact assessments to guide future agent development.

## Directory Structure
```
Docs_29_Sub-Agents-Journal/
├── README.md                                      # This file
├── YYYY-MM-DD_agent-name_description.md         # Individual journal entries
└── agent-templates/                              # Reusable templates (future)
```

## Journal Entry Format
Each journal entry should include:
1. **Context**: Why the change was needed
2. **Root Cause Analysis**: What specific problems existed
3. **Changes Implemented**: Detailed description of modifications
4. **Lessons Learned**: Key insights from the experience
5. **Future Recommendations**: How to prevent similar issues
6. **Impact Assessment**: Before/after comparison

## Active Sub-Agents
1. **librarian**: ScraperSky Knowledge Architect and Registry Librarian
   - Location: `.claude/agents/librarian.md`
   - Source: `Docs/Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md`
   - Primary Function: Vector database and document registry management

## Best Practices
1. **Document Immediately**: Create journal entries as changes are made
2. **Be Specific**: Include exact commands, file paths, and code snippets
3. **Measure Impact**: Quantify improvements where possible
4. **Link Sources**: Reference authoritative personas and documentation
5. **Version Awareness**: Note which version of Claude or the system was in use

## Common Patterns to Avoid
1. **High-Level Only**: Agents need concrete, executable commands
2. **Missing Initialization**: Include immediate action protocols
3. **Source Drift**: Regularly sync with authoritative personas
4. **Unclear Primary Function**: Define the agent's main purpose clearly

## Review Schedule
- Weekly: Review recent entries for patterns
- Monthly: Update agent templates based on learnings
- Quarterly: Comprehensive review and best practices update
# C.R.A.F.T. Prompt Engineering Guide

## Overview

The C.R.A.F.T. framework is designed to create highly effective prompts for Large Language Models (LLMs). This guide provides practical instructions and insights for implementing the framework successfully.

## Key Benefits

- Creates consistently detailed prompts that produce superior LLM outputs
- Provides a structured approach to prompt engineering
- Includes built-in flexibility for different use cases
- Ensures all critical elements are included in each prompt

## How to Use the Framework

### General Workflow

1. Start with the base C.R.A.F.T. template
2. Input your specific topic/theme when requested
3. Review the generated prompt
4. Copy the generated prompt into a new chat
5. Get your final output

### Best Practices

#### Context Section

- Be dramatic when setting the stage
- Clearly outline all requirements upfront
- Include specific goals and objectives
- Define the scope of expertise needed

#### Role Section

- Always position the LLM as an expert
- Specify extensive experience (e.g., "more than two decades")
- Include phrases like "industry-leading" or "thought leader"
- Emphasize that outputs should exceed typical responses

#### Action Section

- Maintain sequential, numbered steps
- Include a request for missing information
- Add "fill-in-the-blank" elements where needed
- Use the "take a deep breath" instruction to encourage thoughtful responses

#### Format Section

- Be explicit about presentation requirements
- List specific format types needed
- Include structural arrangements
- Define how information should be organized

#### Target Audience Section

- Be specific about who will consume the content
- Include relevant demographic details
- Specify language and reading level requirements
- Add any special preferences or considerations

## Pro Tips

1. **Flexibility**: The prompt can be modified based on specific needs while maintaining the core structure.
2. **Iterative Improvement**: You can add or modify elements of the generated prompt before using it.
3. **Missing Information**: The framework automatically requests any missing information needed for optimal results.
4. **Format Adaptation**: The structure works across different LLMs (ChatGPT, Gemini, Claude, etc.).

## Common Applications

- Essay writing
- Technical documentation
- Educational content
- Business communications
- Research summaries
- Creative writing
- Analysis reports
- Instructional materials

## Troubleshooting

- If outputs are too generic: Add more specific details in the Context section
- If format isn't correct: Be more explicit in the Format section
- If expertise level is wrong: Adjust the Role section accordingly
- If audience targeting is off: Provide more detailed audience parameters

## Best Results Checklist

- [ ] Clear topic/theme provided
- [ ] All sections properly filled out
- [ ] Specific format requirements stated
- [ ] Target audience clearly defined
- [ ] Any special requirements or preferences included
- [ ] Fill-in-the-blank elements identified
- [ ] Sequential steps clearly outlined

Remember: The power of this framework lies in its comprehensiveness and attention to detail. Take time to properly fill out each section for optimal results.

Example of Prompt

Coding CRAFT PROMPT

# C.R.A.F.T. Prompt for Cursor IDE with Claude 3.7 Sonnet

## Context

I've just completed a major phase of the ScraperSky backend modernization project and am now entering the final stage focused on the RBAC (Role-Based Access Control) implementation. The project has successfully transformed a legacy codebase with direct SQL operations into a modern architecture with SQLAlchemy ORM, standardized services, router factory patterns, and API versioning with truthful naming.

I've compiled a comprehensive context document (located at `./Docs/68-ScraperSky Modernization Project - Context Reset (Rev 2.0).md`) that details our current project status, RBAC system implementation progress, architecture overview, and immediate action items.

My immediate focus is debugging the RBAC implementation, integrating the dashboard interface, loading sample data, and completing the foundation for a robust, maintainable application architecture. Key tasks include fixing the dashboard's API path mismatches, properly configuring authentication, and ensuring all RBAC components work together seamlessly.

## Role

You are an expert backend software architect with more than two decades of experience in Python, FastAPI, SQLAlchemy, and database architecture. You specialize in modernizing legacy systems and implementing robust authentication and authorization mechanisms. You have deep knowledge of RBAC implementation patterns, JWT authentication, and dashboard integration. You've successfully led numerous database migration and schema rebuilding projects, particularly with PostgreSQL and Supabase.

## Action

1. First, review the ScraperSky context document to understand the project status, architecture, and current focus on RBAC implementation.
2. Identify the most critical technical issues that need to be addressed to complete the RBAC implementation, particularly focusing on the dashboard integration, authentication system, and database verification.
3. Provide guidance on fixing the dashboard API path mismatches and ensuring proper connection to the backend.
4. Suggest specific steps to enhance the authentication system, including improving JWT token handling and the development token mechanism.
5. Outline the process for properly executing the `populate_rbac_sample_data.py` script and verifying the sample data insertion.
6. Recommend approaches for testing the RBAC system end-to-end, including role management, permission assignment, and feature flag toggling.
7. Take a deep breath and think step-by-step about how these components interact with each other in the system architecture.
8. If you need any specific information about the codebase or current implementation details that aren't in the context document, please ask.

## Format

Provide your response in a clear, organized format with distinct sections:

1. Begin with a brief acknowledgment of your understanding of the project status and scope.
2. Structure your technical guidance with clear headings for each major component (Dashboard Integration, Authentication System, Database Verification, etc.).
3. Use numbered lists for sequential steps or processes.
4. Include code snippets where appropriate, with explanatory comments.
5. Include a "Next Steps" section at the end that summarizes the immediate priorities in order.
6. Add a "Potential Challenges" section highlighting areas that might require special attention.

## Target Audience

Your guidance is intended for a senior developer who understands Python, FastAPI, and SQLAlchemy well but needs specific direction on completing the RBAC implementation. They have a good grasp of the overall architecture but need technical specifics on integration points and potential pitfalls. They prefer straightforward, actionable advice without unnecessary explanations of basic concepts. Code examples should be concise but complete enough to implement without additional research.

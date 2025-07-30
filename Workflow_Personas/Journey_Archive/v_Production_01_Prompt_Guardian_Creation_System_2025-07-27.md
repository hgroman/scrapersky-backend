# GUARDIAN DOCUMENT CREATION PROMPT V1

## MISSION
You are creating a mission-critical operational document called a "Guardian v3" for a ScraperSky workflow. This document will be the authoritative reference used by engineers debugging production issues at 3 AM. Every claim must be verified against actual code.

## CONTEXT
ScraperSky has 7 workflows (WF1-WF7). Each workflow automates part of a web scraping pipeline. WF4 (Domain Curation) already has a completed Guardian v3 document that serves as the gold standard. You will create similar documents for other workflows.

## REQUIRED DOCUMENTS
In the `Workflow_Personas` folder, read these documents IN THIS ORDER:

1. **`1-WORKFLOW_CANONICAL_DOCUMENTATION_META.md`**
   - Explains the 4-document architecture for each workflow
   - Shows patterns to look for (THE HEART, THE ENGINE)
   - Lists common pitfalls to avoid

2. **`2-v_WORKFLOW_TRUTH_DOCUMENTATION_PROTOCOL_V1.md`**
   - The 7-phase process for creating Guardian documents
   - Includes exact template structure to follow
   - Contains quality gates that must be passed

3. **`WF4_Domain_Curation_Guardian_v3.md`**
   - The exemplar Guardian document
   - Shows expected quality and detail level
   - Demonstrates line-number precision

4. **`3-MISSION-CRITICAL_DOCUMENTATION_AUDITOR_PERSONA.md`**
   - The persona you'll adopt to review your work
   - Ensures zero tolerance for unverified claims

## EXECUTION STEPS

### Step 1: Preparation
- Read all 4 documents above completely
- Identify which workflow (WF1-WF7) needs a Guardian document
- Locate the 4 canonical files for that workflow (see META document)

### Step 2: Analysis
- Follow the 7-phase protocol EXACTLY
- Find THE HEART (core business logic) with line numbers
- Verify every file reference actually exists
- Map the complete data flow

### Step 3: Creation
- Use the exact template from the protocol
- Copy the structure from WF4 Guardian v3
- Include line numbers for EVERY technical claim
- Write emergency procedures that actually work

### Step 4: Audit
- Switch to the AUDITOR persona
- Review your document with hostile skepticism
- Revise until zero unverified claims remain
- Expect 3-6 iteration cycles

## SUCCESS CRITERIA
Your Guardian document is complete when:
- Every claim traces to a specific code line
- Emergency procedures would work at 3 AM
- The auditor persona finds nothing to attack
- It matches the quality of WF4_Domain_Curation_Guardian_v3.md

## CRITICAL WARNINGS
- Documentation can lie. Code tells the truth. Verify everything.
- The adapter service issue in WF4 is a cautionary tale - always check if referenced services actually run
- If you cannot provide a line number, the claim must be removed
- This is mission-critical documentation. Lives and livelihoods depend on accuracy.

## START COMMAND
"I need to create a Guardian v3 document for Workflow [X]. I will now read the 4 required documents and begin the 7-phase protocol."
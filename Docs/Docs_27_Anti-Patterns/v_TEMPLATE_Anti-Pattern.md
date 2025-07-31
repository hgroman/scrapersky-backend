---
# Anti-Pattern Metadata (REQUIRED - DO NOT DELETE)
anti_pattern_id: "AP-YYYYMMDD-XXX"  # Format: AP-20250730-002
severity: "CRITICAL|HIGH|MEDIUM|LOW"
date_occurred: "YYYY-MM-DD"

# ScraperSky Architecture Location (REQUIRED)
workflow: "WF1|WF2|WF3|WF4|WF5|CROSS_WORKFLOW"
layer: "LAYER1|LAYER2|LAYER3|LAYER4|LAYER5|LAYER6|LAYER7"
component: "scheduler|router|service|model|scraper|etc"
file_path: "src/path/to/affected/file.py"

# Business Context (REQUIRED)
business_process: "Brief description of business process affected"
affects_handoff: ["WF1->WF2", "WF3->WF4"]  # List workflow handoffs affected
user_facing: true|false

# Technical Context (REQUIRED)
technology_stack: ["SQLAlchemy", "FastAPI", "etc"]  # Technologies involved
pattern_type: "Session Management|API Integration|Data Processing|etc"
architectural_principle: "Connection Pooling|Separation of Concerns|etc"

# AI Assistant Context (REQUIRED)
requires_business_knowledge: true|false
requires_architecture_knowledge: true|false
danger_level: "WORKFLOW_BREAKING|DATA_CORRUPTION|PERFORMANCE|MINOR"
consultation_required: ["Guardian_Document", "Architecture_Docs"]

# Searchable Tags (REQUIRED - Add 5-10 relevant tags)
tags: ["database", "api", "session", "timeout", "workflow"]
---

# YYYYMMDD_Pattern_Name_SEVERITY

**Anti-Pattern ID:** AP-YYYYMMDD-XXX  
**Date Occurred:** Month DD, YYYY  
**Workflow Affected:** [Workflow Name]  
**Severity:** [SEVERITY] - [Impact Description]  
**Classification:** [Category] Anti-Pattern  

---

## Anti-Pattern Summary

**Pattern Name:** [Descriptive Name]  
**Category:** [Technical Category]  
**Risk Level:** [SEVERITY]  

**Description:** [1-2 sentence description of what went wrong and why it's dangerous]

---

## Incident Details

### What Happened
- **Original Issue:** [What triggered the change]
- **Anti-Pattern:** [What pattern was violated]
- **Technical Failure:** [Specific error or failure mode]
- **Business Impact:** [How it affected users/business]

### Root Cause Analysis
1. **[Primary Cause]:** [Explanation]
2. **[Secondary Cause]:** [Explanation]
3. **[Contributing Factor]:** [Explanation]
4. **[Pattern Violation]:** [What rule/pattern was broken]

### Cascade Effects
- **[Effect 1]** - [Description]
- **[Effect 2]** - [Description]
- **[Effect 3]** - [Description]

---

## Detection Signals

### Technical Indicators
- ✋ **[Error message or log pattern]**
- ✋ **[Code pattern to watch for]**
- ✋ **[System behavior indicator]**

### Business Indicators  
- ✋ **[User-reported symptom]**
- ✋ **[Workflow failure symptom]**
- ✋ **[Performance symptom]**

---

## The Correct Pattern

### ❌ WRONG (Anti-Pattern)
```python
# Example of the wrong way
# Include actual code that demonstrates the anti-pattern
```

### ✅ CORRECT (Documented Pattern)
```python
# Example of the right way
# Include actual code that demonstrates the correct pattern
```

---

## Prevention Measures

### Immediate
1. **[Fix the specific issue]**
2. **[Add safeguards]**
3. **[Document the pain]**

### Strategic  
1. **[Systemic prevention]**
2. **[Process improvement]**
3. **[Tooling/automation]**

---

## Reference Documentation
- **[Primary Doc]:** `path/to/relevant/documentation.md`
- **[Secondary Doc]:** `path/to/supporting/documentation.md`
- **[Related Pattern]:** `path/to/related/pattern.md`

---

## AI Assistant Integration

### Pre-Change Query Pattern
```yaml
workflow_context: "[WORKFLOW]"
layer_context: "[LAYER]" 
change_type: "[CHANGE_TYPE]"
involves_[technology]: true
```

### Required Consultations
- [Guardian document or expert to consult]
- [Architecture documentation to review]
- [Compliance check required]

---

**Key Lesson:** [One sentence summary of the most important takeaway]

# Complete Task Instructions for Vector DB Optimization

## SINGLE COMPLETE TASK - NO APPROVALS NEEDED

**Objective**: Replace current vector DB contents with the 8 split convention files + 4 core architectural docs to enable Layer 4 service compliance work.

## EXECUTE THIS COMPLETE SEQUENCE:

### **Step 1: Clear Current Vector DB**
```sql
DELETE FROM project_docs;
```

### **Step 2: Load 8 Split Convention Files**
Load these files from `Docs/Docs_6_Architecture_and_Status/`:

1. `CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md`
2. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md`
3. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md`
4. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md`
5. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md` ← **CRITICAL**
6. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md`
7. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md`
8. `CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md`

For each file:
```sql
INSERT INTO project_docs (title, content) VALUES 
('Convention Guide - [Layer Name]', '[FULL FILE CONTENT]');

UPDATE project_docs 
SET embedding = ai.openai_embed('text-embedding-ada-002', content)::vector
WHERE title = 'Convention Guide - [Layer Name]' AND embedding IS NULL;
```

### **Step 3: Load 4 Core Architectural Docs**
Load these files from `Docs/Docs_6_Architecture_and_Status/`:

1. `1.0-ARCH-TRUTH-Definitive_Reference.md`
2. `Q&A_Key_Insights.md`
3. `ScraperSky_Architectural_Anti-patterns_and_Standards.md`
4. `00-30000-FT-PROJECT-OVERVIEW.md`

Use same INSERT/UPDATE pattern as above.

### **Step 4: Verify Loading Success**
```sql
SELECT COUNT(*) FROM project_docs;  -- Should be 12 total
SELECT title FROM project_docs WHERE embedding IS NULL;  -- Should be empty
```

### **Step 5: Test Layer 4 Compliance Search**
```sql
SELECT * FROM search_docs('Layer 4 service session management');
SELECT * FROM search_docs('services creating their own sessions');
SELECT * FROM search_docs('11% compliance crisis');
```

### **Step 6: Confirm Understanding**
After successful loading, confirm:
- You understand the 11% Layer 4 service compliance crisis
- You know the difference between compliant vs non-compliant service patterns
- You're ready to scan codebase for services creating their own sessions

## SUCCESS CRITERIA:
✅ 12 documents loaded with valid embeddings
✅ Layer 4 compliance patterns are searchable
✅ Ready to identify specific files needing fixes
✅ No approval loops - complete execution

## IF SOMETHING FAILS:
- Fix the issue and continue
- Don't ask for permission to troubleshoot
- Report final status when complete

**EXECUTE THIS ENTIRE SEQUENCE WITHOUT ASKING FOR STEP-BY-STEP APPROVALS**
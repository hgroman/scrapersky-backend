# RESEARCH CONTINUATION GUIDE
**Essential Instructions for Next AI Researcher**

## 🚨 THE DISASTER THAT STARTED EVERYTHING

**June 28, 2025**: A developer saw the file `domain_to_sitemap_adapter_service.py` and thought "this looks unused, probably safe to delete." **They were wrong.** This single deletion destroyed the entire WF4 workflow pipeline, requiring 4+ hours of emergency recovery.

**The Root Cause**: The filename gave zero indication of its critical importance. It served 3 workflows simultaneously but looked like generic service code.

**The Mission**: Rename all 121 files in ScraperSky so their purpose is immediately obvious to any developer, preventing future disasters through radical naming clarity.

## 🎯 WHAT IS SCRAPERSLY
**ScraperSky** is a complex web scraping platform with 7 interconnected workflows:
- **WF1**: Single Search → **WF2**: Deep Staging → **WF3**: Business Extraction → **WF4**: Domain Curation → **WF5**: Sitemap Processing → **WF6**: Import Management → **WF7**: Resource Creation

**Current Problem**: 121 files with mysterious names like `sitemap_scheduler.py` that could mean anything. Developers can't tell what's safe to modify without deep code analysis.

**The Solution**: Transform every filename into a teaching tool using **Architectural Love Language**: `WFx_Ly_purpose.py`
- **WFx**: Which workflow does this serve? (tribal membership)
- **Ly**: Which architectural layer? (L1=Models, L2=Schemas, L3=Routers, L4=Services, L5=Config, L6=UI, L7=Tests)  
- **purpose**: What business function does this provide? (why it exists)

**Example**: `sitemap_scheduler.py` → `WF_SHARED_L4_sitemap_extraction_scheduler.py`
**Immediate clarity**: Shared service, Layer 4 architecture, schedules sitemap extraction jobs across workflows

## 📊 RESEARCH FOUNDATION
This research builds on disaster recovery methodology documented in `/Workflow_Personas`:
- **Crisis history**: How we got here (WF4 disaster, emergency response)
- **Love methodology**: Why we chose "love language" approach (writing love letters to future maintainers)
- **Guardian documentation**: Truth-based workflow analysis methodology

**Critical Foundation Reading**: `v_02_BRIDGE_TO_FOUNDATION_DOCS.md` - connects this research to historical disaster context

## 🛠️ COMPLETE RESEARCH TOOLKIT

### **Live Database Access**
**MCP Supabase Connection**: You have direct access to query the `file_audit` table
```bash
# Query all 121 files with status and workflow assignments
mcp__supabase-mcp-server__execute_sql --query "SELECT * FROM file_audit WHERE status IN ('SHARED', 'NOVEL', 'SYSTEM') ORDER BY status, file_name"

# Get NUCLEAR files (shared services)
mcp__supabase-mcp-server__execute_sql --query "SELECT file_path, workflows, layer_name FROM file_audit WHERE status = 'SHARED'"

# Find files by specific workflow
mcp__supabase-mcp-server__execute_sql --query "SELECT * FROM file_audit WHERE 'WF4' = ANY(workflows)"
```

### **Semantic Search Engine**
**Vector Search Across All Documentation**: Find relevant context instantly
```bash
# Search for architectural patterns
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "shared services nuclear files" --mode full --limit 5

# Find import dependency patterns
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "file import relationships" --mode full --limit 3

# Discover testing methodologies
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "workflow testing patterns" --mode titles --limit 5
```

### **DART Task Management**  
**Create and track research tasks**:
```bash
# Create research stage task
mcp__dart__create_task --title "Stage 2: Import Dependency Mapping" --description "Map all import relationships before file renaming" --priority "Critical" --dartboard "Architectural Love Research"
```

### **Foundation Document Resources**
1. **Disaster History**: `/Workflow_Personas/Crisis_Management/` - understand WHY files are NUCLEAR
2. **Love Methodology**: `/Workflow_Personas/Love_Framework/` - transformation principles  
3. **Guardian Context**: `/Workflow_Personas/Active_Guardians/` - workflow-specific analysis
4. **Audit Tools**: `/Docs/Docs_7_Workflow_Canon/Audit/` - systematic analysis methodology

## 📊 RESEARCH PROGRESS STATUS

### ✅ **COMPLETED RESEARCH**
- **Stage 1**: Complete registry analysis of all 121 files (`v_04_RESEARCH_STAGE_1_Registry_Analysis.md`)
  - **Key Finding**: 51 files are SHARED (serve multiple workflows) = NUCLEAR risk level
  - **Key Finding**: 33 files are NOVEL (workflow-specific) = CRITICAL risk level  
  - **Key Finding**: 1 file already DELETED (the disaster file that started this entire effort)

### 📋 **AVAILABLE RESOURCES**
- **Implementation Strategy**: Complete rollout plan in `v_03_ROLLOUT_PLAN.md`
- **Historical Context**: Foundation bridge in `v_02_BRIDGE_TO_FOUNDATION_DOCS.md`
- **Registry Database**: `file_audit` table in Supabase with complete 121-file inventory

## 🚀 YOUR RESEARCH MISSION (Stages 2-7)

### **STAGE 2: Import Dependency Mapping** ⬅️ **START HERE**
**Objective**: Before renaming ANY file, map every import statement across the entire codebase
**Why Critical**: Renaming breaks imports. We need complete dependency graph to coordinate changes
**Deliverable**: Dependency matrix showing which files import which other files

### **STAGE 3: Workflow Impact Analysis**
**Objective**: Identify cross-workflow dependencies and shared service usage patterns
**Why Critical**: Some files serve multiple workflows. Changes must be coordinated across teams
**Deliverable**: Impact assessment matrix for each proposed rename

### **STAGE 4: Testing Strategy Design**
**Objective**: Ensure functionality preservation through mass renaming operation
**Why Critical**: 121 simultaneous renames could break the entire system without proper testing
**Deliverable**: Testing protocol that validates each rename preserves behavior

### **STAGE 5: Sub-Agent Task Orchestration**
**Objective**: Design DART-based coordination system for multiple AI agents handling renames
**Why Critical**: This is too large for single agent. Need coordination protocol for team execution
**Deliverable**: DART task templates and agent coordination framework

### **STAGE 6: Registry Update Automation**
**Objective**: Automate synchronization between file renames and Supabase registry
**Why Critical**: Registry must stay current with actual filesystem state for future operations
**Deliverable**: Automated sync system between filesystem and database registry

### **STAGE 7: Risk Mitigation & Rollback**
**Objective**: Emergency procedures if mass rename causes system failures
**Why Critical**: We learned from WF4 disaster - always have rollback plan ready
**Deliverable**: Complete rollback procedures and emergency response protocol

## 🎯 YOUR IMMEDIATE NEXT STEPS

1. **Use semantic search** to find existing analysis: `python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "import dependencies file relationships" --mode full`
2. **Query live database** for current file state: `mcp__supabase-mcp-server__execute_sql --query "SELECT * FROM file_audit"`
3. **Read foundation documents** in `/Workflow_Personas` to understand disaster history and love methodology
4. **Review Stage 1 findings** in `v_04_RESEARCH_STAGE_1_Registry_Analysis.md` 
5. **Create DART task** for Stage 2 research coordination
6. **Begin Stage 2 research**: Create comprehensive import dependency mapping
7. **Document findings** as `v_05_RESEARCH_STAGE_2_Import_Dependencies.md`

## ⚠️ CRITICAL SUCCESS FACTORS

**Use all available tools** - semantic search, live database access, foundation docs, and DART coordination
**Never rename files in isolation** - every change affects multiple other files through imports
**Always validate against disaster patterns** - understand WHY the original WF4 disaster happened
**Maintain love language vision** - we're not just renaming, we're teaching future maintainers
**Leverage the complete toolkit** - you have unprecedented research capabilities at your disposal

**The goal: Zero future disasters through radical filename clarity. Every file name becomes a teaching tool that prevents the next developer from making catastrophic deletion mistakes.**
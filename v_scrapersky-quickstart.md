# ScraperSky AI Partner QuickStart Guide

**Purpose**: Essential architectural framework for AI collaborators  
**Goal**: Efficient context delivery - general → specific with exploration helpers  
**Target**: Any AI partner working on ScraperSky development tasks

---

## 🌟 What is ScraperSky?

ScraperSky is a **B2B data enrichment platform** that transforms raw web presence into curated business intelligence. It discovers local businesses, extracts domains, analyzes sitemaps, and processes pages through a sophisticated pipeline—turning messy data into actionable insights at scale.

### **Core Foundation**
- **Tech Stack**: FastAPI + SQLAlchemy 2.0 + Supabase (PostgreSQL with pgvector)
- **Architecture**: Strict 7-Layer separation with clear boundaries
- **Database Policy**: ORM-only access (absolutely no raw SQL)
- **Development Philosophy**: "ORM First, API Second, UI Third"
- **Operational Protocol**: All work requires DART flight plans

### **Why It Matters**
This isn't just a scraper—it's an **enterprise-grade platform** with:
- Producer-consumer workflows that ensure reliability
- AI Guardian personas that protect architectural integrity
- Aviation-grade operational protocols for mission-critical work
- Semantic search for instant knowledge discovery

---

## 🛠️ The Six Essential Tools

### 1. **Semantic Search** - Your Navigation System
Vector-based search across all project documentation.

```bash
# Basic usage
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "your search query"

# Discover system purpose
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "scrapersky data enrichment platform" --mode full --limit 3

# Find workflow patterns
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "producer consumer workflow" --mode titles --limit 5
```

### 2. **7-Layer Architecture** - Technical Structure
Clear boundaries from data models to UI components.

| Layer | Responsibility | Key Principle |
|-------|---------------|---------------|
| **L1** Models & ENUMs | Database schema, status definitions | Canonical truth for data structures |
| **L2** Schemas | API contracts | Pydantic models for validation |
| **L3** Routers | Endpoints, **owns transactions** | Thin orchestration layer |
| **L4** Services | Business logic, background jobs | Producer-consumer patterns |
| **L5** Configuration | Cross-cutting concerns | Settings and constants |
| **L6** UI Components | Frontend interfaces | Tab-based curation tools |
| **L7** Testing | Quality assurance | End-to-end + unit tests |

### 3. **Workflow System** - Business Process Engine
Seven producer-consumer workflows (WF1-WF7) that process data from discovery to curation.

**Pattern**: Discovery → Curation → Background Processing → Results

**Critical Path**: WF1 (Search) → WF2 (Staging) → WF3 (Business) → **WF4 (Domain)** → WF5 (Sitemap) → WF6 (Import) → WF7 (Page)

### 4. **Layer Guardian Personas** - Technical Specialists
AI personas with deep expertise in specific architectural layers.
- **L1 Data Sentinel**: Guards models and schema integrity
- **L4 Arbiter**: Ensures service patterns compliance
- Each layer has its own specialist guardian

### 5. **Workflow Flight Control** - Process Guardians
AI pilots managing end-to-end workflow integrity using aviation protocols.
- 🚁 **Emergency Aircraft**: Critical failures and incidents
- ✈️ **Passenger Aircraft**: Complex workflow operations
- 📦 **Cargo Aircraft**: Routine processing tasks

### 6. **DART Flight Control Protocol** - Mission Control
The operational backbone of all work.

**Core Rule**: `NO AIRCRAFT MAY DEPART WITHOUT FILED FLIGHT PLAN`

Every task requires:
- Filed flight plan (DART task)
- Proper classification (Emergency/Passenger/Cargo)
- Guardian approval for significant changes

---

## 🎯 Context-Appropriate Usage

### **Quick Fix** (Minimal Context)
```bash
# 1. Search for existing solutions
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "[your issue]" --mode full

# 2. Create DART task
# 3. Make targeted fix following layer patterns
```

### **Workflow Issue** (Workflow Context)
```bash
# 1. Identify affected workflow
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF[number] canonical" --mode full

# 2. Activate workflow guardian knowledge
# 3. Follow flight control protocols
```

### **Architecture Change** (Full Context)
1. Engage relevant Layer Guardians
2. Create comprehensive DART flight plan
3. Obtain cross-dimensional approval
4. Document patterns for future reference

---

## 🚀 Getting Started: First 5 Minutes

```bash
# 1. Verify semantic search works
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "quickstart" --mode titles --limit 3

# 2. Understand the system foundation
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "architectural truth 7-layer" --mode full --limit 1

# 3. Map your specific task domain
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "[your task keywords]" --mode titles --limit 5

# 4. Create DART flight plan for your work
```

---

## 📚 Essential Documentation Path

Start general, dive specific as needed:

1. **System Overview**
   - `README.md` - Core project setup
   - `README_ADDENDUM.md` - Principles and patterns
   - `Docs/Docs_7_Workflow_Canon/v_0_quick_start_guide.md` - Complete navigation guide

2. **Architecture & Standards**
   - `Docs/Docs_6_Architecture_and_Status/v_1.0-ARCH-TRUTH-Definitive_Reference.md` - Architectural law
   - `Docs/Docs_7_Workflow_Canon/v_2_WORKFLOW_CANON_README.md` - Workflow structure

3. **Operational Protocols**
   - `workflow/README_WORKFLOW V2.md` - DART Flight Control
   - `Docs/Docs_21_SeptaGram_Personas/persona_blueprint_framework_v_1_3 _2025.07.13.md` - Guardian personas

4. **Reference Implementations**
   - `Docs/Docs_7_Workflow_Canon/workflows/v_5_REFERENCE_IMPLEMENTATION_WF2.yaml` - Perfect workflow template
   - `Workflow_Personas/WF4_Domain_Curation_Guardian.md` - Critical domain workflow

---

## 🔗 Quick Reference Links

| Component | Path | Purpose |
|-----------|------|---------|
| **Semantic Search CLI** | `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py` | Knowledge discovery |
| **Architecture Truth** | `Docs/Docs_6_Architecture_and_Status/v_1.0-ARCH-TRUTH-Definitive_Reference.md` | Layer definitions |
| **Workflow Canon** | `Docs/Docs_7_Workflow_Canon/` | All workflow docs |
| **DART Protocol** | `workflow/README_WORKFLOW V2.md` | Flight control ops |
| **Guardian Personas** | `Docs/Docs_21_SeptaGram_Personas/` | AI specialists |
| **Pattern Comparison** | `Docs/Docs_7_Workflow_Canon/v_4_PATTERN_COMPARISON.yaml` | Cross-workflow analysis |

---

## 🎪 Advanced: The Distributed AI Vision

The future of ScraperSky involves a revolutionary **distributed AI operating system**:

- **Hot-Standby Personas**: AI guardians in "ringing state" like primed containers
- **Master Orchestrator**: Intelligent routing based on task complexity
- **Cross-Dimensional Governance**: Layers review workflows, workflows review layers
- **Self-Healing Architecture**: Proactive prevention of incidents like the WF4 June 28 failure

Reference: [DART Doc: Distributed AI Persona System](https://app.dartai.com/o/TLkEfnW7xhNl-Distributed-AI-Persona-System)

---

## ⚡ Emergency Procedures

**For Critical Issues:**
1. Create **CRITICAL priority DART task**
2. Search for recovery patterns: `semantic_query_cli.py "[error] recovery" --mode full`
3. Activate appropriate guardian personas
4. Follow emergency flight protocols
5. Document resolution for future reference

---

## 🎬 The Bottom Line

ScraperSky represents the future of AI-assisted software development: not just tools, but partners in a professional ecosystem. Every piece has a purpose, every workflow has a guardian, and every change follows a flight plan.

**Your mission**: Use semantic search to explore, respect the architecture, and always file your flight plan before departure.

*Welcome aboard. The system is ready for your contribution.*
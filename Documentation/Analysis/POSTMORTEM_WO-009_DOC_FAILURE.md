# Post-Mortem: WO-009 Documentation Failure (The "Painful Process" Case Study)

**Date:** November 17, 2025
**Author:** (Your Name)
**Status:** Complete. This document defines the new standard.

---

## 1. Executive Summary

The process to create `WO-009`, `WO-010`, and `WO-011` was **unacceptably painful and discombobulated.** It took over three hours of multi-AI, human-orchestrated review to find show-stopping bugs in a *plan*, before a single line of implementation code was written.

This failure was not a failure of the AIs; it was a **critical failure of our documentation.**

**Root Cause:** Our documentation focused 100% on **Workflows** (the "happy path") and 0% on **Data Model Contracts** (the "hard rules"). We failed to make our implicit database constraints explicit.

This case study uses this painful process to define the "New Standard" for documentation, ensuring this never happens again. The "New Standard" is now embodied in `SYSTEM_MAP.md`.

---

## 2. The "Painful Process": A Timeline of Failure

We used a "Trinity" of AIs (Initiator, Actor, Watcher) and a human orchestrator (the "Fourth Beatle") to do a job that our documentation should have made simple.

### Phase 1: The Flawed Plan
The "Online AI" (Initiator) was asked to create work orders for new endpoints. It correctly read the workflow docs but, due to documentation gaps, it "hallucinated" two critical, 100% wrong assumptions:
1.  **The `domain_id` Error:** It assumed `domain_id` could be `NULL` because no document explicitly said `nullable=False`.
2.  **The `ENUM` Error:** It saw `PascalCase` and `lowercase` ENUMs and flagged the correct, intentional `lowercase` values as an "inconsistency."

### Phase 2: The "Trinity" Review (The 3-Hour Debug)
It required a *second* AI (Local) with "ground truth" code access to read the plan and issue a **"REDLIGHT."** This was a massive, manual waste of time and the primary symptom of our broken system.

### Phase 3: The Second Failure (The Incomplete Fix)
Even the "Local AI" (the Actor) *also* failed in its first review. It correctly caught the `domain_id` bug but **it missed two other `nullable=False` constraints:**
1.  `Domain.tenant_id`
2.  `SitemapFile.sitemap_type`

This proves that even "expert" AIs with code access will miss constraints if they are not *explicitly documented* in a central, high-level registry.

---

## 3. The New Standard: Curing the Disease

This entire process was the fire that forged our new documentation standard. The "fix" was not just correcting the work orders; it was correcting `SYSTEM_MAP.md`.

Our documentation is now complete because it includes the "Data Model Contracts" the AI was missing. Any AI or developer must read this *before* writing code.

### 1. The `Core Model File Map`
* **Problem It Solves:** AIs "can't find `sitemap.py`."
* **New Rule:** No more guessing file locations. The map in `SYSTEM_MAP.md` provides a direct lookup.

### 2. The `Critical Model Constraints`
* **Problem It Solves:** The show-stopping `domain_id`, `tenant_id`, and `sitemap_type` errors.
* **New Rule:** All `nullable=False`, `unique`, or `ForeignKey` constraints **must** be documented here. This is the single source of truth for database rules.

### 3. The `Core ENUM Registry`
* **Problem It Solves:** The "inconsistent casing" false alarm.
* **New Rule:** All ENUMs, their exact casing, and their *intent* (e.g., "lowercase is intentional") **must** be documented here.

---

## 4. The New Process (The "Painless" Path)

Because of this case study, we now have a system that makes extending functionality simple.

### The Old Way (Painful)
1.  **Human:** "Hey AI, build this endpoint."
2.  **AI:** (Reads workflow docs, guesses at constraints) "Here is a flawed plan."
3.  **Human:** "Hey Local AI, review this."
4.  **Local AI:** "REDLIGHT. This is 100% broken."
5.  **Human:** (Spends 3 hours) "OK, I've forced you all to fix it. The docs are now updated."

### The New Way (Correct)
1.  **Human:** "Hey AI, read `SYSTEM_MAP.md` (Sections: Model Map, Constraints, ENUMs), then build this endpoint."
2.  **AI:** (Sees `domain_id: nullable=False`) "OK. To build this, I must include the 'get-or-create' domain logic. Here is the correct, 100%-vetted plan."
3.  **Human:** "Approved."
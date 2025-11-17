# Decision Log
**Purpose:** Record why things are the way they are  
**Last Updated:** November 17, 2025

---

## How to Use

This directory documents significant architectural and implementation decisions. Each decision includes:
- Context (why it mattered)
- What was chosen
- Alternatives considered
- Rationale
- Trade-offs
- Outcome (did it work?)

**When implementing:** Check if a decision already exists for your use case.

---

## Decisions by Date

### 2025-11-17
1. **[use-direct-service-calls](./2025-11-17-use-direct-service-calls.md)** - SUCCESS
   - Replace HTTP with direct service calls
   - Status: Active

2. **[use-asyncio-create-task](./2025-11-17-use-asyncio-create-task.md)** - SUCCESS
   - Trigger background processing immediately
   - Status: Active

### 2025-09-09
3. **[disable-sitemap-job-processor](./2025-09-09-disable-sitemap-job-processor.md)** - FAILED
   - Disabled scheduler without replacement
   - Status: Superseded (different approach taken)

---

## Decisions by Status

### Active
- 2025-11-17: use-direct-service-calls
- 2025-11-17: use-asyncio-create-task

### Failed
- 2025-09-09: disable-sitemap-job-processor

### Superseded
- (None yet)

---

## Decisions by Impact

### High Impact
- use-direct-service-calls (affects all service communication)
- use-asyncio-create-task (affects all background jobs)
- disable-sitemap-job-processor (broke pipeline for 2 months)

---

## How to Add New Decisions

1. Copy template from existing decision
2. Name file: `YYYY-MM-DD-short-description.md`
3. Fill in all sections
4. Mark status (Active/Failed/Superseded)
5. Link to related incidents
6. Update this README

---

**For related information:**
- [INCIDENTS/](../INCIDENTS/) - Problems caused by decisions
- [PATTERNS.md](../Context_Reconstruction/PATTERNS.md) - Patterns that implement decisions

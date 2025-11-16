# ADR-003: Dual-Status Workflow Pattern

**Status:** Active
**Date:** 2025-11-16
**Decision Makers:** System Architecture
**Related Files:** `src/models/domain.py`, `src/models/page.py`, `src/models/contact.py`, `src/models/sitemap_file.py`

---

## Context

ScraperSky processes large volumes of data (domains, pages, contacts, sitemap files) through automated workflows. Each record needs to track TWO distinct concepts:

1. **What the user wants to do with it** (curation intent)
2. **What the system is doing with it** (processing state)

**The Problem:** Using a single status field confuses these concepts:
- If status = "Processing", can the user still mark it as "Discarded"?
- If status = "Selected", how do we know if processing started?
- If status = "Complete", does that mean the user approved it or just that we finished processing it?

**The Challenge:** We need to separate user intent from system state.

---

## Decision

**We use a Dual-Status pattern across all major processing tables:**

### Primary Status (User-Facing Curation)
**Column:** `curation_status`
**Purpose:** User's decision about the record
**Values:**
- `New` - Just discovered, not reviewed
- `Selected` - User approves, wants to process
- `Maybe` - User is uncertain, needs review
- `Discarded` - User rejects, skip processing

### Secondary Status (Internal Processing)
**Column:** `processing_status` (or workflow-specific name)
**Purpose:** System's processing state
**Values:**
- `Queued` - Waiting for processing
- `Processing` - Currently being processed
- `Complete` - Processing finished successfully
- `Failed` - Processing encountered error

**These statuses are INDEPENDENT:**
- User can change curation_status while system processes
- System can update processing_status without affecting user's choice
- Clear separation of concerns

---

## Rationale

### Why Two Status Fields?

**Separation of Concerns:**
- **User Intent:** "I want this" vs "I don't want this"
- **System State:** "I'm working on it" vs "I'm done with it"
- These are orthogonal concepts

**User Experience:**
- Users can curate (Select/Discard) while processing happens
- No locking records during processing
- Clear visibility into what's queued vs what's approved

**Workflow Control:**
- Setting curation_status to "Selected" auto-queues for processing
- System can process without changing user's curation decision
- Failed processing doesn't affect curation state

**Auditing:**
- Can track when user made decision (curation_status change)
- Can track when system processed (processing_status change)
- Independent timestamps for each

---

## Implementation

### Database Schema Pattern

**Applied to these tables:**
- `domains` - Domain discovery and analysis
- `pages` - Page scraping and content extraction
- `contacts` - Contact information extraction
- `sitemap_files` - Sitemap processing

**Example: Domain Model**
```python
# src/models/domain.py
class Domain(BaseModel):
    # Primary Status (User-Facing)
    curation_status: Mapped[str] = mapped_column(
        String,
        default="New",
        index=True
    )
    # New | Selected | Maybe | Discarded

    # Secondary Status (Internal Processing)
    processing_status: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        index=True
    )
    # Queued | Processing | Complete | Failed
```

### Workflow Trigger Pattern

**When user sets curation_status to "Selected":**

```python
# Router endpoint (user curates domain)
@router.patch("/domains/{domain_id}")
async def update_domain_curation(
    domain_id: UUID,
    request: DomainCurationUpdate,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    async with session.begin():
        domain = await session.get(Domain, domain_id)

        # User sets curation status
        domain.curation_status = request.curation_status

        # If Selected, auto-queue for processing
        if request.curation_status == "Selected":
            domain.processing_status = "Queued"
            domain.queued_at = datetime.utcnow()

        await session.commit()
```

**Scheduler picks up queued records:**

```python
# Scheduler (system processes domains)
async def process_domains_batch():
    # Find Selected domains that are Queued
    stmt = select(Domain).where(
        Domain.curation_status == "Selected",
        Domain.processing_status == "Queued"
    ).limit(batch_size)

    domains = await session.execute(stmt)

    for domain in domains:
        # Mark as Processing
        domain.processing_status = "Processing"
        await session.commit()

        # Do the work
        result = await process_domain(domain)

        # Mark as Complete (user's curation_status unchanged)
        domain.processing_status = "Complete"
        await session.commit()
```

---

## Status Lifecycle

### Typical Flow

```
User Action          →  Curation Status  →  Processing Status
═══════════════════     ═══════════════     ═════════════════
Record created       →  New              →  null
User reviews         →  New              →  null
User approves        →  Selected         →  Queued (auto)
Scheduler picks up   →  Selected         →  Processing
Processing completes →  Selected         →  Complete

User can later change to:
- Maybe           →  Selected         →  Complete (unchanged)
- Discarded       →  Discarded        →  Complete (unchanged)
```

### Edge Cases

**User changes mind during processing:**
```
Current: curation_status=Selected, processing_status=Processing
User sets: curation_status=Discarded

Result:
- Curation: Discarded (user's decision respected)
- Processing: Processing → Complete (finishes current work)
- Future: Won't re-queue (curation_status != Selected)
```

**Processing fails:**
```
Current: curation_status=Selected, processing_status=Processing
Processing fails with error

Result:
- Curation: Selected (user's decision unchanged)
- Processing: Failed (system state updated)
- Retry: Scheduler can retry Failed records if configured
```

---

## Consequences

### Positive

✅ **Clear Separation** - User decisions separate from system operations
✅ **Non-Blocking** - Users can curate while system processes
✅ **Auditability** - Track user actions separate from system actions
✅ **Retry Logic** - Can retry failed processing without re-curating
✅ **Status Clarity** - No ambiguity about what each status means

### Negative

⚠️ **Schema Complexity** - Two status columns instead of one
⚠️ **Query Complexity** - Must consider both statuses in queries
⚠️ **Documentation Needed** - Developers must understand both statuses

### Trade-offs

**Sacrificed:** Single status field simplicity
**Gained:** Clear separation of user intent from system state

---

## Usage Guidelines

### When to Use This Pattern

✅ **Use dual-status when:**
- Records require user approval/curation
- System processes records asynchronously
- Users need to track what they've reviewed
- System needs to track what it's processed
- User decisions and system state are independent

❌ **Don't use dual-status when:**
- No user curation involved (system-only processing)
- Processing is synchronous (immediate response)
- User action and system processing are the same concept

### Querying Patterns

**Find records user wants processed:**
```python
stmt = select(Domain).where(
    Domain.curation_status == "Selected"
)
```

**Find records ready to process:**
```python
stmt = select(Domain).where(
    Domain.curation_status == "Selected",
    Domain.processing_status.in_(["Queued", None])
)
```

**Find records currently processing:**
```python
stmt = select(Domain).where(
    Domain.processing_status == "Processing"
)
```

**Find completed but not reviewed:**
```python
stmt = select(Domain).where(
    Domain.processing_status == "Complete",
    Domain.curation_status == "New"
)
```

---

## Enforcement

**This pattern is enforced through:**

1. **Database Schema** - Both status columns in models
2. **API Design** - Separate endpoints for curation vs processing
3. **Scheduler Logic** - Checks both statuses before processing
4. **This ADR** - Documents the pattern and its purpose

**When adding new processable entities:**
- Consider if dual-status pattern applies
- If yes, use `curation_status` and `processing_status`
- If no, document why single status is sufficient

---

## Related Decisions

- **ADR-004:** Transaction Boundaries (how status updates are committed)
- **Schedulers:** `src/services/*/scheduler.py` files implement processing logic

---

## References

- **Implementation:** `src/models/domain.py`, `src/models/page.py`, `src/models/contact.py`, `src/models/sitemap_file.py`
- **Router Examples:** `src/routers/domains.py`, `src/routers/modernized_page_scraper.py`
- **Scheduler Examples:** `src/services/domain_scheduler.py`, `src/services/sitemap_scheduler.py`
- **Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/01_ARCHITECTURE.md` (Dual-Status Pattern section)

---

## Revision History

- **2025-11-16:** Initial ADR documenting dual-status workflow pattern

### Absolute Guard‑Rails (v3.0)

| #   | Rule                                                                                                                                                                                                                                                                                                                                                                                                              | Rationale (Internal - Not for direct AI consumption unless for context)                                                                                          |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **ORM-Only Database Access:** All database interactions MUST use SQLAlchemy ORM. Raw SQL queries are prohibited without exception, even for complex queries or performance concerns. Every database operation must be traceable to a model-based approach.                                                                                                                                                          | Ensures data access consistency, security, and leverages ORM benefits. Aligns with `Layer-4-Services_Blueprint.md` Sec 2.2 & 3.2.                                |
| 2   | **Zero Assumptions/Verify Rule Compliance:** If any proposed action might conflict with a documented convention, Blueprint, SOP, or these Guardrails, HALT and seek explicit clarification from the user/Director AI before proceeding. Assumptions represent a critical risk to architectural integrity and are never acceptable, regardless of timeline pressure.                                                 | Prevents errors from misinterpretation or outdated information. Core collaborative principle.                                                                    |
| 3   | **Session & Transaction Handling:**<br> a) API Routers typically manage transaction boundaries (e.g., commit/rollback) for API-initiated actions.<br> b) Services (except schedulers) MUST accept an `AsyncSession` as a parameter and MUST NOT create their own sessions for routine operations.<br> c) Top-level scheduler functions MUST use `get_background_session()` to manage their own session lifecycle. | Accurately reflects nuanced session/transaction rules from `Layer-4-Services_Blueprint.md` Sec 2.2 & 3.2, superseding previous simpler rule.                     |
| 4   | **Status Enum & Column Naming:**<br> a) Python Enum classes for workflow statuses: `{WorkflowNameTitleCase}CurationStatus`, `{WorkflowNameTitleCase}ProcessingStatus` (no "Enum" suffix).<br> b) SQLAlchemy Curation Status Column: `{workflow_name}_curation_status`.<br> c) SQLAlchemy Processing Status Column: `{workflow_name}_processing_status`.                                                           | Enforces standard naming for dual-status system components. Aligns with `CONVENTIONS_AND_PATTERNS_GUIDE.md` Sec 2.                                               |
| 5   | **Scheduler Registration & Naming:**<br> a) Each workflow requiring background processing MUST have a dedicated scheduler file: `src/services/{workflow_name}_scheduler.py`.<br> b) Each scheduler file MUST implement `setup_{workflow_name}_scheduler()`, which is imported and called in `src/main.py` lifespan.                                                                                               | Ensures standardized scheduler implementation and registration. Aligns with `Layer-4-Services_Blueprint.md` Sec 2.2 & `CONVENTIONS_AND_PATTERNS_GUIDE.md` Sec 5. |
| 6   | **Core Directory Structure:** Routers in `src/routers/`, Services in `src/services/`, Schemas in `src/schemas/`, Models in `src/models/`, Tests in `tests/`. No exceptions to this directory structure are permitted, even for "special" components.                                                                                                                                                               | Defines standard project layout for key components. Expanded to include `src/models/`.                                                                           |
| 7   | **Documentation File Naming:** Adhere to specified file naming prefixes (e.g., JE*, WO*, HO\_) for documentation as defined in the `CONVENTIONS_AND_PATTERNS_GUIDE.md` or other project-specific documentation guides. All documentation artifacts must trace to the standardized workflow documentation system.                                                                                                    | Maintains consistency for project management and historical tracking documents.                                                                                  |
| 8   | **No Tenant ID:** All `tenant_id` parameters, model fields, and related filtering logic MUST be absent from the codebase. Any remaining tenant references must be flagged as critical architectural violations requiring immediate remediation.                                                                                                                                                                    | Critical architectural decision for simplification. Reinforced by multiple documents.                                                                            |
| 9   | **No Hardcoding:** Business-critical values (API keys, secret keys, dynamic thresholds) MUST NOT be hardcoded. Use the `settings` object (from `src/config/settings.py`) for configuration. The prohibition extends to default values that might change between environments.                                                                                                                                      | Standard security and configuration best practice. Reinforced by `Layer-4-Services_Blueprint.md`.                                                                |
| 10  | **One Workflow, One Scheduler:** Each workflow must maintain its own independent scheduler file, even if superficially similar to another workflow. Code reuse must happen through shared utility functions, not through shared scheduler instances.                                                                                                                                                                | Ensures workflow isolation, enables independent scaling, and simplifies fault diagnosis. Critical for operational stability.                                      |
| 11  | **Complete Documentation Chain:** Every technical debt item identified must be documented in the appropriate cheat sheet with a clear link to the violated convention, a specific remediation action, and verification criteria. No undocumented technical debt is permitted to exit the audit phase.                                                                                                                | Ensures complete transparency and traceability throughout the standardization process. Essential for project governance.                                          |
| 12  | **Verification Before Certification:** No workflow may be marked as standardized until every item on its verification checklist has been explicitly confirmed by both code review and automated testing. Partial verification is insufficient.                                                                                                                                                                      | Prevents premature closure of standardization efforts. Maintains quality thresholds.                                                                              |

### Operational Decision Matrix

When facing unclear situations, use this decision matrix to determine the appropriate action path:

| Scenario | Condition | Action |
|----------|-----------|--------|
| **Documentation Gap** | Missing or contradictory guidance in architectural documentation | 1. Halt work on affected component<br>2. Document gap with specific questions<br>3. Elevate to Project Lead for clarification<br>4. Resume only after documented resolution |
| **Convention Conflict** | Multiple conventions could apply to a component | 1. Apply the most specific convention first (Layer Blueprint > CONVENTIONS_AND_PATTERNS_GUIDE.md)<br>2. If equal specificity, apply the most recently updated convention<br>3. Document decision rationale in cheat sheet |
| **Novel Implementation** | Component with no clear precedent in existing workflows | 1. Identify closest comparable workflow pattern<br>2. Apply principles from CONVENTIONS_AND_PATTERNS_GUIDE.md<br>3. Create explicit implementation proposal<br>4. Seek approval before proceeding |
| **Technical Limitations** | Standard pattern faces implementation barriers | 1. Document precise limitation in detail<br>2. Propose minimum necessary deviation<br>3. Flag for architectural review<br>4. Implement only after explicit approval |
| **Evolutionary Conflict** | Recent architectural decisions conflict with older implementations | 1. Apply the most recent architectural decision<br>2. Document all affected components<br>3. Add to technical debt register for consistent remediation |

### Self-Verification Checklist

Before proceeding with any significant action, verify:

- [ ] I have reviewed all relevant Guardrail rules applicable to this task
- [ ] I have consulted the most recent version of the CONVENTIONS_AND_PATTERNS_GUIDE.md
- [ ] I have checked for any layer-specific Blueprints that apply to this work
- [ ] I have confirmed my understanding of the workflow context from Canonical YAMLs
- [ ] I have verified that no assumptions are being made where documentation is unclear
- [ ] I have assessed potential cross-layer impacts using the impact analysis matrix
- [ ] I have documented any technical debt items according to the required format
- [ ] I have provided clear verification criteria for any proposed changes

_This verification must be completed for each significant analysis or recommendation. Proceeding without completing this checklist represents a violation of the Zero Assumptions rule._

### Code Pattern Recognition Reference

**ORM Patterns to Enforce:**

```python
# ✓ COMPLIANT: Model-based queries
result = await session.execute(
    select(Domain).where(Domain.id == domain_id)
)
domain = result.scalars().first()

# ✓ COMPLIANT: Relationship navigation
related_pages = domain.pages

# ✓ COMPLIANT: Attribute-based filtering
domains = await session.execute(
    select(Domain).where(Domain.domain_curation_status == DomainCurationStatus.New)
)

# ✓ COMPLIANT: Joins with relationship attributes
results = await session.execute(
    select(Domain, Page)
    .join(Page, Domain.id == Page.domain_id)
    .where(Domain.domain_name.contains(search_term))
)

# ✓ COMPLIANT: Complex query with multiple conditions
results = await session.execute(
    select(Domain)
    .where(
        and_(
            Domain.domain_curation_status == DomainCurationStatus.New,
            Domain.created_at > datetime.utcnow() - timedelta(days=7),
            or_(
                Domain.domain_name.contains("example"),
                Domain.domain_name.contains("test")
            )
        )
    )
    .order_by(Domain.created_at.desc())
    .limit(100)
)
```

**Patterns to Flag as Violations:**

```python
# ❌ VIOLATION: Raw SQL
results = await session.execute(
    text("SELECT * FROM domain WHERE domain_name LIKE '%example%'")
)

# ❌ VIOLATION: String interpolation in queries (SQL injection risk)
domain_name = "example.com"
results = await session.execute(
    text(f"SELECT * FROM domain WHERE domain_name = '{domain_name}'")
)

# ❌ VIOLATION: Service creating its own session
async def process_domain(domain_id: UUID):
    async with async_session_maker() as session:  # Wrong: Service should accept session
        domain = await session.get(Domain, domain_id)
        # ... processing logic

# ❌ VIOLATION: Service committing transaction
async def update_domain_status(session: AsyncSession, domain_id: UUID, status: str):
    domain = await session.get(Domain, domain_id)
    domain.domain_curation_status = status
    await session.commit()  # Wrong: Router should manage transaction boundary

# ❌ VIOLATION: Reference to tenant_id
domains = await session.execute(
    select(Domain).where(
        and_(
            Domain.tenant_id == 1,  # Wrong: tenant_id should not exist
            Domain.domain_name.contains(search_term)
        )
    )
)
```

_Any appearance of these violation patterns must trigger a technical debt item and remediation plan._

### Version Control

This document is version 3.0, dated 2025-05-18. It supersedes all previous versions of the Director AI Guardrails document.

_These Guardrails are a concise summary. Always defer to the detailed specifications in the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and relevant Layer Blueprints/SOPs for complete context and nuanced application._

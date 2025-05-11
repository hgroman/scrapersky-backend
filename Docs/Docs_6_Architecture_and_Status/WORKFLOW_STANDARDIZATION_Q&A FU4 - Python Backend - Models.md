# Follow-up Questions for Section 4: Python Backend - Models

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 4)

---

**Regarding Answer Q4.1 (Status Enum Naming - `{WorkflowNameTitleCase}CurationStatus` vs. `{SourceTableTitleCase}CurationStatus`):**
The answer states: "The standard pattern is `{WorkflowNameTitleCase}CurationStatus` and `{WorkflowNameTitleCase}ProcessingStatus`. For example: `PageCurationStatus` and `PageProcessingStatus` in `src/models/page.py` (Layer 1: Models & ENUMs)... This ensures clear association with the specific workflow rather than the more general source table, especially important when multiple workflows might operate on the same table."

- **Follow-up Question 4.1.1:** The rationale provided ("ensures clear association with the specific workflow... especially important when multiple workflows might operate on the same table") is clear. To make this an explicit rule in the `CONVENTIONS_AND_PATTERNS_GUIDE.md`:
  - Should the rule state: "Python Status Enum classes (e.g., for CurationStatus, ProcessingStatus) **must** always be named using the `{WorkflowNameTitleCase}` prefix (e.g., `{WorkflowNameTitleCase}CurationStatus`) and _not_ the `{SourceTableTitleCase}` prefix, regardless of whether other workflows operate on the same table, to maintain universal consistency?"
  - Are there _any_ existing counter-examples in `src/models/` (Layer 1: Models & ENUMs) where a status Enum directly associated with a specific workflow (and not a generic entity status) uses the `{SourceTableTitleCase}` prefix for its name? If so, should these be considered technical debt?

**ANSWER:**

Yes, the rule in the `CONVENTIONS_AND_PATTERNS_GUIDE.md` should explicitly state that Python Status Enum classes **must** always use the `{WorkflowNameTitleCase}` prefix pattern and not the `{SourceTableTitleCase}` prefix. This makes the convention unambiguous and ensures future implementations consistently follow the pattern.

There are indeed counter-examples in the codebase that should be considered technical debt:

1. In `src/models/sitemap.py` (Layer 1: Models & ENUMs), the workflow-specific enums use inconsistent naming patterns:

   ```python
   # Lines 44-51
   class SitemapImportCurationStatusEnum(enum.Enum):
       """Status values for Sitemap Import Curation Status"""
       New = "New"
       Selected = "Selected"
       Maybe = "Maybe"
       Not_a_Fit = "Not a Fit"
       Archived = "Archived"
   ```

   This should ideally be named `SitemapImportCurationStatus` (without the "Enum" suffix) to match the standardized pattern seen in `PageCurationStatus`.

2. In `src/models/domain.py` (Layer 1: Models & ENUMs), another inconsistency is found:
   ```python
   # Lines 34-39
   class SitemapCurationStatusEnum(enum.Enum):
       New = "New"
       Selected = "Selected"
       Maybe = "Maybe"
       Not_a_Fit = "Not a Fit"  # Match API potentially needed space
       Archived = "Archived"
   ```
   This uses the source table naming pattern (`Sitemap` rather than a workflow name like `DomainCuration`) and includes the non-standard "Enum" suffix.

Both examples also use a different enum base class approach (`enum.Enum` vs. `str, Enum` in the standard pattern), which contributes to the inconsistency.

These counter-examples should definitely be classified as technical debt that should be addressed in future refactoring, as they introduce inconsistency in naming patterns that could lead to confusion and mistakes when implementing new workflows.

---

**Regarding Answer Q4.2 (Standard Enum Values - Strictness):**
The answer states: "For new workflows, the mandated standard values should be strictly followed with no custom additions to maintain consistency." The mandated standard values are Curation: `New, Queued, Processing, Complete, Error, Skipped` and Processing: `Queued, Processing, Complete, Error`. It also notes some legacy models have different values.

- **Follow-up Question 4.2.1:** The answer mentions `sitemap.py` (Layer 1: Models & ENUMs) and `domain.py` (Layer 1: Models & ENUMs) have "workflow-specific values for historical reasons (e.g., Selected, Maybe, Not_a_Fit)."
  - Could you specify which Enums within `src/models/sitemap.py` (Layer 1: Models & ENUMs) and `src/models/domain.py` (Layer 1: Models & ENUMs) exhibit these non-standard values?

**ANSWER:**

Examining the code, I can identify the specific enums with non-standard values:

1. In `src/models/sitemap.py` (Layer 1: Models & ENUMs):

   - `SitemapImportCurationStatusEnum` (lines 44-51) uses non-standard values:
     ```python
     class SitemapImportCurationStatusEnum(enum.Enum):
         """Status values for Sitemap Import Curation Status"""
         New = "New"               # Standard
         Selected = "Selected"     # Non-standard (should be "Queued")
         Maybe = "Maybe"           # Non-standard (not in standard set)
         Not_a_Fit = "Not a Fit"   # Non-standard (not in standard set)
         Archived = "Archived"     # Non-standard (not in standard set)
     ```
   - `SitemapImportProcessStatusEnum` (lines 55-64) has a mostly standard set but with one non-standard value:
     ```python
     class SitemapImportProcessStatusEnum(enum.Enum):
         Queued = "Queued"         # Standard
         Processing = "Processing" # Standard
         Completed = "Completed"   # Non-standard naming (should be "Complete")
         Error = "Error"           # Standard
         Submitted = "Submitted"   # Non-standard (not in standard set)
     ```

2. In `src/models/domain.py` (Layer 1: Models & ENUMs):
   - `SitemapCurationStatusEnum` (lines 34-39) deviates from the standard set:
     ```python
     class SitemapCurationStatusEnum(enum.Enum):
         New = "New"               # Standard
         Selected = "Selected"     # Non-standard (should be "Queued")
         Maybe = "Maybe"           # Non-standard (not in standard set)
         Not_a_Fit = "Not a Fit"   # Non-standard (not in standard set)
         Archived = "Archived"     # Non-standard (not in standard set)
     ```
   - `SitemapAnalysisStatusEnum` (lines 43-49) mostly follows standards but with naming inconsistency:
     ```python
     class SitemapAnalysisStatusEnum(enum.Enum):
         Queued = "Queued"         # Standard
         Processing = "Processing" # Standard
         Completed = "Completed"   # Non-standard naming (should be "Complete")
         Error = "Error"           # Standard
     ```

These deviations from the standard enum values demonstrate historical inconsistencies that should be addressed in future refactoring. The most significant non-standard values are:

1. Using `Selected` instead of `Queued` for curation status
2. Including workflow-specific statuses like `Maybe`, `Not_a_Fit`, and `Archived`
3. Using `Completed` instead of `Complete` for process status completion
4. Adding additional status `Submitted` beyond the standard set

These inconsistencies are particularly notable in the curation status enums, where the standard values (`New, Queued, Processing, Complete, Error, Skipped`) are significantly different from the legacy implementations.

- Are these specific non-standard Enums documented as technical debt or exceptions in their respective canonical YAML files (e.g., under `known_issues`)?
- **Follow-up Question 4.2.2:** If a new workflow _absolutely requires_ a user-selectable state that is not covered by the standard CurationStatus Enum values (e.g., an "On Hold" or "Pending Review" state that is distinct from `New` or `Queued` and does not trigger processing), what is the mandated approach?
  - Is the standard CurationStatus Enum still used, and this additional state is managed by a _separate, new status field_ on the model (Layer 1: Models & ENUMs) (as per Q4.3)?
  - Or, in such a rare, justified case, would a deviation to extend the _standard_ CurationStatus Enum itself be permissible (following the deviation protocol from Q11.1)?

---

**Regarding Answer Q4.3 (Column Naming for Non-Standard Statuses):**
The answer suggests: "If additional status fields are absolutely necessary, they should follow the pattern: `{workflow_name}_{status_purpose}_status`. The corresponding enum would be named `{WorkflowName}{StatusPurpose}Status." It also notes "the architecture strongly discourages additional status fields."

- **Follow-up Question 4.3.1:** Can you provide a concrete, existing code example from `src/models/` (Layer 1: Models & ENUMs) where such an additional, non-standard status field (i.e., not the primary `_curation_status` or `_processing_status`) has been implemented on a model? Please include:
  - The model (Layer 1: Models & ENUMs) file path.
  - The exact column name.
  - The name of its Python Enum class.
  - The name of its PostgreSQL ENUM type.
- **Follow-up Question 4.3.2:** When such an additional status field is used, how does its update logic typically integrate with the primary dual-status (curation/processing) flow? Is it managed independently, or can changes to it affect/be affected by the primary curation/processing statuses?
- **Follow-up Question 4.3.3:** The answer strongly discourages these. Before a developer implements such an additional status field, what level of justification or review is required, and where should this justification be documented (e.g., in the workflow's canonical YAML)?

---

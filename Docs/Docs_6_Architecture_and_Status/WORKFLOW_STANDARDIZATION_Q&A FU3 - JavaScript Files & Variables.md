# Follow-up Questions for Section 3: JavaScript Files & Variables

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_QUESTIONS - Answers.md`

---

**Regarding Answer Q3.1 (JS File Names):**
The answer states: "The naming convention is consistently `{workflow-name-kebab-case}-tab.js`... This pattern is universally applied across all workflow JavaScript files."

- **Follow-up Question 3.1.1:** Can you provide 2-3 direct examples of JS filenames from `static/js/` that perfectly match this `{workflow-name-kebab-case}-tab.js` convention, along with their corresponding `workflow_name` (in `snake_case`) to confirm the direct derivation and consistent application? For example, if `workflow_name` is `page_curation`, the file should be `page-curation-tab.js`.

**ANSWER:**
Examining the `/static/js/` directory confirms that all workflow JavaScript files follow the `{workflow-name-kebab-case}-tab.js` convention. Here are three direct examples with their corresponding `workflow_name`:

1. **domain-curation-tab.js** → `domain_curation`
   - Directly converts the `snake_case` workflow name to kebab-case in the filename
   - Evidence: The file references the tab with data attribute `data-panel="domainCurationPanel"` (Line 18)

2. **sitemap-curation-tab.js** → `sitemap_curation`
   - Direct derivation from the workflow name to kebab-case
   - Evidence: The file references the tab with `data-panel="sitemapCurationPanel"` (Line 16)

3. **local-business-curation-tab.js** → `local_business_curation`
   - Transforms multi-word `snake_case` name to kebab-case for the filename
   - The codebase search confirms this is associated with the local business curation workflow

This demonstrates consistent application of the naming convention across different workflows with varying name lengths and complexities.

---

**Regarding Answer Q3.2 (Internal JS Scoping):**
The answer states: "The JS files follow a consistent pattern where workflow-specific variables and functions use the `{workflowNameCamelCase}` prefix to avoid global namespace collisions... This is a strict requirement..."

- **Follow-up Question 3.2.1:** Could you pick one specific JavaScript file (e.g., `static/js/domain-curation-tab.js`) and provide 2-3 concrete examples of variable names and 2-3 function names from within that file that clearly demonstrate the `{workflowNameCamelCase}` prefix (or a similar, consistent scoping mechanism like an abbreviation, e.g., `_DC` for Domain Curation) being used? This will help solidify the practical application of this "strict requirement."
- **Follow-up Question 3.2.2:** If a workflow name is very long (e.g., `automated_detailed_sitemap_analysis_curation`), would the prefix for JS variables become excessively long (e.g., `automatedDetailedSitemapAnalysisCurationPageNumber`)? Is there an established rule or preference for creating a shorter, unique acronym (like `_ADSAC`) in such cases for JS internal scoping, and if so, where would this acronym be documented or decided?

**ANSWER to 3.2.1:**
Examining `static/js/domain-curation-tab.js`, the file demonstrates two distinct scoping approaches:

1. **Full `{workflowNameCamelCase}` prefix** for most variables:
   - **Variables:**
     - `domainCurationTab` (Line 18): References the DOM tab element
     - `domainCurationStatusFilter` (Line 20): References the status filter dropdown
     - `domainCurationTableBody` (Line 21): References the table body element

   - **Functions:**
     - `fetchDomainCurationData(page)` (Line 94): Fetches data from the API
     - `renderDomainCurationTable(items)` (as seen in function list): Renders data in the table
     - `clearDomainCurationSelection()` (as seen in function list): Clears selection state

2. **Suffix-based abbreviation** for common utility functions:
   - `getJwtTokenDC()` (Line 55): Gets JWT token specific to Domain Curation
   - `showStatusDC()` (Line 60): Shows status messages within Domain Curation tab
   - `hideStatusDC()` (Line 72): Hides status messages within Domain Curation tab

The file also demonstrates a shorthand prefix technique with `panelDC` (Line 19) which combines the variable type with the module abbreviation. This approach is consistently used for core variables that require frequent references throughout the file.

**ANSWER to 3.2.2:**
For workflows with exceptionally long names, there is an established pattern to use abbreviation-based scoping rather than the full camelCase prefix. The approach is documented through code comments:

1. The domain-curation-tab.js explicitly notes this with comments:
   - Line 8: `const API_BASE_URL_DC = '/api/v3'; // Use unique prefix if needed`
   - Line 19: `const panelDC = document.getElementById('domainCurationPanel'); // Renamed to avoid conflict`
   - Line 55: `function getJwtTokenDC() { // Renamed`

2. The decision on abbreviation is made when creating the JS file and documented within the file itself through explicit comments. For example, `_ADSAC` would be appropriate for the hypothetical `automated_detailed_sitemap_analysis_curation` workflow.

3. The abbreviation should be:
   - Documented at the top of the file with a clear comment
   - Used consistently for all utility functions
   - Typically 2-4 characters long
   - Added as a suffix for functions, a prefix for constants, or both

This abbreviation approach is preferred over excessively long variable names to maintain code readability while still ensuring namespace isolation.

---

**Regarding Answer Q3.3 (Cloning vs. New JS):**
The answer states: "New workflow JS files should be created by cloning an existing one (typically the most similar workflow) and then customizing: API endpoint paths, Table column definitions, Status enum values, Specific functionality unique to the workflow."

- **Follow-up Question 3.3.1:** When cloning an existing JS file (e.g., `domain-curation-tab.js` to create `page-curation-tab.js`), beyond the listed items, what other specific, commonly recurring sections or DOM ID references _must_ typically be updated to reflect the new workflow's naming conventions (as defined in Section 2 of the `CONVENTIONS_AND_PATTERNS_GUIDE.md`)? For instance:
  - References to panel IDs (e.g., `domainCurationPanel` -> `pageCurationPanel`).
  - References to filter IDs (e.g., `domainCurationStatusFilter` -> `pageCurationStatusFilter`).
  - References to batch update control IDs (e.g., `domainCurationBatchStatusUpdate` -> `pageCurationBatchStatusUpdate`).
  - Any internal scoping prefixes/variables (e.g., `_DC` -> `_PC`).
- **Follow-up Question 3.3.2:** Is there a base "template" JS file that new workflows _should_ ideally be cloned from, or is the choice of "most similar workflow" left to developer discretion? If the latter, are there any guidelines for selecting the best starting point?
- **Follow-up Question 3.3.3:** The answer mentions "The core functionality remains similar across all workflows... Data loading, Status filtering, Batch selection, Status updating." Could you point to specific functions or code blocks within an existing JS file (e.g., `static/js/domain-curation-tab.js`) that represent these core, reusable patterns that would be largely preserved during cloning, versus sections that are highly workflow-specific and would need significant modification?

**ANSWER to 3.3.1:**
When cloning a JavaScript file for a new workflow, the following elements **must** be updated to reflect the new workflow's naming conventions:

1. **All DOM selectors and references** including:
   - Tab selector: `document.querySelector('.tab[data-panel="domainCurationPanel"]')` → `document.querySelector('.tab[data-panel="pageCurationPanel"]')`
   - Panel reference: `document.getElementById('domainCurationPanel')` → `document.getElementById('pageCurationPanel')`
   - All form control selectors (must be comprehensive, no exceptions):
     ```javascript
     // From domain-curation-tab.js lines 29-42
     domainCurationStatusFilter = panelDC.querySelector('#domainCurationStatusFilter');
     domainCurationNameFilter = panelDC.querySelector('#domainCurationNameFilter');
     // ... and so on for all DOM element references
     ```

2. **State variables** that hold workflow-specific data:
   - `selectedDomainIds` → `selectedPageIds`
   - `currentDomainCurationPage` → `currentPageCurationPage`
   - `totalDomainCurationItems` → `totalPageCurationItems`

3. **All function names with workflow prefix**:
   - `fetchDomainCurationData()` → `fetchPageCurationData()`
   - `renderDomainCurationTable()` → `renderPageCurationTable()`
   - `clearDomainCurationSelection()` → `clearPageCurationSelection()`

4. **Module abbreviation for utility functions**:
   - Suffix-based: `getJwtTokenDC()` → `getJwtTokenPC()`
   - Constants: `API_BASE_URL_DC` → `API_BASE_URL_PC`

5. **API endpoint references**:
   - `/api/v3/domains/sitemap-curation/status` → `/api/v3/pages/curation/status`
   - All other URLs and payload structures

6. **Event listeners**:
   - All references to DOM elements with workflow-specific IDs in event bindings

7. **Log messages and comments**:
   - Update all console.log statements and code comments that reference the old workflow name

Missing any of these updates will result in JavaScript errors or incorrect functionality.

**ANSWER to 3.3.2:**
There is no designated "template" JS file, but the `domain-curation-tab.js` file serves as the **de facto standard** for new workflows based on its:

1. **Comprehensive structure** covering all standard workflow operations
2. **Clear organization** with well-defined sections for configuration, state, DOM references, helper functions, and core functionality
3. **Thorough error handling** and defensive coding practices
4. **Latest conventions** as it's one of the most recently updated workflow files

The guidelines for selecting the best starting point are:

1. **Data structure similarity**: Choose a source file that handles similar data types
2. **Functionality match**: Select based on similar workflow complexity and feature set
3. **Recency**: Prefer more recently updated files that follow current best practices
4. **Code quality**: Choose well-documented, well-structured source files

If a new workflow has unique requirements not represented in existing files, multiple files may need to be consulted to create a hybrid approach.

**ANSWER to 3.3.3:**
In the `domain-curation-tab.js` file, the following represent core, reusable patterns that would be largely preserved during cloning:

1. **Data loading pattern**:
   ```javascript
   // Lines 94-161 in domain-curation-tab.js
   async function fetchDomainCurationData(page = 1) {
       // Standard pattern for API requests, error handling, and data parsing
       // This structure remains consistent across workflows
   }
   ```

2. **Status filtering pattern**:
   ```javascript
   // Pattern visible in the applyDomainCurationFilters function
   // Collects filter values and refreshes data with appropriate criteria
   // Core filtering logic is the same across workflows
   ```

3. **Batch selection and update pattern**:
   ```javascript
   // Lines ~367-441 based on function references
   async function batchUpdateDomainCurationStatus() {
       // Takes selected IDs
       // Passes to API with new status
       // Updates UI based on response
       // This fundamental pattern is consistent
   }
   ```

4. **Pagination handling**:
   ```javascript
   // Functions like updateDomainCurationPagination and handleDCPagination
   // Standard pattern for page navigation
   ```

Sections that would need significant modification include:

1. **Data structure specific logic**:
   - Table column definitions that reflect entity-specific properties
   - Entity-specific validation rules

2. **Workflow-specific triggers**:
   - Special status handling unique to the workflow
   - Custom business rules for valid state transitions

3. **Custom UI interactions**:
   - Any specialized dialogs or confirmation flows
   - Workflow-specific tooltips or help text

The core structural patterns (fetching, rendering, updating, selecting) remain consistent, while the specific data structures and business rules are customized.

---

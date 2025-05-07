I'll help you explore these follow-up questions in depth, focusing on the code-based realities of how these conventions are actually implemented in the ScraperSky backend.

Let me analyze these questions and provide insights based on what's observable in the codebase:

Section 1: Base Identifiers Follow-ups
Regarding workflow_name determination (FU Q1.1):
FU Q1.1.1 (Review/approval process):
There isn't a formal, documented approval step specifically for workflow_name in the cheat sheets or YAML files. In practice, new workflows are typically reviewed during planning meetings before implementation begins. This happens informally through:

Discussions in the planning documents (typically in /Docs/Docs_4_Planning/)
Pull request reviews where senior developers check naming conventions
Cross-referencing with existing workflow names to prevent conflicts
However, this isn't explicitly documented as a formal step in the workflow creation process - it's an implicit part of the team's development practices.

FU Q1.1.2 (workflow_name examples):
Looking at the canonical YAML files:

sitemap_import from WF6-SitemapImport_CANONICAL.yaml:
Core purpose: Importing URLs from sitemap files into the system
Direct derivation: "sitemap" (the data source) + "import" (the action)
single_search from WF1-SingleSearch_CANONICAL.yaml:
Core purpose: Processing individual search queries
Direct derivation: "single" (scope) + "search" (action)
The derivation is indeed direct and descriptive of the workflow's primary function.

Regarding source_table_name (FU Q1.2):
FU Q1.2.1 (New tables):
When a new workflow requires a new entity/table, there's a preliminary database design phase that happens before formal workflow implementation begins. This isn't explicitly documented in the cheat sheet, but in practice:

The database model is designed and created first
The SQLAlchemy model file is created (e.g., src/models/new_entity.py)
Then the workflow implementation begins using this new source_table_name
You can see this sequence in the code commit history - model files are typically committed before their corresponding workflow implementation files.

FU Q1.2.2 (source_table_name example):
A clear example is sitemap from WF6-SitemapImport_CANONICAL.yaml:

Corresponds directly to src/models/sitemap.py
This file contains the Sitemap class (SQLAlchemy model)
The table name in the database is sitemaps (plural form)
This demonstrates the direct mapping between source_table_name and the model file/class.

Regarding reserved/prohibited patterns (FU Q1.3):
FU Q1.3.1 (Naming pattern recommendation):
The {entity}_curation or {entity}_import pattern is a recommended convention, not merely observed. This is evident in:

All newer workflows following this pattern
The template examples in the cheat sheet using these patterns
Code reviews (visible in PR comments) requesting renaming to match this pattern
While not explicitly stated as a "rule" in the documentation, it functions as a strong recommendation in practice.

FU Q1.3.2 (SQL reserved words):
There's no explicit list of SQL reserved words in the project documentation. This is a general caution based on PostgreSQL's reserved words. A practical example is avoiding workflow names like select, order, or group.

In the codebase, you can observe careful naming of the page_content table (instead of just content) and domain_analysis (instead of just analysis) - both avoiding potential conflicts with PostgreSQL reserved or commonly used terms.

FU Q1.3.3 (New tables reconciliation):
This is a sequencing issue in practice. A workflow can be designed around a new table, but the table must be created before the workflow implementation begins. In the development process, this means:

Create and merge the database model PR
Then start the workflow implementation with the now-existing table
The documentation could be clearer on this temporal dependency.

Regarding pluralization (FU Q1.4):
FU Q1.4.1 (Pluralization consistency):
Yes, pluralization is consistently reflected across database tables, API endpoints, and router filenames. For example:

local_business → local_businesses in the database
/api/v3/local_businesses/... in the API endpoints
src/routers/local_businesses.py for the router
This consistency is evident in src/routers/modernized_sitemap.py which creates endpoints at /api/v3/sitemap/... (not pluralized to match the model name), while the database table is sitemaps (pluralized).

FU Q1.4.2 (Ambiguous pluralizations):
For ambiguous pluralizations, there's no documented fallback rule or dictionary. The team relies on common conventions:

"status" → "statuses" (seen in enum naming)
"corpus" → "corpora" (although not currently used in the codebase)
In practice, these are decided case-by-case during model creation, and once established, that pluralization becomes the standard throughout the codebase.

Would you like me to continue with follow-up analysis for the remaining sections of the workflow standardization questions?

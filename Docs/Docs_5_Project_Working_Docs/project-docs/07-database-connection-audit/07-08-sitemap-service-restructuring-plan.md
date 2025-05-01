---
title: Sitemap Service Restructuring Plan
date: 2025-03-26
author: System
status: Action Required
priority: High
---

# Sitemap Service Restructuring Plan

## Overview

This document outlines the specific steps to restructure the sitemap-related code to follow a consistent organizational pattern. We will move the sitemap functionality from its current scattered locations into a unified directory structure under `/src/services/sitemap/`.

## Current Structure

```
/src/
  ├── services/
  │   ├── sitemap_service.py  <- standalone file
  │   └── sitemap/            <- directory exists but underutilized
  └── scraper/
      └── sitemap_analyzer.py <- core analyzer code in wrong location
```

## Target Structure

```
/src/
  └── services/
      └── sitemap/
          ├── analyzer_service.py  <- moved from scraper
          ├── background_service.py <- new file
          └── sitemap_service.py    <- moved from services root
```

## Implementation Steps

### 1. Create the Directory Structure

```bash
# Ensure directory exists
mkdir -p /src/services/sitemap
```

### 2. Move Sitemap Analyzer

1. **Create new file**:

   ```bash
   cp /src/scraper/sitemap_analyzer.py /src/services/sitemap/analyzer_service.py
   ```

2. **Update imports in the new file**:

   - Change relative imports to match new location

   ```python
   # From: from ..models import SitemapFile
   # To:   from ...models import SitemapFile
   ```

   - Update any other imports that may be affected

3. **Fix dependencies**:

   ```bash
   # Find all files that import the old module
   grep -r "from ..scraper.sitemap_analyzer" ./src
   grep -r "import sitemap_analyzer" ./src
   ```

4. **Update all imports in dependent files**:
   ```python
   # From: from ..scraper.sitemap_analyzer import SitemapAnalyzer
   # To:   from ..services.sitemap.analyzer_service import SitemapAnalyzer
   ```

### 3. Move Sitemap Service

1. **Create new file**:

   ```bash
   cp /src/services/sitemap_service.py /src/services/sitemap/sitemap_service.py
   ```

2. **Update imports in the new file**:

   - Change relative imports to match new location

   ```python
   # From: from ..models import SitemapFile
   # To:   from ...models import SitemapFile
   ```

3. **Fix dependencies**:

   ```bash
   # Find all files that import the old module
   grep -r "from ..services.sitemap_service" ./src
   grep -r "import sitemap_service" ./src
   ```

4. **Update all imports in dependent files**:
   ```python
   # From: from ..services.sitemap_service import SitemapService
   # To:   from ..services.sitemap.sitemap_service import SitemapService
   ```

### 4. Create Background Service

1. Create the new background service file at `/src/services/sitemap/background_service.py` as described in the implementation plan.

2. Ensure it has the proper imports relative to its new location:
   ```python
   from ...session.async_session import get_session
   from ..job_service import job_service
   from .analyzer_service import SitemapAnalyzer
   ```

### 5. Update Router to Use New Structure

1. **Update modernized_sitemap.py**:

   ```python
   # From:
   from ..services.sitemap_service import SitemapService
   from ..scraper.sitemap_analyzer import SitemapAnalyzer

   # To:
   from ..services.sitemap.sitemap_service import SitemapService
   from ..services.sitemap.analyzer_service import SitemapAnalyzer
   from ..services.sitemap.background_service import process_domain_background, process_batch_background
   ```

### 6. Testing

1. Run the sitemap tests:

   ```bash
   pytest tests/services/sitemap/
   ```

2. Run the debug script:
   ```bash
   python project-docs/07-database-connection-audit/scripts/debug_sitemap_flow.py
   ```

### 7. Cleanup

After verifying functionality:

1. Remove the original files:
   ```bash
   rm /src/scraper/sitemap_analyzer.py
   rm /src/services/sitemap_service.py
   ```

## Execution Plan

Execute these steps in sequence:

1. Create directory structure
2. Move sitemap_analyzer.py to analyzer_service.py
3. Move sitemap_service.py
4. Create background_service.py
5. Update all imports in dependent files
6. Run tests
7. Clean up original files

## Rollback Plan

If issues arise:

1. Restore original files from their previous locations
2. Revert import changes
3. Remove the new files/structure

## Success Criteria

1. All code successfully runs from new locations
2. No references to old file locations remain in the codebase
3. The debug_sitemap_flow.py script executes successfully
4. Directory structure follows the consistent pattern described

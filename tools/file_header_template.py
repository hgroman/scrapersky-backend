"""
ScraperSky Backend File Header Template
======================================

This template shows how to add the standard file header to Python source files
that includes the file_number from the Supabase File Audit System.

Usage:
1. Copy this template to the top of your Python file
2. Update the file_number with the assigned number from file_audit table
3. Fill in the purpose, layer, and workflows information
4. Keep the header format consistent across all files
"""

"""
FILE: {file_path}
FILE_NUMBER: {file_number}
LAYER: Layer {layer_number} - {layer_name}
STATUS: {status} - {workflow_description}
PURPOSE: {purpose}

This file is part of the ScraperSky Backend.
Standardized: {standardized_date}
Last Audit: {audit_date}

[STANDARDIZED] - This file has been standardized according to ScraperSky conventions
"""

# Example usage (replace with actual code):
"""
FILE: src/services/sitemap/sitemap_service.py
FILE_NUMBER: 3025
LAYER: Layer 4 - Services
STATUS: SHARED - Used by multiple workflows (WF5, WF6)
PURPOSE: Provides core sitemap processing functionality for sitemap curation

This file is part of the ScraperSky Backend.
Standardized: 2025-05-19
Last Audit: 2025-05-19

[STANDARDIZED] - This file has been standardized according to ScraperSky conventions
"""

# Example of how a file might be updated with the header:
"""
FILE: src/models/place.py
FILE_NUMBER: 0100
LAYER: Layer 1 - Models & ENUMs
STATUS: SHARED - Used by multiple workflows (WF1, WF2, WF3)
PURPOSE: Defines the Place model and associated enums for place data

This file is part of the ScraperSky Backend.
Standardized: 2025-05-19
Last Audit: 2025-05-19

[STANDARDIZED] - This file has been standardized according to ScraperSky conventions
"""

# Actual file content begins here...

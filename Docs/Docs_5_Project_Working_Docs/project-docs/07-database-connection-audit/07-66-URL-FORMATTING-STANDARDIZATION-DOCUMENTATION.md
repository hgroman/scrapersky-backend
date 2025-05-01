# 07-66 URL Formatting Standardization Documentation

**Document ID:** 07-66-URL-FORMATTING-STANDARDIZATION-DOCUMENTATION
**Date:** 2025-03-29
**Author:** ScraperSky Engineering Team
**Status:** Completed

## Overview

This document details how the ScraperSky backend handles URL formatting, specifically focusing on the automatic conversion of HTTP URLs to HTTPS for security purposes. The standardization ensures all domain processing is consistent regardless of how users input domain URLs.

## Problem Statement

Users may submit domains to the ScraperSky API in various formats:

- Domain name only (e.g., `example.com`)
- With HTTP protocol (e.g., `http://example.com`)
- With HTTPS protocol (e.g., `https://example.com`)
- With www prefix (e.g., `www.example.com`)
- Various combinations of the above

For security and consistency reasons, all domains must be processed using HTTPS regardless of input format. This document explains how the system standardizes these inputs.

## Implementation Details

### URL Conversion Logic

The core conversion logic is implemented in `src/scraper/metadata_extractor.py`:

```python
# Ensure all connections use HTTPS for security
if domain.startswith('http://'):
    # Convert HTTP to HTTPS
    url = 'https://' + domain[7:]
    logger.info(f"Upgrading HTTP to HTTPS: {domain} → {url}")
elif domain.startswith('https://'):
    # Already HTTPS, use as-is
    url = domain
else:
    # No protocol specified, add HTTPS
    url = f"https://{domain}"
```

This handles three cases:

1. HTTP URLs are upgraded to HTTPS
2. HTTPS URLs remain unchanged
3. Domain names without protocols get HTTPS added

### Domain Standardization

The system also performs domain standardization in `src/scraper/domain_utils.py`:

```python
def standardize_domain(input_domain: str) -> str:
    """
    Standardize domain input and return the clean domain.
    """
    # Strip whitespace and convert to lowercase
    domain = input_domain.strip().lower()

    # If it's already a URL, extract the domain
    if '://' in domain:
        parsed = urlparse(domain)
        domain = parsed.netloc or domain  # Fallback to original if netloc is empty

    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remove any paths or query parameters
    domain = domain.split('/')[0]

    # Validate domain format
    domain_pattern = r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$'
    if not re.match(domain_pattern, domain):
        raise ValueError(f"Invalid domain format: {domain}")

    return domain
```

### Domain URL Generation

Once standardized, the system generates the full HTTPS URL:

```python
def get_domain_url(domain: str) -> str:
    """
    Get the full URL for a domain.
    """
    return f"https://{domain}"
```

## Testing Verification

The system correctly handles HTTP URLs by upgrading them to HTTPS. This was verified with the following test:

1. Request sent:

```bash
curl -X POST "http://localhost:8000/api/v3/modernized_page_scraper/scan" -H "Content-Type: application/json" -d '{"base_url": "http://prosymmetry.com", "max_pages": 5}'
```

2. System response (job status):

```json
{
  "job_id": "265",
  "status": "processing",
  "domain": null,
  "progress": 0.0,
  "created_at": "2025-03-29T01:22:49.298413",
  "updated_at": "2025-03-29T01:22:49.298413",
  "result": null,
  "error": null,
  "metadata": {
    "domain": "https://prosymmetry.com",
    "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
    "max_pages": 5,
    "start_time": "2025-03-29T01:22:50.473633"
  }
}
```

Note that although the request was made with `http://prosymmetry.com`, the metadata shows `https://prosymmetry.com`, confirming the upgrade was successful.

## Benefits

This standardization provides several benefits:

1. **Security**: All scraping is done over HTTPS, reducing risks associated with unencrypted connections
2. **Consistency**: Internal processing always uses the same URL format
3. **Simplicity**: Users can input domains in various formats without worrying about protocol specification
4. **Compatibility**: Some sites may redirect HTTP to HTTPS; standardizing avoids this redirect overhead

## Edge Cases Handled

The system properly handles:

- URLs with or without protocol prefixes
- URLs with www prefix (stripped during standardization)
- HTTP URLs (automatically upgraded to HTTPS)
- Lowercase conversion for consistency
- Removal of trailing paths or query parameters

## Future Recommendations

1. Add comprehensive logging of URL transformations to assist in debugging
2. Consider implementing a warning mechanism when HTTP is upgraded to HTTPS
3. Add metrics to track how often HTTP to HTTPS conversion occurs
4. Verify SSL certificate validation is properly enabled for all HTTPS requests

## Related Documentation

- [07-36-MODERNIZED-PAGE-SCRAPER-FIX-WORK-ORDER-2025-03-26.md](./07-36-MODERNIZED-PAGE-SCRAPER-FIX-WORK-ORDER-2025-03-26.md)
- [07-37-MODERNIZED-PAGE-SCRAPER-FIX-IMPLEMENTATION-2025-03-27.md](./07-37-MODERNIZED-PAGE-SCRAPER-FIX-IMPLEMENTATION-2025-03-27.md)

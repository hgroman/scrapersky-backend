# Service Interface Standardization

This document outlines standardized patterns for service interfaces throughout the ScraperSky codebase. Consistent interfaces ensure that services work together properly and make the codebase more maintainable.

## Current Issues

Several issues have been identified with service interfaces:

1. **Inconsistent Parameter Formats:**

   - Some services expect URLs with protocols, others without
   - Parameter naming is inconsistent across similar methods
   - Type expectations are not always clear

2. **Validation Mismatches:**

   - Validation and processing services have incompatible expectations
   - Validation patterns don't account for all valid input formats
   - Error handling is inconsistent across validation methods

3. **Interface Documentation:**
   - Many services lack clear interface documentation
   - Type hints are missing or incorrect
   - Return type specifications are often absent

## Standardization Principles

To address these issues, we're implementing the following standardization principles:

1. **Consistent Input Format Handling:**

   - Services must handle inputs in both normalized and non-normalized forms
   - URL/domain validation must handle both formats with and without protocols
   - Input parameters should have clear type hints

2. **Standardized Method Signatures:**

   - Common operations should have consistent parameter names
   - Return types should be clearly specified
   - Async methods should be used consistently

3. **Error Handling Standards:**
   - Services should use standardized exception types
   - Validation errors should provide clear, helpful messages
   - Error states should be properly propagated

## Validation Service Standards

The validation service must be updated to follow these patterns:

```python
class ValidationService:
    """Standardized validation service for all input validation."""

    def validate_domain(self, domain: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate a domain or URL.

        Args:
            domain: The domain or URL to validate (handles both formats)

        Returns:
            Tuple containing:
            - bool: Whether validation passed
            - str: Error message if failed, success message if passed
            - Optional[str]: Normalized domain if passed, None if failed
        """
        try:
            # Handle both domain formats (with or without protocol)
            normalized_domain = self.normalize_domain(domain)

            # Additional validation
            if not self._is_valid_domain_format(normalized_domain):
                return False, f"Invalid domain format: {domain}", None

            return True, "Domain validated successfully", normalized_domain
        except Exception as e:
            return False, f"Validation error: {str(e)}", None

    def normalize_domain(self, domain: str) -> str:
        """
        Normalize a domain to a standard format.

        Args:
            domain: Domain or URL (with or without protocol)

        Returns:
            Normalized domain without protocol
        """
        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            parsed = urlparse(domain)
            domain = parsed.netloc

        # Additional normalization
        domain = domain.split('/')[0]  # Remove path
        domain = domain.split(':')[0]  # Remove port
        domain = domain.lower()        # Lowercase

        return domain
```

## Processing Service Standards

The processing service must standardize how it handles domains and URLs:

```python
class ProcessingService:
    """Standardized processing service for domain operations."""

    async def initiate_domain_scan(
        self,
        session: AsyncSession,
        url_or_domain: str,
        tenant_id: str,
        user_id: str = "system",
        max_pages: int = 1000
    ) -> Dict[str, Any]:
        """
        Initiate a scan for a single domain.

        Args:
            session: Database session
            url_or_domain: URL or domain to scan (handles both formats)
            tenant_id: Tenant ID for the scan
            user_id: User ID initiating the scan
            max_pages: Maximum number of pages to scan

        Returns:
            Dictionary with job_id and status_url

        Raises:
            ValueError: If domain validation fails
        """
        # Validate domain (pass original input, get normalized result)
        is_valid, message, domain = await self.validation_service.validate_domain(url_or_domain)
        if not is_valid or not domain:
            raise ValueError(message)

        # Use normalized domain for further processing
        # ...
```

## API Response Standards

All services should follow consistent response patterns:

```python
@router.post("/scan", response_model=JobResponse)
async def scan_domain(
    request: DomainScanRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Scan a single domain.

    Args:
        request: Domain scan request containing base_url, tenant_id, etc.
        session: Database session from dependency

    Returns:
        JobResponse with job_id and status_url
    """
    try:
        # Validation happens inside the service
        result = await processing_service.initiate_domain_scan(
            session=session,
            url_or_domain=request.base_url,
            tenant_id=request.tenant_id,
            max_pages=request.max_pages
        )

        return JobResponse(
            job_id=result["job_id"],
            status_url=result["status_url"]
        )
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle other errors
        logger.error(f"Error in scan_domain: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Implementation Plan

1. **Update Validation Service First:**

   - Refactor `validation_service.py` to handle both URL formats
   - Ensure consistent return types across all validation methods
   - Add proper error handling

2. **Standardize Processing Services:**

   - Update `processing_service.py` to work with standardized validation
   - Fix parameter naming to be consistent
   - Update error handling

3. **Update Router Interfaces:**

   - Ensure all router methods follow standardized patterns
   - Update request/response models for consistency
   - Add proper error handling

4. **Documentation:**
   - Document all service interfaces with proper docstrings
   - Create standardized examples for the most common operations
   - Update technical documentation with interface guidelines

## Conclusion

Standardizing service interfaces is a critical step in our modernization effort. By ensuring consistent interfaces, we'll make the codebase more maintainable, reduce bugs from mismatched expectations, and accelerate development with predictable patterns.

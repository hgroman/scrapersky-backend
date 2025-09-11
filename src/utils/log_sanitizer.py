"""
Log Sanitization Utilities

Security utilities to prevent sensitive information from appearing in logs.
"""

import re
from typing import Any


def sanitize_api_keys(text: str) -> str:
    """
    Remove API keys from text to prevent exposure in logs.
    
    Args:
        text: Text that may contain API keys in URLs or error messages
        
    Returns:
        Sanitized text with API keys replaced by redaction placeholders
    """
    if not text:
        return text
    
    # Pattern to match various API key formats in URLs
    patterns = [
        r'key=[^&\s]+',              # Google Maps API: key=abc123
        r'api_key=[^&\s]+',          # Generic: api_key=abc123
        r'apikey=[^&\s]+',           # Alternative: apikey=abc123
        r'token=[^&\s]+',            # Auth tokens: token=abc123
        r'access_token=[^&\s]+',     # OAuth: access_token=abc123
    ]
    
    sanitized = text
    for pattern in patterns:
        sanitized = re.sub(pattern, lambda m: m.group().split('=')[0] + '=***REDACTED***', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def sanitize_exception_message(exception: Exception) -> str:
    """
    Create a sanitized string representation of an exception.
    
    Args:
        exception: The exception to sanitize
        
    Returns:
        Sanitized exception message with API keys redacted
    """
    return sanitize_api_keys(str(exception))


def get_safe_exception_info(exception: Exception) -> dict:
    """
    Get safe exception information for logging without sensitive data.
    
    Args:
        exception: The exception to process
        
    Returns:
        Dictionary with safe exception details
    """
    return {
        "exception_type": type(exception).__name__,
        "exception_module": type(exception).__module__,
        "sanitized_message": sanitize_exception_message(exception),
        "has_args": len(exception.args) > 0,
        "args_count": len(exception.args)
    }
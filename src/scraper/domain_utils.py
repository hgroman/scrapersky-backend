import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def standardize_domain(input_domain: str) -> str:
    """
    Standardize domain input and return the clean domain.

    Args:
        input_domain: Raw domain input (can be domain.com, www.domain.com, http://domain.com etc)

    Returns:
        str: clean_domain (e.g. 'domain.com')

    Raises:
        ValueError: If the domain format is invalid
    """
    try:
        # Strip whitespace and convert to lowercase
        domain = input_domain.strip().lower()

        # If it's already a URL, extract the domain
        if "://" in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc or domain  # Fallback to original if netloc is empty

        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        # Remove any paths or query parameters
        domain = domain.split("/")[0]

        # Validate domain format
        domain_pattern = r"^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$"
        if not re.match(domain_pattern, domain):
            raise ValueError(f"Invalid domain format: {domain}")

        return domain

    except Exception as e:
        logger.error(f"Error standardizing domain {input_domain}: {str(e)}")
        raise ValueError(f"Invalid domain format: {input_domain}")


def get_domain_url(domain: str) -> str:
    """
    Get the full URL for a domain.

    Args:
        domain: Clean domain (e.g. 'domain.com')

    Returns:
        str: Full URL (e.g. 'https://domain.com')
    """
    return f"https://{domain}"


def extract_domain_from_url(url: str) -> str:
    """
    Extract clean domain from a full URL.

    Args:
        url: Full URL (e.g. https://www.domain.com/path)

    Returns:
        str: Clean domain (e.g. 'domain.com')
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    return domain

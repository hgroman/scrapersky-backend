"""
Validation Service

This module provides validation utilities for common data types
and domain-specific validation logic.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import validators

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service for validating input data.

    Provides methods for validating common data types and domain-specific validation.
    """

    # URL validation regex
    URL_REGEX = re.compile(
        r"^(http|https)://"  # scheme
        r"([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"  # domain
        r"(/[a-zA-Z0-9_\-./~!*\'();:@&=+$,?%]*)?"  # path
        r"(\?[a-zA-Z0-9_\-./~!*\'();:@&=+$,%?]*)?"  # query string
        r"(#[a-zA-Z0-9_\-./~!*\'();:@&=+$,%?]*)?$"  # fragment
    )

    # Email validation regex
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate_url(self, url: str) -> bool:
        """
        Validate a URL string.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise

        Raises:
            ValueError: If URL is invalid with reason
        """
        if not url:
            raise ValueError("URL cannot be empty")

        # Check if URL starts with http:// or https://
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        # Try multiple validation methods
        if not validators.url(url):
            # Try our regex as a fallback
            if not self.URL_REGEX.match(url):
                raise ValueError(f"Invalid URL format: {url}")

        return True

    def validate_domain(self, domain: str) -> bool:
        """
        Validate a domain string.

        Args:
            domain: Domain to validate

        Returns:
            True if domain is valid, False otherwise

        Raises:
            ValueError: If domain is invalid with reason
        """
        if not domain:
            raise ValueError("Domain cannot be empty")

        # Remove protocol if present
        if domain.startswith(("http://", "https://")):
            domain = re.sub(r"^https?://", "", domain)

        # Remove path if present
        domain = domain.split("/")[0]

        # Check domain with library
        if not validators.domain(domain):
            raise ValueError(f"Invalid domain format: {domain}")

        return True

    def validate_email(self, email: str) -> bool:
        """
        Validate an email address.

        Args:
            email: Email to validate

        Returns:
            True if email is valid, False otherwise

        Raises:
            ValueError: If email is invalid with reason
        """
        if not email:
            raise ValueError("Email cannot be empty")

        if not validators.email(email) and not self.EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email format: {email}")

        return True

    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Validate a UUID string.

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if UUID is valid, False otherwise

        Raises:
            ValueError: If UUID is invalid with reason
        """
        if not uuid_str:
            raise ValueError("UUID cannot be empty")

        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            raise ValueError(f"Invalid UUID format: {uuid_str}")

    def validate_date(self, date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """
        Validate a date string.

        Args:
            date_str: Date string to validate
            format_str: Expected date format (default: YYYY-MM-DD)

        Returns:
            True if date is valid, False otherwise

        Raises:
            ValueError: If date is invalid with reason
        """
        if not date_str:
            raise ValueError("Date cannot be empty")

        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            raise ValueError(f"Invalid date format. Expected {format_str}: {date_str}")

    def validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """
        Validate that all required fields are present in the data.

        Args:
            data: Data dictionary to validate
            required_fields: List of field names that are required

        Returns:
            True if all required fields are present, False otherwise

        Raises:
            ValueError: If any required fields are missing
        """
        missing_fields = [
            field
            for field in required_fields
            if field not in data or data[field] is None
        ]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return True

    def validate_string_length(
        self,
        value: str,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> bool:
        """
        Validate a string's length.

        Args:
            value: String to validate
            field_name: Name of the field for error messages
            min_length: Minimum allowed length (optional)
            max_length: Maximum allowed length (optional)

        Returns:
            True if string length is valid, False otherwise

        Raises:
            ValueError: If string length is invalid with reason
        """
        if value is None:
            raise ValueError(f"{field_name} cannot be None")

        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        if min_length is not None and len(value) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")

        if max_length is not None and len(value) > max_length:
            raise ValueError(f"{field_name} cannot exceed {max_length} characters")

        return True

    def validate_numeric_range(
        self,
        value: Union[int, float],
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> bool:
        """
        Validate a numeric value's range.

        Args:
            value: Numeric value to validate
            field_name: Name of the field for error messages
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)

        Returns:
            True if numeric value is valid, False otherwise

        Raises:
            ValueError: If numeric value is invalid with reason
        """
        if value is None:
            raise ValueError(f"{field_name} cannot be None")

        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number")

        if min_value is not None and value < min_value:
            raise ValueError(f"{field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} cannot exceed {max_value}")

        return True

    def validate_enum_value(self, value: Any, enum_class: Any, field_name: str) -> bool:
        """
        Validate that a value is a valid enum value.

        Args:
            value: Value to validate
            enum_class: Enum class to validate against
            field_name: Name of the field for error messages

        Returns:
            True if value is a valid enum value, False otherwise

        Raises:
            ValueError: If value is not a valid enum value with reason
        """
        if value is None:
            raise ValueError(f"{field_name} cannot be None")

        try:
            # Try to convert string to enum value
            if isinstance(value, str):
                enum_class(value)
            # Try to check if value is in enum
            elif value not in enum_class.__members__.values():
                raise ValueError
        except ValueError:
            valid_values = [e.value for e in enum_class]
            raise ValueError(f"{field_name} must be one of: {', '.join(valid_values)}")

        return True


# Create a singleton instance
validation_service = ValidationService()

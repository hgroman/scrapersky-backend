"""
Custom SQLAlchemy Types

This module contains custom SQLAlchemy type decorators for handling specific
database type requirements, particularly for PostgreSQL enum serialization.
"""

from enum import Enum
from typing import Optional, Type

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.types import TypeDecorator


class PostgreSQLEnum(TypeDecorator):
    """
    Custom TypeDecorator for PostgreSQL Enum types that ensures proper serialization.

    This decorator fixes the issue where SQLAlchemy + AsyncPG serializes Python enum
    objects using their .name attribute instead of their .value attribute, causing
    PostgreSQL enum constraint violations.

    Usage:
        class MyModel(Base):
            status: Column[MyEnum] = Column(
                PostgreSQLEnum(MyEnum, name="my_enum_type", create_type=False),
                nullable=False
            )
    """

    impl = String
    cache_ok = True

    def __init__(
        self, enum_class: Type[Enum], name: str, create_type: bool = False, **kwargs
    ):
        """
        Initialize the PostgreSQL enum type decorator.

        Args:
            enum_class: The Python enum class
            name: PostgreSQL enum type name
            create_type: Whether to create the enum type (should be False for existing types)
            **kwargs: Additional arguments passed to the underlying PgEnum
        """
        self.enum_class = enum_class
        self.name = name
        self.create_type = create_type

        # Create the underlying PostgreSQL ENUM type for schema generation
        self.pg_enum = PgEnum(enum_class, name=name, create_type=create_type, **kwargs)

        super().__init__(**kwargs)

    def process_bind_param(self, value: Optional[Enum], dialect) -> Optional[str]:
        """
        Convert Python enum object to string value for database storage.

        This ensures that enum.value (e.g., "unknown") is stored in the database
        instead of enum.name (e.g., "UNKNOWN").

        Args:
            value: Python enum object or None
            dialect: SQLAlchemy dialect

        Returns:
            String value for database or None
        """
        if value is None:
            return None

        if isinstance(value, self.enum_class):
            # Use the enum's value attribute for database storage
            return value.value

        # If it's already a string, pass it through (should match enum value)
        if isinstance(value, str):
            return value

        # Convert to string as fallback
        return str(value)

    def process_result_value(self, value: Optional[str], dialect) -> Optional[Enum]:
        """
        Convert database string value back to Python enum object.

        Args:
            value: String value from database or None
            dialect: SQLAlchemy dialect

        Returns:
            Python enum object or None
        """
        if value is None:
            return None

        # Convert database string value back to enum object
        try:
            return self.enum_class(value)
        except ValueError:
            # If the database value doesn't match any enum value,
            # this could indicate data inconsistency
            raise ValueError(
                f"Invalid enum value '{value}' for {self.enum_class.__name__}. "
                f"Valid values are: {[e.value for e in self.enum_class]}"
            )

    def copy(self, **kwargs):
        """Create a copy of this type."""
        return PostgreSQLEnum(
            self.enum_class, name=self.name, create_type=self.create_type, **kwargs
        )

    @property
    def python_type(self):
        """Return the Python type for this column."""
        return self.enum_class

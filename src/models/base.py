"""
Base SQLAlchemy Model Module

Provides the declarative base and common model utilities.
"""

import datetime
import uuid
from typing import Any, Dict

from sqlalchemy import UUID, Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base
Base = declarative_base()


class BaseModel:
    """
    Common fields for all models.

    This mixin provides standard fields that should be included in all models:
    - id: UUID primary key
    - created_at: Creation timestamp with server-side default
    - updated_at: Update timestamp that automatically updates
    """

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


# Define serialization function separately - can be used with any model instance
def model_to_dict(model: Any) -> Dict[str, Any]:
    """
    Convert a model instance to a dictionary with serialized values.

    Args:
        model: SQLAlchemy model instance

    Returns:
        Dictionary with column names as keys and serialized values
    """
    if not hasattr(model, "__table__"):
        return {}

    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        # Convert UUID objects to strings
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Convert datetime objects to ISO format strings
        elif isinstance(value, datetime.datetime):
            value = value.isoformat()
        result[column.name] = value
    return result

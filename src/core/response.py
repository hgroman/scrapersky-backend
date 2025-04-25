"""
Core Response Module

This module provides standard response formatting functions.
"""

from typing import Any, Dict, List, Union


def standard_response(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Create a standardized response format.

    Args:
        data: The data to wrap in the standard response format

    Returns:
        A dictionary with the data wrapped in a standard format
    """
    return {"data": data}

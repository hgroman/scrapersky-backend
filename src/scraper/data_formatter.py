"""
Data formatting module for website metadata.
Handles conversion of metadata into Supabase-compatible format.
"""

from datetime import datetime, timezone
from typing import Dict, Any
import json
from ..models import SiteMetadata

def _get_model_data(model_obj) -> dict:
    """
    Attempt to extract data from a Pydantic model using model_dump() (v2) or dict() (v1).
    If the model_obj is not a Pydantic model, return it directly.
    """
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump()
    elif hasattr(model_obj, "dict"):
        return model_obj.dict()
    return model_obj

def format_website_data(url: str, metadata: SiteMetadata) -> Dict[str, Any]:
    """
    Format website metadata for Supabase insertion.
    
    Args:
        url: Website URL.
        metadata: Extracted metadata.
        
    Returns:
        Dict containing formatted data matching Supabase schema.
    """
    # Build the tech_stack dictionary
    tech_stack = {
        "is_wordpress": metadata.is_wordpress,
        "wordpress_version": metadata.wordpress_version,
        "has_elementor": metadata.has_elementor,
        "analytics": [
            id for id in [metadata.google_analytics_id, metadata.google_tag_manager_id] 
            if id is not None
        ]
    }
    
    # Use a single timestamp for both first_scan and last_scan
    current_timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "domain": str(url),
        "sitemap_url": f"{url}/sitemap.xml",
        "title": metadata.title,
        "description": metadata.description,
        "language": metadata.language,
        "tech_stack": json.dumps(tech_stack),
        "social_links": json.dumps(_get_model_data(metadata.social_links)),
        "has_cookie_notice": metadata.has_cookie_notice,
        "has_privacy_policy": metadata.has_privacy_policy,
        "has_terms_of_service": metadata.has_terms_of_service,
        "first_scan": current_timestamp,
        "last_scan": current_timestamp
    }

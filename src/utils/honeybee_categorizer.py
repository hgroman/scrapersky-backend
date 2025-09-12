import re
from urllib.parse import urlparse

from src.models.enums import PageTypeEnum


class HoneybeeCategorizer:
    """
    URL categorization system for filtering low-value pages during sitemap import.
    Uses regex patterns to identify high-value contact pages and filter out blog content.
    """
    
    # High-value page patterns with confidence scores
    R_POS = {
        "contact_root": re.compile(r"^/contact(?:-us)?/?$", re.I),
        "career_contact": re.compile(r"^/(?:career|careers|jobs?|recruit)[^/]*/?contact[^/]*/*$", re.I),
        "legal_root": re.compile(r"^/legal/(?:privacy|terms)(?:/|$)", re.I),
    }
    
    # Low-value page exclusion patterns
    R_EX = [
        re.compile(r"^/blog/.+", re.I),
        re.compile(r"^/about(?:-us)?/.+", re.I),
        re.compile(r"^/contact(?:-us)?/.+", re.I),
        re.compile(r"^/services?/.+", re.I),
        re.compile(r"\.(pdf|jpg|jpeg|png|gif|mp4|avi)$", re.I),
    ]
    
    # WordPress signal pattern for higher confidence
    R_WP = re.compile(r"/(?:wp-(?:content|admin|includes))|\?(?:^|.*)p=\d+(?:&|$)", re.I)
    
    # Confidence scores based on analysis of real data
    CONF = {
        "contact_root": 0.9,
        "career_contact": 0.7, 
        "legal_root": 0.6,
        "wp_prospect": 0.9
    }

    @staticmethod
    def _depth(path: str) -> int:
        """Calculate URL path depth by counting non-empty segments."""
        return sum(1 for s in path.split("/") if s)

    def categorize(self, url: str) -> dict:
        """
        Categorize a URL and return decision, category, confidence, and metadata.
        
        Args:
            url: Full URL to categorize
            
        Returns:
            dict: {
                "decision": "skip"|"include",
                "category": str,
                "confidence": float,
                "matched": str|None,
                "exclusions": list,
                "depth": int
            }
        """
        p = urlparse(url)
        path = p.path or "/"
        q = "?" + p.query if p.query else ""
        
        # Check exclusion patterns first
        for ex in self.R_EX:
            if ex.search(path):
                return {
                    "decision": "skip",
                    "category": PageTypeEnum.UNKNOWN,
                    "confidence": 0.0,
                    "matched": None,
                    "exclusions": ["rule_hit"],
                    "depth": self._depth(path)
                }
        
        # Check high-value patterns
        for name, rgx in self.R_POS.items():
            if rgx.match(path):
                enum_value = getattr(PageTypeEnum, name.upper())
                return {
                    "decision": "include",
                    "category": enum_value,
                    "confidence": self.CONF.get(name, 0.5),
                    "matched": name,
                    "exclusions": [],
                    "depth": self._depth(path)
                }
        
        # Check WordPress signals
        if self.R_WP.search(path + q):
            return {
                "decision": "include",
                "category": PageTypeEnum.WP_PROSPECT,
                "confidence": self.CONF["wp_prospect"],
                "matched": "wp_signal",
                "exclusions": [],
                "depth": self._depth(path)
            }
        
        # Default case - low confidence unknown page
        return {
            "decision": "include",
            "category": PageTypeEnum.UNKNOWN,
            "confidence": 0.2,
            "matched": None,
            "exclusions": [],
            "depth": self._depth(path)
        }
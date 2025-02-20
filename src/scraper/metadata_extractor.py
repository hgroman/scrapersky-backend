"""Website metadata extraction module."""
import re
import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from datetime import datetime
from ..utils.scraper_api import ScraperAPIClient

async def detect_site_metadata(url: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a website.
    
    Args:
        url: Website URL to scrape
        
    Returns:
        Dictionary containing extracted metadata
    """
    scraper = ScraperAPIClient()
    metadata = {
        "tech_stack": {},
        "contact_info": {},
        "social_links": {},
        "performance_metrics": {}
    }
    
    try:
        # Get HTML via ScraperAPI
        html = await scraper.fetch(url, render_js=True)
        if not html:
            raise ValueError('No HTML returned from ScraperAPI')
            
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Basic metadata
        metadata["title"] = soup.title.string.strip() if soup.title else None
        meta_desc = soup.find('meta', {'name': 'description'})
        metadata["description"] = meta_desc.get('content') if meta_desc else None
        
        # Language detection
        html_tag = soup.find('html')
        metadata["language"] = html_tag.get('lang', '').strip().lower() if html_tag else None
        
        # WordPress detection
        wp_content = soup.find('link', {'href': re.compile(r'/wp-content/')}) or \
                    soup.find('script', {'src': re.compile(r'/wp-content/')})
        metadata["is_wordpress"] = bool(wp_content)
        
        if metadata["is_wordpress"]:
            generator = soup.find('meta', {'name': 'generator'})
            if generator and generator.get('content'):
                wp_version = re.search(r'WordPress (\d+\.\d+\.?\d*)', generator['content'])
                metadata["wordpress_version"] = wp_version.group(1) if wp_version else None
        
        # Elementor detection
        metadata["has_elementor"] = bool(soup.find('script', {'src': re.compile(r'/elementor/')}))
        
        # Favicon detection
        favicon = soup.find('link', rel=lambda x: x and any(r in x.lower() for r in ['icon', 'shortcut icon']))
        metadata["favicon_url"] = favicon.get('href') if favicon else None
        
        # Logo detection
        logo = soup.find('img', {'class': re.compile(r'logo|brand', re.I)})
        metadata["logo_url"] = logo.get('src') if logo else None
        
        # Contact information
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        
        metadata["contact_info"]["email"] = list(set(re.findall(email_pattern, text)))
        metadata["contact_info"]["phone"] = list(set(re.findall(phone_pattern, text)))
        
        # Social media links
        social_patterns = {
            'facebook': r'facebook\.com/([^/"\s]+)',
            'twitter': r'twitter\.com/([^/"\s]+)',
            'linkedin': r'linkedin\.com/(?:company|in)/([^/"\s]+)',
            'instagram': r'instagram\.com/([^/"\s]+)',
            'youtube': r'youtube\.com/(?:user|channel|c)/([^/"\s]+)'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, html)
            if matches:
                metadata["social_links"][platform] = f"https://{platform}.com/{matches[0]}"
        
        # Technology stack detection
        tech_indicators = {
            'jquery': r'jquery.*\.js',
            'bootstrap': r'bootstrap.*\.(?:js|css)',
            'react': r'react.*\.js',
            'google_analytics': r'google-analytics.com|gtag|googletagmanager',
            'facebook_pixel': r'connect\.facebook\.net'
        }
        
        for tech, pattern in tech_indicators.items():
            if soup.find('script', {'src': re.compile(pattern, re.I)}):
                metadata["tech_stack"][tech] = True
        
        # Performance metrics
        metadata["performance_metrics"] = {
            "page_size": len(html),
            "image_count": len(soup.find_all('img')),
            "script_count": len(soup.find_all('script')),
            "css_count": len(soup.find_all('link', {'rel': 'stylesheet'}))
        }
        
        return metadata
        
    except Exception as e:
        logging.error(f"Error extracting metadata from {url}: {str(e)}")
        return None
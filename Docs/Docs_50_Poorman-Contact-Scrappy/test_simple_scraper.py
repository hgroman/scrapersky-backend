#!/usr/bin/env python3
"""
Simple scraper that ACTUALLY WORKS
No bullshit, no complex frameworks, just get the fucking email
"""

import requests
import re
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_page_simple(url):
    """Scrape a page and extract email/phone - NO BULLSHIT"""
    
    print(f"🔍 Scraping: {url}")
    
    # Headers that work (same as curl)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Make the request (disable SSL verification like curl -k)
        response = requests.get(url, headers=headers, verify=False, timeout=20, allow_redirects=True)
        response.raise_for_status()
        
        print(f"✅ HTTP {response.status_code} - Content length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract emails using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, response.text)
        
        # Extract phone numbers using regex
        phone_pattern = r'(\([0-9]{3}\)\s?[0-9]{3}-[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4}|\([0-9]{3}\)[0-9]{3}-[0-9]{4}|[0-9]{10})'
        phones = re.findall(phone_pattern, response.text)
        
        # Remove duplicates
        emails = list(set(emails))
        phones = list(set(phones))
        
        print(f"📧 Found {len(emails)} emails: {emails}")
        print(f"📞 Found {len(phones)} phones: {phones}")
        
        return {
            'success': True,
            'emails': emails,
            'phones': phones,
            'content_length': len(response.text),
            'status_code': response.status_code
        }
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return {
            'success': False,
            'error': str(e),
            'emails': [],
            'phones': []
        }

def main():
    """Test the scraper on our target page"""
    
    print("🚀 SIMPLE SCRAPER TEST")
    print("=" * 50)
    
    # Test URL that we know has contact info
    test_url = "https://acuitylaservision.com/our-laser-vision-correction-surgeon/"
    
    result = scrape_page_simple(test_url)
    
    print("\n" + "=" * 50)
    if result['success']:
        print("🎯 SUCCESS!")
        print(f"   Emails: {result['emails']}")
        print(f"   Phones: {result['phones']}")
        
        # Check if we found the expected contact
        expected_email = "svale@acuitylaservision.com"
        expected_phone = "1661396306"
        
        if expected_email in result['emails']:
            print(f"✅ Found expected email: {expected_email}")
        else:
            print(f"❌ Expected email not found: {expected_email}")
            
        if expected_phone in result['phones']:
            print(f"✅ Found expected phone: {expected_phone}")
        else:
            print(f"❌ Expected phone not found: {expected_phone}")
            
    else:
        print("💥 FAILED!")
        print(f"   Error: {result['error']}")

if __name__ == "__main__":
    main()

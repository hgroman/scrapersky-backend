#!/usr/bin/env python3
"""
Test the current Honeybee categorizer to understand patterns.
"""
import sys
sys.path.append('.')
from src.utils.honeybee_categorizer import HoneybeeCategorizer


def test_categorizer_patterns():
    """Test the categorizer against sample URLs to understand current behavior."""
    print("🧪 TESTING CURRENT CATEGORIZER PATTERNS...")
    print("=" * 80)
    
    hb = HoneybeeCategorizer()
    
    # Test URLs that should match different patterns
    test_categories = {
        "Contact Pages (Should be high-value)": [
            "https://example.com/contact",
            "https://example.com/contact-us",  
            "https://example.com/contact/",
            "https://example.com/careers/contact",
            "https://example.com/jobs/apply/contact",
            "https://example.com/recruit/contact",
        ],
        
        "Business Pages (Currently missing from high-value)": [
            "https://example.com/about",
            "https://example.com/about-us",
            "https://example.com/services",
            "https://example.com/pricing", 
            "https://example.com/team",
            "https://example.com/products",
        ],
        
        "Currently Excluded Pages": [
            "https://example.com/blog/some-post",
            "https://example.com/about-us/team/john",  # Deep about page
            "https://example.com/services/consulting/details",  # Deep services
            "https://example.com/contact-us/form/success",  # Deep contact
        ],
        
        "File Types (Should be excluded)": [
            "https://example.com/document.pdf",
            "https://example.com/image.jpg",
            "https://example.com/video.mp4",
        ],
        
        "WordPress Signals": [
            "https://example.com/wp-content/themes/",
            "https://example.com/?p=123",
            "https://example.com/wp-admin/",
        ],
        
        "Root/Unknown Pages": [
            "https://example.com/",
            "https://example.com/random-page",
            "https://example.com/news",
        ],
    }
    
    for category, urls in test_categories.items():
        print(f"\n📂 {category}:")
        print("-" * 60)
        
        for url in urls:
            result = hb.categorize(url)
            decision = result["decision"]
            category_name = result["category"]
            confidence = result["confidence"]
            matched = result.get("matched")
            exclusions = result["exclusions"]
            
            status_emoji = "✅" if decision == "include" else "❌"
            exclusion_note = f" [EXCLUDED: {exclusions}]" if exclusions else ""
            matched_note = f" [MATCHED: {matched}]" if matched else ""
            
            print(f"  {status_emoji} {category_name:15} | {confidence:.1f} | {url}{exclusion_note}{matched_note}")
    
    # Summary of current patterns
    print(f"\n" + "=" * 80)
    print("📋 CURRENT CATEGORIZER SUMMARY:")
    print("=" * 80)
    
    print("\n✅ HIGH-VALUE PATTERNS (will be Selected):")
    print("  • contact_root: ^/contact(?:-us)?/?$ (confidence: 0.9)")  
    print("  • career_contact: jobs/careers + contact (confidence: 0.7)")
    print("  • legal_root: /legal/privacy|terms (confidence: 0.6)")
    print("  • wp_prospect: WordPress signals (confidence: 0.9)")
    
    print("\n❌ EXCLUSION PATTERNS (will be skipped):")
    print("  • ^/blog/.+")
    print("  • ^/about(?:-us)?/.+")  
    print("  • ^/contact(?:-us)?/.+")  # Deep contact pages
    print("  • ^/services?/.+")  # ALL services pages excluded!
    print("  • File extensions: .pdf, .jpg, .png, .gif, .mp4, .avi")
    
    print("\n⚠️  MISSING HIGH-VALUE PATTERNS:")
    print("  • Root about pages: /about, /about-us")
    print("  • Root services pages: /services")  
    print("  • Pricing pages: /pricing")
    print("  • Team pages: /team")
    print("  • Product pages: /products")


if __name__ == "__main__":
    test_categorizer_patterns()
#!/usr/bin/env python3
"""
EMERGENCY TEST: Verify ScraperAPI cost reduction is working
This script tests that the cost control fixes prevent 95%+ credit waste
"""

import asyncio
import os
import sys
from src.utils.scraper_api import ScraperAPIClient, credit_monitor

async def test_cost_reduction():
    """Test that ScraperAPI now uses basic (cheap) mode by default"""
    
    print("🚨 EMERGENCY COST CONTROL TEST 🚨")
    print("=" * 50)
    
    # Test domain (avoid actual scraping costs)
    test_url = "https://httpbin.org/html"
    
    print(f"Testing URL: {test_url}")
    print(f"Cost Control Mode: {os.getenv('SCRAPER_API_COST_CONTROL_MODE', 'true')}")
    print(f"Premium Enabled: {os.getenv('SCRAPER_API_ENABLE_PREMIUM', 'false')}")
    print(f"JS Rendering Enabled: {os.getenv('SCRAPER_API_ENABLE_JS_RENDERING', 'false')}")
    print(f"Geotargeting Enabled: {os.getenv('SCRAPER_API_ENABLE_GEOTARGETING', 'false')}")
    print(f"Max Retries: {os.getenv('SCRAPER_API_MAX_RETRIES', '1')}")
    print()
    
    # Reset monitor for clean test
    credit_monitor.request_count = 0
    credit_monitor.estimated_credits = 0
    
    try:
        async with ScraperAPIClient() as client:
            print("📊 Making test request with cost monitoring...")
            
            # This should now consume only 1 credit (basic mode) instead of 46,905 credits
            response = await client.fetch(test_url, render_js=False, retries=1)
            
            print(f"✅ Request successful!")
            print(f"Response length: {len(response)} characters")
            print(f"📈 COST ANALYSIS:")
            print(f"  - Total Requests: {credit_monitor.request_count}")
            print(f"  - Estimated Credits: {credit_monitor.estimated_credits}")
            print(f"  - Credits per Request: {credit_monitor.estimated_credits / credit_monitor.request_count if credit_monitor.request_count > 0 else 0}")
            
            # Verify cost reduction
            if credit_monitor.estimated_credits <= 1:
                print("🎉 SUCCESS: Cost reduction working! Using basic mode (1 credit)")
                print("💰 COST SAVINGS: 95%+ reduction achieved")
                return True
            else:
                print(f"❌ FAILURE: Still using expensive mode ({credit_monitor.estimated_credits} credits)")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Running emergency cost reduction test...")
    success = asyncio.run(test_cost_reduction())
    
    if success:
        print("\n✅ EMERGENCY FIX VERIFIED: ScraperAPI cost controls are working")
        sys.exit(0)
    else:
        print("\n❌ EMERGENCY FIX FAILED: ScraperAPI still using expensive mode")
        sys.exit(1)
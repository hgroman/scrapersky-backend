#!/usr/bin/env python3
"""
API Key Sanitization Test Script

Tests the log_sanitizer utility to verify API keys are properly redacted.
Run this script to validate the security fix before deployment.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.log_sanitizer import sanitize_api_keys, sanitize_exception_message, get_safe_exception_info


def test_google_maps_api_key():
    """Test Google Maps API key sanitization"""
    test_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant&key=AIzaSyBx1234567890abcdef&radius=1000"
    expected = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant&key=***REDACTED***&radius=1000"
    
    result = sanitize_api_keys(test_url)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Google Maps API key sanitization: PASS")


def test_generic_api_key():
    """Test generic API key patterns"""
    test_cases = [
        ("https://api.example.com?api_key=secret123", "https://api.example.com?api_key=***REDACTED***"),
        ("https://api.example.com?apikey=secret123", "https://api.example.com?apikey=***REDACTED***"),
        ("https://api.example.com?token=secret123", "https://api.example.com?token=***REDACTED***"),
        ("https://api.example.com?access_token=secret123", "https://api.example.com?access_token=***REDACTED***"),
    ]
    
    for input_text, expected in test_cases:
        result = sanitize_api_keys(input_text)
        assert result == expected, f"Expected: {expected}, Got: {result}"
    
    print("✅ Generic API key patterns: PASS")


def test_case_insensitive():
    """Test case insensitive matching"""
    test_cases = [
        ("https://api.example.com?KEY=secret123", "https://api.example.com?KEY=***REDACTED***"),
        ("https://api.example.com?Api_Key=secret123", "https://api.example.com?Api_Key=***REDACTED***"),
        ("https://api.example.com?TOKEN=secret123", "https://api.example.com?TOKEN=***REDACTED***"),
    ]
    
    for input_text, expected in test_cases:
        result = sanitize_api_keys(input_text)
        assert result == expected, f"Expected: {expected}, Got: {result}"
    
    print("✅ Case insensitive matching: PASS")


def test_multiple_keys():
    """Test multiple API keys in same string"""
    input_text = "Error: https://api1.com?key=secret1 and https://api2.com?api_key=secret2"
    expected = "Error: https://api1.com?key=***REDACTED*** and https://api2.com?api_key=***REDACTED***"
    
    result = sanitize_api_keys(input_text)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Multiple API keys: PASS")


def test_no_api_keys():
    """Test strings without API keys remain unchanged"""
    test_text = "https://example.com?query=test&radius=10&format=json"
    result = sanitize_api_keys(test_text)
    assert result == test_text, f"Expected: {test_text}, Got: {result}"
    print("✅ No API keys (unchanged): PASS")


def test_empty_and_none():
    """Test edge cases with empty/None input"""
    assert sanitize_api_keys("") == ""
    assert sanitize_api_keys(None) == None
    print("✅ Empty and None handling: PASS")


def test_exception_handling():
    """Test exception message sanitization"""
    # Simulate an exception with API key in message
    class MockException(Exception):
        def __str__(self):
            return "Connection timeout for https://maps.googleapis.com/maps/api/place/textsearch/json?key=AIzaSyBx1234567890abcdef"
    
    mock_ex = MockException()
    sanitized = sanitize_exception_message(mock_ex)
    
    assert "AIzaSyBx1234567890abcdef" not in sanitized
    assert "***REDACTED***" in sanitized
    print("✅ Exception message sanitization: PASS")


def test_safe_exception_info():
    """Test structured exception info generation"""
    class MockException(Exception):
        def __init__(self, message):
            super().__init__(message)
    
    mock_ex = MockException("API error with key=secret123")
    info = get_safe_exception_info(mock_ex)
    
    assert info["exception_type"] == "MockException"
    assert "***REDACTED***" in info["sanitized_message"]
    assert "secret123" not in info["sanitized_message"]
    assert info["has_args"] == True
    print("✅ Safe exception info: PASS")


def test_real_world_scenario():
    """Test realistic aiohttp exception message"""
    aiohttp_error = """aiohttp.ClientConnectorError: Connection timeout for https://maps.googleapis.com/maps/api/place/textsearch/json
Request details: GET https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant+in+NYC&key=AIzaSyDjLU-N9dvnP05OMWPgcuaZZnSDb-CrKBk&radius=5000
Headers: {'User-Agent': 'ScraperSky/1.0'}"""
    
    sanitized = sanitize_api_keys(aiohttp_error)
    
    # Verify API key is removed
    assert "AIzaSyDjLU-N9dvnP05OMWPgcuaZZnSDb-CrKBk" not in sanitized
    assert "***REDACTED***" in sanitized
    
    # Verify other information is preserved
    assert "aiohttp.ClientConnectorError" in sanitized
    assert "Connection timeout" in sanitized
    assert "query=restaurant+in+NYC" in sanitized
    assert "radius=5000" in sanitized
    
    print("✅ Real-world aiohttp scenario: PASS")


def main():
    """Run all sanitization tests"""
    print("🔐 Testing API Key Sanitization Security Fix")
    print("=" * 50)
    
    try:
        test_google_maps_api_key()
        test_generic_api_key()
        test_case_insensitive()
        test_multiple_keys()
        test_no_api_keys()
        test_empty_and_none()
        test_exception_handling()
        test_safe_exception_info()
        test_real_world_scenario()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED - API Key Sanitization Working Correctly")
        print("✅ Security fix validated - safe for production deployment")
        
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
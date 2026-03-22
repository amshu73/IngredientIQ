#!/usr/bin/env python3
"""Test script to verify barcode fallback fix"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_barcode(barcode, description):
    """Test a single barcode"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Barcode: {barcode}")
    print('='*60)
    
    payload = {
        "barcode": barcode,
        "user_profiles": []
    }
    
    try:
        print("Making request...")
        response = requests.post(
            f"{BASE_URL}/scan/barcode",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS:")
            print(f"   Product: {data.get('product_name', 'N/A')}")
            print(f"   Grade: {data.get('grade', 'N/A')}")
            print(f"   Overall Score: {data.get('overall_score', 'N/A')}")
            print(f"   Ingredients: {data.get('ingredient_count', 0)}")
            print(f"   Recommendation: {data.get('recommendation', 'N/A')[:80]}...")
            return True
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    print("Testing barcode fallback fix...")
    print(f"Base URL: {BASE_URL}")
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is ready!")
                break
        except:
            print(f"   Attempt {i+1}/10 - server not yet responsive...")
            time.sleep(1)
    
    # Test cases
    tests = [
        ("5449000000996", "Coca-Cola (should have real data)"),
        ("5449000112019", "Pepsi (may have demo data fallback)"),
        ("5000159511834", "Random barcode (should have demo data fallback)"),
        ("1234567890123", "Invalid barcode (should have demo data fallback)"),
    ]
    
    results = []
    for barcode, desc in tests:
        result = test_barcode(barcode, desc)
        results.append((desc, result))
        time.sleep(1)  # Rate limit
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for desc, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {desc}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

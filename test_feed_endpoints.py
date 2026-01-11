"""
Test script to verify all feed endpoints work correctly.

This tests:
- PART 1: Basic feed functionality (explore, following)
- PART 2: Metadata extras (is_new, content_tone, time_context, etc.)
- PART 3: Daily reflection endpoint

Run this after starting the FastAPI server.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# You'll need a valid JWT token - get it from /auth/login
# Replace this with your actual token after logging in
TOKEN = None


def test_with_auth(endpoint, method="GET", data=None, params=None):
    """Helper function to make authenticated requests."""
    if not TOKEN:
        print("❌ No TOKEN set. Please login first and set TOKEN variable.")
        return None
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params)
    elif method == "POST":
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
    
    return response


def print_response(title, response):
    """Pretty print response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success")
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print("❌ Failed")
        print(response.text)


def run_tests():
    """Run all feed endpoint tests."""
    
    print("\n" + "="*60)
    print("FAITHCONNECT FEED SYSTEM TEST")
    print("="*60)
    
    if not TOKEN:
        print("\n⚠️  To run these tests:")
        print("1. Start the FastAPI server: fastapi dev app/main.py")
        print("2. Login using /auth/login endpoint to get a JWT token")
        print("3. Set TOKEN variable in this script")
        print("4. Run this script: python test_feed_endpoints.py")
        return
    
    # Test 1: Explore Feed (PART 1 + PART 2)
    print("\n\n📋 TEST 1: Explore Feed (with metadata)")
    response = test_with_auth("/feed/explore", params={"page": 1, "page_size": 5})
    if response:
        print_response("Explore Feed", response)
        
        # Verify PART 2 metadata fields
        if response.status_code == 200:
            data = response.json()
            if data["posts"]:
                first_post = data["posts"][0]
                print("\n🔍 Checking PART 2 metadata fields:")
                print(f"  - is_daily_reflection: {first_post.get('is_daily_reflection')}")
                print(f"  - content_tone: {first_post.get('content_tone')}")
                print(f"  - time_context: {first_post.get('time_context')}")
                print(f"  - is_new: {first_post.get('is_new')}")
                print(f"  - feed_reason: {first_post.get('feed_reason')}")
    
    # Test 2: Explore Feed with Mode Parameter
    print("\n\n📋 TEST 2: Explore Feed with mode=inspiration")
    response = test_with_auth("/feed/explore", params={"page": 1, "page_size": 3, "mode": "inspiration"})
    if response:
        print_response("Explore Feed (Inspiration Mode)", response)
    
    # Test 3: Following Feed (worshiper only)
    print("\n\n📋 TEST 3: Following Feed (worshiper only)")
    response = test_with_auth("/feed/following", params={"page": 1, "page_size": 5})
    if response:
        print_response("Following Feed", response)
    
    # Test 4: Daily Reflection (PART 3)
    print("\n\n📋 TEST 4: Daily Reflection ⭐ NEW")
    response = test_with_auth("/feed/daily-reflection")
    if response:
        print_response("Daily Reflection", response)
        
        if response.status_code == 200:
            data = response.json()
            print("\n🔍 Daily Reflection Details:")
            print(f"  - Date: {data.get('date')}")
            print(f"  - Message: {data.get('message')}")
            if data.get('post'):
                print(f"  - Post ID: {data['post']['id']}")
                print(f"  - Leader: {data['post']['leader']['name']}")
                print(f"  - Content preview: {data['post']['content_text'][:100]}...")
                print(f"  - feed_reason: {data['post']['feed_reason']}")
            else:
                print("  - No post available today")
    
    print("\n\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)


def quick_login_test():
    """Helper to test if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"   Health check: {response.json()}")
            return True
        else:
            print("❌ Server responded but with error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure FastAPI is running at {BASE_URL}")
        return False


if __name__ == "__main__":
    print("FaithConnect Feed System Test Suite")
    print("=" * 60)
    
    # Check server health
    if quick_login_test():
        run_tests()
    else:
        print("\n⚠️  Please start the FastAPI server first:")
        print("   cd c:\\FaithConnect\\backend")
        print("   .\\venv\\Scripts\\Activate.ps1")
        print("   fastapi dev app/main.py")

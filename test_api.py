#!/usr/bin/env python

import requests
import json

TOKEN = "0768e2ec-4d0e-42b0-bb51-eec0c5943f3a"
COURSE_INSTANCE_ID = "206336"
BASE_URL = "https://us.prairielearn.com/pl/api/v1"

headers = {"Private-Token": TOKEN}

print("Testing PrairieLearn API access...")
print(f"Token: {TOKEN[:8]}...{TOKEN[-8:]}")
print(f"Course Instance ID: {COURSE_INSTANCE_ID}")
print()

# Test 1: Try to access the course instance
print("=" * 60)
print("Test 1: Getting course instance info")
print("=" * 60)
url = f"{BASE_URL}/course_instances/{COURSE_INSTANCE_ID}"
print(f"URL: {url}")
print()

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print()
print(f"Response Body:")
print(response.text[:1000])  # First 1000 characters
print()

if response.status_code == 403:
    print("⚠️  403 Forbidden Error - Possible causes:")
    print("   1. Token doesn't have access to this course instance")
    print("   2. Token is invalid or expired")
    print("   3. Course instance ID is incorrect")
    print()
    print("Please verify:")
    print("   - Your token is correct (check PrairieLearn Settings)")
    print("   - You have instructor access to this course instance")
    print("   - The course instance ID matches the URL in PrairieLearn")
elif response.status_code == 200:
    print("✓ Success! Your token works.")
    print()
    try:
        data = response.json()
        print("Course Instance Data:")
        print(json.dumps(data, indent=2))
    except:
        print("Could not parse JSON response")
else:
    print(f"Unexpected status code: {response.status_code}")

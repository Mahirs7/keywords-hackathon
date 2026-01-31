#!/usr/bin/env python

import requests
import json

TOKEN = "0768e2ec-4d0e-42b0-bb51-eec0c5943f3a"
COURSE_INSTANCE_ID = "206336"
BASE_URL = "https://us.prairielearn.com/pl/api/v1"

headers = {"Private-Token": TOKEN}

print("Testing PrairieLearn API - Assessments Endpoint")
print("=" * 60)
print()

# Test 1: List all assessments for the course instance
print("Test 1: Listing all assessments")
print("-" * 60)
url = f"{BASE_URL}/course_instances/{COURSE_INSTANCE_ID}/assessments"
print(f"URL: {url}")
print(f"Method: GET")
print()

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print()

if response.status_code == 200:
    print("✓ Success! Got assessments list")
    print()
    try:
        data = response.json()
        print(f"Number of assessments: {len(data)}")
        print()
        print("Assessments:")
        print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
        
        # If we have assessments, try to get the first one
        if data and len(data) > 0:
            assessment_id = data[0].get('assessment_id')
            if assessment_id:
                print()
                print("=" * 60)
                print(f"Test 2: Getting specific assessment (ID: {assessment_id})")
                print("-" * 60)
                url2 = f"{BASE_URL}/course_instances/{COURSE_INSTANCE_ID}/assessments/{assessment_id}"
                print(f"URL: {url2}")
                print()
                
                response2 = requests.get(url2, headers=headers)
                print(f"Status Code: {response2.status_code}")
                print()
                
                if response2.status_code == 200:
                    print("✓ Success! Got specific assessment")
                    print()
                    data2 = response2.json()
                    print(json.dumps(data2, indent=2)[:2000])
                else:
                    print(f"❌ Error: {response2.status_code}")
                    print(response2.text[:500])
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(response.text[:1000])
elif response.status_code == 403:
    print("❌ 403 Forbidden - No access to this course instance")
    print(response.text)
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])

#!/usr/bin/env python3
"""
Test script to verify the get_user_details API endpoint
"""

import requests
import json

def test_user_details_api():
    """Test the user details API endpoint"""
    
    # Test with student ID 3 (our test student)
    student_id = 3
    url = f"http://127.0.0.1:5003/admin/get_user_details/{student_id}"
    
    try:
        # Note: This might not work without authentication session, but let's try
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == '__main__':
    test_user_details_api()

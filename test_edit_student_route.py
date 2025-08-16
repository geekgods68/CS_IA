#!/usr/bin/env python3
"""
Test the edit_student route using Flask test client
"""

import sys
import os
sys.path.append('.')

# Import the Flask app
from app import app

def test_edit_student_route():
    """Test the edit_student route with authentication"""
    try:
        with app.test_client() as client:
            # First login as admin
            login_response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            
            if login_response.status_code == 200:
                print("✅ Login successful")
                
                # Now test the edit_student route
                response = client.get('/admin/edit_student/14')
                print(f"Edit student route status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Edit student page loaded successfully!")
                    print(f"Response content length: {len(response.data)} bytes")
                    
                    # Check if the page contains expected content
                    content = response.data.decode('utf-8')
                    if 'Edit Student: test_student' in content:
                        print("✅ Page contains correct student name")
                    else:
                        print("❌ Page does not contain expected student name")
                    
                    if 'Subject Interests' in content:
                        print("✅ Page contains subject interests section")
                    else:
                        print("❌ Page missing subject interests section")
                        
                    return True
                else:
                    print(f"❌ Edit student route failed with status: {response.status_code}")
                    print(f"Response: {response.data.decode('utf-8')[:500]}...")
                    return False
            else:
                print(f"❌ Login failed with status: {login_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edit_student_route()
    sys.exit(0 if success else 1)

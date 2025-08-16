#!/usr/bin/env python3

import requests
import sqlite3

def test_student_login():
    """Test student login functionality"""
    base_url = "http://127.0.0.1:5003"
    
    # Get the database connection
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Check if test student exists
    cur.execute("SELECT id, username, email FROM users WHERE role = 'student' LIMIT 1")
    student = cur.fetchone()
    
    if not student:
        print("❌ No student found in database")
        conn.close()
        return False
    
    student_id, username, email = student
    print(f"✅ Found test student: {username} (ID: {student_id}, Email: {email})")
    
    # Test login with session
    session = requests.Session()
    
    # First get the login page
    login_response = session.get(f"{base_url}/login")
    print(f"Login page status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Could not access login page")
        conn.close()
        return False
    
    # Login with student credentials
    login_data = {
        'username': username,
        'password': 'student123'  # Correct test password
    }
    
    post_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"Login POST status: {post_response.status_code}")
    
    if post_response.status_code == 302:
        print("✅ Login redirect successful")
        # Check where it redirected
        location = post_response.headers.get('Location', '')
        print(f"Redirect location: {location}")
        
        # Follow the redirect to student dashboard
        dashboard_response = session.get(f"{base_url}/student/site")
        print(f"Student dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ Student dashboard accessible")
            return True
        else:
            print(f"❌ Student dashboard error: {dashboard_response.status_code}")
            print(dashboard_response.text[:500])
            return False
    else:
        print(f"❌ Login failed with status: {post_response.status_code}")
        print(post_response.text[:500])
        return False
    
    conn.close()

if __name__ == '__main__':
    test_student_login()

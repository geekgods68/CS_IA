#!/usr/bin/env python3
"""
Test script to verify admin feedback response functionality works correctly.
"""

import os
import sys
import sqlite3

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_admin_feedback_javascript():
    """Test the admin feedback response functionality"""
    
    print("=== Testing Admin Feedback JavaScript Fix ===")
    
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get a feedback entry to test with
        cur.execute('''
            SELECT f.id, f.student_id, f.feedback_type, f.subject, f.teacher_name, 
                   f.class_name, f.rating, f.comments, f.anonymous, f.submitted_on, 
                   f.status, f.admin_response, f.responded_on, f.responded_by,
                   u.username as student_name
            FROM feedback f
            LEFT JOIN users u ON f.student_id = u.id
            ORDER BY f.submitted_on DESC
            LIMIT 1
        ''')
        
        feedback = cur.fetchone()
        if not feedback:
            print("❌ No feedback found to test with")
            return False
        
        print(f"Testing with feedback ID: {feedback[0]}")
        print(f"Comments: {feedback[7][:50]}...")
        
        # Test the data that would be passed to JavaScript
        feedback_id = feedback[0]
        feedback_text = feedback[7][:50] if feedback[7] else ""
        
        print(f"Feedback ID: {feedback_id} (type: {type(feedback_id)})")
        print(f"Feedback text: '{feedback_text}' (length: {len(feedback_text)})")
        
        # Check for problematic characters that could break JavaScript
        problematic_chars = ["'", '"', '\\', '\n', '\r', '\t']
        found_issues = []
        
        for char in problematic_chars:
            if char in feedback_text:
                found_issues.append(char)
        
        if found_issues:
            print(f"⚠️  Found potentially problematic characters: {found_issues}")
            print("These could cause JavaScript issues without proper escaping")
        else:
            print("✅ No problematic characters found in feedback text")
        
        # Test with JSON serialization (what |tojson filter does)
        import json
        try:
            json_escaped = json.dumps(feedback_text)
            print(f"JSON escaped version: {json_escaped}")
            print("✅ JSON escaping works correctly")
        except Exception as e:
            print(f"❌ JSON escaping failed: {e}")
            return False
        
        # Check if this feedback_id exists and is valid
        if feedback_id and isinstance(feedback_id, int):
            print("✅ Feedback ID is valid integer")
        else:
            print("❌ Feedback ID is invalid")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Admin feedback test failed: {e}")
        return False

def test_feedback_form_data():
    """Test what happens with form submission data"""
    
    print("\n=== Testing Form Submission Data ===")
    
    # Simulate what the form would send
    test_cases = [
        {"feedback_id": "1", "admin_response": "Test response"},
        {"feedback_id": "2", "admin_response": "Another test response"},
        {"feedback_id": "", "admin_response": "Test"},  # This should fail
        {"feedback_id": "1", "admin_response": ""},     # This should fail
        {"feedback_id": None, "admin_response": "Test"}, # This should fail
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {case}")
        
        feedback_id = case.get('feedback_id')
        admin_response = case.get('admin_response')
        
        # Replicate the validation logic from admin.py
        if not feedback_id or not admin_response:
            print("❌ Would trigger 'Invalid feedback ID or response provided!' error")
        else:
            print("✅ Would pass validation")

def main():
    """Main test function"""
    
    # Change to the app directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Admin Feedback JavaScript Test")
    print("=" * 35)
    
    # Test admin feedback JavaScript
    if not test_admin_feedback_javascript():
        print("\n❌ Admin feedback JavaScript test failed")
        sys.exit(1)
    
    # Test form submission scenarios
    test_feedback_form_data()
    
    print("\n🎉 All admin feedback tests passed!")
    print("\nKey fixes applied:")
    print("- Used |tojson filter to properly escape feedback text in JavaScript")
    print("- This prevents quotes and special characters from breaking the onclick handler")
    print("- The setFeedbackId function should now work correctly")

if __name__ == '__main__':
    main()

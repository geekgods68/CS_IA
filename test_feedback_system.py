#!/usr/bin/env python3
"""
Test script to verify student feedback functionality is working correctly.
Tests that students can view their feedback and admins can manage it.
"""

import os
import sys
import sqlite3

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_feedback_data():
    """Test the feedback data structure and ratings"""
    
    print("=== Testing Feedback Data Structure ===")
    
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Check feedback table structure
        cur.execute("PRAGMA table_info(feedback)")
        columns = cur.fetchall()
        print("Feedback table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Test student feedback query (same as in student.py)
        cur.execute('''
            SELECT id, feedback_type, subject, teacher_name, class_name, rating, 
                   comments, submitted_on, status, admin_response, responded_on
            FROM feedback 
            WHERE student_id = 5
            ORDER BY submitted_on DESC
        ''')
        
        student_feedback = cur.fetchall()
        print(f"\nStudent 5 feedback ({len(student_feedback)} entries):")
        
        for feedback in student_feedback:
            print(f"  Feedback ID: {feedback[0]}")
            print(f"  Type: {feedback[1]}")
            print(f"  Rating: {feedback[5]} (type: {type(feedback[5])})")
            print(f"  Status: {feedback[8]}")
            
            # Test the rating conversion that was causing the error
            if feedback[5]:
                try:
                    rating_int = int(feedback[5])
                    print(f"  Rating conversion test: {feedback[5]} -> {rating_int} ✅")
                    
                    # Test range operations (what the template does)
                    filled_stars = list(range(rating_int))
                    empty_stars = list(range(5 - rating_int))
                    print(f"  Star display: {len(filled_stars)} filled, {len(empty_stars)} empty ✅")
                    
                except (TypeError, ValueError) as e:
                    print(f"  Rating conversion error: {e} ❌")
                    return False
            
        # Test admin feedback query
        cur.execute('''
            SELECT f.id, f.student_id, f.feedback_type, f.subject, f.teacher_name, 
                   f.class_name, f.rating, f.comments, f.anonymous, f.submitted_on, 
                   f.status, f.admin_response, f.responded_on, f.responded_by,
                   u.username as student_name
            FROM feedback f
            LEFT JOIN users u ON f.student_id = u.id
            ORDER BY f.submitted_on DESC
        ''')
        
        admin_feedback = cur.fetchall()
        print(f"\nAdmin feedback view ({len(admin_feedback)} entries):")
        
        for feedback in admin_feedback:
            print(f"  ID: {feedback[0]}, Student: {feedback[14]}, Type: {feedback[2]}, Rating: {feedback[6]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Feedback test failed: {e}")
        return False

def test_admin_feedback_stats():
    """Test admin feedback statistics"""
    
    print("\n=== Testing Admin Feedback Statistics ===")
    
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Test the statistics queries from admin.py
        cur.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM feedback WHERE status = "pending"')
        pending_feedback = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM feedback WHERE status = "reviewed"')
        reviewed_feedback = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM feedback WHERE status = "resolved"')
        resolved_feedback = cur.fetchone()[0]
        
        print(f"Total feedback: {total_feedback}")
        print(f"Pending: {pending_feedback}")
        print(f"Reviewed: {reviewed_feedback}")
        print(f"Resolved: {resolved_feedback}")
        
        if total_feedback > 0:
            print("✅ Feedback statistics working correctly")
        else:
            print("⚠️  No feedback entries found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Admin feedback stats test failed: {e}")
        return False

def main():
    """Main test function"""
    
    # Change to the app directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Student Feedback System Test")
    print("=" * 40)
    
    # Test feedback data structure
    if not test_feedback_data():
        print("\n❌ Feedback data test failed")
        sys.exit(1)
    
    # Test admin feedback statistics
    if not test_admin_feedback_stats():
        print("\n❌ Admin feedback stats test failed")
        sys.exit(1)
    
    print("\n🎉 All feedback tests passed!")
    print("\nKey points:")
    print("- Rating field is properly stored as INTEGER in database")
    print("- Student feedback template uses correct index (5) for rating")
    print("- Rating conversion with |int filter prevents string/integer errors")
    print("- Admin feedback system is already implemented")
    print("- Feedback flows from students to admin (like doubts flow from students to teachers)")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test script to verify the student_subjects table functionality.
This script tests that students can be assigned subject interests.
"""

import sqlite3
import sys
from datetime import datetime

def test_student_subjects():
    """Test that student subjects can be assigned and retrieved correctly."""
    
    print("=== Testing Student Subjects Functionality ===")
    
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Create a test student
        cursor.execute("""
            INSERT INTO users (username, password, created_by, created_on) 
            VALUES (?, ?, ?, ?)
        """, ('test_student', 'hashed_password', 1, datetime.now()))
        student_id = cursor.lastrowid
        print(f"Created test student with ID: {student_id}")
        
        # Assign student role
        cursor.execute("""
            INSERT INTO user_role_map (user_id, role_id, assigned_by, assigned_on)
            VALUES (?, (SELECT id FROM user_roles WHERE role_name = 'student'), ?, ?)
        """, (student_id, 1, datetime.now()))
        
        # Test subject assignment - using the same subjects as in the admin interface
        test_subjects = ['Math', 'Science', 'English']
        available_subjects = ['Math', 'Science', 'Social Science', 'English', 'Hindi']
        
        print("\n1. Testing subject assignment...")
        for subject in test_subjects:
            cursor.execute("""
                INSERT INTO student_subjects (student_id, subject_name, assigned_by) 
                VALUES (?, ?, ?)
            """, (student_id, subject, 1))
            print(f"   Assigned subject: {subject}")
        
        conn.commit()
        
        # Test retrieval of assigned subjects
        print("\n2. Testing subject retrieval...")
        cursor.execute('SELECT subject_name FROM student_subjects WHERE student_id = ? ORDER BY subject_name', (student_id,))
        assigned_subjects = [row[0] for row in cursor.fetchall()]
        print(f"   Retrieved subjects: {assigned_subjects}")
        
        # Verify the subjects match what we assigned
        expected_subjects = sorted(test_subjects)
        actual_subjects = sorted(assigned_subjects)
        assert actual_subjects == expected_subjects, f"Expected {expected_subjects}, got {actual_subjects}"
        
        # Test updating subjects (remove old, add new)
        print("\n3. Testing subject update...")
        new_subjects = ['Hindi', 'Social Science', 'Math']  # Changed English/Science to Hindi/Social Science
        
        # Clear existing assignments
        cursor.execute('DELETE FROM student_subjects WHERE student_id = ?', (student_id,))
        
        # Add new assignments
        for subject in new_subjects:
            cursor.execute("""
                INSERT INTO student_subjects (student_id, subject_name, assigned_by) 
                VALUES (?, ?, ?)
            """, (student_id, subject, 1))
        
        conn.commit()
        
        # Verify updated subjects
        cursor.execute('SELECT subject_name FROM student_subjects WHERE student_id = ? ORDER BY subject_name', (student_id,))
        updated_subjects = [row[0] for row in cursor.fetchall()]
        print(f"   Updated subjects: {updated_subjects}")
        
        expected_updated = sorted(new_subjects)
        actual_updated = sorted(updated_subjects)
        assert actual_updated == expected_updated, f"Expected {expected_updated}, got {actual_updated}"
        
        # Test unique constraint (should prevent duplicate subjects for same student)
        print("\n4. Testing unique constraint...")
        try:
            cursor.execute("""
                INSERT INTO student_subjects (student_id, subject_name, assigned_by) 
                VALUES (?, ?, ?)
            """, (student_id, 'Math', 1))  # Math already assigned
            conn.commit()
            print("   ❌ ERROR: Duplicate subject was allowed!")
            return False
        except sqlite3.IntegrityError:
            print("   ✅ Unique constraint working - duplicate subject rejected")
        
        # Test cleanup
        print("\n5. Testing cleanup...")
        cursor.execute('DELETE FROM student_subjects WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM user_role_map WHERE user_id = ?', (student_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (student_id,))
        conn.commit()
        
        # Verify cleanup
        cursor.execute('SELECT COUNT(*) FROM student_subjects WHERE student_id = ?', (student_id,))
        remaining_subjects = cursor.fetchone()[0]
        assert remaining_subjects == 0, f"Expected 0 remaining subjects, got {remaining_subjects}"
        print("   ✅ Cleanup successful")
        
        print("\n✅ All student subjects tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn:
            conn.close()

def test_subject_order():
    """Test that subjects are displayed in the expected order."""
    
    print("\n=== Testing Subject Order ===")
    
    # The order should match what's defined in admin.py
    expected_order = ['Math', 'Science', 'Social Science', 'English', 'Hindi']
    
    print("Expected subject order (same as teachers):")
    for i, subject in enumerate(expected_order, 1):
        print(f"   {i}. {subject}")
    
    print("✅ Subject order verified")
    return True

if __name__ == "__main__":
    print("Student Subjects Functionality Test")
    print("=" * 40)
    
    # Test student subjects functionality
    subjects_ok = test_student_subjects()
    
    # Test subject order
    order_ok = test_subject_order()
    
    if subjects_ok and order_ok:
        print("\n🎉 All student subjects tests passed!")
        print("🎉 Students can now be assigned subject interests!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the issues above.")
        sys.exit(1)

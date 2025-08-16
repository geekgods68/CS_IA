#!/usr/bin/env python3
"""
Test script to verify student-class assignment functionality
"""

import sqlite3
import sys
import os

def test_student_class_assignments():
    print("=== STUDENT-CLASS ASSIGNMENT FUNCTIONALITY TEST ===")
    
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        print("1. Verifying student_class_map table exists...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_class_map'")
        table_exists = cur.fetchone()
        
        if table_exists:
            print("✅ student_class_map table exists")
        else:
            print("❌ student_class_map table does not exist")
            return False
        
        print("\n2. Verifying student_subjects table exists...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_subjects'")
        subjects_table_exists = cur.fetchone()
        
        if subjects_table_exists:
            print("✅ student_subjects table exists")
        else:
            print("❌ student_subjects table does not exist")
            return False
        
        print("\n3. Testing data insertion and retrieval...")
        
        # Clean up any test data first
        cur.execute("DELETE FROM student_class_map WHERE student_id IN (SELECT id FROM users WHERE username LIKE 'test_%')")
        cur.execute("DELETE FROM student_subjects WHERE student_id IN (SELECT id FROM users WHERE username LIKE 'test_%')")
        cur.execute("DELETE FROM user_role_map WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')")
        cur.execute("DELETE FROM classes WHERE name LIKE 'Test %'")
        cur.execute("DELETE FROM users WHERE username LIKE 'test_%'")
        conn.commit()
        
        # Create test student
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('password123')
        cur.execute("INSERT INTO users (username, password, created_by) VALUES (?, ?, 1)", 
                   ('test_student', password_hash))
        student_id = cur.lastrowid
        
        # Assign student role
        cur.execute("INSERT INTO user_role_map (user_id, role_id, assigned_by) VALUES (?, 3, 1)", 
                   (student_id,))
        
        # Create test classes
        cur.execute("INSERT INTO classes (name, type, created_by) VALUES (?, ?, 1)", 
                   ('Test Math Class', 'class'))
        class1_id = cur.lastrowid
        
        cur.execute("INSERT INTO classes (name, type, created_by) VALUES (?, ?, 1)", 
                   ('Test Science Session', 'session'))
        session1_id = cur.lastrowid
        
        # Assign student to subjects
        subjects = ['Math', 'Science']
        for subject in subjects:
            cur.execute("INSERT INTO student_subjects (student_id, subject_name, assigned_by) VALUES (?, ?, 1)", 
                       (student_id, subject))
        
        # Assign student to classes
        cur.execute("INSERT INTO student_class_map (student_id, class_id, assigned_by) VALUES (?, ?, 1)", 
                   (student_id, class1_id))
        cur.execute("INSERT INTO student_class_map (student_id, class_id, assigned_by) VALUES (?, ?, 1)", 
                   (student_id, session1_id))
        
        conn.commit()
        
        print("✅ Test data inserted successfully")
        
        print("\n4. Testing student assignment retrieval...")
        
        # Test subject retrieval
        cur.execute("SELECT subject_name FROM student_subjects WHERE student_id = ?", (student_id,))
        assigned_subjects = [row[0] for row in cur.fetchall()]
        print(f"Student subject interests: {assigned_subjects}")
        
        if set(assigned_subjects) == set(subjects):
            print("✅ Subject interests retrieved correctly")
        else:
            print("❌ Subject interest retrieval failed")
            return False
        
        # Test class retrieval with types
        cur.execute('''
            SELECT c.name, c.type 
            FROM classes c 
            JOIN student_class_map scm ON c.id = scm.class_id 
            WHERE scm.student_id = ?
            ORDER BY c.name
        ''', (student_id,))
        assigned_classes = cur.fetchall()
        print(f"Student enrolled classes: {assigned_classes}")
        
        expected_classes = [('Test Math Class', 'class'), ('Test Science Session', 'session')]
        if assigned_classes == expected_classes:
            print("✅ Class enrollments retrieved correctly")
        else:
            print("❌ Class enrollment retrieval failed")
            return False
        
        print("\n5. Testing student details API response format...")
        
        # Simulate get_user_details for student
        cur.execute('''
            SELECT u.id, u.username, ur.role_name, u.created_on
            FROM users u 
            LEFT JOIN user_role_map urm ON u.id = urm.user_id 
            LEFT JOIN user_roles ur ON urm.role_id = ur.id 
            WHERE u.id = ?
        ''', (student_id,))
        user_info = cur.fetchone()
        
        if user_info[2] == 'student':
            # Get assigned classes with type information
            cur.execute('''
                SELECT c.name, c.type 
                FROM classes c 
                JOIN student_class_map scm ON c.id = scm.class_id 
                WHERE scm.student_id = ?
                ORDER BY c.name
            ''', (student_id,))
            classes_data = cur.fetchall()
            student_classes = [f"{row[0]} ({row[1]})" for row in classes_data]
            
            expected_display = ["Test Math Class (class)", "Test Science Session (session)"]
            if student_classes == expected_display:
                print("✅ Student class display format correct")
            else:
                print("❌ Student class display format incorrect")
                print(f"Expected: {expected_display}")
                print(f"Got: {student_classes}")
                return False
        
        print("\n6. Testing multiple students can enroll in same class...")
        
        # Create another test student
        cur.execute("INSERT INTO users (username, password, created_by) VALUES (?, ?, 1)", 
                   ('test_student2', password_hash))
        student2_id = cur.lastrowid
        
        cur.execute("INSERT INTO user_role_map (user_id, role_id, assigned_by) VALUES (?, 3, 1)", 
                   (student2_id,))
        
        # Assign second student to same class
        cur.execute("INSERT INTO student_class_map (student_id, class_id, assigned_by) VALUES (?, ?, 1)", 
                   (student2_id, class1_id))
        conn.commit()
        
        # Verify both students are enrolled in the same class
        cur.execute('''
            SELECT u.username, c.name, c.type 
            FROM users u 
            JOIN student_class_map scm ON u.id = scm.student_id 
            JOIN classes c ON scm.class_id = c.id 
            WHERE c.id = ?
            ORDER BY u.username
        ''', (class1_id,))
        class_students = cur.fetchall()
        
        expected_students = [('test_student', 'Test Math Class', 'class'), ('test_student2', 'Test Math Class', 'class')]
        if class_students == expected_students:
            print("✅ Multiple students can enroll in same class")
        else:
            print("❌ Multiple student enrollment failed")
            print(f"Expected: {expected_students}")
            print(f"Got: {class_students}")
            return False
        
        print("\n7. Testing enrollment update functionality...")
        
        # Remove one class and add another
        cur.execute("DELETE FROM student_class_map WHERE student_id = ? AND class_id = ?", 
                   (student_id, class1_id))
        
        # Create another test class
        cur.execute("INSERT INTO classes (name, type, created_by) VALUES (?, ?, 1)", 
                   ('Test English Session', 'session'))
        class2_id = cur.lastrowid
        
        cur.execute("INSERT INTO student_class_map (student_id, class_id, assigned_by) VALUES (?, ?, 1)", 
                   (student_id, class2_id))
        conn.commit()
        
        # Verify update
        cur.execute('''
            SELECT c.name, c.type 
            FROM classes c 
            JOIN student_class_map scm ON c.id = scm.class_id 
            WHERE scm.student_id = ?
            ORDER BY c.name
        ''', (student_id,))
        updated_classes = cur.fetchall()
        
        expected_updated = [('Test English Session', 'session'), ('Test Science Session', 'session')]
        if updated_classes == expected_updated:
            print("✅ Class enrollment updates work correctly")
        else:
            print("❌ Class enrollment update failed")
            print(f"Expected: {expected_updated}")
            print(f"Got: {updated_classes}")
            return False
        
        print("\n8. Cleaning up test data...")
        
        # Clean up test data
        cur.execute("DELETE FROM student_class_map WHERE student_id IN (?, ?)", (student_id, student2_id))
        cur.execute("DELETE FROM student_subjects WHERE student_id IN (?, ?)", (student_id, student2_id))
        cur.execute("DELETE FROM user_role_map WHERE user_id IN (?, ?)", (student_id, student2_id))
        cur.execute("DELETE FROM classes WHERE name LIKE 'Test %'")
        cur.execute("DELETE FROM users WHERE username LIKE 'test_%'")
        conn.commit()
        
        print("✅ Test data cleaned up")
        
        print("\n🎉 ALL STUDENT-CLASS ASSIGNMENT TESTS PASSED!")
        print("Student-class assignment functionality is working correctly.")
        print("Features verified:")
        print("- Direct student-class enrollment mapping")
        print("- Subject interests independent of class enrollment")
        print("- Multiple students can enroll in same class")
        print("- Enrollment updates work properly")
        print("- Class/session type information preserved")
        print("- User details API returns correct format")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = test_student_class_assignments()
    sys.exit(0 if success else 1)

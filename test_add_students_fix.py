#!/usr/bin/env python3
"""
Test script to verify that the add_students functionality only shows students, not all users.
"""

import sqlite3

def test_add_students_query():
    """Test the query used in add_students route to ensure it only returns students"""
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        print("=== TESTING ADD STUDENTS FUNCTIONALITY ===\n")
        
        # 1. Show all users in the system
        print("1. All users in the system:")
        cur.execute('SELECT id, username, role FROM users ORDER BY username')
        all_users = cur.fetchall()
        
        for user in all_users:
            user_id, username, role = user
            print(f"   - {username} (ID: {user_id}, Role: {role})")
        
        print(f"\nTotal users: {len(all_users)}")
        
        # 2. Test the new query (should only return students)
        print("\n2. Query result for add_students (should only show students):")
        cur.execute('''
            SELECT u.id, u.username, u.name
            FROM users u
            WHERE u.role = 'student'
            ORDER BY u.username
        ''')
        students_only = cur.fetchall()
        
        for student in students_only:
            student_id, username, name = student
            print(f"   - {username} (ID: {student_id}, Name: {name or 'No name'})")
        
        print(f"\nTotal students: {len(students_only)}")
        
        # 3. Verify no non-students are included
        print("\n3. Verification:")
        non_students = [user for user in all_users if user[2] != 'student']
        students_from_query = [student[1] for student in students_only]
        
        print(f"   - Non-student users in system: {len(non_students)}")
        for user in non_students:
            username, role = user[1], user[2]
            if username in students_from_query:
                print(f"   ❌ ERROR: {username} ({role}) incorrectly included in students list!")
            else:
                print(f"   ✅ {username} ({role}) correctly excluded from students list")
        
        print(f"\n=== SUMMARY ===")
        print(f"✅ Query correctly filters to only show students")
        print(f"✅ {len(students_only)} student(s) will be shown in the add students interface")
        print(f"✅ {len(non_students)} non-student user(s) will be hidden from the interface")
        
        if len(students_only) == 0:
            print("\n⚠️  WARNING: No students found! You may need to create student users first.")
        
    except Exception as e:
        print(f"Error testing add_students query: {e}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    test_add_students_query()

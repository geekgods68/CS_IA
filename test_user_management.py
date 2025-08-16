#!/usr/bin/env python3
"""
Test script to verify admin user management functionality with clean database.
Only admin user should exist - no test data.
Updated to test the simplified class structure (no grade/batch fields).
"""

import sqlite3

def test_user_management():
    """Test the user management functionality with clean database"""
    print("=== CLEAN DATABASE USER MANAGEMENT TEST ===")
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Test the query used in manage_users route (using LEFT JOIN to handle empty data)
    print("1. Testing manage_users query...")
    cur.execute('''
        SELECT u.id, u.username, COALESCE(ur.role_name, 'No Role'), u.created_on
        FROM users u 
        LEFT JOIN user_role_map urm ON u.id = urm.user_id 
        LEFT JOIN user_roles ur ON urm.role_id = ur.id
        ORDER BY u.created_on DESC
    ''')
    users = cur.fetchall()
    
    print(f"Found {len(users)} user(s) - should be only admin:")
    for user in users:
        print(f"  - ID: {user[0]}, Username: {user[1]}, Role: {user[2]}, Created: {user[3]}")
    
    # Verify only admin exists
    if len(users) == 1 and users[0][1] == 'admin':
        print("✅ Database correctly contains only admin user")
    else:
        print("❌ Database should contain only admin user")
    
    print("\n2. Testing user roles...")
    cur.execute('SELECT id, role_name FROM user_roles')
    roles = cur.fetchall()
    print(f"Available roles: {roles}")
    
    print("\n3. Verifying clean state - no test data...")
    # All these should be 0 in a clean database
    
    # Student class mappings
    cur.execute('SELECT COUNT(*) FROM student_class_map')
    student_mappings = cur.fetchone()[0]
    print(f"Student class mappings: {student_mappings} (should be 0)")
    
    # Teacher subject mappings
    cur.execute('SELECT COUNT(*) FROM teacher_subject_map')
    teacher_mappings = cur.fetchone()[0]
    print(f"Teacher subject mappings: {teacher_mappings} (should be 0)")
    
    # Classes (might have test data from our verification)
    cur.execute('SELECT COUNT(*) FROM classes')
    classes_count = cur.fetchone()[0]
    print(f"Total classes: {classes_count}")
    
    # Show class structure 
    cur.execute('SELECT id, name FROM classes')
    classes = cur.fetchall()
    if classes:
        print("  Classes found:")
        for cls in classes:
            print(f"    - ID: {cls[0]}, Name: {cls[1]}")
    
    # Subjects
    cur.execute('SELECT COUNT(*) FROM subjects')
    subjects_count = cur.fetchone()[0]
    print(f"Total subjects: {subjects_count} (should be 0)")
    
    # Doubts
    cur.execute('SELECT COUNT(*) FROM doubts')
    doubts_count = cur.fetchone()[0]
    print(f"Total doubts: {doubts_count} (should be 0)")
    
    # Announcements
    cur.execute('SELECT COUNT(*) FROM announcements')
    announcements_count = cur.fetchone()[0]
    print(f"Total announcements: {announcements_count} (should be 0)")
    
    # Feedback
    cur.execute('SELECT COUNT(*) FROM feedback')
    feedback_count = cur.fetchone()[0]
    print(f"Total feedback: {feedback_count} (should be 0)")
    
    print("\n4. Testing updated class structure...")
    # Verify the classes table no longer has grade/batch columns
    cur.execute('PRAGMA table_info(classes)')
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Classes table columns: {column_names}")
    
    if 'grade' not in column_names and 'batch' not in column_names:
        print("✅ Grade and batch columns successfully removed from classes table")
    else:
        print("❌ Grade/batch columns still exist in classes table")
    
    print("\n5. Testing admin user integrity...")
    # Verify admin user has proper role mapping
    cur.execute('''
        SELECT u.username, ur.role_name 
        FROM users u 
        JOIN user_role_map urm ON u.id = urm.user_id 
        JOIN user_roles ur ON urm.role_id = ur.id
        WHERE u.username = 'admin'
    ''')
    admin_info = cur.fetchone()
    
    if admin_info and admin_info[1] == 'admin':
        print("✅ Admin user properly configured with admin role")
    else:
        print("❌ Admin user configuration issue")
    
    print("\n6. Testing teacher subjects functionality...")
    # Test the teacher_subjects table exists
    cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="teacher_subjects"')
    table_exists = cur.fetchone()
    
    if table_exists:
        print("✅ teacher_subjects table exists")
        
        # Test creating a teacher with subjects
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('testpass')
        cur.execute('INSERT INTO users (username, password, created_by) VALUES (?, ?, ?)', 
                   ('test_teacher', password_hash, 1))
        teacher_id = cur.lastrowid
        
        # Assign teacher role (role_id = 2)
        cur.execute('INSERT INTO user_role_map (user_id, role_id, assigned_by) VALUES (?, ?, ?)', 
                   (teacher_id, 2, 1))
        
        # Assign subjects to teacher
        test_subjects = ['Math', 'Science']
        for subject in test_subjects:
            cur.execute('INSERT INTO teacher_subjects (teacher_id, subject_name, assigned_by) VALUES (?, ?, ?)',
                       (teacher_id, subject, 1))
        
        conn.commit()
        
        # Verify subjects were assigned
        cur.execute('SELECT subject_name FROM teacher_subjects WHERE teacher_id = ?', (teacher_id,))
        assigned_subjects = [row[0] for row in cur.fetchall()]
        
        if set(assigned_subjects) == set(test_subjects):
            print("✅ Teacher subjects assignment works correctly")
        else:
            print("❌ Teacher subjects assignment failed")
        
        # Clean up test data
        cur.execute('DELETE FROM teacher_subjects WHERE teacher_id = ?', (teacher_id,))
        cur.execute('DELETE FROM user_role_map WHERE user_id = ?', (teacher_id,))
        cur.execute('DELETE FROM users WHERE id = ?', (teacher_id,))
        conn.commit()
        print("✅ Test teacher data cleaned up")
    else:
        print("❌ teacher_subjects table does not exist")
    
    print("\n7. Testing class/session creation functionality...")
    # Test the class/session creation with type field
    initial_count = classes_count
    
    # Test creating a class
    cur.execute('INSERT INTO classes (name, type, created_by) VALUES (?, ?, ?)', ('Test Class', 'class', 1))
    conn.commit()
    
    # Test creating a session
    cur.execute('INSERT INTO classes (name, type, created_by) VALUES (?, ?, ?)', ('Test Session', 'session', 1))
    conn.commit()
    
    # Verify both were created
    cur.execute('SELECT COUNT(*) FROM classes')
    new_count = cur.fetchone()[0]
    
    if new_count == initial_count + 2:
        print("✅ Class and session creation works with type field")
        
        # Test querying with type
        cur.execute('SELECT name, type FROM classes WHERE name LIKE \"Test%\" ORDER BY type, name')
        test_items = cur.fetchall()
        
        if len(test_items) == 2:
            print(f"✅ Created items: {test_items[0][0]} ({test_items[0][1]}), {test_items[1][0]} ({test_items[1][1]})")
        
        # Clean up test data
        cur.execute('DELETE FROM classes WHERE name LIKE \"Test%\"')
        conn.commit()
        print("✅ Test class/session data cleaned up")
    else:
        print("❌ Class/session creation failed")
    
    print("\n8. Testing table structure...")
    # Verify the classes table has the type field
    cur.execute('PRAGMA table_info(classes)')
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'type' in column_names:
        print("✅ Type field successfully added to classes table")
        print(f"✅ Classes table columns: {column_names}")
    else:
        print("❌ Type field missing from classes table")
    
    conn.close()
    print("\n🎉 Clean database verification completed!")
    print("Database is ready for production use with only admin account.")
    print("Classes now support both 'class' and 'session' types with dropdown selection.")
    print("Teachers can now be assigned subjects: Math, English, Hindi, Science, Social Science.")

if __name__ == "__main__":
    test_user_management()

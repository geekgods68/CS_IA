#!/usr/bin/env python3

import sqlite3
import hashlib

def create_test_teacher():
    """Create a test teacher account for testing"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Hash password
    password = "teacher123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Create test teacher
    try:
        cur.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_teacher', hashed_password, 'teacher', 'Test Teacher', 'teacher@test.com'))
        
        teacher_id = cur.lastrowid
        print(f"✅ Created test teacher with ID: {teacher_id}")
        print(f"   Username: test_teacher")
        print(f"   Password: teacher123")
        print(f"   Role: teacher")
        
        # Assign some subjects to the teacher
        subjects = ['Math', 'Science', 'English']
        for subject in subjects:
            cur.execute('''
                INSERT INTO teacher_subjects (teacher_id, subject_name, assigned_by)
                VALUES (?, ?, ?)
            ''', (teacher_id, subject, 1))  # Assigned by admin (ID 1)
        
        print(f"✅ Assigned subjects: {', '.join(subjects)}")
        
        # Get existing classes and assign teacher to some of them
        cur.execute('SELECT id, name FROM classes LIMIT 2')
        classes = cur.fetchall()
        
        for class_info in classes:
            cur.execute('''
                INSERT INTO teacher_class_map (teacher_id, class_id, assigned_by)
                VALUES (?, ?, ?)
            ''', (teacher_id, class_info[0], 1))
            print(f"✅ Assigned to class: {class_info[1]}")
        
        conn.commit()
        print(f"\n🎉 Test teacher account created successfully!")
        print(f"You can now login with username 'test_teacher' and password 'teacher123'")
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Teacher account already exists or error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_teacher()

#!/usr/bin/env python3
"""
Test script to create a sample student with subjects and verify user details functionality
"""

import sqlite3
import hashlib

def simple_hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_student():
    """Create a test student with subjects"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        # Create a test student
        student_password = simple_hash_password('student123')
        cur.execute('''
            INSERT INTO users (username, password, role, name, email, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('test_student', student_password, 'student', 'Test Student', 'test@student.com', 1))
        
        student_id = cur.lastrowid
        
        # Assign subjects to the student
        subjects = ['Math', 'Science', 'English']
        for subject in subjects:
            cur.execute('''
                INSERT INTO student_subjects (student_id, subject_name, assigned_by)
                VALUES (?, ?, ?)
            ''', (student_id, subject, 1))
        
        # Create a test class and assign student to it
        cur.execute('''
            INSERT INTO classes (name, type, created_by)
            VALUES (?, ?, ?)
        ''', ('Class 10A', 'regular', 1))
        
        class_id = cur.lastrowid
        
        cur.execute('''
            INSERT INTO student_class_map (student_id, class_id, assigned_by)
            VALUES (?, ?, ?)
        ''', (student_id, class_id, 1))
        
        conn.commit()
        
        print(f"✅ Created test student with ID: {student_id}")
        print(f"   Username: test_student")
        print(f"   Password: student123")
        print(f"   Subjects: {', '.join(subjects)}")
        print(f"   Class: Class 10A")
        
        return student_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating test student: {e}")
        return None
    finally:
        conn.close()

def test_user_details(user_id):
    """Test the user details query"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        # Get user basic info
        cur.execute('''
            SELECT u.id, u.username, u.role, u.name, u.email, u.created_on
            FROM users u
            WHERE u.id = ?
        ''', (user_id,))
        user_info = cur.fetchone()
        
        if not user_info:
            print("❌ User not found")
            return
        
        user_id_db, username, role, name, email, created_on = user_info
        print(f"\n📋 User Details for ID {user_id}:")
        print(f"   Username: {username}")
        print(f"   Role: {role}")
        print(f"   Name: {name}")
        print(f"   Email: {email}")
        print(f"   Created: {created_on}")
        
        if role == 'student':
            # Get assigned classes
            cur.execute('''
                SELECT c.name, c.type 
                FROM classes c 
                JOIN student_class_map scm ON c.id = scm.class_id 
                WHERE scm.student_id = ? AND scm.status = 'active'
                ORDER BY c.name
            ''', (user_id,))
            classes_data = cur.fetchall()
            classes = [f"{row[0]} ({row[1]})" for row in classes_data]
            
            # Get assigned subjects
            cur.execute('SELECT subject_name FROM student_subjects WHERE student_id = ? ORDER BY subject_name', (user_id,))
            subjects_data = cur.fetchall()
            subjects = [row[0] for row in subjects_data]
            
            print(f"   Classes: {', '.join(classes) if classes else 'None'}")
            print(f"   Subjects: {', '.join(subjects) if subjects else 'None'}")
        
    except Exception as e:
        print(f"❌ Error getting user details: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔧 Creating test student...")
    student_id = create_test_student()
    
    if student_id:
        print("\n🔍 Testing user details query...")
        test_user_details(student_id)
        
        # Also test with admin user
        print("\n🔍 Testing admin user details...")
        test_user_details(1)

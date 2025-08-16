#!/usr/bin/env python3
"""
Test script to create a student user with subjects and classes for testing the user details modal.
"""

import sqlite3
import hashlib
from datetime import datetime

def simple_hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_student():
    """Create a test student with subjects for testing"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        # Create a test student
        student_username = "test_student"
        student_password = simple_hash_password("password123")
        student_name = "John Doe"
        student_email = "john.doe@example.com"
        created_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if student already exists
        cur.execute('SELECT id FROM users WHERE username = ?', (student_username,))
        existing = cur.fetchone()
        
        if existing:
            print(f"Student '{student_username}' already exists with ID {existing[0]}")
            student_id = existing[0]
        else:
            # Insert the student
            cur.execute('''
                INSERT INTO users (username, password, role, name, email, created_on) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_username, student_password, 'student', student_name, student_email, created_on))
            
            student_id = cur.lastrowid
            print(f"Created student '{student_username}' with ID {student_id}")
        
        # Clear existing subjects for this student
        cur.execute('DELETE FROM student_subjects WHERE student_id = ?', (student_id,))
        
        # Add subjects for the student
        subjects = ['Math', 'Science', 'English']
        for subject in subjects:
            cur.execute('''
                INSERT INTO student_subjects (student_id, subject_name) 
                VALUES (?, ?)
            ''', (student_id, subject))
        
        print(f"Assigned subjects {subjects} to student")
        
        # Create a test class if it doesn't exist
        cur.execute('SELECT id FROM classes WHERE name = ?', ('Class 10A',))
        class_result = cur.fetchone()
        
        if class_result:
            class_id = class_result[0]
            print(f"Using existing class 'Class 10A' with ID {class_id}")
        else:
            cur.execute('''
                INSERT INTO classes (name, type, description, created_on) 
                VALUES (?, ?, ?, ?)
            ''', ('Class 10A', 'Academic', 'Test class for grade 10', created_on))
            class_id = cur.lastrowid
            print(f"Created class 'Class 10A' with ID {class_id}")
        
        # Clear existing class assignments for this student
        cur.execute('DELETE FROM student_class_map WHERE student_id = ?', (student_id,))
        
        # Assign student to class
        cur.execute('''
            INSERT INTO student_class_map (student_id, class_id, status) 
            VALUES (?, ?, ?)
        ''', (student_id, class_id, 'active'))
        
        print(f"Assigned student to class 'Class 10A'")
        
        conn.commit()
        print("\nTest student created successfully!")
        print(f"Login credentials: {student_username} / password123")
        
        # Verify the data
        print("\nVerifying student data:")
        cur.execute('''
            SELECT s.subject_name 
            FROM student_subjects s 
            WHERE s.student_id = ?
        ''', (student_id,))
        subjects_result = cur.fetchall()
        print(f"Subjects: {[s[0] for s in subjects_result]}")
        
        cur.execute('''
            SELECT c.name, c.type 
            FROM classes c 
            JOIN student_class_map scm ON c.id = scm.class_id 
            WHERE scm.student_id = ? AND scm.status = 'active'
        ''', (student_id,))
        classes_result = cur.fetchall()
        print(f"Classes: {[f'{c[0]} ({c[1]})' for c in classes_result]}")
        
    except Exception as e:
        print(f"Error creating test student: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == '__main__':
    create_test_student()

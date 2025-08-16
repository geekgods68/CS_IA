#!/usr/bin/env python3

import sqlite3
import sys

def test_view_class():
    """Test the view_class functionality to identify the error"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # First, check if we have any classes
    cur.execute('SELECT id, name FROM classes')
    classes = cur.fetchall()
    print(f"Available classes: {classes}")
    
    if not classes:
        print("No classes found. Creating a test class...")
        cur.execute('''
            INSERT INTO classes (name, type, description, created_by)
            VALUES (?, ?, ?, ?)
        ''', ('Test Class', 'regular', 'Test class for debugging', 1))
        conn.commit()
        class_id = cur.lastrowid
        print(f"Created test class with ID: {class_id}")
    else:
        class_id = classes[0][0]
        print(f"Using existing class with ID: {class_id}")
    
    try:
        # Test the same query from view_class route
        cur.execute('SELECT * FROM classes WHERE id = ?', (class_id,))
        class_info = cur.fetchone()
        print(f"Class info: {class_info}")
        
        # Test student query
        cur.execute('''
            SELECT u.id, u.username
            FROM users u
            JOIN student_class_map scm ON u.id = scm.student_id
            WHERE scm.class_id = ?
            ORDER BY u.username
        ''', (class_id,))
        students = cur.fetchall()
        print(f"Students: {students}")
        
        # Test teacher query
        cur.execute('''
            SELECT u.id, u.username
            FROM users u
            JOIN teacher_class_map tcm ON u.id = tcm.teacher_id
            WHERE tcm.class_id = ?
            ORDER BY u.username
        ''', (class_id,))
        teachers = cur.fetchall()
        print(f"Teachers: {teachers}")
        
        # Test subjects query
        cur.execute('''
            SELECT DISTINCT ss.subject_name
            FROM student_subjects ss
            JOIN student_class_map scm ON ss.student_id = scm.student_id
            WHERE scm.class_id = ? AND scm.status = 'active'
            UNION
            SELECT DISTINCT ts.subject_name
            FROM teacher_subjects ts
            JOIN teacher_class_map tcm ON ts.teacher_id = tcm.teacher_id
            WHERE tcm.class_id = ?
            ORDER BY subject_name
        ''', (class_id, class_id))
        subjects_data = cur.fetchall()
        subjects = [{'name': row[0]} for row in subjects_data]
        print(f"Subjects: {subjects}")
        
        print("All queries completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print(f"Error type: {type(e)}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    test_view_class()

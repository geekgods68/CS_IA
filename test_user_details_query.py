#!/usr/bin/env python3
"""
Test script to verify the get_user_details functionality directly
"""

import sqlite3
import json

def test_user_details_query():
    """Test the user details query directly on the database"""
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        student_id = 3  # Our test student
        
        # Get user basic info (same query as in admin.py)
        cur.execute('''
            SELECT u.id, u.username, u.role, u.name, u.email, u.created_on
            FROM users u
            WHERE u.id = ?
        ''', (student_id,))
        user_info = cur.fetchone()
        
        if not user_info:
            print("User not found")
            return
        
        user_id_db, username, role, name, email, created_on = user_info
        data = {
            'id': user_id_db,
            'username': username,
            'role': role,
            'name': name,
            'email': email,
            'created_on': created_on,
            'classes': [],
            'subjects': []
        }
        
        # Get assignments based on role
        if role == 'student':
            # Get assigned classes
            cur.execute('''
                SELECT c.name, c.type 
                FROM classes c 
                JOIN student_class_map scm ON c.id = scm.class_id 
                WHERE scm.student_id = ? AND scm.status = 'active'
                ORDER BY c.name
            ''', (student_id,))
            classes_data = cur.fetchall()
            data['classes'] = [f"{row[0]} ({row[1]})" for row in classes_data]
            
            # Get assigned subjects
            cur.execute('SELECT subject_name FROM student_subjects WHERE student_id = ? ORDER BY subject_name', (student_id,))
            subjects_data = cur.fetchall()
            data['subjects'] = [row[0] for row in subjects_data]
        
        print("User Details Query Result:")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error querying user details: {e}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    test_user_details_query()

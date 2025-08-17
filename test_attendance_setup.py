#!/usr/bin/env python3
"""
Test script for attendance functionality
"""

import sqlite3
from datetime import datetime, timedelta
import hashlib

def simple_hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def test_attendance_setup():
    """Test attendance table and create sample data"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        print("=== Testing Attendance Setup ===")
        
        # Check if attendance table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
        if cur.fetchone():
            print("✓ Attendance table exists")
        else:
            print("✗ Attendance table not found")
            return
        
        # Create test teacher if not exists
        cur.execute("SELECT id FROM users WHERE username = 'teacher_test' AND role = 'teacher'")
        teacher = cur.fetchone()
        
        if not teacher:
            print("Creating test teacher...")
            cur.execute('''
                INSERT INTO users (username, password, role, name, email) 
                VALUES (?, ?, 'teacher', 'Test Teacher', 'teacher@test.com')
            ''', ('teacher_test', simple_hash_password('test123')))
            teacher_id = cur.lastrowid
            print(f"✓ Test teacher created with ID: {teacher_id}")
        else:
            teacher_id = teacher[0]
            print(f"✓ Test teacher exists with ID: {teacher_id}")
        
        # Create test student if not exists
        cur.execute("SELECT id FROM users WHERE username = 'student_test' AND role = 'student'")
        student = cur.fetchone()
        
        if not student:
            print("Creating test student...")
            cur.execute('''
                INSERT INTO users (username, password, role, name, email) 
                VALUES (?, ?, 'student', 'Test Student', 'student@test.com')
            ''', ('student_test', simple_hash_password('test123')))
            student_id = cur.lastrowid
            print(f"✓ Test student created with ID: {student_id}")
        else:
            student_id = student[0]
            print(f"✓ Test student exists with ID: {student_id}")
        
        # Create test class if not exists
        cur.execute("SELECT id FROM classes WHERE name = 'Test Class'")
        class_result = cur.fetchone()
        
        if not class_result:
            print("Creating test class...")
            cur.execute('''
                INSERT INTO classes (name, type, description, grade_level, status, created_by) 
                VALUES ('Test Class', 'regular', 'Test class for attendance', 'Grade 10', 'active', 1)
            ''')
            class_id = cur.lastrowid
            print(f"✓ Test class created with ID: {class_id}")
        else:
            class_id = class_result[0]
            print(f"✓ Test class exists with ID: {class_id}")
        
        # Assign teacher to class
        cur.execute("SELECT 1 FROM teacher_class_map WHERE teacher_id = ? AND class_id = ?", (teacher_id, class_id))
        if not cur.fetchone():
            print("Assigning teacher to class...")
            cur.execute('''
                INSERT INTO teacher_class_map (teacher_id, class_id, assigned_by) 
                VALUES (?, ?, 1)
            ''', (teacher_id, class_id))
            print("✓ Teacher assigned to class")
        else:
            print("✓ Teacher already assigned to class")
        
        # Assign student to class
        cur.execute("SELECT 1 FROM student_class_map WHERE student_id = ? AND class_id = ?", (student_id, class_id))
        if not cur.fetchone():
            print("Assigning student to class...")
            cur.execute('''
                INSERT INTO student_class_map (student_id, class_id, assigned_by, status) 
                VALUES (?, ?, 1, 'active')
            ''', (student_id, class_id))
            print("✓ Student assigned to class")
        else:
            print("✓ Student already assigned to class")
        
        # Create sample attendance records
        print("Creating sample attendance records...")
        today = datetime.now()
        for i in range(5):
            attendance_date = (today - timedelta(days=i)).date()
            status = 'present' if i % 2 == 0 else 'absent'
            
            # Check if attendance already exists
            cur.execute('''
                SELECT 1 FROM attendance 
                WHERE student_id = ? AND class_id = ? AND attendance_date = ?
            ''', (student_id, class_id, attendance_date))
            
            if not cur.fetchone():
                cur.execute('''
                    INSERT INTO attendance (student_id, class_id, attendance_date, status, marked_by, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (student_id, class_id, attendance_date, status, teacher_id, f'Sample record {i+1}'))
                print(f"  ✓ Created attendance for {attendance_date}: {status}")
            else:
                print(f"  ✓ Attendance already exists for {attendance_date}")
        
        conn.commit()
        
        # Test attendance queries
        print("\n=== Testing Attendance Queries ===")
        
        # Test attendance summary
        cur.execute('''
            SELECT 
                u.name as student_name,
                c.name as class_name,
                COUNT(*) as total_days,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_days,
                SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent_days,
                ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as attendance_percentage
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            JOIN classes c ON a.class_id = c.id
            WHERE a.student_id = ? AND a.class_id = ?
            GROUP BY u.id, c.id
        ''', (student_id, class_id))
        
        result = cur.fetchone()
        if result:
            print(f"✓ Attendance summary: {result[0]} in {result[1]}")
            print(f"  Total days: {result[2]}, Present: {result[3]}, Absent: {result[4]}, Percentage: {result[5]}%")
        else:
            print("✗ No attendance summary found")
        
        # Test teacher's class query
        cur.execute('''
            SELECT c.id, c.name, c.grade_level 
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND c.status = 'active'
        ''', (teacher_id,))
        
        teacher_classes = cur.fetchall()
        print(f"✓ Teacher has access to {len(teacher_classes)} class(es)")
        for cls in teacher_classes:
            print(f"  Class: {cls[1]} ({cls[2]})")
        
        print("\n=== Attendance Setup Complete ===")
        print(f"Test teacher login: teacher_test / test123")
        print(f"Test student login: student_test / test123")
        print(f"Admin can view all attendance records")
        print(f"Teacher can mark attendance for their classes")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_attendance_setup()

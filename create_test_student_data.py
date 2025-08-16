#!/usr/bin/env python3

import sqlite3
import hashlib

def create_test_student_data():
    """Create a test student account and test data"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    print("🧪 Creating Test Student and Data")
    print("=" * 40)
    
    # Hash password
    password = "student123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Create test student
    try:
        cur.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_student', hashed_password, 'student', 'Test Student', 'student@test.com'))
        
        student_id = cur.lastrowid
        print(f"✅ Created test student with ID: {student_id}")
        print(f"   Username: test_student")
        print(f"   Password: student123")
        print(f"   Role: student")
        
        # Create test classes
        test_classes = [
            ('Class 10', 'Test class description', '10', 'regular', 'Monday, Wednesday, Friday', '09:00', '10:30'),
            ('Math Advanced', 'Advanced mathematics class', '10', 'session', 'Tuesday, Thursday', '11:00', '12:30')
        ]
        
        class_ids = []
        for class_data in test_classes:
            cur.execute('''
                INSERT INTO classes (name, description, grade_level, type, schedule_days, schedule_time_start, schedule_time_end, created_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*class_data, 1, 'active'))
            class_ids.append(cur.lastrowid)
            print(f"✅ Created class: {class_data[0]}")
        
        # Assign student to classes
        for class_id in class_ids:
            cur.execute('''
                INSERT INTO student_class_map (student_id, class_id, assigned_by)
                VALUES (?, ?, ?)
            ''', (student_id, class_id, 1))
            print(f"✅ Assigned student to class ID: {class_id}")
        
        # Assign subjects to student
        subjects = ['Math', 'Science', 'English']
        for subject in subjects:
            cur.execute('''
                INSERT INTO student_subjects (student_id, subject_name, assigned_by)
                VALUES (?, ?, ?)
            ''', (student_id, subject, 1))
        
        print(f"✅ Assigned subjects: {', '.join(subjects)}")
        
        # Create some test doubts
        cur.execute('''
            INSERT INTO doubts (student_id, subject, doubt_text, status)
            VALUES (?, ?, ?, ?)
        ''', (student_id, 'Math', 'How do I solve quadratic equations?', 'open'))
        
        print(f"✅ Created test doubt")
        
        conn.commit()
        print(f"\n🎉 Test student and data created successfully!")
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Student account already exists or error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_student_data()

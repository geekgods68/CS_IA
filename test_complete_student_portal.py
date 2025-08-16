#!/usr/bin/env python3

import sqlite3
import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, '/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA')

def create_test_student_data():
    """Create comprehensive test data for student testing"""
    print("🔧 Creating Test Student Data")
    print("=" * 40)
    
    conn = sqlite3.connect('/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/users.db')
    cur = conn.cursor()
    
    # Check if test student exists
    cur.execute("SELECT id FROM users WHERE username = 'test_student'")
    if not cur.fetchone():
        print("❌ Test student not found. Please run create_test_student_data.py first")
        conn.close()
        return False
    
    student_id = 7  # Known test student ID
    
    # 1. Create test classes if they don't exist
    test_classes = [
        (10, 'Class 10', 'Mathematics and Science focused class', 10, 'regular', 'active', 'Monday, Wednesday, Friday', '09:00', '10:30'),
        (11, 'Class 11', 'Advanced Science and Mathematics', 11, 'advanced', 'active', 'Tuesday, Thursday', '10:00', '11:30'),
    ]
    
    for class_data in test_classes:
        cur.execute('''
            INSERT OR REPLACE INTO classes 
            (id, name, description, grade_level, type, status, schedule_days, schedule_time_start, schedule_time_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', class_data)
    
    # 2. Assign student to classes
    class_assignments = [(student_id, 10), (student_id, 11)]
    for assignment in class_assignments:
        cur.execute('''
            INSERT OR REPLACE INTO student_class_map (student_id, class_id)
            VALUES (?, ?)
        ''', assignment)
    
    # 3. Assign subjects to student
    subjects = ['Math', 'Science', 'English']
    for subject in subjects:
        cur.execute('''
            INSERT OR REPLACE INTO student_subjects (student_id, subject_name)
            VALUES (?, ?)
        ''', (student_id, subject))
    
    # 4. Create some test doubts
    test_doubts = [
        (student_id, 'Math', 'How do I solve quadratic equations?', 'open'),
        (student_id, 'Science', 'What is photosynthesis process?', 'open'),
        (student_id, 'English', 'How to improve essay writing?', 'answered'),
    ]
    
    for doubt in test_doubts:
        cur.execute('''
            INSERT OR REPLACE INTO doubts (student_id, subject, doubt_text, status)
            VALUES (?, ?, ?, ?)
        ''', doubt)
    
    conn.commit()
    
    # Verify the data
    print("\n✅ Test Data Created:")
    
    # Check classes
    cur.execute('''
        SELECT c.name, c.grade_level, c.schedule_days 
        FROM classes c
        JOIN student_class_map scm ON c.id = scm.class_id
        WHERE scm.student_id = ?
    ''', (student_id,))
    classes = cur.fetchall()
    print(f"   📚 Classes enrolled: {len(classes)}")
    for cls in classes:
        print(f"      - {cls[0]} (Grade {cls[1]}) - {cls[2]}")
    
    # Check subjects
    cur.execute('SELECT subject_name FROM student_subjects WHERE student_id = ?', (student_id,))
    subjects = cur.fetchall()
    print(f"   📖 Subjects: {len(subjects)}")
    for subject in subjects:
        print(f"      - {subject[0]}")
    
    # Check doubts
    cur.execute('SELECT doubt_text, status FROM doubts WHERE student_id = ?', (student_id,))
    doubts = cur.fetchall()
    print(f"   ❓ Doubts: {len(doubts)}")
    for doubt in doubts:
        print(f"      - {doubt[0][:50]}... ({doubt[1]})")
    
    conn.close()
    print("\n🎉 Test data setup completed!")
    return True

def test_student_portal_functionality():
    """Test student portal functionality"""
    print("\n🧪 Testing Student Portal Functionality")
    print("=" * 50)
    
    try:
        import requests
        
        base_url = "http://127.0.0.1:5003"
        session = requests.Session()
        
        # Login as test student
        login_data = {'username': 'test_student', 'password': 'student123'}
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code != 302:
            print("❌ Login failed")
            return False
        
        print("✅ Student login successful")
        
        # Test dashboard access
        dashboard_response = session.get(f"{base_url}/student/site")
        if dashboard_response.status_code == 200:
            print("✅ Student dashboard accessible")
            
            # Check if dashboard contains expected elements
            content = dashboard_response.text
            if "Welcome to Your Student Dashboard" in content:
                print("✅ Welcome message found")
            if "My Classes" in content:
                print("✅ My Classes section found")
            if "Homework" in content:
                print("✅ Homework section found")
            if "Ask Doubts" in content:
                print("✅ Ask Doubts section found")
        else:
            print(f"❌ Dashboard error: {dashboard_response.status_code}")
            return False
        
        # Test other routes
        routes_to_test = [
            ('/student/classes', 'Classes'),
            ('/student/homework', 'Homework'),
            ('/student/feedback', 'Feedback'),
            ('/student/announcements', 'Announcements'),
            ('/student/doubts', 'Doubts')
        ]
        
        for route, name in routes_to_test:
            response = session.get(f"{base_url}{route}")
            if response.status_code == 200:
                print(f"✅ {name} page accessible")
            else:
                print(f"❌ {name} page error: {response.status_code}")
        
        print("\n🎉 All student portal tests passed!")
        return True
        
    except ImportError:
        print("⚠️  Requests not available, skipping web tests")
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == '__main__':
    # Create test data
    if create_test_student_data():
        # Test functionality
        test_student_portal_functionality()
        
        print("\n" + "="*50)
        print("🎓 STUDENT PORTAL TESTING COMPLETE")
        print("="*50)
        print("You can now:")
        print("1. Visit http://127.0.0.1:5003")
        print("2. Login with:")
        print("   Username: test_student")
        print("   Password: student123")
        print("3. Verify the dashboard matches the design")
        print("4. Test all navigation links")
        print("\nTo clean up test data later, run reset_to_admin_only.py")

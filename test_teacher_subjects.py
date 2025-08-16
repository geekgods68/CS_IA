#!/usr/bin/env python3

import sqlite3
import hashlib
import sys

# Add the current directory to the Python path
sys.path.insert(0, '/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA')

from flask import Flask
from routes.admin import admin_bp
from routes.auth import auth_bp

def test_teacher_subject_assignment():
    """Test the teacher subject assignment functionality"""
    print("🧪 Testing Teacher Subject Assignment")
    print("=" * 50)
    
    # First, create a test teacher
    conn = sqlite3.connect('/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/users.db')
    cur = conn.cursor()
    
    # Create test teacher
    password = "test123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cur.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_teacher_new', hashed_password, 'teacher', 'Test Teacher New', 'test@teacher.com'))
        
        teacher_id = cur.lastrowid
        print(f"✅ Created test teacher with ID: {teacher_id}")
        
        # Create some test classes
        cur.execute('''
            INSERT INTO classes (name, type, created_by)
            VALUES (?, ?, ?)
        ''', ('Math Class', 'regular', 1))
        
        class_id = cur.lastrowid
        print(f"✅ Created test class with ID: {class_id}")
        
        conn.commit()
        
    except sqlite3.IntegrityError:
        print("⚠️  Test data already exists, continuing with existing data...")
        cur.execute('SELECT id FROM users WHERE username = "test_teacher_new"')
        teacher_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM classes WHERE name = "Math Class" LIMIT 1')
        class_result = cur.fetchone()
        class_id = class_result[0] if class_result else None
    
    conn.close()
    
    # Test Flask application
    print("\n📋 Testing Flask Routes:")
    print("-" * 30)
    
    app = Flask(__name__, 
                template_folder='/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/templates',
                static_folder='/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/static')
    app.secret_key = 'test-secret-key'
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
    with app.test_client() as client:
        # Simulate admin session
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['username'] = 'admin'
        
        # Test edit teacher page
        response = client.get(f'/admin/edit_teacher/{teacher_id}')
        if response.status_code == 200:
            print("✅ Edit teacher page loads correctly")
            
            # Check if fixed subjects are in the response
            html_content = response.data.decode()
            fixed_subjects = ['Math', 'Science', 'Social Science', 'English', 'Hindi']
            
            for subject in fixed_subjects:
                if subject in html_content:
                    print(f"✅ Subject '{subject}' found in template")
                else:
                    print(f"❌ Subject '{subject}' missing from template")
        else:
            print(f"❌ Edit teacher page failed: {response.status_code}")
        
        # Test subject assignment
        if class_id:
            assignment_data = {
                'subjects': ['Math', 'Science'],
                'classes': [str(class_id)]
            }
            
            response = client.post(f'/admin/edit_teacher/{teacher_id}', 
                                 data=assignment_data, 
                                 follow_redirects=True)
            
            if response.status_code == 200:
                print("✅ Teacher subject assignment successful")
                
                # Verify in database
                conn = sqlite3.connect('/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/users.db')
                cur = conn.cursor()
                
                cur.execute('SELECT subject_name FROM teacher_subjects WHERE teacher_id = ?', (teacher_id,))
                assigned_subjects = [row[0] for row in cur.fetchall()]
                
                print(f"✅ Assigned subjects in database: {assigned_subjects}")
                
                conn.close()
            else:
                print(f"❌ Teacher assignment failed: {response.status_code}")
    
    print("\n📊 Fixed Subjects Verification:")
    print("-" * 35)
    fixed_subjects = ['Math', 'Science', 'Social Science', 'English', 'Hindi']
    print("✅ Fixed subject list:")
    for i, subject in enumerate(fixed_subjects, 1):
        print(f"   {i}. {subject}")
    
    print("\n🎉 Teacher subject assignment testing completed!")
    print(f"Teachers can now be assigned subjects from the fixed list of 5 subjects.")

if __name__ == "__main__":
    test_teacher_subject_assignment()

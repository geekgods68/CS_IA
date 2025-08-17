#!/usr/bin/env python3
"""
SMCT LMS Development Tools
Database seeding, resetting, and testing utilities
"""

import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_db():
    """Get database connection with foreign keys enabled"""
    conn = sqlite3.connect('users.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_to_admin_only():
    """Reset database to only admin user and clean schema"""
    print("🔄 Resetting database to admin-only state...")
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Delete all data except admin user (in correct order to avoid FK constraints)
        tables_to_clear = [
            'marks', 'assessments', 'attendance', 'feedback', 'doubts',
            'student_class_map', 'teacher_class_map', 'student_subjects', 'teacher_subjects', 
            'classes'
        ]
        
        # Disable foreign keys temporarily for cleanup
        cur.execute("PRAGMA foreign_keys = OFF")
        
        for table in tables_to_clear:
            try:
                cur.execute(f"DELETE FROM {table}")
                print(f"  ✅ Cleared {table} table")
            except sqlite3.OperationalError as e:
                if "no such table" not in str(e):
                    raise
                print(f"  ⚠️  Table {table} does not exist, skipping")
        
        # Re-enable foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        # Delete all users except admin
        cur.execute("DELETE FROM users WHERE role != 'admin'")
        deleted_users = cur.rowcount
        print(f"  ✅ Deleted {deleted_users} non-admin users")
        
        # Reset admin password to 'admin123'
        admin_hash = hash_password('admin123')
        cur.execute("""
            UPDATE users 
            SET password = ?, updated_on = CURRENT_TIMESTAMP 
            WHERE role = 'admin'
        """, (admin_hash,))
        
        conn.commit()
        print("  ✅ Reset admin password to 'admin123'")
        print("✅ Database reset complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error resetting database: {e}")
    finally:
        conn.close()

def seed_demo_data():
    """Create demo data for testing and development"""
    print("🌱 Seeding demo data...")
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create demo teachers
        teachers = [
            ('teacher1', 'teacher123', 'john.smith@school.edu', 'John Smith', '+1-555-0101', '123 Teacher St'),
            ('teacher2', 'teacher123', 'mary.jones@school.edu', 'Mary Jones', '+1-555-0102', '456 Education Ave'),
            ('teacher3', 'teacher123', 'david.wilson@school.edu', 'David Wilson', '+1-555-0103', '789 Academic Blvd'),
        ]
        
        teacher_ids = []
        for teacher in teachers:
            hashed_pw = hash_password(teacher[1])
            cur.execute("""
                INSERT INTO users (username, password, role, email, name, phone, address, created_by, created_on)
                VALUES (?, ?, 'teacher', ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            """, (teacher[0], hashed_pw, teacher[2], teacher[3], teacher[4], teacher[5]))
            teacher_ids.append(cur.lastrowid)
        
        print(f"  ✅ Created {len(teachers)} demo teachers")
        
        # Create demo students
        students = [
            ('student1', 'student123', 'alice.brown@student.edu', 'Alice Brown', '+1-555-0201', '111 Student Rd'),
            ('student2', 'student123', 'bob.davis@student.edu', 'Bob Davis', '+1-555-0202', '222 Learning Ln'),
            ('student3', 'student123', 'carol.miller@student.edu', 'Carol Miller', '+1-555-0203', '333 Study St'),
            ('student4', 'student123', 'daniel.garcia@student.edu', 'Daniel Garcia', '+1-555-0204', '444 Knowledge Ave'),
            ('student5', 'student123', 'emma.martinez@student.edu', 'Emma Martinez', '+1-555-0205', '555 Wisdom Way'),
            ('student6', 'student123', 'frank.rodriguez@student.edu', 'Frank Rodriguez', '+1-555-0206', '666 Scholar St'),
            ('student7', 'student123', 'grace.lopez@student.edu', 'Grace Lopez', '+1-555-0207', '777 Academic Ave'),
            ('student8', 'student123', 'henry.gonzalez@student.edu', 'Henry Gonzalez', '+1-555-0208', '888 Education Blvd'),
        ]
        
        student_ids = []
        for student in students:
            hashed_pw = hash_password(student[1])
            cur.execute("""
                INSERT INTO users (username, password, role, email, name, phone, address, created_by, created_on)
                VALUES (?, ?, 'student', ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            """, (student[0], hashed_pw, student[2], student[3], student[4], student[5]))
            student_ids.append(cur.lastrowid)
        
        print(f"  ✅ Created {len(students)} demo students")
        
        # Create demo classes
        classes = [
            ('Mathematics 10A', 10, 'Advanced Mathematics for Grade 10', 'https://meet.google.com/math-10a'),
            ('English 11B', 11, 'Literature and Composition', 'https://zoom.us/j/english11b'),
            ('Science 9C', 9, 'General Science and Lab Work', 'https://teams.microsoft.com/science9c'),
            ('History 12A', 12, 'World History and Current Events', 'https://meet.google.com/hist-12a'),
        ]
        
        class_ids = []
        for i, class_info in enumerate(classes):
            cur.execute("""
                INSERT INTO classes (name, grade_level, description, meeting_link, status, created_by, created_on)
                VALUES (?, ?, ?, ?, 'active', 1, CURRENT_TIMESTAMP)
            """, class_info)
            class_ids.append(cur.lastrowid)
        
        print(f"  ✅ Created {len(classes)} demo classes")
        
        # Assign teachers to subjects
        subjects = ['Mathematics', 'English', 'Science', 'History', 'Computer Science', 'Art']
        teacher_subject_assignments = [
            (teacher_ids[0], ['Mathematics', 'Computer Science']),  # John Smith
            (teacher_ids[1], ['English', 'History']),              # Mary Jones  
            (teacher_ids[2], ['Science', 'Art']),                  # David Wilson
        ]
        
        for teacher_id, assigned_subjects in teacher_subject_assignments:
            for subject in assigned_subjects:
                cur.execute("""
                    INSERT INTO teacher_subjects (teacher_id, subject_name, assigned_by, assigned_on)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                """, (teacher_id, subject))
        
        print("  ✅ Assigned subjects to teachers")
        
        # Assign teachers to classes
        teacher_class_assignments = [
            (teacher_ids[0], class_ids[0]),  # John -> Math 10A
            (teacher_ids[1], class_ids[1]),  # Mary -> English 11B
            (teacher_ids[2], class_ids[2]),  # David -> Science 9C
            (teacher_ids[1], class_ids[3]),  # Mary -> History 12A
        ]
        
        for teacher_id, class_id in teacher_class_assignments:
            cur.execute("""
                INSERT INTO teacher_class_map (teacher_id, class_id, assigned_by, assigned_on)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            """, (teacher_id, class_id))
        
        print("  ✅ Assigned teachers to classes")
        
        # Assign students to classes (distribute evenly)
        for i, student_id in enumerate(student_ids):
            # Assign each student to 2-3 classes
            assigned_classes = random.sample(class_ids, random.randint(2, 3))
            for class_id in assigned_classes:
                cur.execute("""
                    INSERT INTO student_class_map (student_id, class_id, status, assigned_by, assigned_on)
                    VALUES (?, ?, 'active', 1, CURRENT_TIMESTAMP)
                """, (student_id, class_id))
        
        print("  ✅ Assigned students to classes")
        
        # Assign subjects to students
        for student_id in student_ids:
            # Each student gets 3-4 subjects
            assigned_subjects = random.sample(subjects, random.randint(3, 4))
            for subject in assigned_subjects:
                cur.execute("""
                    INSERT INTO student_subjects (student_id, subject_name, assigned_by, assigned_on)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                """, (student_id, subject))
        
        print("  ✅ Assigned subjects to students")
        
        # Create demo assessments
        assessment_titles = [
            'Unit 1 Quiz', 'Midterm Exam', 'Chapter Test', 'Project Presentation',
            'Lab Report', 'Essay Assignment', 'Final Exam', 'Pop Quiz'
        ]
        
        assessment_count = 0
        for teacher_id, class_id in teacher_class_assignments:
            # Get teacher's subjects
            cur.execute("SELECT subject_name FROM teacher_subjects WHERE teacher_id = ?", (teacher_id,))
            teacher_subjects = [row[0] for row in cur.fetchall()]
            
            for subject in teacher_subjects:
                # Create 2-4 assessments per teacher per subject
                for i in range(random.randint(2, 4)):
                    title = f"{random.choice(assessment_titles)} {i+1}"  # Make titles unique
                    assessment_date = datetime.now() - timedelta(days=random.randint(1, 60))
                    max_score = random.choice([20, 25, 50, 100])
                    weight = random.choice([0.1, 0.2, 0.3, 0.4])
                    
                    # Ensure unique combination
                    try:
                        cur.execute("""
                            INSERT INTO assessments (class_id, subject_name, teacher_id, title, description, 
                                                   assessment_date, max_score, weight, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (class_id, subject, teacher_id, title, 
                             f"Assessment for {subject} - {title}", 
                             assessment_date.strftime('%Y-%m-%d'), max_score, weight))
                        
                        assessment_id = cur.lastrowid
                        assessment_count += 1
                        
                        # Add marks for some students in this class
                        cur.execute("""
                            SELECT student_id FROM student_class_map WHERE class_id = ?
                        """, (class_id,))
                        class_students = [row[0] for row in cur.fetchall()]
                        
                        # 70-90% of students have marks
                        if class_students:
                            students_with_marks = random.sample(class_students, 
                                                              max(1, int(len(class_students) * random.uniform(0.7, 0.9))))
                            
                            for student_id in students_with_marks:
                                # Generate realistic scores (bell curve around 75%)
                                base_score = max_score * 0.75
                                variation = max_score * 0.25
                                score = max(0, min(max_score, 
                                                 base_score + random.gauss(0, variation/3)))
                                
                                comments = [
                                    'Good work!', 'Well done!', 'Needs improvement', 
                                    'Excellent!', 'Keep it up!', 'See me after class',
                                    'Great effort!', 'Study harder', ''
                                ]
                                comment = random.choice(comments)
                                
                                cur.execute("""
                                    INSERT INTO marks (assessment_id, student_id, score, comment, updated_at)
                                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                                """, (assessment_id, student_id, round(score, 1), comment))
                    
                    except sqlite3.IntegrityError:
                        # Skip if duplicate, continue with next assessment
                        continue
        
        print(f"  ✅ Created {assessment_count} demo assessments with marks")
        
        # Create demo attendance records
        attendance_count = 0
        for class_id in class_ids:
            # Get students in this class
            cur.execute("""
                SELECT student_id FROM student_class_map WHERE class_id = ?
            """, (class_id,))
            class_students = [row[0] for row in cur.fetchall()]
            
            # Create attendance for last 14 days
            for day in range(14):
                attendance_date = datetime.now() - timedelta(days=day)
                
                for student_id in class_students:
                    # 85% attendance rate
                    status = random.choices(['present', 'absent', 'late'], 
                                          weights=[0.85, 0.10, 0.05])[0]
                    
                    notes = ''
                    if status == 'absent':
                        notes = random.choice(['Sick', 'Family emergency', 'Medical appointment', ''])
                    elif status == 'late':
                        notes = random.choice(['Traffic', 'Bus delay', 'Medical appointment', ''])
                    
                    cur.execute("""
                        INSERT INTO attendance (student_id, class_id, attendance_date, status, notes, 
                                             marked_on, marked_by)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
                    """, (student_id, class_id, attendance_date.strftime('%Y-%m-%d'), status, notes))
                    attendance_count += 1
        
        print(f"  ✅ Created {attendance_count} attendance records")
        
        conn.commit()
        print("✅ Demo data seeding complete!")
        
        # Print summary
        print("\n📊 Demo Data Summary:")
        print(f"  Teachers: {len(teachers)}")
        print(f"  Students: {len(students)}")
        print(f"  Classes: {len(classes)}")
        print(f"  Assessments: {assessment_count}")
        print(f"  Attendance Records: {attendance_count}")
        print("\n🔑 Login Credentials:")
        print("  Admin: admin / admin123")
        print("  Teachers: teacher1, teacher2, teacher3 / teacher123")
        print("  Students: student1-8 / student123")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding demo data: {e}")
        raise
    finally:
        conn.close()

def show_database_stats():
    """Display current database statistics"""
    print("📊 Database Statistics:")
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Count records in each table
        tables = [
            'users', 'classes', 'assessments', 'marks', 'attendance',
            'teacher_subjects', 'student_subjects', 'teacher_class_map', 'student_class_map'
        ]
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  {table}: {count}")
            except sqlite3.OperationalError:
                print(f"  {table}: Table not found")
        
        # Show user breakdown
        cur.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        print("\n👥 Users by Role:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Show recent activity
        cur.execute("""
            SELECT COUNT(*) FROM assessments 
            WHERE created_at >= date('now', '-7 days')
        """)
        recent_assessments = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE attendance_date >= date('now', '-7 days')
        """)
        recent_attendance = cur.fetchone()[0]
        
        print(f"\n📈 Recent Activity (Last 7 Days):")
        print(f"  New Assessments: {recent_assessments}")
        print(f"  Attendance Records: {recent_attendance}")
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    finally:
        conn.close()

def verify_schema():
    """Verify database schema integrity"""
    print("🔍 Verifying database schema...")
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Check if all required tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cur.fetchall()]
        
        required_tables = [
            'users', 'user_roles', 'user_role_map', 'subjects', 'classes',
            'teacher_subjects', 'student_subjects', 'teacher_class_map', 'student_class_map',
            'attendance', 'assessments', 'marks'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            print(f"  ❌ Missing tables: {missing_tables}")
            return False
        
        print("  ✅ All required tables exist")
        
        # Check foreign key constraints
        cur.execute("PRAGMA foreign_key_check")
        fk_violations = cur.fetchall()
        if fk_violations:
            print(f"  ❌ Foreign key violations: {fk_violations}")
            return False
        
        print("  ✅ Foreign key constraints valid")
        
        # Check for admin user
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cur.fetchone()[0]
        if admin_count == 0:
            print("  ❌ No admin user found")
            return False
        
        print("  ✅ Admin user exists")
        print("✅ Schema verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function with command-line interface"""
    if len(sys.argv) < 2:
        print("""
🛠️  SMCT LMS Development Tools

Usage: python devtools.py <command>

Commands:
  reset       - Reset database to admin-only state
  seed        - Seed database with demo data
  stats       - Show database statistics
  verify      - Verify database schema
  full-reset  - Reset and seed (complete refresh)

Examples:
  python devtools.py reset
  python devtools.py seed
  python devtools.py stats
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'reset':
        reset_to_admin_only()
    elif command == 'seed':
        seed_demo_data()
    elif command == 'stats':
        show_database_stats()
    elif command == 'verify':
        verify_schema()
    elif command == 'full-reset':
        print("🔄 Performing full reset...")
        reset_to_admin_only()
        print("\n" + "="*50 + "\n")
        seed_demo_data()
        print("\n" + "="*50 + "\n")
        show_database_stats()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python devtools.py' for help")

if __name__ == '__main__':
    main()

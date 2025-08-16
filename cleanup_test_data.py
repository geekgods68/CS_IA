#!/usr/bin/env python3

import sqlite3
import sys
import os

def reset_database_to_admin_only():
    """Reset database to only admin user and clean structure"""
    print("🧹 Resetting Database to Admin Only")
    print("=" * 50)
    
    conn = sqlite3.connect('/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/users.db')
    cur = conn.cursor()
    
    try:
        # 1. Remove all test data from mapping tables
        print("🗑️  Cleaning mapping tables...")
        cur.execute('DELETE FROM student_class_map')
        cur.execute('DELETE FROM teacher_class_map') 
        cur.execute('DELETE FROM student_subjects')
        cur.execute('DELETE FROM teacher_subjects')
        
        # 2. Remove all test classes
        print("🗑️  Removing test classes...")
        cur.execute('DELETE FROM classes')
        
        # 3. Remove all doubts and feedback
        print("🗑️  Removing doubts and feedback...")
        cur.execute('DELETE FROM doubts')
        cur.execute('DELETE FROM feedback')
        
        # 4. Remove all users except admin
        print("🗑️  Removing all non-admin users...")
        cur.execute("DELETE FROM users WHERE username != 'admin'")
        
        # 5. Reset auto-increment counters
        print("🔄 Resetting auto-increment counters...")
        cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'classes', 'doubts', 'feedback')")
        
        conn.commit()
        
        # Verify the cleanup
        print("\n✅ Database Reset Complete:")
        
        # Check remaining users
        cur.execute('SELECT id, username, role FROM users')
        users = cur.fetchall()
        print(f"   👤 Users remaining: {len(users)}")
        for user in users:
            print(f"      - {user[1]} ({user[2]})")
        
        # Check empty tables
        tables = ['classes', 'student_class_map', 'teacher_class_map', 'student_subjects', 'teacher_subjects', 'doubts', 'feedback']
        for table in tables:
            cur.execute(f'SELECT COUNT(*) FROM {table}')
            count = cur.fetchone()[0]
            print(f"   📊 {table}: {count} records")
        
        print("\n🎉 Database successfully reset to production state!")
        print("\nAdmin Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\nThe system is now ready for real users and data.")
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    # Confirm the action
    print("⚠️  WARNING: This will delete ALL test data and users except admin!")
    confirm = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if confirm == 'yes':
        reset_database_to_admin_only()
    else:
        print("Operation cancelled.")

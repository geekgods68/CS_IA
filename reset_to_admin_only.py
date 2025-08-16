#!/usr/bin/env python3

import sqlite3
import hashlib

def reset_database_to_admin_only():
    """Reset database to contain only the admin user"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    print("🔄 Resetting database to admin only...")
    print("=" * 50)
    
    # First, let's see what we have
    cur.execute('SELECT id, username, role FROM users')
    users = cur.fetchall()
    print(f"Current users in database: {len(users)}")
    for user in users:
        print(f"   - ID {user[0]}: {user[1]} ({user[2]})")
    
    # Remove all non-admin users
    cur.execute('DELETE FROM users WHERE role != "admin"')
    deleted_users = cur.rowcount
    print(f"\n✅ Deleted {deleted_users} non-admin users")
    
    # Clear all assignment tables
    tables_to_clear = [
        'student_class_map',
        'teacher_class_map', 
        'student_subjects',
        'teacher_subjects',
        'feedback',
        'doubts'
    ]
    
    for table in tables_to_clear:
        cur.execute(f'DELETE FROM {table}')
        deleted_count = cur.rowcount
        print(f"✅ Cleared {deleted_count} records from {table}")
    
    # Remove all classes except keep one for testing if needed
    cur.execute('SELECT COUNT(*) FROM classes')
    class_count = cur.fetchone()[0]
    
    if class_count > 0:
        cur.execute('DELETE FROM classes')
        print(f"✅ Deleted {class_count} classes")
    
    # Remove all subjects
    cur.execute('SELECT COUNT(*) FROM subjects')
    subject_count = cur.fetchone()[0]
    
    if subject_count > 0:
        cur.execute('DELETE FROM subjects')
        print(f"✅ Deleted {subject_count} subjects")
    
    # Verify admin user exists and get details
    cur.execute('SELECT id, username, role FROM users WHERE role = "admin"')
    admin_user = cur.fetchone()
    
    if admin_user:
        print(f"\n✅ Admin user preserved:")
        print(f"   - ID: {admin_user[0]}")
        print(f"   - Username: {admin_user[1]}")
        print(f"   - Role: {admin_user[2]}")
    else:
        # Create admin user if not exists
        admin_password = "admin123"
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
        
        cur.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'admin', 'Administrator', 'admin@system.com'))
        
        admin_id = cur.lastrowid
        print(f"✅ Created new admin user with ID: {admin_id}")
        print(f"   - Username: admin")
        print(f"   - Password: admin123")
    
    # Final verification
    cur.execute('SELECT COUNT(*) FROM users')
    final_user_count = cur.fetchone()[0]
    
    cur.execute('SELECT username, role FROM users')
    remaining_users = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Database Reset Summary:")
    print(f"   - Total users remaining: {final_user_count}")
    print(f"   - Users: {', '.join([f'{u[0]} ({u[1]})' for u in remaining_users])}")
    print(f"   - All test data removed")
    print(f"   - All classes and assignments cleared")
    
    print(f"\n🎉 Database successfully reset to admin-only state!")
    print(f"You can now login with username 'admin' and password 'admin123'")

if __name__ == "__main__":
    response = input("⚠️  This will delete ALL non-admin users and test data. Continue? (y/N): ")
    if response.lower() == 'y':
        reset_database_to_admin_only()
    else:
        print("❌ Operation cancelled.")

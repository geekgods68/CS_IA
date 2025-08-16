#!/usr/bin/env python3
"""
Database reset script for School Management Portal
Backs up current database and creates a fresh one with only admin user
"""

import sqlite3
import hashlib
import os
import shutil
from datetime import datetime

def simple_hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def backup_database():
    """Create a backup of the current database"""
    if os.path.exists('users.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'users_backup_{timestamp}.db'
        shutil.copy2('users.db', backup_name)
        print(f"✅ Database backed up as: {backup_name}")
        return backup_name
    else:
        print("ℹ️  No existing database found to backup")
        return None

def reset_database():
    """Reset database to initial state with only admin user"""
    
    # Backup existing database
    backup_file = backup_database()
    
    # Remove existing database
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("🗑️  Existing database removed")
    
    # Create fresh database
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    print("🔧 Creating fresh database structure...")
    
    # Create users table
    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            email TEXT,
            name TEXT,
            phone TEXT,
            address TEXT,
            created_by INTEGER,
            created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            updated_on DATETIME,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Create user_roles table
    cur.execute('''
        CREATE TABLE user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_on DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_role_map table
    cur.execute('''
        CREATE TABLE user_role_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES user_roles(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(user_id, role_id)
        )
    ''')
    
    # Create subjects table
    cur.execute('''
        CREATE TABLE subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            grade_level TEXT,
            created_by INTEGER,
            created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Create classes table
    cur.execute('''
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'regular',
            description TEXT,
            grade_level TEXT,
            section TEXT,
            schedule_days TEXT,
            schedule_time_start TEXT,
            schedule_time_end TEXT,
            schedule_pdf_path TEXT,
            room_number TEXT,
            max_students INTEGER DEFAULT 30,
            status TEXT DEFAULT 'active',
            created_by INTEGER,
            created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            updated_on DATETIME,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    ''')
    
    # Create student_class_map table
    cur.execute('''
        CREATE TABLE student_class_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (class_id) REFERENCES classes(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(student_id, class_id)
        )
    ''')
    
    # Create teacher_class_map table
    cur.execute('''
        CREATE TABLE teacher_class_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT DEFAULT 'primary',
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (class_id) REFERENCES classes(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(teacher_id, class_id)
        )
    ''')
    
    # Create student_subjects table
    cur.execute('''
        CREATE TABLE student_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            assigned_by INTEGER,
            assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(student_id, subject_name)
        )
    ''')
    
    # Create teacher_subjects table
    cur.execute('''
        CREATE TABLE teacher_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            assigned_by INTEGER,
            assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(teacher_id, subject_name)
        )
    ''')
    
    # Create feedback table
    cur.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            feedback_text TEXT NOT NULL,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    ''')
    
    # Create doubts table
    cur.execute('''
        CREATE TABLE doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            doubt_text TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_on DATETIME,
            resolved_by INTEGER,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (resolved_by) REFERENCES users(id)
        )
    ''')
    
    print("📋 Inserting initial data...")
    
    # Insert initial user roles
    roles = [
        ('admin', 'Administrator with full access'),
        ('teacher', 'Teacher with classroom management access'),
        ('student', 'Student with learning portal access')
    ]
    
    cur.executemany('INSERT INTO user_roles (role_name, description) VALUES (?, ?)', roles)
    
    # Insert admin user
    admin_password = simple_hash_password('admin123')
    cur.execute('''
        INSERT INTO users (username, password, role, name, email)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'admin', 'System Administrator', 'admin@school.edu'))
    
    admin_user_id = cur.lastrowid
    
    # Assign admin role to admin user
    cur.execute('SELECT id FROM user_roles WHERE role_name = ?', ('admin',))
    admin_role_id = cur.fetchone()[0]
    
    cur.execute('''
        INSERT INTO user_role_map (user_id, role_id, assigned_by)
        VALUES (?, ?, ?)
    ''', (admin_user_id, admin_role_id, admin_user_id))
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database reset completed successfully!")
    print("=" * 50)
    print("🔑 Admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 50)
    
    if backup_file:
        print(f"📁 Previous database backed up as: {backup_file}")
    
    print("\nℹ️  The database now contains:")
    print("   • 1 admin user")
    print("   • 3 user roles (admin, teacher, student)")
    print("   • Empty tables for all other entities")

if __name__ == '__main__':
    print("🔄 Starting database reset...")
    print("⚠️  This will remove all existing data!")
    
    confirm = input("\nDo you want to continue? (yes/no): ").lower().strip()
    
    if confirm in ['yes', 'y']:
        reset_database()
    else:
        print("❌ Database reset cancelled.")

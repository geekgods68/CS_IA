#!/usr/bin/env python3
"""
Test script to verify the database reset resolved foreign key constraint issues.
This script tests user creation and deletion to ensure everything works correctly.
"""

import sqlite3
import sys
from datetime import datetime

def test_database_reset():
    """Test that the database was reset correctly and users can be created/deleted."""
    
    print("=== Testing Database Reset ===")
    
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Test 1: Verify initial state
        print("\n1. Checking initial database state...")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Initial user count: {user_count}")
        assert user_count == 1, f"Expected 1 user (admin), got {user_count}"
        
        cursor.execute("SELECT username FROM users")
        admin_user = cursor.fetchone()[0]
        print(f"   Admin user: {admin_user}")
        assert admin_user == 'admin', f"Expected admin user, got {admin_user}"
        
        # Test 2: Create a test user
        print("\n2. Creating test users...")
        
        # Create teacher user
        cursor.execute("""
            INSERT INTO users (username, password, created_by, created_on) 
            VALUES (?, ?, ?, ?)
        """, ('test_teacher', 'hashed_password', 1, datetime.now()))
        teacher_id = cursor.lastrowid
        print(f"   Created teacher user with ID: {teacher_id}")
        
        # Assign teacher role
        cursor.execute("""
            INSERT INTO user_role_map (user_id, role_id, assigned_by, assigned_on)
            VALUES (?, (SELECT id FROM user_roles WHERE role_name = 'teacher'), ?, ?)
        """, (teacher_id, 1, datetime.now()))
        
        # Create student user
        cursor.execute("""
            INSERT INTO users (username, password, created_by, created_on) 
            VALUES (?, ?, ?, ?)
        """, ('test_student', 'hashed_password', 1, datetime.now()))
        student_id = cursor.lastrowid
        print(f"   Created student user with ID: {student_id}")
        
        # Assign student role
        cursor.execute("""
            INSERT INTO user_role_map (user_id, role_id, assigned_by, assigned_on)
            VALUES (?, (SELECT id FROM user_roles WHERE role_name = 'student'), ?, ?)
        """, (student_id, 1, datetime.now()))
        
        conn.commit()
        
        # Test 3: Verify users were created
        print("\n3. Verifying user creation...")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Total users after creation: {user_count}")
        assert user_count == 3, f"Expected 3 users, got {user_count}"
        
        # Test 4: Test user deletion (this was failing before)
        print("\n4. Testing user deletion...")
        
        # Delete student user and related records
        cursor.execute("DELETE FROM user_role_map WHERE user_id = ?", (student_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))
        print(f"   Deleted student user (ID: {student_id})")
        
        # Delete teacher user and related records
        cursor.execute("DELETE FROM user_role_map WHERE user_id = ?", (teacher_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (teacher_id,))
        print(f"   Deleted teacher user (ID: {teacher_id})")
        
        conn.commit()
        
        # Test 5: Verify users were deleted
        print("\n5. Verifying user deletion...")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Total users after deletion: {user_count}")
        assert user_count == 1, f"Expected 1 user (admin), got {user_count}"
        
        cursor.execute("SELECT username FROM users")
        remaining_user = cursor.fetchone()[0]
        print(f"   Remaining user: {remaining_user}")
        assert remaining_user == 'admin', f"Expected admin user, got {remaining_user}"
        
        # Test 6: Verify no orphaned role mappings
        cursor.execute("SELECT COUNT(*) FROM user_role_map")
        role_mapping_count = cursor.fetchone()[0]
        print(f"   Role mappings count: {role_mapping_count}")
        assert role_mapping_count == 1, f"Expected 1 role mapping (admin), got {role_mapping_count}"
        
        print("\n✅ All tests passed! Database reset was successful.")
        print("✅ Foreign key constraint issues have been resolved.")
        print("✅ Users can now be created and deleted without issues.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn:
            conn.close()

def test_table_structure():
    """Verify that all required tables exist with correct structure."""
    
    print("\n=== Testing Table Structure ===")
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'users', 'user_roles', 'user_role_map', 'user_profiles',
            'classes', 'subjects', 'teacher_subject_map', 'teacher_subjects',
            'student_subjects', 'teacher_class_map', 'student_class_map', 'attendance', 
            'resources', 'doubts', 'assessments', 'announcements', 'feedback'
        ]
        
        print(f"Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        extra_tables = set(tables) - set(expected_tables)
        if extra_tables:
            print(f"ℹ️ Extra tables: {extra_tables}")
        
        print("✅ All required tables exist.")
        return True
        
    except Exception as e:
        print(f"❌ Table structure test failed: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Database Reset Verification Test")
    print("=" * 40)
    
    # Test table structure
    structure_ok = test_table_structure()
    
    # Test database functionality
    db_ok = test_database_reset()
    
    if structure_ok and db_ok:
        print("\n🎉 All tests passed! Database is ready for use.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the issues above.")
        sys.exit(1)

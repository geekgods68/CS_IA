#!/usr/bin/env python3

"""
Final comprehensive test for SMCT LMS admin attendance functionality
"""

import sqlite3
from app import create_app

def test_attendance_functionality():
    print("=== COMPREHENSIVE ATTENDANCE TEST ===")
    
    app = create_app()
    
    with app.test_client() as client:
        # Simulate admin login
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        print("\n1. Testing Admin Attendance Dashboard...")
        response = client.get('/admin/attendance')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.get_data(as_text=True)
        
        required_elements = [
            "Attendance Management",
            "Mark Attendance", 
            "Generate Report",
            "Quick Actions",
            "Recent Attendance Records",
            "Select Class"
        ]
        
        for element in required_elements:
            assert element in content, f"Missing: {element}"
            print(f"✅ {element}")
        
        print("\n2. Testing Mark Attendance Page...")
        # Get first available class
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM classes WHERE status = 'active' LIMIT 1")
        class_result = cur.fetchone()
        
        if class_result:
            class_id = class_result[0]
            response = client.get(f'/admin/attendance/mark?class_id={class_id}&date=2025-08-16')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print("✅ Mark attendance page loads with parameters")
        else:
            print("⚠️  No classes available for testing")
        
        print("\n3. Testing Attendance Report Page...")
        response = client.get('/admin/attendance/report')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Attendance report page loads")
        
        print("\n4. Testing Mark Attendance with Class...")
        if class_result:
            # This is already tested above, so just confirm
            print("✅ Mark attendance with class parameters works")
        
        conn.close()
        
        print("\n5. Testing Attendance Report with Class...")
        if class_result:
            response = client.get(f'/admin/attendance/report?class_id={class_id}')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print("✅ Attendance report with class parameters works")
        
        print("\n✅ ALL ATTENDANCE TESTS PASSED!")

def test_database_integrity():
    print("\n=== DATABASE INTEGRITY TEST ===")
    
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Check required tables exist
        tables = ['classes', 'attendance', 'users']
        for table in tables:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cur.fetchone(), f"Table {table} missing"
            print(f"✅ Table {table} exists")
        
        # Check classes have meeting_link (not room_number)
        cur.execute("PRAGMA table_info(classes)")
        columns = [row[1] for row in cur.fetchall()]
        assert 'meeting_link' in columns, "meeting_link column missing from classes"
        assert 'room_number' not in columns, "room_number column should be removed"
        print("✅ Classes table has meeting_link column")
        
        # Check attendance table structure
        cur.execute("PRAGMA table_info(attendance)")
        attendance_columns = [row[1] for row in cur.fetchall()]
        required_attendance_cols = ['id', 'student_id', 'class_id', 'attendance_date', 'status', 'notes', 'marked_by', 'marked_on']
        
        for col in required_attendance_cols:
            assert col in attendance_columns, f"Attendance column {col} missing"
        print("✅ Attendance table structure correct")
        
        # Check data integrity
        cur.execute("SELECT COUNT(*) FROM classes WHERE status = 'active'")
        active_classes = cur.fetchone()[0]
        print(f"✅ Active classes: {active_classes}")
        
        cur.execute("SELECT COUNT(*) FROM attendance")
        attendance_records = cur.fetchone()[0]
        print(f"✅ Attendance records: {attendance_records}")
        
        conn.close()
        print("✅ DATABASE INTEGRITY VERIFIED!")
        
    except Exception as e:
        print(f"❌ Database integrity error: {e}")
        raise

def main():
    try:
        test_database_integrity()
        test_attendance_functionality()
        print("\n🎉 ALL TESTS PASSED! ATTENDANCE FEATURE IS WORKING CORRECTLY!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

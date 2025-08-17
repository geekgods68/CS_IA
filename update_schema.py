#!/usr/bin/env python3
"""
Update database schema to add attendance table
"""

import sqlite3

def update_database_schema():
    """Add attendance table to existing database"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    try:
        print("=== Updating Database Schema ===")
        
        # Check if attendance table already exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
        if cur.fetchone():
            print("✓ Attendance table already exists")
            return
        
        print("Creating attendance table...")
        
        # Create attendance table
        cur.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                attendance_date DATE NOT NULL,
                status TEXT NOT NULL DEFAULT 'present',  -- present, absent, late, excused
                marked_by INTEGER NOT NULL,  -- Teacher or admin who marked attendance
                marked_on DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,  -- Optional notes about attendance (reason for absence, etc.)
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (marked_by) REFERENCES users(id),
                UNIQUE(student_id, class_id, attendance_date)
            )
        ''')
        
        print("✓ Attendance table created")
        
        # Create indexes for attendance table
        print("Creating attendance indexes...")
        
        cur.execute('CREATE INDEX idx_attendance_student ON attendance(student_id)')
        print("✓ Created index on student_id")
        
        cur.execute('CREATE INDEX idx_attendance_class ON attendance(class_id)')
        print("✓ Created index on class_id")
        
        cur.execute('CREATE INDEX idx_attendance_date ON attendance(attendance_date)')
        print("✓ Created index on attendance_date")
        
        cur.execute('CREATE INDEX idx_attendance_status ON attendance(status)')
        print("✓ Created index on status")
        
        cur.execute('CREATE INDEX idx_attendance_marked_by ON attendance(marked_by)')
        print("✓ Created index on marked_by")
        
        cur.execute('CREATE INDEX idx_attendance_marked_on ON attendance(marked_on)')
        print("✓ Created index on marked_on")
        
        conn.commit()
        print("\n=== Database Schema Update Complete ===")
        print("Attendance table and indexes have been added to the database.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema()

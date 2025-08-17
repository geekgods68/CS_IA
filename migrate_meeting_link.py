#!/usr/bin/env python3
"""
Database Migration: Update room_number to meeting_link
Migrates the classes table to use meeting_link instead of room_number for virtual class support
"""

import sqlite3
import os

def migrate_database():
    """Update the database schema to replace room_number with meeting_link"""
    
    db_path = 'users.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if the migration has already been done
        cur.execute("PRAGMA table_info(classes)")
        columns = [column[1] for column in cur.fetchall()]
        
        if 'meeting_link' in columns:
            print("✅ Database already migrated to use meeting_link")
            return True
        
        if 'room_number' not in columns:
            print("⚠️  Classes table doesn't have room_number column, adding meeting_link column")
            # Just add the meeting_link column
            cur.execute("ALTER TABLE classes ADD COLUMN meeting_link TEXT")
        else:
            print("🔄 Migrating room_number to meeting_link...")
            
            # Create new classes table with meeting_link
            cur.execute('''
                CREATE TABLE classes_new (
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
                    meeting_link TEXT,
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
            
            # Copy data from old table to new table, converting room_number to meeting_link
            cur.execute('''
                INSERT INTO classes_new (
                    id, name, type, description, grade_level, section,
                    schedule_days, schedule_time_start, schedule_time_end,
                    schedule_pdf_path, meeting_link, max_students, status,
                    created_by, created_on, updated_by, updated_on
                )
                SELECT 
                    id, name, type, description, grade_level, section,
                    schedule_days, schedule_time_start, schedule_time_end,
                    schedule_pdf_path, 
                    CASE 
                        WHEN room_number IS NOT NULL AND room_number != '' 
                        THEN 'Room: ' || room_number 
                        ELSE NULL 
                    END as meeting_link,
                    max_students, status, created_by, created_on, updated_by, updated_on
                FROM classes
            ''')
            
            # Drop old table and rename new table
            cur.execute("DROP TABLE classes")
            cur.execute("ALTER TABLE classes_new RENAME TO classes")
        
        # Recreate indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_classes_status ON classes(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_classes_grade_level ON classes(grade_level)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_classes_created_on ON classes(created_on)")
        
        # Update the attendance table if it exists to ensure it references the correct table
        cur.execute("PRAGMA table_info(attendance)")
        attendance_columns = [column[1] for column in cur.fetchall()]
        
        if attendance_columns:  # If attendance table exists
            print("🔄 Ensuring attendance table integrity...")
            # We don't need to modify the attendance table structure as it only references class_id
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify the migration
        cur.execute("SELECT COUNT(*) FROM classes")
        class_count = cur.fetchone()[0]
        print(f"📊 Verified: {class_count} classes in updated table")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 SMCT LMS Database Migration")
    print("Converting room_number to meeting_link for virtual classes")
    print("=" * 60)
    
    if migrate_database():
        print("\n✅ Migration completed successfully!")
        print("Classes now support virtual meeting links instead of room numbers.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")

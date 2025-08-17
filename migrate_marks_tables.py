#!/usr/bin/env python3

"""
Migration script to add assessments and marks tables for Teacher Marks & Reports feature
"""

import sqlite3
import os

def migrate_marks_tables():
    """Add assessments and marks tables to the database"""
    print("=== Migrating Marks & Reports Tables ===")
    
    db_path = 'users.db'
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Enable foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        
        # Check if tables already exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessments'")
        assessments_exists = cur.fetchone() is not None
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marks'")
        marks_exists = cur.fetchone() is not None
        
        if assessments_exists and marks_exists:
            print("✅ Assessments and marks tables already exist")
            return True
        
        print("Creating assessments table...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                assessment_date DATE NOT NULL,
                max_score REAL NOT NULL CHECK(max_score > 0),
                weight REAL NOT NULL DEFAULT 1.0 CHECK(weight >= 0 AND weight <= 1),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(class_id, subject_name, title, assessment_date)
            )
        ''')
        
        print("Creating marks table...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                score REAL NOT NULL CHECK(score >= 0),
                comment TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(assessment_id, student_id)
            )
        ''')
        
        print("Creating indexes...")
        cur.execute('CREATE INDEX IF NOT EXISTS idx_assessments_class_subject ON assessments(class_id, subject_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_assessments_teacher_date ON assessments(teacher_id, assessment_date)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_marks_assessment ON marks(assessment_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_marks_student ON marks(student_id)')
        
        print("Creating triggers...")
        cur.execute('''
            CREATE TRIGGER IF NOT EXISTS check_mark_score 
                BEFORE INSERT ON marks
                FOR EACH ROW
            BEGIN
                SELECT CASE 
                    WHEN NEW.score > (SELECT max_score FROM assessments WHERE id = NEW.assessment_id)
                    THEN RAISE(ABORT, 'Score cannot exceed maximum score for assessment')
                END;
            END
        ''')
        
        cur.execute('''
            CREATE TRIGGER IF NOT EXISTS check_mark_score_update 
                BEFORE UPDATE ON marks
                FOR EACH ROW
            BEGIN
                SELECT CASE 
                    WHEN NEW.score > (SELECT max_score FROM assessments WHERE id = NEW.assessment_id)
                    THEN RAISE(ABORT, 'Score cannot exceed maximum score for assessment')
                END;
            END
        ''')
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('assessments', 'marks')")
        tables = cur.fetchall()
        print(f"✅ Created tables: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    migrate_marks_tables()

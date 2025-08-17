-- SMCT LMS Database Schema
-- School Management and Communication Technology - Learning Management System
-- Created for IBDP Computer Science Internal Assessment

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CORE USER MANAGEMENT TABLES
-- ============================================================================

-- Main users table with basic authentication and profile information
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- SHA256 hashed passwords
    role TEXT NOT NULL DEFAULT 'student',  -- admin, teacher, student
    email TEXT,
    name TEXT,
    phone TEXT,
    address TEXT,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- User roles definition table for role-based access control
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for user-role mapping (supports multiple roles per user)
CREATE TABLE user_role_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(user_id, role_id)
);

-- ============================================================================
-- ACADEMIC STRUCTURE TABLES
-- ============================================================================

-- Subjects definition (currently using fixed subject list in application)
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    grade_level TEXT,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Classes/courses with scheduling and organizational information
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'regular',  -- regular, advanced, remedial
    description TEXT,
    grade_level TEXT,
    section TEXT,
    schedule_days TEXT,  -- JSON array of days
    schedule_time_start TEXT,  -- HH:MM format
    schedule_time_end TEXT,    -- HH:MM format
    schedule_pdf_path TEXT,    -- File path for uploaded PDF schedules
    meeting_link TEXT,  -- Virtual meeting link for online classes (Zoom, Teams, etc.)
    max_students INTEGER DEFAULT 30,
    status TEXT DEFAULT 'active',  -- active, inactive, archived
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- ============================================================================
-- ASSIGNMENT AND MAPPING TABLES
-- ============================================================================

-- Student-to-class assignments with enrollment tracking
CREATE TABLE student_class_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',  -- active, inactive, dropped
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(student_id, class_id)
);

-- Teacher-to-class assignments with teaching roles
CREATE TABLE teacher_class_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT DEFAULT 'primary',  -- primary, assistant, substitute
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(teacher_id, class_id)
);

-- Student subject assignments (fixed subjects: Math, Science, Social Science, English, Hindi)
CREATE TABLE student_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_name TEXT NOT NULL,  -- Using fixed subject names instead of FK
    assigned_by INTEGER,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(student_id, subject_name)
);

-- Teacher subject assignments (subjects they are qualified to teach)
CREATE TABLE teacher_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_name TEXT NOT NULL,  -- Using fixed subject names instead of FK
    assigned_by INTEGER,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(teacher_id, subject_name)
);

-- ============================================================================
-- COMMUNICATION AND FEEDBACK TABLES
-- ============================================================================

-- Student feedback system for anonymous suggestions and complaints
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),  -- 1-5 star rating system
    submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- ATTENDANCE TRACKING TABLES
-- ============================================================================

-- Student attendance tracking for classes
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'present',  -- present, absent, late, excused
    remarks TEXT,  -- Optional notes for attendance status
    marked_by INTEGER NOT NULL,  -- Teacher/admin who marked attendance
    marked_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id),
    -- Ensure student_id references a user with student role
    CONSTRAINT check_student_role CHECK (
        student_id IN (SELECT id FROM users WHERE role = 'student')
    ),
    -- Ensure only one attendance record per student per class per date
    UNIQUE(student_id, class_id, attendance_date)
);

-- Student doubts/questions system with teacher response capability
CREATE TABLE doubts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,  -- Subject category for the doubt
    doubt_text TEXT NOT NULL,
    status TEXT DEFAULT 'open',  -- open, answered, resolved
    submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_on DATETIME,
    resolved_by INTEGER,  -- Teacher/admin who resolved the doubt
    response TEXT,  -- Response text from teacher/admin
    response_time DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id)
);

-- ============================================================================
-- ASSESSMENTS AND MARKS TABLES
-- ============================================================================

-- Assessments created by teachers for classes and subjects
CREATE TABLE assessments (
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
);

-- Student marks for assessments
CREATE TABLE marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    score REAL NOT NULL CHECK(score >= 0),
    comment TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(assessment_id, student_id)
);

-- Indexes for assessments table
CREATE INDEX idx_assessments_class_subject ON assessments(class_id, subject_name);
CREATE INDEX idx_assessments_teacher_date ON assessments(teacher_id, assessment_date);

-- Indexes for marks table
CREATE INDEX idx_marks_assessment ON marks(assessment_id);
CREATE INDEX idx_marks_student ON marks(student_id);

-- Trigger to enforce score <= max_score constraint
CREATE TRIGGER check_mark_score 
    BEFORE INSERT ON marks
    FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN NEW.score > (SELECT max_score FROM assessments WHERE id = NEW.assessment_id)
        THEN RAISE(ABORT, 'Score cannot exceed maximum score for assessment')
    END;
END;

-- Trigger to enforce score <= max_score constraint on updates
CREATE TRIGGER check_mark_score_update 
    BEFORE UPDATE ON marks
    FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN NEW.score > (SELECT max_score FROM assessments WHERE id = NEW.assessment_id)
        THEN RAISE(ABORT, 'Score cannot exceed maximum score for assessment')
    END;
END;

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- User authentication and lookup indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_on ON users(created_on);

-- Class and assignment lookup indexes
CREATE INDEX idx_classes_status ON classes(status);
CREATE INDEX idx_classes_grade_level ON classes(grade_level);
CREATE INDEX idx_classes_created_on ON classes(created_on);

-- Student assignment indexes
CREATE INDEX idx_student_class_map_student ON student_class_map(student_id);
CREATE INDEX idx_student_class_map_class ON student_class_map(class_id);
CREATE INDEX idx_student_class_map_status ON student_class_map(status);

-- Teacher assignment indexes
CREATE INDEX idx_teacher_class_map_teacher ON teacher_class_map(teacher_id);
CREATE INDEX idx_teacher_class_map_class ON teacher_class_map(class_id);

-- Subject assignment indexes
CREATE INDEX idx_student_subjects_student ON student_subjects(student_id);
CREATE INDEX idx_student_subjects_subject ON student_subjects(subject_name);
CREATE INDEX idx_teacher_subjects_teacher ON teacher_subjects(teacher_id);
CREATE INDEX idx_teacher_subjects_subject ON teacher_subjects(subject_name);

-- Communication system indexes
CREATE INDEX idx_feedback_student ON feedback(student_id);
CREATE INDEX idx_feedback_submitted ON feedback(submitted_on);
CREATE INDEX idx_doubts_student ON doubts(student_id);
CREATE INDEX idx_doubts_status ON doubts(status);
CREATE INDEX idx_doubts_subject ON doubts(subject);
CREATE INDEX idx_doubts_submitted ON doubts(submitted_on);

-- Attendance system indexes
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_class ON attendance(class_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_attendance_marked_by ON attendance(marked_by);
CREATE INDEX idx_attendance_marked_on ON attendance(marked_on);

-- ============================================================================
-- INITIAL DATA INSERTION
-- ============================================================================

-- Insert default user roles
INSERT INTO user_roles (role_name, description) VALUES 
    ('admin', 'System administrator with full access'),
    ('teacher', 'Teaching staff with class and student management access'),
    ('student', 'Students with access to classes, doubts, and feedback');

-- Insert default admin user (password: admin123, hashed with SHA256)
INSERT INTO users (username, password, role, name, email, created_on) VALUES 
    ('admin', 'ac9689e2272427085e35b9d3e3e8bed88cb3434828b43b86fc0596cad4c6e270', 'admin', 'System Administrator', 'admin@smctlms.edu', CURRENT_TIMESTAMP);

-- Insert default subjects (fixed subject list used in application)
INSERT INTO subjects (name, description, created_by) VALUES 
    ('Math', 'Mathematics including algebra, geometry, and calculus', 1),
    ('Science', 'General science including physics, chemistry, and biology', 1),
    ('Social Science', 'History, geography, civics, and economics', 1),
    ('English', 'English language, literature, and communication skills', 1),
    ('Hindi', 'Hindi language and literature', 1);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for user details with role information
CREATE VIEW user_details AS
SELECT 
    u.id,
    u.username,
    u.role,
    u.name,
    u.email,
    u.phone,
    u.address,
    u.created_on,
    creator.username as created_by_username
FROM users u
LEFT JOIN users creator ON u.created_by = creator.id;

-- View for class enrollment statistics
CREATE VIEW class_enrollment_stats AS
SELECT 
    c.id,
    c.name,
    c.type,
    c.grade_level,
    c.status,
    COUNT(DISTINCT scm.student_id) as student_count,
    COUNT(DISTINCT tcm.teacher_id) as teacher_count,
    c.max_students,
    ROUND((COUNT(DISTINCT scm.student_id) * 100.0 / c.max_students), 2) as enrollment_percentage
FROM classes c
LEFT JOIN student_class_map scm ON c.id = scm.class_id AND scm.status = 'active'
LEFT JOIN teacher_class_map tcm ON c.id = tcm.class_id
GROUP BY c.id, c.name, c.type, c.grade_level, c.status, c.max_students;

-- View for student dashboard statistics
CREATE VIEW student_dashboard_stats AS
SELECT 
    u.id as student_id,
    u.username,
    COUNT(DISTINCT scm.class_id) as enrolled_classes,
    COUNT(DISTINCT ss.subject_name) as assigned_subjects,
    COUNT(DISTINCT CASE WHEN d.status = 'open' THEN d.id END) as pending_doubts,
    COUNT(DISTINCT d.id) as total_doubts
FROM users u
LEFT JOIN student_class_map scm ON u.id = scm.student_id AND scm.status = 'active'
LEFT JOIN student_subjects ss ON u.id = ss.student_id
LEFT JOIN doubts d ON u.id = d.student_id
WHERE u.role = 'student'
GROUP BY u.id, u.username;

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- ============================================================================

-- Trigger to update user updated_on timestamp
CREATE TRIGGER update_users_timestamp 
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users SET updated_on = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update class updated_on timestamp
CREATE TRIGGER update_classes_timestamp 
    AFTER UPDATE ON classes
    FOR EACH ROW
BEGIN
    UPDATE classes SET updated_on = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to automatically resolve doubts when response is added
CREATE TRIGGER auto_resolve_doubts 
    AFTER UPDATE ON doubts
    FOR EACH ROW
    WHEN NEW.response IS NOT NULL AND OLD.response IS NULL
BEGIN
    UPDATE doubts 
    SET status = 'answered', 
        resolved_on = CURRENT_TIMESTAMP,
        response_time = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ============================================================================
-- ANNOUNCEMENTS TABLE
-- ============================================================================

-- Announcements posted by teachers/admins
CREATE TABLE announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    class_id INTEGER,  -- NULL means announcement for all classes
    subject_name TEXT,  -- NULL means announcement for all subjects
    priority TEXT DEFAULT 'normal' CHECK(priority IN ('low', 'normal', 'high', 'urgent')),
    is_active BOOLEAN DEFAULT 1,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME,
    expires_on DATETIME,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Index for announcements
CREATE INDEX idx_announcements_author ON announcements(author_id);
CREATE INDEX idx_announcements_class ON announcements(class_id);
CREATE INDEX idx_announcements_active ON announcements(is_active, created_on);
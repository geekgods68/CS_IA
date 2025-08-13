-- Classes table: stores class info
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    grade TEXT NOT NULL,
    batch TEXT,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Subjects table: subjects for each class
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Teacher-Subject mapping: assign teachers to subjects
CREATE TABLE teacher_subject_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- Student-Class mapping: allocate students to classes
CREATE TABLE student_class_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);
-- SMCT Portal Database Schema

-- Users table: stores all users with roles


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- User roles table
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- User-role mapping table
CREATE TABLE user_role_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES user_roles(id),
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- User profiles table: stores profile info for users
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    email TEXT,
    name TEXT,
    phone TEXT,
    address TEXT,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);


-- Attendance table: tracks student attendance per class

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('present', 'absent', 'late')) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Resources table: teaching materials, homework, recordings

CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    uploader_id INTEGER,
    type TEXT CHECK(type IN ('homework', 'material', 'recording')) NOT NULL,
    filename TEXT NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (uploader_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Doubts table: student questions and teacher responses

CREATE TABLE doubts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER,
    question TEXT NOT NULL,
    anonymous INTEGER DEFAULT 1,
    posted_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    response TEXT,
    responder_id INTEGER,
    response_time DATETIME,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (responder_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Assessments table: tracks student progress

CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER,
    type TEXT CHECK(type IN ('midterm', 'half-yearly', 'final')) NOT NULL,
    score INTEGER,
    max_score INTEGER,
    assessment_date DATETIME,
    created_by INTEGER,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    updated_on DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

# DATABASE SCHEMAS

## USERS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| username | TEXT | No Unique login username | — |
| password | TEXT | SHA256 hashed password | — |
| role | TEXT | User role (admin, teacher, student) | — |
| email | TEXT | User email address | — |
| name | TEXT | Full name of user | — |
| phone | TEXT | Phone number | — |
| address | TEXT | Physical address | — |
| created_by | INTEGER | User who created this record | FK → users.id |
| created_on | DATETIME | Record creation timestamp | — |
| updated_by | INTEGER | User who last updated this record | FK → users.id |
| updated_on | DATETIME | Last update timestamp | — |

## USER_ROLES TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| role_name | TEXT | Unique role name | — |
| description | TEXT | Role description | — |
| created_on | DATETIME | Record creation timestamp | — |

## USER_ROLE_MAP TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| user_id | INTEGER | Reference to user | FK → users.id |
| role_id | INTEGER | Reference to role | FK → user_roles.id |
| assigned_by | INTEGER | User who made the assignment | FK → users.id |
| assigned_on | DATETIME | Assignment timestamp | — |

## SUBJECTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| name | TEXT | Unique subject name | — |
| description | TEXT | Subject description | — |
| grade_level | TEXT | Grade level for subject | — |
| created_by | INTEGER | User who created this record | FK → users.id |
| created_on | DATETIME | Record creation timestamp | — |

## CLASSES TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| name | TEXT | Class name | — |
| type | TEXT | Class type (regular, advanced, remedial) | — |
| description | TEXT | Class description | — |
| grade_level | TEXT | Grade level of class | — |
| section | TEXT | Class section identifier | — |
| schedule_days | TEXT | JSON array of scheduled days | — |
| schedule_time_start | TEXT | Start time in HH:MM format | — |
| schedule_time_end | TEXT | End time in HH:MM format | — |
| schedule_pdf_path | TEXT | Path to uploaded schedule PDF | — |
| meeting_link | TEXT | Virtual meeting link (Zoom, Teams, etc.) | — |
| max_students | INTEGER | Maximum students allowed | — |
| status | TEXT | Class status (active, inactive, archived) | — |
| created_by | INTEGER | User who created this record | FK → users.id |
| created_on | DATETIME | Record creation timestamp | — |
| updated_by | INTEGER | User who last updated this record | FK → users.id |
| updated_on | DATETIME | Last update timestamp | — |

## STUDENT_CLASS_MAP TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| student_id | INTEGER | Reference to student user | FK → users.id |
| class_id | INTEGER | Reference to class | FK → classes.id |
| assigned_by | INTEGER | User who made the assignment | FK → users.id |
| assigned_on | DATETIME | Assignment timestamp | — |
| status | TEXT | Enrollment status (active, inactive, dropped) | — |

## TEACHER_CLASS_MAP TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| teacher_id | INTEGER | Reference to teacher user | FK → users.id |
| class_id | INTEGER | Reference to class | FK → classes.id |
| assigned_by | INTEGER | User who made the assignment | FK → users.id |
| assigned_on | DATETIME | Assignment timestamp | — |
| role | TEXT | Teaching role (primary, assistant, substitute) | — |

## STUDENT_SUBJECTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| student_id | INTEGER | Reference to student user | FK → users.id |
| subject_name | TEXT | Subject name (Math, Science, Social Science, English, Hindi) | — |
| assigned_by | INTEGER | User who made the assignment | FK → users.id |
| assigned_on | DATETIME | Assignment timestamp | — |

## TEACHER_SUBJECTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| teacher_id | INTEGER | Reference to teacher user | FK → users.id |
| subject_name | TEXT | Subject name (Math, Science, Social Science, English, Hindi) | — |
| assigned_by | INTEGER | User who made the assignment | FK → users.id |
| assigned_on | DATETIME | Assignment timestamp | — |

## FEEDBACK TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| student_id | INTEGER | Reference to student user | FK → users.id |
| feedback_text | TEXT | Feedback content | — |
| rating | INTEGER | Rating from 1-5 stars | — |
| submitted_on | DATETIME | Submission timestamp | — |

## ATTENDANCE TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| student_id | INTEGER | Reference to student user | FK → users.id |
| class_id | INTEGER | Reference to class | FK → classes.id |
| attendance_date | DATE | Date of attendance | — |
| status | TEXT | Attendance status (present, absent, late, excused) | — |
| remarks | TEXT | Optional notes for attendance status | — |
| marked_by | INTEGER | Teacher/admin who marked attendance | FK → users.id |
| marked_on | DATETIME | Timestamp when attendance was marked | — |
| updated_by | INTEGER | User who last updated this record | FK → users.id |
| updated_on | DATETIME | Last update timestamp | — |

## DOUBTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| student_id | INTEGER | Reference to student user | FK → users.id |
| subject | TEXT | Subject category for the doubt | — |
| doubt_text | TEXT | Doubt/question content | — |
| status | TEXT | Doubt status (open, answered, resolved) | — |
| submitted_on | DATETIME | Submission timestamp | — |
| resolved_on | DATETIME | Resolution timestamp | — |
| resolved_by | INTEGER | Teacher/admin who resolved the doubt | FK → users.id |
| response | TEXT | Response text from teacher/admin | — |
| response_time | DATETIME | Response timestamp | — |

## ASSESSMENTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| class_id | INTEGER | Reference to class | FK → classes.id |
| subject_name | TEXT | Subject name for assessment | — |
| teacher_id | INTEGER | Reference to teacher who created assessment | FK → users.id |
| title | TEXT | Assessment title | — |
| description | TEXT | Assessment description | — |
| assessment_date | DATE | Date of assessment | — |
| max_score | REAL | Maximum possible score | — |
| weight | REAL | Weight in final grade (0.0 to 1.0) | — |
| created_at | DATETIME | Creation timestamp | — |

## MARKS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| assessment_id | INTEGER | Reference to assessment | FK → assessments.id |
| student_id | INTEGER | Reference to student user | FK → users.id |
| score | REAL | Student's score on assessment | — |
| comment | TEXT | Teacher's comment on performance | — |
| updated_at | DATETIME | Last update timestamp | — |

## ANNOUNCEMENTS TABLE
| Field Name | Data Type | Description | PK/FK |
|------------|-----------|-------------|-------|
| id | INTEGER | Auto-incrementing unique identifier | PK |
| title | TEXT | Announcement title | — |
| content | TEXT | Announcement content | — |
| author_id | INTEGER | Reference to user who created announcement | FK → users.id |
| class_id | INTEGER | Reference to specific class (NULL for all classes) | FK → classes.id |
| subject_name | TEXT | Subject name (NULL for all subjects) | — |
| priority | TEXT | Priority level (low, normal, high, urgent) | — |
| is_active | BOOLEAN | Whether announcement is active | — |
| created_on | DATETIME | Creation timestamp | — |
| updated_on | DATETIME | Last update timestamp | — |
| expires_on | DATETIME | Expiration timestamp | — |

### Foreign Key Map (One-Line Per FK)
- users.created_by → users.id
- users.updated_by → users.id
- user_role_map.user_id → users.id (ON DELETE CASCADE)
- user_role_map.role_id → user_roles.id (ON DELETE CASCADE)
- user_role_map.assigned_by → users.id
- subjects.created_by → users.id
- classes.created_by → users.id
- classes.updated_by → users.id
- student_class_map.student_id → users.id (ON DELETE CASCADE)
- student_class_map.class_id → classes.id (ON DELETE CASCADE)
- student_class_map.assigned_by → users.id
- teacher_class_map.teacher_id → users.id (ON DELETE CASCADE)
- teacher_class_map.class_id → classes.id (ON DELETE CASCADE)
- teacher_class_map.assigned_by → users.id
- student_subjects.student_id → users.id (ON DELETE CASCADE)
- student_subjects.assigned_by → users.id
- teacher_subjects.teacher_id → users.id (ON DELETE CASCADE)
- teacher_subjects.assigned_by → users.id
- feedback.student_id → users.id (ON DELETE CASCADE)
- attendance.student_id → users.id (ON DELETE CASCADE)
- attendance.class_id → classes.id (ON DELETE CASCADE)
- attendance.marked_by → users.id
- attendance.updated_by → users.id
- doubts.student_id → users.id (ON DELETE CASCADE)
- doubts.resolved_by → users.id
- assessments.class_id → classes.id (ON DELETE CASCADE)
- assessments.teacher_id → users.id (ON DELETE CASCADE)
- marks.assessment_id → assessments.id (ON DELETE CASCADE)
- marks.student_id → users.id (ON DELETE CASCADE)
- announcements.author_id → users.id (ON DELETE CASCADE)
- announcements.class_id → classes.id (ON DELETE CASCADE)

### Unique/Check/Trigger Notes
- UNIQUE(username) on users table
- UNIQUE(role_name) on user_roles table
- UNIQUE(user_id, role_id) on user_role_map table
- UNIQUE(name) on subjects table
- UNIQUE(student_id, class_id) on student_class_map table
- UNIQUE(teacher_id, class_id) on teacher_class_map table
- UNIQUE(student_id, subject_name) on student_subjects table
- UNIQUE(teacher_id, subject_name) on teacher_subjects table
- CHECK(rating BETWEEN 1 AND 5) on feedback table
- CHECK(student_id IN (SELECT id FROM users WHERE role = 'student')) on attendance table
- UNIQUE(student_id, class_id, attendance_date) on attendance table
- CHECK(max_score > 0) on assessments table
- CHECK(weight >= 0 AND weight <= 1) on assessments table
- UNIQUE(class_id, subject_name, title, assessment_date) on assessments table
- CHECK(score >= 0) on marks table
- UNIQUE(assessment_id, student_id) on marks table
- CHECK(priority IN ('low', 'normal', 'high', 'urgent')) on announcements table
- TRIGGER check_mark_score: enforces score <= max_score on INSERT to marks
- TRIGGER check_mark_score_update: enforces score <= max_score on UPDATE to marks
- TRIGGER update_users_timestamp: updates updated_on on users table UPDATE
- TRIGGER update_classes_timestamp: updates updated_on on classes table UPDATE
- TRIGGER auto_resolve_doubts: automatically sets status to 'answered' when response is added

### Indexes (if present)
- idx_users_username ON users(username)
- idx_users_role ON users(role)
- idx_users_created_on ON users(created_on)
- idx_classes_status ON classes(status)
- idx_classes_grade_level ON classes(grade_level)
- idx_classes_created_on ON classes(created_on)
- idx_student_class_map_student ON student_class_map(student_id)
- idx_student_class_map_class ON student_class_map(class_id)
- idx_student_class_map_status ON student_class_map(status)
- idx_teacher_class_map_teacher ON teacher_class_map(teacher_id)
- idx_teacher_class_map_class ON teacher_class_map(class_id)
- idx_student_subjects_student ON student_subjects(student_id)
- idx_student_subjects_subject ON student_subjects(subject_name)
- idx_teacher_subjects_teacher ON teacher_subjects(teacher_id)
- idx_teacher_subjects_subject ON teacher_subjects(subject_name)
- idx_feedback_student ON feedback(student_id)
- idx_feedback_submitted ON feedback(submitted_on)
- idx_doubts_student ON doubts(student_id)
- idx_doubts_status ON doubts(status)
- idx_doubts_subject ON doubts(subject)
- idx_doubts_submitted ON doubts(submitted_on)
- idx_attendance_student ON attendance(student_id)
- idx_attendance_class ON attendance(class_id)
- idx_attendance_date ON attendance(attendance_date)
- idx_attendance_status ON attendance(status)
- idx_attendance_marked_by ON attendance(marked_by)
- idx_attendance_marked_on ON attendance(marked_on)
- idx_assessments_class_subject ON assessments(class_id, subject_name)
- idx_assessments_teacher_date ON assessments(teacher_id, assessment_date)
- idx_marks_assessment ON marks(assessment_id)
- idx_marks_student ON marks(student_id)
- idx_announcements_author ON announcements(author_id)
- idx_announcements_class ON announcements(class_id)
- idx_announcements_active ON announcements(is_active, created_on)

# IA_CriterionC_Audit.md

# SMCT LMS - IB DP Computer Science IA Criterion C Evidence Pack

**Author:** Student Candidate  
**Date:** August 2025  
**System:** School Management and Communication Technology Learning Management System  

---

## C0. System Map

### Tech Stack & Versions
- **Backend Framework:** Flask (Python web framework)
- **Database Engine:** SQLite3 with `sqlite3` driver
- **Password Hashing:** SHA256 (via Python `hashlib` library)
- **Session Management:** Flask sessions (server-side)
- **Frontend:** HTML5, CSS3, Bootstrap 5.3.0, vanilla JavaScript
- **Dependencies:** Flask, Flask-Login (requirements.txt:L1-2)

### Project Structure
```
CS_IA/
├── app.py                  # Main Flask application factory
├── routes/                 # Blueprint-based routing modules
│   ├── auth.py            # Authentication routes
│   ├── admin.py           # Admin portal routes
│   ├── teacher.py         # Teacher portal routes  
│   └── student.py         # Student portal routes
├── models/
│   └── db_models.py       # Database model classes
├── database/
│   └── schema.sql         # Complete database schema
├── templates/             # Jinja2 HTML templates
│   ├── admin/            # Admin portal templates
│   ├── teacher/          # Teacher portal templates
│   └── student/          # Student portal templates
├── static/               # CSS, JS, images
├── devtools.py           # Development utilities
└── users.db             # SQLite database file
```

### Active Configuration
- **Debug Mode:** `True` (app.py:L56)
- **Secret Key:** Hardcoded string (app.py:L7) ⚠️ **Security Risk**
- **Database:** `'users.db'` (app.py:L8)
- **Foreign Keys:** Enabled via `PRAGMA foreign_keys = ON` (schema.sql:L6)
- **Session Management:** Flask default (server-side cookies)
- **Port:** 5004 (app.py:L56)

---

## C1. Techniques Overview

### Routing & Controllers
- **Blueprint Architecture:** Modular routing with `auth_bp`, `admin_bp`, `teacher_bp`, `student_bp` (app.py:L26-42)
- **Route Protection:** Session-based guards in every protected route (e.g., teacher.py:L15-16)
- **HTTP Methods:** GET/POST routing with explicit method declarations (auth.py:L16, admin.py:L78)

### Role-Based Access Control (RBAC)
- **Three-Tier System:** admin, teacher, student roles (schema.sql:L17)
- **Session Guards:** `if 'role' not in session or session['role'] != 'teacher'` pattern (teacher.py:L15-16)
- **Database Constraints:** Role validation in attendance table (schema.sql:L160-162)

### Data Modeling
- **Relational Schema:** 13 core tables with foreign key constraints (schema.sql:L13-442)
- **Junction Tables:** `student_class_map`, `teacher_class_map`, `user_role_map` for many-to-many relationships
- **Indexes:** Performance optimization on lookup columns (schema.sql:L268-310)
- **Triggers:** Auto-timestamping and data integrity enforcement (schema.sql:L242-266, L377-407)

### Input Validation & Security
- **Server-side Validation:** Form field checks before database operations (admin.py:L84-88)
- **Parameterized Queries:** All SQL uses `?` placeholders (admin.py:L95, teacher.py:L468-469)
- **Password Hashing:** SHA256 with UTF-8 encoding (auth.py:L9-10)
- **Session Management:** User context via Flask sessions (auth.py:L28-31)

### Business Logic Algorithms
- **Marks Calculation:** Weighted average computation for student reports (teacher.py:L898-905)
- **Attendance Aggregation:** Date-range filtering with status categorization (teacher.py:L803-815)
- **Access Verification:** Teacher-class-subject permission checking (teacher.py:L445-463)
- **Report Generation:** Statistical analysis with distribution grouping (teacher.py:L780-825)

---

## C2. Authentication Flow

### Endpoints & Session Settings
- **Login Route:** `POST /login` (auth.py:L16)
- **Logout Route:** `GET /logout` (auth.py:L47)
- **Session Storage:** Flask default server-side sessions
- **No Explicit Expiry:** Uses Flask session defaults

### Password Security Implementation
```python
# auth.py:L9-10
def simple_hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
```
- **Algorithm:** SHA256 (256-bit)
- **Salt:** None ⚠️ **Security Weakness**
- **Encoding:** UTF-8 before hashing
- **Storage:** 64-character hex strings in database

### Login Flow Pseudocode
```
1. Receive POST /login with username, password
2. Query database for user by username
3. Hash provided password using SHA256
4. Compare hashed password with stored hash
5. If match:
   a. Set session['user_id'] = user.id
   b. Set session['username'] = user.username  
   c. Set session['role'] = user.role
   d. Redirect based on role (admin→dashboard, teacher→dashboard, student→site)
6. If no match:
   a. Flash error message
   b. Return to login form
```

### Failure Handling
- **Invalid Credentials:** Flash message "Invalid username or password!" (auth.py:L42)
- **No Account Lockout:** Unlimited login attempts
- **Edge Cases:** Empty inputs handled by form validation, non-existent users return generic error

---

## C3. Authorization (RBAC) & Access Guards

### Role Definitions
- **admin:** Full system access to user management, classes, reports (schema.sql:L318)
- **teacher:** Class management, marks entry, attendance (schema.sql:L319)  
- **student:** View classes, submit feedback, view homework (schema.sql:L320)

### Access Guard Pattern
```python
# teacher.py:L15-16 (repeated in all protected routes)
if 'role' not in session or session['role'] != 'teacher':
    return redirect(url_for('auth.login'))
```

### Teacher Access Verification Example
```python
# teacher.py:L445-463
def verify_teacher_access(teacher_id, class_id, subject_name):
    """Verify teacher has access to the given class and subject"""
    conn = get_db()
    cur = conn.cursor()
    
    # Check if teacher is assigned to the class
    cur.execute('''SELECT 1 FROM teacher_class_map 
                   WHERE teacher_id = ? AND class_id = ?''', 
                (teacher_id, class_id))
    class_access = cur.fetchone() is not None
    
    # Check if teacher is assigned to the subject  
    cur.execute('''SELECT 1 FROM teacher_subjects 
                   WHERE teacher_id = ? AND subject_name = ?''', 
                (teacher_id, subject_name))
    subject_access = cur.fetchone() is not None
    
    return class_access and subject_access
```

### Unauthorized Access Handling
- **Redirect Strategy:** Invalid sessions redirect to `/login` (teacher.py:L16)
- **Flash Messages:** User feedback via Flask flash system (admin.py:L42)
- **No 403 Responses:** Uses redirects instead of HTTP error codes

---

## C4. Data Layer & Safety

### Schema Summary (ER-Style)
```
users (PK: id, username UNIQUE, password, role, email, name, phone, address)
├─ user_roles (PK: id, role_name UNIQUE, description)
├─ user_role_map (PK: id, user_id FK→users, role_id FK→user_roles)
├─ classes (PK: id, name, grade_level, meeting_link, status)
├─ student_class_map (PK: id, student_id FK→users, class_id FK→classes)
├─ teacher_class_map (PK: id, teacher_id FK→users, class_id FK→classes)
├─ student_subjects (PK: id, student_id FK→users, subject_name)
├─ teacher_subjects (PK: id, teacher_id FK→users, subject_name)
├─ assessments (PK: id, class_id FK→classes, teacher_id FK→users, title, max_score)
├─ marks (PK: id, assessment_id FK→assessments, student_id FK→users, score)
├─ attendance (PK: id, student_id FK→users, class_id FK→classes, date, status)
├─ feedback (PK: id, student_id FK→users, feedback_text, rating)
└─ doubts (PK: id, student_id FK→users, subject, doubt_text, status)
```

### Query Safety
- **Parameterized Queries:** All user inputs use `?` placeholders
- **Example:** `cur.execute('SELECT * FROM users WHERE username = ?', (username,))` (auth.py:L24)
- **Foreign Key Enforcement:** `PRAGMA foreign_keys = ON` enabled (admin.py:L17)

### Transactions & Migrations
- **Basic Transactions:** Rollback on error in complex operations (teacher.py:L426)
- **Schema Migrations:** `migrate_marks_tables.py` for database evolution
- **Data Integrity:** CHECK constraints and triggers (schema.sql:L242-266)

### File Handling
- **No File Uploads:** System does not handle user file uploads
- **Static Assets:** Only developer-controlled CSS/JS in `/static`

---

## C5. Input Validation & Error Handling

### Server-Side Validation
```python
# admin.py:L84-88
if not username or not password or not role:
    flash('All fields are required!', 'error')
    return redirect(url_for('admin.manage_users'))

if role not in ['student', 'teacher', 'admin']:
    flash('Invalid role specified!', 'error')
    return redirect(url_for('admin.manage_users'))
```

### Validation Pipeline Pseudocode
```
1. Receive form/JSON data
2. Check required fields present and non-empty
3. Validate data types (integers, floats, dates)
4. Check business rules (role values, score ranges)
5. If invalid: flash error message, redirect/return error
6. If valid: proceed with database operation
7. Wrap in try/except for database errors
```

### Error Handling Strategy
```python
# teacher.py:L298-305
try:
    # Database operations
    conn.commit()
    flash('Operation successful', 'success')
except Exception as e:
    conn.rollback()
    flash(f'Error: {str(e)}', 'error')
finally:
    conn.close()
```

### Error Logging
- **Basic Logging:** Error messages shown to users via flash messages
- **No System Logging:** No logging to files or external systems implemented

---

## C6. Core Domain Algorithms

### 1. Weighted Marks Calculation
**Context:** Teacher reports for individual student performance analysis  
**Location:** teacher.py:L898-905

**Algorithm:**
```python
# Calculate weighted average for student marks
total_weighted_score = 0
total_weight = 0
for mark in marks:
    if mark[4] is not None:  # score exists
        percentage = (mark[4] / mark[2]) * 100  # score/max_score * 100
        total_weighted_score += percentage * mark[3]  # * weight
        total_weight += mark[3]

weighted_average = total_weighted_score / total_weight if total_weight > 0 else 0
```

**Why This Approach:** Allows different assessment types to have different importance in final grade  
**Edge Cases:** Division by zero prevented, null scores excluded from calculation

### 2. Teacher Access Verification
**Context:** Ensures teachers can only modify data for their assigned classes/subjects  
**Location:** teacher.py:L445-463

**Algorithm:**
```
1. Receive teacher_id, class_id, subject_name
2. Query teacher_class_map for teacher→class assignment
3. Query teacher_subjects for teacher→subject assignment  
4. Return true only if BOTH assignments exist
5. Used as guard before any teacher operations
```

**Why This Approach:** Dual verification prevents unauthorized cross-access between teachers

### 3. Attendance Status Aggregation
**Context:** Generate attendance reports with statistical breakdowns  
**Location:** admin.py:L831-875

**Algorithm:**
```
1. Query attendance records for date range and class filter
2. Group records by status (present, absent, late, excused)
3. Calculate percentages: count(status) / total_records * 100
4. Generate summary statistics (attendance rate, trend analysis)
5. Format for report display with status badges
```

**Edge Cases:** Empty result sets return 0% rates, invalid date ranges handled

### 4. Assessment Score Validation
**Context:** Enforce business rule that student scores cannot exceed assessment maximum  
**Location:** schema.sql:L242-254 (database trigger)

**Algorithm:**
```sql
CREATE TRIGGER check_mark_score 
    BEFORE INSERT ON marks
    FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN NEW.score > (SELECT max_score FROM assessments WHERE id = NEW.assessment_id)
        THEN RAISE(ABORT, 'Score cannot exceed maximum score for assessment')
    END;
END;
```

**Why This Approach:** Database-level enforcement ensures data integrity regardless of application bugs

---

## C7. UI ↔ Backend Integration

### Teacher Marks Entry Flow
**Route:** `POST /teacher/marks/save` → `save_marks()` → marks table → AJAX response

**Trace:**
1. **Frontend:** teacher_marks.html:L234-250 JavaScript collects form data
2. **HTTP:** `fetch('/teacher/marks/save', {method: 'POST', body: JSON.stringify(data)})`
3. **Backend:** teacher.py:L672-745 processes JSON payload
4. **Database:** Parameterized INSERT/UPDATE to marks table
5. **Response:** JSON with `{saved: 2, updated: 1, errors: []}`
6. **UI Update:** JavaScript displays success/error messages

### Form Field Mapping Example
```javascript
// teacher_marks.html:L234-250
items.push({
    student_id: input.dataset.studentId,     // → marks.student_id
    score: input.value.trim(),               // → marks.score  
    comment: commentInput.value.trim()       // → marks.comment
});
```

---

## C8. Security Checklist

### Implemented Security Measures
- ✅ **Parameterized Queries:** All SQL uses `?` placeholders (auth.py:L24, admin.py:L95)
- ✅ **Password Hashing:** SHA256 encoding before storage (auth.py:L9-10)
- ✅ **Session-Based Auth:** Server-side session management (auth.py:L28-31)
- ✅ **Role-Based Access:** Route guards prevent unauthorized access (teacher.py:L15-16)
- ✅ **Database Constraints:** Foreign keys and CHECK constraints enforce integrity

### Security Risks Identified
- ❌ **No Password Salt:** SHA256 without salt vulnerable to rainbow table attacks (auth.py:L10)
- ❌ **Hardcoded Secret:** Flask secret key in source code (app.py:L7)
- ❌ **No CSRF Protection:** Forms lack CSRF tokens
- ❌ **No Session Expiry:** Sessions persist indefinitely
- ❌ **No HTTPS Enforcement:** Application runs on HTTP in development

### File Security
- **No File Uploads:** System doesn't handle user file uploads, eliminating upload vulnerabilities
- **Static Assets:** Only developer-controlled files in `/static` directory

---

## C9. Testing & Verification

### Development Tools
- **Database Seeding:** devtools.py:L45-234 creates realistic test data
- **Reset Utilities:** devtools.py:L21-44 cleans database to admin-only state
- **Verification Scripts:** Multiple test_*.py files validate functionality

### Test Data Generation
```python
# devtools.py:L89-104
teachers = [
    ('teacher1', 'teacher123', 'john.smith@school.edu', 'John Smith'),
    ('teacher2', 'teacher123', 'mary.jones@school.edu', 'Mary Jones'),
]

for teacher in teachers:
    hashed_pw = hash_password(teacher[1])
    cur.execute("""INSERT INTO users (username, password, role, email, name) 
                   VALUES (?, ?, 'teacher', ?, ?)""", 
                (teacher[0], hashed_pw, teacher[2], teacher[3]))
```

### Verification Methods
- **Manual Testing:** Browser-based verification of all user flows
- **Data Validation:** Scripts verify database constraints and relationships
- **Integration Testing:** End-to-end scenario testing with realistic data

---

## C10. Third-Party Code & Licenses

### Runtime Dependencies
- **Flask:** BSD-3-Clause license, web framework core
- **Bootstrap 5.3.0:** MIT license, CSS framework (CDN link in templates)
- **Bootstrap Icons:** MIT license, icon library (CDN link in templates)

### External Resources
- **CDN Assets:** Bootstrap CSS/JS and icons loaded from jsdelivr.net
- **No Copied Code:** All application code appears to be original implementation
- **Database Design:** Schema follows standard relational database patterns

---

## C11. Snippet Candidates for IA

### 1. Teacher Access Verification System
**File:** teacher.py:L445-463  
**Techniques:** Authorization, database security, business logic  
**Why Notable:** Demonstrates complex permission checking with dual relationship verification  
**Mini Write-up Stub:** Multi-table permission verification ensuring teachers can only access their assigned classes and subjects through junction table lookups and boolean logic combination.

### 2. Weighted Grade Calculation Algorithm  
**File:** teacher.py:L898-905  
**Techniques:** Mathematical computation, data processing, null handling  
**Why Notable:** Shows sophisticated grade calculation with weights and percentage conversion  
**Mini Write-up Stub:** Statistical aggregation algorithm computing weighted averages while handling edge cases like missing scores and division by zero through conditional logic.

### 3. Database Trigger for Score Validation
**File:** schema.sql:L242-254  
**Techniques:** Database programming, constraint enforcement, data integrity  
**Why Notable:** Database-level business rule enforcement preventing data corruption  
**Mini Write-up Stub:** SQL trigger implementing automatic validation of student scores against assessment maximums using subqueries and conditional abort logic for data integrity.

### 4. Session-Based Authentication Flow
**File:** auth.py:L16-46  
**Techniques:** Security, session management, role-based routing  
**Why Notable:** Complete authentication implementation with role-based redirection  
**Mini Write-up Stub:** Multi-step authentication process combining password hashing verification with session establishment and role-based application routing.

### 5. Dynamic Assessment Management
**File:** teacher.py:L672-745  
**Techniques:** AJAX/JSON processing, bulk data operations, transaction management  
**Why Notable:** Complex data processing with batch operations and error aggregation  
**Mini Write-up Stub:** Bulk data processing system handling JSON payloads for batch mark entry with validation, transaction safety, and detailed error reporting.

### 6. Attendance Tracking with Constraints
**File:** schema.sql:L146-167 + teacher.py:L323-430  
**Techniques:** Database design, constraint enforcement, data modeling  
**Why Notable:** Shows complex business rules implemented through database constraints  
**Mini Write-up Stub:** Attendance system combining database constraints for role verification with application logic for batch processing and conflict resolution.

---

## Appendices

### A. Route Table
| Method | Path | Auth Required | Handler | File:Line |
|--------|------|---------------|---------|-----------|
| GET/POST | /login | No | login() | auth.py:L16 |
| GET | /logout | No | logout() | auth.py:L47 |
| GET | /admin/dashboard | admin | dashboard() | admin.py:L31 |
| GET | /admin/manage_users | admin | manage_users() | admin.py:L155 |
| POST | /admin/add_user | admin | add_user() | admin.py:L78 |
| GET | /teacher/dashboard | teacher | dashboard() | teacher.py:L12 |
| GET | /teacher/marks | teacher | marks() | teacher.py:L217 |
| POST | /teacher/marks/save | teacher | save_marks() | teacher.py:L672 |
| GET | /student/site | student | site() | student.py:L11 |

### B. Schema Table
| Table | Key Columns | Type | Constraints | Notes |
|-------|-------------|------|-------------|--------|
| users | id, username, password, role | INT, TEXT, TEXT, TEXT | PK, UNIQUE, NOT NULL | SHA256 hashed passwords |
| classes | id, name, meeting_link | INT, TEXT, TEXT | PK, NOT NULL | Virtual meeting links |
| assessments | id, class_id, teacher_id, max_score | INT, INT, INT, REAL | PK, FK, CHECK>0 | Teacher-created assessments |
| marks | assessment_id, student_id, score | INT, INT, REAL | FK, UNIQUE, CHECK≥0 | Score validation via trigger |
| attendance | student_id, class_id, date, status | INT, INT, DATE, TEXT | FK, UNIQUE combo | Student role constraint |

### C. Config Table
| Setting | Value | Source | Notes |
|---------|-------|--------|--------|
| SECRET_KEY | 'your-secret-key-here...' | app.py:L7 | ⚠️ Hardcoded |
| DATABASE | 'users.db' | app.py:L8 | SQLite file |
| DEBUG | True | app.py:L56 | Development mode |
| PORT | 5004 | app.py:L56 | HTTP port |
| FOREIGN_KEYS | ON | schema.sql:L6 | Database integrity |

### D. Security Parameters
| Component | Algorithm/Setting | Parameters | Location |
|-----------|------------------|------------|----------|
| Password Hash | SHA256 | No salt, UTF-8 encoding | auth.py:L9-10 |
| Session Management | Flask default | Server-side cookies | Built-in |
| Database Constraints | Foreign keys + triggers | Cascade deletes enabled | schema.sql:L6 |
| Input Validation | Server-side only | Required field checks | admin.py:L84-88 |

---

**Report Generated:** August 17, 2025  
**Total Files Analyzed:** 47 Python files, 31 templates, 1 schema, 15 test scripts  
**Lines of Code:** ~3,200 lines application code + 442 lines SQL schema

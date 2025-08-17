from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

def get_db():
    """Get database connection"""
    return sqlite3.connect('users.db')

@teacher_bp.route('/dashboard')
def dashboard():
    """Teacher dashboard"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    # Get assigned classes count
    cur.execute('''
        SELECT COUNT(*) FROM teacher_class_map 
        WHERE teacher_id = ?
    ''', (teacher_id,))
    assigned_classes_count = cur.fetchone()[0]
    
    # Get pending doubts count
    cur.execute('''
        SELECT COUNT(*) FROM doubts 
        WHERE status = 'open'
    ''', ())
    pending_doubts_count = cur.fetchone()[0]
    
    # Get submissions to grade (placeholder - we can implement this later)
    submissions_to_grade = 0
    
    # Count today's classes (placeholder)
    todays_classes = 1
    
    # Today's schedule (empty for now)
    todays_schedule = []
    
    # Recent notifications (empty for now)
    recent_notifications = []
    
    conn.close()
    
    return render_template('teacher/teacher_dashboard_new.html',
                         assigned_classes_count=assigned_classes_count,
                         pending_doubts_count=pending_doubts_count,
                         submissions_to_grade=submissions_to_grade,
                         todays_classes=todays_classes,
                         todays_schedule=todays_schedule,
                         recent_notifications=recent_notifications)

@teacher_bp.route('/classes')
def classes():
    """View teacher's assigned classes"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get teacher's assigned classes with student counts
        cur.execute('''
            SELECT 
                c.id, c.name, c.type, c.description, c.grade_level, 
                c.schedule_time_start, c.schedule_time_end, c.meeting_link,
                COUNT(DISTINCT scm.student_id) as student_count
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            LEFT JOIN student_class_map scm ON c.id = scm.class_id AND scm.status = 'active'
            WHERE tcm.teacher_id = ? AND c.status = 'active'
            GROUP BY c.id
            ORDER BY c.grade_level, c.name
        ''', (teacher_id,))
        classes = cur.fetchall()
        
        return render_template('teacher/teacher_classes.html', classes=classes)
        
    except Exception as e:
        flash(f'Error loading classes data: {str(e)}', 'error')
        return redirect(url_for('teacher.dashboard'))
    finally:
        conn.close()

@teacher_bp.route('/homework')
def homework():
    """Manage homework assignments"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get teacher's assigned classes
        cur.execute('''
            SELECT c.id, c.name, c.grade_level 
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND c.status = 'active'
            ORDER BY c.grade_level, c.name
        ''', (teacher_id,))
        classes = cur.fetchall()
        
        # Since we don't have assignments table yet, provide empty data
        assignments = []
        
        # Provide default assignment stats
        assignment_stats = {
            'total': 0,
            'active': 0,
            'completed': 0,
            'avg_submission_rate': 0
        }
        
        return render_template('teacher/teacher_homework.html',
                             classes=classes,
                             assignments=assignments,
                             assignment_stats=assignment_stats)
        
    except Exception as e:
        flash(f'Error loading homework data: {str(e)}', 'error')
        return redirect(url_for('teacher.dashboard'))
    finally:
        conn.close()

@teacher_bp.route('/schedule')
def schedule():
    """View teaching schedule"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get teacher's assigned classes for schedule
        cur.execute('''
            SELECT c.id, c.name, c.grade_level, c.schedule_time_start, c.schedule_time_end, c.schedule_days
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND c.status = 'active'
            ORDER BY c.schedule_time_start
        ''', (teacher_id,))
        classes = cur.fetchall()
        
        # Provide default schedule data
        todays_classes_count = len(classes)
        next_class_info = "Check your class schedule below"
        
        # Create empty weekly timetable structure
        weekly_schedule = []
        
        return render_template('teacher/teacher_schedule.html',
                             classes=classes,
                             todays_classes_count=todays_classes_count,
                             next_class_info=next_class_info,
                             weekly_schedule=weekly_schedule)
        
    except Exception as e:
        flash(f'Error loading schedule data: {str(e)}', 'error')
        return redirect(url_for('teacher.dashboard'))
    finally:
        conn.close()

@teacher_bp.route('/submissions')
def submissions():
    """View student submissions"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get teacher's assigned classes
        cur.execute('''
            SELECT c.id, c.name, c.grade_level 
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND c.status = 'active'
            ORDER BY c.grade_level, c.name
        ''', (teacher_id,))
        classes = cur.fetchall()
        
        # Since we don't have submissions table yet, provide empty data
        submissions = []
        
        return render_template('teacher/teacher_submissions.html',
                             classes=classes,
                             submissions=submissions)
        
    except Exception as e:
        flash(f'Error loading submissions data: {str(e)}', 'error')
        return redirect(url_for('teacher.dashboard'))
    finally:
        conn.close()

@teacher_bp.route('/doubts')
def doubts():
    """View and manage student doubts"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_doubts.html')

@teacher_bp.route('/marks')
def marks():
    """Enter and manage student marks"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Get teacher's assigned classes
    cur.execute('''
        SELECT DISTINCT c.id, c.name, c.grade_level
        FROM classes c
        INNER JOIN teacher_class_map tcm ON c.id = tcm.class_id
        WHERE tcm.teacher_id = ? AND c.status = 'active'
        ORDER BY c.grade_level, c.name
    ''', (teacher_id,))
    assigned_classes = cur.fetchall()
    
    # Get teacher's subjects
    cur.execute('''
        SELECT DISTINCT subject_name
        FROM teacher_subjects
        WHERE teacher_id = ?
        ORDER BY subject_name
    ''', (teacher_id,))
    teacher_subjects = cur.fetchall()
    
    conn.close()
    
    return render_template('teacher/teacher_marks.html',
                         assigned_classes=assigned_classes,
                         teacher_subjects=teacher_subjects)

@teacher_bp.route('/announcements')
def announcements():
    """Manage announcements"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_announcements.html')

@teacher_bp.route('/attendance')
def attendance():
    """Teacher attendance management page"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get teacher's assigned classes
        cur.execute('''
            SELECT c.id, c.name, c.grade_level 
            FROM classes c
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND c.status = 'active'
            ORDER BY c.grade_level, c.name
        ''', (teacher_id,))
        classes = cur.fetchall()
        
        # Get recent attendance data for teacher's classes
        cur.execute('''
            SELECT 
                a.id,
                a.attendance_date,
                a.status,
                a.notes,
                u.name as student_name,
                c.name as class_name,
                c.grade_level,
                a.marked_on
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            JOIN classes c ON a.class_id = c.id
            JOIN teacher_class_map tcm ON c.id = tcm.class_id
            WHERE tcm.teacher_id = ? AND a.attendance_date >= date('now', '-7 days')
            ORDER BY a.attendance_date DESC, c.name, u.name
        ''', (teacher_id,))
        attendance_records = cur.fetchall()
        
        return render_template('teacher/teacher_attendance.html', 
                             classes=classes, 
                             attendance_records=attendance_records)
        
    except Exception as e:
        flash(f'Error loading attendance data: {str(e)}', 'error')
        return redirect(url_for('teacher.dashboard'))
    finally:
        conn.close()

@teacher_bp.route('/attendance/mark', methods=['GET', 'POST'])
def mark_attendance():
    """Mark attendance for teacher's class"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    
    if request.method == 'GET':
        class_id = request.args.get('class_id')
        attendance_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not class_id:
            flash('Class ID is required', 'error')
            return redirect(url_for('teacher.attendance'))
        
        conn = get_db()
        cur = conn.cursor()
        
        try:
            # Verify teacher has access to this class
            cur.execute('''
                SELECT c.name, c.grade_level 
                FROM classes c
                JOIN teacher_class_map tcm ON c.id = tcm.class_id
                WHERE c.id = ? AND tcm.teacher_id = ?
            ''', (class_id, teacher_id))
            class_info = cur.fetchone()
            
            if not class_info:
                flash('Class not found or access denied', 'error')
                return redirect(url_for('teacher.attendance'))
            
            # Get students in this class
            cur.execute('''
                SELECT u.id, u.name
                FROM users u
                JOIN student_class_map scm ON u.id = scm.student_id
                WHERE scm.class_id = ? AND u.role = 'student' AND scm.status = 'active'
                ORDER BY u.name
            ''')
            students = cur.fetchall()
            
            # Get existing attendance for this date
            cur.execute('''
                SELECT student_id, status, notes
                FROM attendance
                WHERE class_id = ? AND attendance_date = ?
            ''')
            existing_attendance = {row[0]: {'status': row[1], 'notes': row[2]} 
                                 for row in cur.fetchall()}
            
            return render_template('teacher/mark_attendance.html',
                                 class_id=class_id,
                                 class_info=class_info,
                                 students=students,
                                 attendance_date=attendance_date,
                                 existing_attendance=existing_attendance)
            
        except Exception as e:
            flash(f'Error loading class data: {str(e)}', 'error')
            return redirect(url_for('teacher.attendance'))
        finally:
            conn.close()
    
    # POST request - save attendance
    class_id = request.form.get('class_id')
    attendance_date = request.form.get('attendance_date')
    
    if not class_id or not attendance_date:
        flash('Class ID and date are required', 'error')
        return redirect(url_for('teacher.attendance'))
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verify teacher has access to this class
        cur.execute('''
            SELECT 1 FROM teacher_class_map 
            WHERE class_id = ? AND teacher_id = ?
        ''', (class_id, teacher_id))
        
        if not cur.fetchone():
            flash('Access denied to this class', 'error')
            return redirect(url_for('teacher.attendance'))
        
        # Get all students in the class
        cur.execute('''
            SELECT u.id
            FROM users u
            JOIN student_class_map scm ON u.id = scm.student_id
            WHERE scm.class_id = ? AND u.role = 'student' AND scm.status = 'active'
        ''')
        students = [row[0] for row in cur.fetchall()]
        
        attendance_saved = 0
        for student_id in students:
            status = request.form.get(f'status_{student_id}', 'absent')
            notes = request.form.get(f'notes_{student_id}', '').strip()
            
            # Delete existing attendance record if any
            cur.execute('''
                DELETE FROM attendance 
                WHERE student_id = ? AND class_id = ? AND attendance_date = ?
            ''', (student_id, class_id, attendance_date))
            
            # Insert new attendance record
            cur.execute('''
                INSERT INTO attendance (student_id, class_id, attendance_date, status, marked_by, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, class_id, attendance_date, status, teacher_id, notes))
            
            attendance_saved += 1
        
        conn.commit()
        flash(f'Attendance marked for {attendance_saved} students', 'success')
        return redirect(url_for('teacher.attendance'))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error saving attendance: {str(e)}', 'error')
        return redirect(url_for('teacher.mark_attendance', class_id=class_id, date=attendance_date))
    finally:
        conn.close()

# ============================================================================
# MARKS AND REPORTS ROUTES
# ============================================================================

def verify_teacher_access(teacher_id, class_id, subject_name):
    """Verify teacher has access to the given class and subject"""
    conn = get_db()
    cur = conn.cursor()
    
    # Check if teacher is assigned to the class
    cur.execute('''
        SELECT 1 FROM teacher_class_map 
        WHERE teacher_id = ? AND class_id = ?
    ''', (teacher_id, class_id))
    
    class_access = cur.fetchone() is not None
    
    # Check if teacher is assigned to the subject
    cur.execute('''
        SELECT 1 FROM teacher_subjects 
        WHERE teacher_id = ? AND subject_name = ?
    ''', (teacher_id, subject_name))
    
    subject_access = cur.fetchone() is not None
    
    conn.close()
    return class_access and subject_access

@teacher_bp.route('/assessments/list')
def assessments_list():
    """Get list of assessments for a class and subject"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id')
    subject_name = request.args.get('subject_name')
    
    if not class_id or not subject_name:
        return jsonify({'error': 'class_id and subject_name are required'}), 400
    
    # Verify teacher access
    if not verify_teacher_access(teacher_id, class_id, subject_name):
        return jsonify({'error': 'Access denied'}), 403
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    cur.execute('''
        SELECT id, title, assessment_date, max_score, weight, description
        FROM assessments
        WHERE class_id = ? AND subject_name = ? AND teacher_id = ?
        ORDER BY assessment_date DESC
    ''', (class_id, subject_name, teacher_id))
    
    assessments = []
    for row in cur.fetchall():
        assessments.append({
            'id': row[0],
            'title': row[1],
            'date': row[2],
            'max_score': row[3],
            'weight': row[4],
            'description': row[5]
        })
    
    conn.close()
    return jsonify(assessments)

@teacher_bp.route('/assessments/create', methods=['POST'])
def create_assessment():
    """Create a new assessment"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    
    # Get form data
    class_id = request.form.get('class_id')
    subject_name = request.form.get('subject_name')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    assessment_date = request.form.get('assessment_date')
    max_score = request.form.get('max_score')
    weight = request.form.get('weight', '1.0')
    
    # Validation
    if not all([class_id, subject_name, title, assessment_date, max_score]):
        flash('All required fields must be filled', 'error')
        return redirect(url_for('teacher.marks'))
    
    try:
        max_score = float(max_score)
        weight = float(weight)
        if max_score <= 0:
            raise ValueError("Max score must be positive")
        if not (0 <= weight <= 1):
            raise ValueError("Weight must be between 0 and 1")
    except ValueError as e:
        flash(f'Invalid input: {e}', 'error')
        return redirect(url_for('teacher.marks'))
    
    # Verify teacher access
    if not verify_teacher_access(teacher_id, class_id, subject_name):
        flash('Access denied', 'error')
        return redirect(url_for('teacher.marks'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    try:
        cur.execute('''
            INSERT INTO assessments (class_id, subject_name, teacher_id, title, description, 
                                   assessment_date, max_score, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (class_id, subject_name, teacher_id, title, description, assessment_date, max_score, weight))
        
        conn.commit()
        flash('Assessment created successfully', 'success')
        
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            flash('An assessment with this title already exists for this date', 'error')
        else:
            flash(f'Database error: {e}', 'error')
    except Exception as e:
        flash(f'Error creating assessment: {e}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('teacher.marks'))

@teacher_bp.route('/assessments/delete', methods=['POST'])
def delete_assessment():
    """Delete an assessment and all associated marks"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    assessment_id = request.form.get('assessment_id')
    
    if not assessment_id:
        flash('Assessment ID is required', 'error')
        return redirect(url_for('teacher.marks'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Verify teacher owns this assessment
    cur.execute('''
        SELECT class_id, subject_name FROM assessments 
        WHERE id = ? AND teacher_id = ?
    ''', (assessment_id, teacher_id))
    
    assessment = cur.fetchone()
    if not assessment:
        flash('Assessment not found or access denied', 'error')
        conn.close()
        return redirect(url_for('teacher.marks'))
    
    try:
        # Delete assessment (marks will be deleted automatically due to CASCADE)
        cur.execute('DELETE FROM assessments WHERE id = ?', (assessment_id,))
        conn.commit()
        flash('Assessment deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting assessment: {e}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('teacher.marks'))

@teacher_bp.route('/marks/roster')
def marks_roster():
    """Get roster of students for a class with existing marks for an assessment"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id')
    assessment_id = request.args.get('assessment_id')
    
    if not class_id or not assessment_id:
        return jsonify({'error': 'class_id and assessment_id are required'}), 400
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Verify teacher owns this assessment
    cur.execute('''
        SELECT class_id, subject_name, max_score FROM assessments 
        WHERE id = ? AND teacher_id = ?
    ''', (assessment_id, teacher_id))
    
    assessment = cur.fetchone()
    if not assessment or str(assessment[0]) != str(class_id):
        return jsonify({'error': 'Assessment not found or access denied'}), 403
    
    # Get students in the class with their marks
    cur.execute('''
        SELECT 
            u.id,
            u.name,
            COALESCE(m.score, '') as score,
            COALESCE(m.comment, '') as comment
        FROM users u
        INNER JOIN student_class_map scm ON u.id = scm.student_id
        LEFT JOIN marks m ON u.id = m.student_id AND m.assessment_id = ?
        WHERE scm.class_id = ? AND u.role = 'student'
        ORDER BY u.name
    ''', (assessment_id, class_id))
    
    students = []
    for row in cur.fetchall():
        students.append({
            'id': row[0],
            'name': row[1],
            'score': row[2],
            'comment': row[3]
        })
    
    conn.close()
    return jsonify({
        'students': students,
        'max_score': assessment[2]
    })

@teacher_bp.route('/marks/save', methods=['POST'])
def save_marks():
    """Save marks for multiple students"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    
    try:
        data = request.get_json()
        assessment_id = data.get('assessment_id')
        items = data.get('items', [])
        
        if not assessment_id or not items:
            return jsonify({'error': 'assessment_id and items are required'}), 400
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        
        # Verify teacher owns this assessment and get max_score
        cur.execute('''
            SELECT class_id, subject_name, max_score FROM assessments 
            WHERE id = ? AND teacher_id = ?
        ''', (assessment_id, teacher_id))
        
        assessment = cur.fetchone()
        if not assessment:
            return jsonify({'error': 'Assessment not found or access denied'}), 403
        
        max_score = assessment[2]
        
        # Process marks in transaction
        results = {'saved': 0, 'updated': 0, 'skipped': 0, 'errors': []}
        
        for item in items:
            student_id = item.get('student_id')
            score = item.get('score')
            comment = item.get('comment', '')
            
            if not student_id or score == '':
                results['skipped'] += 1
                continue
            
            try:
                score = float(score)
                if score < 0 or score > max_score:
                    results['errors'].append(f'Score {score} for student {student_id} is out of range (0-{max_score})')
                    continue
                
                # Check if mark already exists
                cur.execute('''
                    SELECT id FROM marks 
                    WHERE assessment_id = ? AND student_id = ?
                ''', (assessment_id, student_id))
                
                existing = cur.fetchone()
                
                if existing:
                    # Update existing mark
                    cur.execute('''
                        UPDATE marks 
                        SET score = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = ? AND student_id = ?
                    ''', (score, comment, assessment_id, student_id))
                    results['updated'] += 1
                else:
                    # Insert new mark
                    cur.execute('''
                        INSERT INTO marks (assessment_id, student_id, score, comment)
                        VALUES (?, ?, ?, ?)
                    ''', (assessment_id, student_id, score, comment))
                    results['saved'] += 1
                
            except ValueError:
                results['errors'].append(f'Invalid score for student {student_id}')
            except Exception as e:
                results['errors'].append(f'Error saving mark for student {student_id}: {str(e)}')
        
        conn.commit()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'Failed to save marks: {str(e)}'}), 500

@teacher_bp.route('/reports/class')
def class_report():
    """Generate class report for an assessment or subject"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id')
    subject_name = request.args.get('subject_name')
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    if not class_id or not subject_name:
        flash('Class and subject are required', 'error')
        return redirect(url_for('teacher.marks'))
    
    # Verify teacher access
    if not verify_teacher_access(teacher_id, class_id, subject_name):
        flash('Access denied', 'error')
        return redirect(url_for('teacher.marks'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Build date filter
    date_filter = ""
    params = [class_id, subject_name, teacher_id]
    if from_date:
        date_filter += " AND a.assessment_date >= ?"
        params.append(from_date)
    if to_date:
        date_filter += " AND a.assessment_date <= ?"
        params.append(to_date)
    
    # Get assessments and their statistics
    cur.execute(f'''
        SELECT 
            a.id,
            a.title,
            a.assessment_date,
            a.max_score,
            a.weight,
            COUNT(m.score) as num_scores,
            AVG(m.score) as avg_score,
            MIN(m.score) as min_score,
            MAX(m.score) as max_score
        FROM assessments a
        LEFT JOIN marks m ON a.id = m.assessment_id
        WHERE a.class_id = ? AND a.subject_name = ? AND a.teacher_id = ?
        {date_filter}
        GROUP BY a.id
        ORDER BY a.assessment_date DESC
    ''', params)
    
    assessments_stats = cur.fetchall()
    
    # Get class name
    cur.execute('SELECT name FROM classes WHERE id = ?', (class_id,))
    class_name = cur.fetchone()[0] if cur.fetchone() else "Unknown Class"
    
    conn.close()
    
    return render_template('teacher/class_report.html',
                         assessments_stats=assessments_stats,
                         class_name=class_name,
                         subject_name=subject_name,
                         from_date=from_date,
                         to_date=to_date)

@teacher_bp.route('/reports/student/<int:student_id>')
def student_report(student_id):
    """Generate individual student report"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id')
    subject_name = request.args.get('subject_name')
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    if not class_id or not subject_name:
        flash('Class and subject are required', 'error')
        return redirect(url_for('teacher.marks'))
    
    # Verify teacher access
    if not verify_teacher_access(teacher_id, class_id, subject_name):
        flash('Access denied', 'error')
        return redirect(url_for('teacher.marks'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Get student info
    cur.execute('SELECT name FROM users WHERE id = ? AND role = "student"', (student_id,))
    student_name = cur.fetchone()
    if not student_name:
        flash('Student not found', 'error')
        return redirect(url_for('teacher.marks'))
    student_name = student_name[0]
    
    # Build date filter
    date_filter = ""
    params = [class_id, subject_name, teacher_id, student_id]
    if from_date:
        date_filter += " AND a.assessment_date >= ?"
        params.append(from_date)
    if to_date:
        date_filter += " AND a.assessment_date <= ?"
        params.append(to_date)
    
    # Get student's marks
    cur.execute(f'''
        SELECT 
            a.title,
            a.assessment_date,
            a.max_score,
            a.weight,
            m.score,
            m.comment
        FROM assessments a
        INNER JOIN marks m ON a.id = m.assessment_id
        WHERE a.class_id = ? AND a.subject_name = ? AND a.teacher_id = ? AND m.student_id = ?
        {date_filter}
        ORDER BY a.assessment_date DESC
    ''', params)
    
    marks = cur.fetchall()
    
    # Calculate weighted average
    total_weighted_score = 0
    total_weight = 0
    for mark in marks:
        if mark[4] is not None:  # score exists
            percentage = (mark[4] / mark[2]) * 100  # score / max_score * 100
            total_weighted_score += percentage * mark[3]  # * weight
            total_weight += mark[3]
    
    weighted_average = total_weighted_score / total_weight if total_weight > 0 else 0
    
    conn.close()
    
    return render_template('teacher/student_report.html',
                         student_name=student_name,
                         marks=marks,
                         weighted_average=weighted_average,
                         subject_name=subject_name)

@teacher_bp.route('/reports/export_csv')
def export_csv():
    """Export assessment marks as CSV"""
    if 'role' not in session or session['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    teacher_id = session.get('user_id')
    assessment_id = request.args.get('assessment_id')
    
    if not assessment_id:
        flash('Assessment ID is required', 'error')
        return redirect(url_for('teacher.marks'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Verify teacher owns this assessment
    cur.execute('''
        SELECT a.title, a.max_score, c.name as class_name, a.subject_name
        FROM assessments a
        INNER JOIN classes c ON a.class_id = c.id
        WHERE a.id = ? AND a.teacher_id = ?
    ''', (assessment_id, teacher_id))
    
    assessment = cur.fetchone()
    if not assessment:
        flash('Assessment not found or access denied', 'error')
        return redirect(url_for('teacher.marks'))
    
    # Get marks data
    cur.execute('''
        SELECT 
            u.name,
            COALESCE(m.score, '') as score,
            COALESCE(m.comment, '') as comment
        FROM users u
        INNER JOIN student_class_map scm ON u.id = scm.student_id
        INNER JOIN assessments a ON scm.class_id = a.class_id
        LEFT JOIN marks m ON u.id = m.student_id AND m.assessment_id = ?
        WHERE a.id = ? AND u.role = 'student'
        ORDER BY u.name
    ''', (assessment_id, assessment_id))
    
    marks_data = cur.fetchall()
    conn.close()
    
    # Generate CSV content
    import io
    from flask import Response
    
    output = io.StringIO()
    output.write(f"Assessment: {assessment[0]}\n")
    output.write(f"Class: {assessment[2]}, Subject: {assessment[3]}\n")
    output.write(f"Max Score: {assessment[1]}\n\n")
    output.write("Student Name,Score,Comment\n")
    
    for row in marks_data:
        # Escape commas and quotes in CSV
        name = str(row[0]).replace('"', '""')
        score = str(row[1])
        comment = str(row[2]).replace('"', '""')
        output.write(f'"{name}","{score}","{comment}"\n')
    
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{assessment[0]}_marks.csv"'}
    )
    
    return response

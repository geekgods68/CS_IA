from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import sqlite3
import os
from models.db_models import UserDB, UserRoleDB

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/site')
@login_required
def site():
    """Student dashboard/home page"""
    return render_template('student/site.html')

@student_bp.route('/classes')
@login_required
def classes():
    """Display student's enrolled classes"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get student's enrolled classes with details
        cur.execute('''
            SELECT c.id, c.name, c.description, c.grade_level, c.section,
                   c.schedule_days, c.schedule_time_start, c.schedule_time_end,
                   c.room_number, c.type,
                   COUNT(DISTINCT scm2.student_id) as total_students
            FROM classes c
            JOIN student_class_map scm ON c.id = scm.class_id
            LEFT JOIN student_class_map scm2 ON c.id = scm2.class_id
            WHERE scm.student_id = ? AND c.status = 'active'
            GROUP BY c.id, c.name, c.description, c.grade_level, c.section,
                     c.schedule_days, c.schedule_time_start, c.schedule_time_end,
                     c.room_number, c.type
            ORDER BY c.name
        ''', (current_user.id,))
        
        enrolled_classes = []
        for row in cur.fetchall():
            class_info = {
                'id': row[0],
                'name': row[1],
                'description': row[2] or 'No description available',
                'grade_level': row[3],
                'section': row[4],
                'schedule_days': row[5],
                'schedule_time_start': row[6],
                'schedule_time_end': row[7],
                'room_number': row[8],
                'type': row[9],
                'total_students': row[10]
            }
            enrolled_classes.append(class_info)
        
        # Get student's subjects
        cur.execute('''
            SELECT subject_name
            FROM student_subjects
            WHERE student_id = ?
            ORDER BY subject_name
        ''', (current_user.id,))
        
        student_subjects = [row[0] for row in cur.fetchall()]
        
        return render_template('student/student_classes.html', 
                             enrolled_classes=enrolled_classes,
                             student_subjects=student_subjects)
    
    except Exception as e:
        flash(f'Error loading classes: {str(e)}', 'error')
        return render_template('student/student_classes.html', 
                             enrolled_classes=[],
                             student_subjects=[])
    finally:
        if conn:
            conn.close()

@student_bp.route('/homework')
@login_required
def homework():
    """Display student homework assignments"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get homework assignments for student's enrolled classes
        cur.execute('''
            SELECT r.id, r.filename, r.upload_time, c.name as class_name,
                   s.name as subject_name, r.type
            FROM resources r
            JOIN classes c ON r.class_id = c.id
            JOIN student_class_map scm ON c.id = scm.class_id
            LEFT JOIN subjects s ON c.id = s.class_id
            WHERE scm.student_id = ? AND r.type = 'homework'
            ORDER BY r.upload_time DESC
        ''', (current_user.id,))
        
        homework_assignments = []
        for row in cur.fetchall():
            homework_assignments.append({
                'id': row[0],
                'title': row[1].replace('.pdf', '').replace('_', ' ').title(),
                'filename': row[1],
                'upload_date': row[2],
                'class_name': row[3],
                'subject_name': row[4] or 'General',
                'type': row[5]
            })
        
        # Get student's subjects for the filter dropdown
        cur.execute('''
            SELECT subject_name
            FROM student_subjects
            WHERE student_id = ?
            ORDER BY subject_name
        ''', (current_user.id,))
        
        student_subjects = [row[0] for row in cur.fetchall()]
        
        return render_template('student/student_homework.html',
                             homework_assignments=homework_assignments,
                             student_subjects=student_subjects,
                             submission_history=[])  # Will be populated when submissions are implemented
    
    except Exception as e:
        flash(f'Error loading homework: {str(e)}', 'error')
        return render_template('student/student_homework.html',
                             homework_assignments=[],
                             student_subjects=[],
                             submission_history=[])
    finally:
        if conn:
            conn.close()

@student_bp.route('/doubts')
@login_required
def doubts():
    """Display student doubts and allow posting new ones"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get student's doubts
        cur.execute('''
            SELECT d.id, d.question, d.subject, d.posted_time, d.response,
                   d.response_time, d.anonymous, c.name as class_name,
                   u.username as responder_name
            FROM doubts d
            LEFT JOIN classes c ON d.class_id = c.id
            LEFT JOIN users u ON d.responder_id = u.id
            WHERE d.student_id = ?
            ORDER BY d.posted_time DESC
        ''', (current_user.id,))
        
        student_doubts = []
        for row in cur.fetchall():
            student_doubts.append({
                'id': row[0],
                'question': row[1],
                'subject': row[2],
                'posted_time': row[3],
                'response': row[4],
                'response_time': row[5],
                'anonymous': row[6],
                'class_name': row[7],
                'responder_name': row[8],
                'status': 'Answered' if row[4] else 'Pending'
            })
        
        # Get student's classes for the form
        cur.execute('''
            SELECT c.id, c.name
            FROM classes c
            JOIN student_class_map scm ON c.id = scm.class_id
            WHERE scm.student_id = ? AND c.status = 'active'
            ORDER BY c.name
        ''', (current_user.id,))
        
        student_classes = [{'id': row[0], 'name': row[1]} for row in cur.fetchall()]
        
        # Get student's subjects
        cur.execute('''
            SELECT subject_name
            FROM student_subjects
            WHERE student_id = ?
            ORDER BY subject_name
        ''', (current_user.id,))
        
        student_subjects = [row[0] for row in cur.fetchall()]
        
        return render_template('student/student_doubts.html',
                             student_doubts=student_doubts,
                             student_classes=student_classes,
                             student_subjects=student_subjects)
    
    except Exception as e:
        flash(f'Error loading doubts: {str(e)}', 'error')
        return render_template('student/student_doubts.html',
                             student_doubts=[],
                             student_classes=[],
                             student_subjects=[])
    finally:
        if conn:
            conn.close()

@student_bp.route('/doubts', methods=['POST'])
@login_required
def post_doubt():
    """Handle posting a new doubt"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        class_id = request.form.get('class_id')
        subject = request.form.get('subject')
        question = request.form.get('question')
        anonymous = 1 if request.form.get('anonymous') else 0
        
        if not question:
            flash('Question cannot be empty', 'error')
            return redirect(url_for('student.doubts'))
        
        cur.execute('''
            INSERT INTO doubts (student_id, class_id, subject, question, anonymous)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_user.id, class_id if class_id else None, subject, question, anonymous))
        
        conn.commit()
        flash('Your doubt has been posted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error posting doubt: {str(e)}', 'error')
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('student.doubts'))

@student_bp.route('/feedback')
@login_required
def feedback():
    """Display student feedback page and submitted feedback"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get student's feedback history
        cur.execute('''
            SELECT id, feedback_type, subject, teacher_name, class_name, 
                   rating, comments, status, admin_response, submitted_on, responded_on
            FROM feedback
            WHERE student_id = ?
            ORDER BY submitted_on DESC
        ''', (current_user.id,))
        
        my_feedback = []
        for row in cur.fetchall():
            my_feedback.append({
                'id': row[0],
                'feedback_type': row[1],
                'subject': row[2],
                'teacher_name': row[3],
                'class_name': row[4],
                'rating': row[5],
                'comments': row[6],
                'status': row[7],
                'admin_response': row[8],
                'submitted_on': row[9],
                'responded_on': row[10]
            })
        
        return render_template('student/student_feedback.html', my_feedback=my_feedback)
    
    except Exception as e:
        flash(f'Error loading feedback: {str(e)}', 'error')
        return render_template('student/student_feedback.html', my_feedback=[])
    finally:
        if conn:
            conn.close()

@student_bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Handle feedback submission"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        feedback_type = request.form.get('feedback_type')
        subject = request.form.get('subject')
        teacher_name = request.form.get('teacher_name')
        class_name = request.form.get('class_name')
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        anonymous = 1 if request.form.get('anonymous') else 0
        
        if not feedback_type or not comments:
            flash('Feedback type and comments are required', 'error')
            return redirect(url_for('student.feedback'))
        
        cur.execute('''
            INSERT INTO feedback (student_id, feedback_type, subject, teacher_name, 
                                class_name, rating, comments, anonymous)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_user.id, feedback_type, subject, teacher_name, 
              class_name, rating, comments, anonymous))
        
        conn.commit()
        flash('Your feedback has been submitted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error submitting feedback: {str(e)}', 'error')
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('student.feedback'))

@student_bp.route('/profile')
@login_required
def profile():
    return render_template('student/student_profile.html')

@student_bp.route('/progress')
@login_required
def progress():
    return render_template('student/student_progress.html')

@student_bp.route('/announcements')
@login_required
def announcements():
    """Display announcements for student"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Get announcements for the student's classes
        cur.execute('''
            SELECT DISTINCT a.id, a.title, a.content, a.priority, a.created_on,
                   u.username as teacher_name, c.name as class_name,
                   s.name as subject_name
            FROM announcements a
            JOIN users u ON a.teacher_id = u.id
            LEFT JOIN classes c ON a.class_id = c.id
            LEFT JOIN subjects s ON a.subject_id = s.id
            LEFT JOIN student_class_map scm ON c.id = scm.class_id
            WHERE (a.target_audience = 'all' 
                   OR (a.target_audience = 'class' AND scm.student_id = ?)
                   OR (a.target_audience = 'subject' AND scm.student_id = ?))
            ORDER BY a.created_on DESC
        ''', (current_user.id, current_user.id))
        
        announcements = []
        for row in cur.fetchall():
            announcements.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'priority': row[3],
                'created_on': row[4],
                'teacher_name': row[5],
                'class_name': row[6] or 'General',
                'subject_name': row[7] or 'General'
            })
        
        # Get student subjects for filter
        cur.execute('''
            SELECT DISTINCT subject_name 
            FROM student_subjects 
            WHERE student_id = ?
        ''', (current_user.id,))
        
        subjects = [row[0] for row in cur.fetchall()]
        
        return render_template('student/student_announcements.html', 
                             announcements=announcements,
                             student_subjects=subjects)
    
    except Exception as e:
        flash(f'Error loading announcements: {str(e)}', 'error')
        return render_template('student/student_announcements.html', 
                             announcements=[],
                             student_subjects=[])
    finally:
        if conn:
            conn.close()

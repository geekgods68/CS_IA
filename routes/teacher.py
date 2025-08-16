from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

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
    
    return render_template('teacher/teacher_classes.html')

@teacher_bp.route('/homework')
def homework():
    """Manage homework assignments"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_homework.html')

@teacher_bp.route('/schedule')
def schedule():
    """View teaching schedule"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_schedule.html')

@teacher_bp.route('/submissions')
def submissions():
    """View student submissions"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_submissions.html')

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
    
    return render_template('teacher/teacher_marks.html')

@teacher_bp.route('/announcements')
def announcements():
    """Manage announcements"""
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/teacher_announcements.html')

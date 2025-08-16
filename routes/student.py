from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os

student_bp = Blueprint('student', __name__, url_prefix='/student')

def get_db():
    """Get database connection"""
    return sqlite3.connect('users.db')

@student_bp.route('/site')
def site():
    """Student dashboard/home page"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    student_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    # Get enrolled classes count
    cur.execute('''
        SELECT COUNT(*) FROM student_class_map 
        WHERE student_id = ?
    ''', (student_id,))
    enrolled_classes_count = cur.fetchone()[0]
    
    # Get subjects count
    cur.execute('''
        SELECT COUNT(*) FROM student_subjects 
        WHERE student_id = ?
    ''', (student_id,))
    subjects_count = cur.fetchone()[0]
    
    # Get pending doubts count
    cur.execute('''
        SELECT COUNT(*) FROM doubts 
        WHERE student_id = ? AND status = 'open'
    ''', (student_id,))
    pending_doubts_count = cur.fetchone()[0]
    
    # Get enrolled classes details
    cur.execute('''
        SELECT c.id, c.name, c.description, c.grade_level, c.type,
               c.schedule_days, c.schedule_time_start, c.schedule_time_end
        FROM classes c
        JOIN student_class_map scm ON c.id = scm.class_id
        WHERE scm.student_id = ? AND c.status = 'active'
        ORDER BY c.name
    ''', (student_id,))
    
    enrolled_classes = []
    for row in cur.fetchall():
        enrolled_classes.append({
            'id': row[0],
            'name': row[1],
            'description': row[2] or 'Test class description',
            'grade_level': row[3] or '10',
            'type': row[4] or 'regular',
            'schedule_days': row[5] or 'Monday, Wednesday, Friday',
            'schedule_time_start': row[6] or '09:00',
            'schedule_time_end': row[7] or '10:30'
        })
    
    conn.close()
    
    return render_template('student/site_new.html',
                         enrolled_classes_count=enrolled_classes_count,
                         subjects_count=subjects_count,
                         pending_doubts_count=pending_doubts_count,
                         enrolled_classes=enrolled_classes)

@student_bp.route('/classes')
def classes():
    """Display student's enrolled classes"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    return render_template('student/student_classes.html')

@student_bp.route('/homework')
def homework():
    """Display homework assignments"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    return render_template('student/student_homework.html')

@student_bp.route('/feedback')
def feedback():
    """Submit anonymous feedback"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    return render_template('student/student_feedback.html')

@student_bp.route('/announcements')
def announcements():
    """View announcements"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    return render_template('student/student_announcements.html')

@student_bp.route('/doubts', methods=['GET', 'POST'])
def doubts():
    """Ask doubts/questions"""
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))
    
    student_id = session.get('user_id')
    conn = get_db()
    cur = conn.cursor()
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        doubt_text = request.form.get('doubt_text')
        
        if subject and doubt_text:
            # Insert new doubt
            cur.execute('''
                INSERT INTO doubts (student_id, subject, doubt_text, status)
                VALUES (?, ?, ?, 'open')
            ''', (student_id, subject, doubt_text))
            conn.commit()
            flash('Your doubt has been submitted successfully!', 'success')
        else:
            flash('Please fill in all fields.', 'error')
    
    # Get student's doubts
    cur.execute('''
        SELECT id, subject, doubt_text, status, submitted_on
        FROM doubts
        WHERE student_id = ?
        ORDER BY submitted_on DESC
    ''', (student_id,))
    
    doubts_data = []
    for row in cur.fetchall():
        doubts_data.append({
            'id': row[0],
            'subject': row[1],
            'doubt_text': row[2],
            'status': row[3],
            'submitted_on': row[4]
        })
    
    conn.close()
    return render_template('student/student_doubts.html', doubts=doubts_data)

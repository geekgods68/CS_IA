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
    
    return render_template('teacher/teacher_dashboard.html')

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

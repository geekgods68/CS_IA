from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
from models.db_models import UserDB, UserRoleDB

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/view_classes')
@login_required
def view_classes():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name, grade, batch FROM classes')
    class_list = cur.fetchall()
    conn.close()
    return render_template('admin/view_classes.html', classes=class_list)

@admin_bp.route('/view_class/<int:class_id>')
@login_required
def view_class(class_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name, description FROM subjects WHERE class_id = ?', (class_id,))
    subjects = cur.fetchall()
    cur.execute('''SELECT u.id, u.username FROM users u
        JOIN student_class_map scm ON u.id = scm.student_id
        WHERE scm.class_id = ?''', (class_id,))
    students = cur.fetchall()
    cur.execute('SELECT name, grade, batch FROM classes WHERE id = ?', (class_id,))
    class_info = cur.fetchone()
    conn.close()
    return render_template('admin/view_class.html', class_info=class_info, subjects=subjects, students=students, class_id=class_id)


@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))
        user_id = cur.lastrowid
        cur.execute('INSERT INTO user_role_map (user_id, role_id, assigned_on) VALUES (?, ?, CURRENT_TIMESTAMP)', (user_id, role_id))
        conn.commit()
        flash('User created successfully!')
        return redirect(url_for('admin.users'))
    cur.execute('SELECT id, role_name FROM user_roles')
    roles = cur.fetchall()
    conn.close()
    return render_template('admin/add_user.html', roles=roles)

@admin_bp.route('/')
@login_required
def dashboard():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users')
    users = cur.fetchall()
    conn.close()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))
        user_id = cur.lastrowid
        cur.execute('INSERT INTO user_role_map (user_id, role_id, assigned_on) VALUES (?, ?, CURRENT_TIMESTAMP)', (user_id, role_id))
        conn.commit()
        flash('User created successfully!')
    cur.execute('SELECT u.id, u.username, ur.role_name FROM users u JOIN user_role_map urm ON u.id = urm.user_id JOIN user_roles ur ON urm.role_id = ur.id')
    users = cur.fetchall()
    cur.execute('SELECT id, role_name FROM user_roles')
    roles = cur.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users, roles=roles)

@admin_bp.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        batch = request.form['batch']
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO classes (name, grade, batch) VALUES (?, ?, ?)', (name, grade, batch))
        conn.commit()
        conn.close()
        flash('Class created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_class.html')

@admin_bp.route('/add_students', methods=['GET', 'POST'])
@login_required
def add_students():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM classes')
    classes = cur.fetchall()
    cur.execute('SELECT id, username FROM users')
    students = cur.fetchall()
    if request.method == 'POST':
        class_id = request.form['class_id']
        student_ids = request.form.getlist('student_ids')
        for student_id in student_ids:
            cur.execute('INSERT INTO student_class_map (student_id, class_id) VALUES (?, ?)', (student_id, class_id))
        conn.commit()
        flash('Students added to class!')
        return redirect(url_for('admin.dashboard'))
    conn.close()
    return render_template('admin/add_students.html', classes=classes, students=students)

@admin_bp.route('/create_subject', methods=['GET', 'POST'])
@login_required
def create_subject():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM classes')
    classes = cur.fetchall()
    if request.method == 'POST':
        class_id = request.form['class_id']
        name = request.form['name']
        description = request.form['description']
        cur.execute('INSERT INTO subjects (class_id, name, description) VALUES (?, ?, ?)', (class_id, name, description))
        conn.commit()
        flash('Subject created!')
        return redirect(url_for('admin.dashboard'))
    conn.close()
    return render_template('admin/create_subject.html', classes=classes)
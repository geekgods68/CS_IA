
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_models import UserDB, UserRoleDB, UserRoleMapDB
import sqlite3

auth_bp = Blueprint('auth', __name__)
DATABASE = 'users.db'


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserDB.find_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            # Fetch user role
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            cur.execute('''SELECT ur.role_name FROM user_roles ur
                JOIN user_role_map urm ON ur.id = urm.role_id
                WHERE urm.user_id = ?''', (user.id,))
            role_row = cur.fetchone()
            conn.close()
            # Store role in session for later use
            from flask import session
            session['role'] = role_row[0] if role_row else None
            login_user(user)
            # Redirect based on role
            if role_row:
                role = role_row[0]
                if role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif role == 'student':
                    return redirect(url_for('student.site'))
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

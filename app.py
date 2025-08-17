from flask import Flask, redirect, url_for, session
import os

def create_app():
    app = Flask(__name__)
    
    # Simple configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['DATABASE'] = 'users.db'
    
    @app.route('/')
    def home():
        # Redirect to login if not authenticated
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Redirect based on role
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif session.get('role') == 'student':
            return redirect(url_for('student.site'))
        else:
            return redirect(url_for('auth.login'))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Optional: Register other blueprints if they exist
    try:
        from routes.teacher import teacher_bp
        app.register_blueprint(teacher_bp)
    except ImportError:
        pass
    
    try:
        from routes.student import student_bp
        app.register_blueprint(student_bp)
    except ImportError:
        pass
    
    try:
        from routes.main import main_bp
        app.register_blueprint(main_bp)
    except ImportError:
        pass

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5004)

from flask import redirect, url_for
from models.db_models import UserDB
from flask import Flask
from config.config import config_by_name
from middleware import log_request
from flask_login import LoginManager
import os


def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.getenv('ENV', 'development')
    app.config.from_object(config_by_name[config_name])
    app.before_request(log_request)

    @app.route('/')
    def home():
        return redirect(url_for('admin.dashboard'))

    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register user_loader after login_manager is initialized
    @login_manager.user_loader
    def load_user(user_id):
        return UserDB.get(user_id)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

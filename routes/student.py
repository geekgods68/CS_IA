from flask import Blueprint, render_template
from flask_login import login_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/site')
@login_required
def site():
    return render_template('student/site.html')

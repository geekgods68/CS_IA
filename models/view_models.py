from datetime import datetime


class UserProfileView:
    def __init__(self, username, name, email, phone=None, address=None):
        self.username = username
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

class UserRoleView:
    def __init__(self, role_name, description):
        self.role_name = role_name
        self.description = description

class UserRoleMapView:
    def __init__(self, username, role_name, assigned_on, assigned_by=None):
        self.username = username
        self.role_name = role_name
        self.assigned_on = assigned_on
        self.assigned_by = assigned_by

class ClassScheduleView:
    def __init__(self, subject, batch, teacher_name, start_time, end_time, zoom_link=None):
        self.subject = subject
        self.batch = batch
        self.teacher_name = teacher_name
        self.start_time = start_time
        self.end_time = end_time
        self.zoom_link = zoom_link

class AttendanceView:
    def __init__(self, student_name, class_subject, status, timestamp):
        self.student_name = student_name
        self.class_subject = class_subject
        self.status = status
        self.timestamp = timestamp

class ResourceView:
    def __init__(self, type, filename, uploader_name, upload_time):
        self.type = type
        self.filename = filename
        self.uploader_name = uploader_name
        self.upload_time = upload_time

class DoubtView:
    def __init__(self, question, student_name, response=None, responder_name=None, posted_time=None, response_time=None, anonymous=True):
        self.question = question
        self.student_name = student_name
        self.response = response
        self.responder_name = responder_name
        self.posted_time = posted_time
        self.response_time = response_time
        self.anonymous = anonymous

class AssessmentView:
    def __init__(self, student_name, class_subject, type, score, max_score, assessment_date):
        self.student_name = student_name
        self.class_subject = class_subject
        self.type = type
        self.score = score
        self.max_score = max_score
        self.assessment_date = assessment_date

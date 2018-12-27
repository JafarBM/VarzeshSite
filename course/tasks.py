from varzeshSite.celery import app
from .models import Enrollment


@app.task
def send_slow_progress_emails():
    enrollments = Enrollment.objects.all()
    for enrollment in enrollments:
        enrollment.check_and_send_slow_progress_email()

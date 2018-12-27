import os

from celery import Celery

from celery.schedules import crontab

from course.constants import SLOW_COURSE_PROGRESS_JOB_RUNTIME

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'varzeshSite.settings')

app = Celery('varzeshSite')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_slow_progress_emails': {
        'task': 'course.tasks.send_slow_progress_emails',
        'schedule': crontab(**SLOW_COURSE_PROGRESS_JOB_RUNTIME),
    },
}

import os

from celery import Celery
from time import sleep, time
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myceleryproject.settings')

app = Celery('myceleryproject')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task
def add(x, y):
    sleep(10)
    return x+y

# @app.task
# def sub(x, y):
#     sleep(20)
#     return x+y

# Method 2
# app.conf.beat_schedule = {
#     'every-10-seconds':{
#         'task': 'myapp.tasks.clear_session_cache',
#         'schedule': 10, 
#         'args': ('11111', )
#     }
# }

# Method 2 using timedelta
# app.conf.beat_schedule = {
#     'every-10-seconds':{
#         'task': 'myapp.tasks.clear_session_cache',
#         'schedule': timedelta(10), 
#         'args': ('11111', )
#     }
# }


from celery.schedules import crontab

app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(hour=1, minute=30, day_of_week=1),
        'args': (16, 16),
    },
}
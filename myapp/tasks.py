from celery import shared_task
from time import sleep
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

@shared_task
def sub(x, y):
    sleep(10)
    return x - y


@shared_task
def clear_session_cache(id):
    print(f'Session Cache cleared: {id}')
    return id

@shared_task
def clear_redis_data(key):
    print(f'Redis Data Cleard: {key}')
    return key

@shared_task
def clear_rabbitmq_data(key):
    print(f'rabbitmq Data Cleard: {key}')
    return key


# Programitically define interval. We do same thing using django admin interval
# 1. Define the interval (e.g., every 10 seconds)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=4,
    period=IntervalSchedule.SECONDS,
)
# 2. Create the periodic task
PeriodicTask.objects.get_or_create(
    name='Importing data every 10s',
    defaults={
        'task': 'myapp.tasks.clear_rabbitmq_data',
        'interval': schedule,
        'args': json.dumps(["hello rabbit"]),
    }
)
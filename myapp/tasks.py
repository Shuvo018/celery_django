from celery import shared_task
from time import sleep
from django_celery_beat.models import PeriodicTask, IntervalSchedule

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

# Programitically define interval. We do same thing using django admin interval
# 1. Define the interval (e.g., every 10 seconds)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.SECONDS,
)
# 2. Create the periodic task
PeriodicTask.objects.create(
    interval=schedule,
    name='Importing data every 10s',
    task='myapp.tasks.clear_redis_data',
)
# 🥬 Celery + Django Integration

A hands-on Django project demonstrating how to integrate **Celery** for asynchronous task processing and periodic scheduling using **Redis** as the message broker.

---
**Resource:**

https://docs.celeryq.dev/en/4.0/userguide/periodic-tasks.html

https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

---

## 📌 What is Celery and Why Do We Need It?

Django handles HTTP requests **synchronously** — one request at a time, in a straight line. This is fine for most tasks, but what happens when a request triggers something slow?

> Sending an email, resizing an image, generating a PDF, calling a third-party API...

If Django handles these inline, the user sits and waits. That's a bad experience.

**Celery** solves this by letting you push slow or scheduled work into a **background queue**, so Django can respond instantly and let a worker process the heavy lifting separately.

```
User Request → Django View → Celery Task (queued) → Instant Response to User
                                    ↓
                             Celery Worker (runs in background)
```

In short: Celery makes your Django app **faster**, **non-blocking**, and capable of running **scheduled jobs**.

---

## ⚙️ Environment Setup

### Prerequisites

- Python 3.8+
- Redis (used as the message broker)

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

### 2. Clone the Repository

```bash
git clone https://github.com/Shuvo018/celery_django.git
cd celery_django
```

### 3. Create & Activate Virtual Environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install django celery redis
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Start the Django Server

```bash
python manage.py runserver
```

### 7. Start the Celery Worker

Open a **new terminal**, activate the virtual environment, then run:

```bash
celery -A myceleryproject worker --loglevel=info
```

### 8. Start Celery Beat (for scheduled tasks)

Using custom scheduler classes:

```bash
# 1. Use pip to install the package:
pip install django-celery-beat

# 2. Add the django_celery_beat module to INSTALLED_APPS in your Django project’ settings.py:

    INSTALLED_APPS = (
        ...,
        'django_celery_beat',
    )
# 3. Apply Django database migrations so that the necessary tables are created:

python manage.py migrate

```

Open another **new terminal** and run:

```bash
celery -A myceleryproject beat --loglevel=info
```

---

## 🔧 Celery Important Settings

These settings go in your `settings.py` file. All Celery settings are prefixed with `CELERY_` when using the `namespace='CELERY'` convention.

```python
# settings.py

# The message broker — Redis in this project
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# Where task results are stored
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


# Timezone — should match Django's TIME_ZONE
CELERY_TIMEZONE = 'Asia/Dhaka'

# For windows
CELERY_WORKER_POOL = "threads"
CELERY_WORKER_CONCURRENCY = 4

# Beat scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

```

And in `myceleryproject/celery.py`, the app is wired up like this:

```python
# myceleryproject/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myceleryproject.settings')

app = Celery('myceleryproject')

# Reads config from settings.py using the CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discovers tasks.py in all INSTALLED_APPS
app.autodiscover_tasks()
```

And in `myceleryproject/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

This ensures the Celery app is loaded when Django starts.

---

## 📚 Key Concepts Explained

### `@shared_task` — Reusable Task Decorator

`@shared_task` lets you define tasks inside a Django **app** (e.g., `myapp/tasks.py`) without importing the specific Celery app instance. This keeps your apps loosely coupled and reusable.

```python
# myapp/tasks.py

from celery import shared_task
import time

@shared_task
def send_welcome_email(user_id):
    # Simulate a slow email sending operation
    time.sleep(3)
    print(f"Welcome email sent to user {user_id}")
    return f"Done for user {user_id}"
```

**Calling it from a view:**

```python
# myapp/views.py

from django.http import JsonResponse
from .tasks import send_welcome_email

def register_user(request):
    user_id = 42
    send_welcome_email.delay(user_id)   # .delay() sends it to the queue
    return JsonResponse({"status": "Registered! Email is being sent."})
```

> `.delay()` queues the task and returns immediately — the user doesn't wait for the email.

---

### `bind=True` — Access Task Metadata

When `bind=True`, the task receives `self` as the first argument, giving access to task metadata like ID, retries, and request info.

```python
from celery import shared_task

@shared_task(bind=True)
def debug_task(self):
    print(f"Task ID: {self.request.id}")
    print(f"Retries so far: {self.request.retries}")
```

---

### `self.retry()` — Automatic Retries

Celery can automatically retry a failed task. Use `self.retry()` inside an exception handler:

```python
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True, max_retries=3)
def fetch_data_from_api(self, url):
    try:
        # Simulated API call
        response = call_external_api(url)
        return response
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)  # Retry after 5 seconds
```

---

### Celery Beat — Periodic / Scheduled Tasks

**Celery Beat** is a scheduler that kicks off tasks at defined intervals. You configure the schedule in `settings.py` using `CELERY_BEAT_SCHEDULE`.

```python
# settings.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {

    # Runs every 10 seconds
    'print-hello-every-10s': {
        'task': 'myapp.tasks.say_hello',
        'schedule': 10.0,
    },

    # Runs every day at midnight
    'daily-cleanup': {
        'task': 'myapp.tasks.cleanup_old_records',
        'schedule': crontab(hour=0, minute=0),
    },

    # Runs every Monday at 9 AM
    'weekly-report': {
        'task': 'myapp.tasks.send_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week='monday'),
    },
}
```

The corresponding tasks:

```python
# myapp/tasks.py

from celery import shared_task

@shared_task
def say_hello():
    print("Hello from Celery Beat!")

@shared_task
def cleanup_old_records():
    # Delete records older than 30 days
    print("Old records cleaned up.")

@shared_task
def send_weekly_report():
    print("Weekly report sent!")
```

> **Note:** Celery Beat only *triggers* tasks — the actual work is still done by the **worker**. Both must be running.

---

### `crontab` — Cron-style Scheduling

`crontab` gives you fine-grained control over when tasks run, just like a Unix cron job.

| Expression | Meaning |
|---|---|
| `crontab()` | Every minute |
| `crontab(minute=0, hour='*/2')` | Every 2 hours |
| `crontab(day_of_week='friday', hour=17, minute=0)` | Every Friday at 5 PM |
| `crontab(day_of_month=1)` | First day of every month |

---

### `.delay()` vs `.apply_async()`

Both send a task to the queue, but `.apply_async()` gives more control:

```python
# Simple — no options
send_welcome_email.delay(user_id)

# Advanced — with countdown, expiry, custom queue
send_welcome_email.apply_async(
    args=[user_id],
    countdown=30,        # Wait 30 seconds before running
    expires=300,         # Cancel if not run within 5 minutes
    queue='high_priority'
)
```

---

## 🗂️ Project Structure

```
celery_django/
├── myceleryproject/        # Django project config
│   ├── __init__.py         # Loads Celery app on startup
│   ├── celery.py           # Celery app configuration
│   ├── settings.py         # Django + Celery settings
│   └── urls.py
├── myapp/                  # Django app
│   ├── tasks.py            # Celery task definitions
│   ├── views.py
│   └── ...
├── manage.py
└── db.sqlite3
```

---

## 🚀 Running Everything Together

You need **3 terminals** running simultaneously:

| Terminal | Command |
|---|---|
| 1 | `python manage.py runserver` |
| 2 | `celery -A myceleryproject worker --loglevel=info` |
| 3 | `celery -A myceleryproject beat --loglevel=info` *(for scheduled tasks)* |

---

## 📄 License

This project is open source and available for learning purposes.

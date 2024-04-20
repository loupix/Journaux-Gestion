import os
from datetime import timedelta
from .settings import BASE_DIR

from celery import Celery
from celery.schedules import crontab


from celery.utils.log import get_task_logger
logger = get_task_logger("tasks")

from post_request_task.task import PostRequestTask

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'journauxGestion.settings')

app = Celery('journauxGestion', task_cls=PostRequestTask, backend='database')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "cluster items": {
        "task":"item.tasks.cluster_items",
        "schedule": 30.0
    },
}
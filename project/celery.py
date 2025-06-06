import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.

# DJANGO_SETTINGS_MODULE = 'project.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 'creat_new_bill_month': {
    #     'task': 'apps.service.tasks.creat_new_bill_month',
    #     'schedule': crontab(minute='*/1'),
    # },
}
# crontab(0, 0, day_of_month='1')

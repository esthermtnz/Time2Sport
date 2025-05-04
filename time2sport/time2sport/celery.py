import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')

#Sets up celery and the tasks for the workers
app = Celery('time2sport')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

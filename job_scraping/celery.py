import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_scraping.settings')

app = Celery('job_scraping')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.update(
    worker_max_tasks_per_child=1,
    broker_pool_limit=None
)

app.conf.beat_schedule = {
    'Execute every three hours': {
        'task': 'hh.tasks.start_crawl',
        'schedule': crontab(minute=0, hour='*/3'),
    },     
}


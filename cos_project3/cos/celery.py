# celery 설정
from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
import os

from datetime import timedelta
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cos.settings')


app = Celery('cos_project3')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'add-week-scraping': {
        'task': 'scraping.add',
        # 매주 월요일 새벽 3시에 스크래핑 스케줄링
        'schedule': crontab(minute = 0, hour=3, day_of_week=1),  # 0 = 일요일, 6 = 토요일
        'args': (),
    }
}
app.conf.timezone = 'Asia/Seoul'
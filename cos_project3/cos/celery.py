# celery 설정
from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cos.settings')
app = Celery('cos_project3')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'add-week-scraping': {
        'task': 'scraping.add',
        # 매주 월요일 새벽 3시에 스크래핑 스케줄링
        'schedule': crontab(minute =23, hour=20, day_of_week=5),  # 0 = 일요일, 6 = 토요일
        'args': (),
    }
}
app.conf.timezone = 'Asia/Seoul'
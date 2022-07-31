from __future__ import absolute_import, unicode_literals
from celery import shared_task, Celery
from app.recommend import excel_recommend
from app.scraping.cos_scraping import scraping

@shared_task(name='scraping.add')
def scraping_scheduling():
    sc = scraping(1)

@shared_task(name="excel_recommend_task")
def excel_recommend_task(image, user, title):
    recommend_object=excel_recommend(image, user, title)
    recommend_object.cosine()
from __future__ import absolute_import, unicode_literals
from celery import shared_task, Celery
from app.recommend import recommend, excel_recommend
from app.scraping.cos_scraping import scraping

# app = Celery('tasks', broker='redis://127.0.0.1:6379/0')

@shared_task(name='scraping.add')
def scraping_scheduling():
    sc = scraping(1)

# @shared_task(name='recommend_task')
# def recommend_task(image):
#     recommend_object = recommend(image)
#     result = recommend_object.cosine()
#     print(result)

@shared_task(name="excel_recommend_task")
def excel_recommend_task(image, user):
    recommend_object=excel_recommend(image, user)
    recommend_object.cosine()
from __future__ import absolute_import, unicode_literals
from celery import shared_task, Celery
from app.recommend import recommend
from app.scraping.cos_scraping import scraping

app = Celery('tasks', broker='redis://127.0.0.1:6379/0')

@shared_task(name='scraping.add')
def scraping_scheduling():
    sc = scraping(1)

# 일단 celery를 통해 추천 리스트를 뽑는 것까지는 완성.
# html에 렌더링하여 반환하는 부분 추가 요망.
@app.task
def recommend_task(image):
    recommend_object = recommend(image)
    result = recommend_object.cosine()
    print(result)
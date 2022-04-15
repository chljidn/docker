# html parser api
import urllib.request
import re
from requests_html import HTMLSession
# 데이터 베이스 및 캐시
import redis
from django.core.cache import cache
from app.models import Cos
import json

class scraping:
    cosmetic = cache.get_or_set('cosmetic', Cos.objects.values('prdname'))
    with open('./cos_project3_settings.json') as f:
        secret = json.loads(f.read())

    def __init__(self, idx):
        self.redis3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)
        self.idx = idx  # 입력 받은 idx부터 시작할 수 있도록 함
        # with open('./cos_project3_settings.json') as f:
        #     self.__secret = json.loads(f.read())
        # lobs_html = self.lobs()

    # 페이지에서 href 링크 모두 뽑아내기
    def get_links(self, html):
        webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
        return webpage_regex.findall(html)

    # 페이지에서 전성분 모두 뽑아내기 - 전성분은 화장품의 성분들 의미
    def get_ingredient(self, html):
        webpage_regex = re.findall('전성분</dt>(.*?)</dd>{1}', html)  # </dd>가 한번 나올 때까지만 찾기
        return webpage_regex

    def detailed_page(self, url):
        session = HTMLSession()
        r = session.get(url)
        r.html.render(scrolldown=3, timeout=40)
        session.close()
        return r

    def lobs(self):
        # html에서 get_links 함수를 통해서 href 링크들을 모두 가져온다(넘어온 xhr은 상품들에 관한 정보만 있으므로 링크들은 모두 상품들의 상세페이지 링크)
        total_link = []
        start_idx = self.idx  # 밑에서 enumerate 돌 때, key로 사용할 시작점으로 사용하기 위함.

        while True:
            try:
                url = scraping.secret['django']['scraping'].format(self.idx)
                # url = self.__secret['django']['scraping'].format(self.idx)
                main_html = urllib.request.urlopen(url).read().decode('utf-8')
                link_list = self.get_links(main_html)

                if link_list == []:
                    break
                total_link.extend(link_list)

                self.idx += 60
            except Exception as e:
                print(e)

        # 링크 뽑아내는 과정에서 같은 상세페이지가 두번씩 추가되므로, 중복 없애기 위해 set 사용
        for j, i in enumerate(set(total_link), start=start_idx):
            print(f'{j}번 째 상품 진행 중...')

            try:
                res = self.detailed_page(i)
            except Exception as e:
                print(j, '번에서', e, '발생')
                continue
            else:
                self.redis3.set(str(j), str(res.html.html))  # 전체 html 캐싱

        from app.scraping import cos_preprocessing
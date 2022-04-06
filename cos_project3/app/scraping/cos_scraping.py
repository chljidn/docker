# html parser api
import urllib.request
import re
from requests_html import HTMLSession

# 데이터 베이스 및 캐시
import redis
from django.core.cache import cache
from app.models import Cos

from bs4 import BeautifulSoup as bs
import json

class scraping:
    cosmetic = cache.get_or_set('cosmetic', Cos.objects.values('prdname'))
    # with open('./cos_project3_settings.json') as f:
        # __secret = json.loads(f.read())

    def __init__(self, idx):
        self.redis3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 상세 페이지 html 가져오기 위함
        self.redis4 = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)  # 각 상품 딕셔너리 저장하기 위함
        self.idx = idx  # 입력 받은 idx부터 시작할 수 있도록 함
        with open('./cos_project3_settings.json') as f:
            self.__secret = json.loads(f.read())
        lobs_html = self.lobs()
        self.preprocessing()

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
        # xhr로 넘어오는 상품들의 html을 가져온다.
        # html에서 get_links 함수를 통해서 href 링크들을 모두 가져온다(넘어온 xhr은 상품들에 관한 정보만 있으므로 링크들은 모두 상품들의 상세페이지 링크)
        total_link = []
        start_idx = self.idx  # 밑에서 enumerate 돌 때, key로 사용할 시작점으로 사용하기 위함.

        while True:
            # url = scraping.__secret['django']['scraping'].format(self.idx)
            url = self.__secret['django']['scraping'].format(self.idx)
            main_html = urllib.request.urlopen(url).read().decode('utf-8')
            link_list = self.get_links(main_html)

            # 가져올 링크가 하나도 없으면 while문 break
            if link_list == []:
                break
            total_link.extend(link_list)

            self.idx += 60

        # 링크 뽑아내는 과정에서 같은 상세페이지가 두번씩 추가되므로, 중복 없애기 위해 set 사용
        for j, i in enumerate(set(total_link), start=start_idx):
            print(f'{j}번 째 상품 진행 중...')

            # 예외처리
            try:
                res = self.detailed_page(i)
            except Exception as e:  # 예외 발생할 정경우, 에러 이름 출력하고 다음 for문 부터 출력
                print(j, '번에서', e, '발생')
                continue
            else:
                # redis 서버에 html을 문자열로 바꾼 후 캐싱하기.
                # html 파일 객체로 담을 수는 없는지 찾아볼 것.
                self.redis3.set(str(j), str(res.html.html))  # 전체 html 캐싱

    def preprocessing(self):
        bulk_data = []
        for i in range(self.redis3.dbsize()):  # dbsize = redis의 해당 데이터베이스에 담긴 데이터 개수
            b = self.redis3.get(str(i))
            # 데이터가 담기지 않은 부분을 제외하기 위함
            # 예외가 발생하거나, 아예 html이 없는 경우 캐싱된 파일이 없을 수 있으므로 이 경우는 그냥 continue로 넘어간다.
            if not b: continue

            # 캐시에 저장될 때, 바이트 타입으로 저장되므로 가져와서 다시 str로 인코딩
            b = b.decode()
            c = self.get_ingredient(b)
            bb = bs(b, 'html.parser')

            # 전성분이 없을 경우 continue
            if c == []: continue

            # 성분 : c[0].replace('<dd data-v-2902b98c="">', '').strip(" ")
            # 가격 : bb.find_all('span', class_='won')[0].text.strip()
            # 이름 : bb.find('div', class_='productName').text.strip()
            # 브랜드 : bb.find('strong').text.strip()
            cos_dict = {
                'name': bb.find('div', class_='productName').text.strip(),
                'price': bb.find_all('span', class_='won')[0].text.strip(),
                'ingredient': c[0].replace('<dd data-v-2902b98c="">', '').strip(" "),
                'brand': bb.find('strong').text.strip(),
                'image': bb.find_all('img', alt=bb.find('div', class_='productName').text.strip())[0]['src'],
            }

            # 같은 이름의 화장품이 데이터베이스 내에 있는지 확인
            # 없을 경우 bulk_data 리스트에 Cos모델 객체 추가
            if {'prdname': cos_dict['name']} not in scraping.cosmetic:
                bulk_data.append(Cos(prdname=cos_dict['name'],
                                     price=cos_dict['price'],
                                     ingredient=cos_dict['ingredient'],
                                     brand=cos_dict['brand'],
                                     image=cos_dict['image']
                                     ))
        Cos.objects.bulk_create(bulk_data)

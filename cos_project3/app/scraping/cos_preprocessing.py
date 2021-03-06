import redis
from bs4 import BeautifulSoup as bs
from app.models import Cos
import re
from django.core.cache import cache
import multiprocessing as mp

redis3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 상세 페이지 html 가져오기 위함
redis4 = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)  # 각 상품 딕셔너리 저장하기 위함
cosmetic = cache.get_or_set('cosmetic', Cos.objects.values('prdname'))
bulk_data = []

def get_ingredient(html):
    webpage_regex = re.findall('전성분</dt>(.*?)</dd>{1}', html)  # </dd>가 한번 나올 때까지만 찾기
    return webpage_regex

def preprocessing(i):
    try:
        each_html = redis3.get(str(i))
        # 예외가 발생하거나, 아예 html이 없는 경우 캐싱된 파일이 없을 수 있으므로 이 경우는 그냥 continue로 넘어간다.
        if not each_html: return

        # 캐시에 저장될 때, 바이트 타입으로 저장되므로 가져와서 다시 str로 인코딩
        each_html = each_html.decode()
        c = get_ingredient(each_html)
        each_html_bs = bs(each_html, 'html.parser')

        # 전성분이 없을 경우 continue
        if c == []: return

        cos_dict = {
            'name': each_html_bs.find('div', class_='productName').text.strip(),
            'price': each_html_bs.find_all('span', class_='won')[0].text.strip(),
            'ingredient': c[0].replace('<dd data-v-2902b98c="">', '').strip(" "),
            'brand': each_html_bs.find('strong').text.strip(),
            'image': each_html_bs.find_all('img', alt=each_html_bs.find('div', class_='productName').text.strip())[0]['src'],
        }

        # 같은 이름의 화장품이 데이터베이스 내에 있는지 확인
        # 없을 경우 bulk_data 리스트에 Cos모델 객체 추가
        if {'prdname': cos_dict['name']} not in cosmetic:
            bulk_data.append(Cos(prdname=cos_dict['name'],
                                 price=cos_dict['price'],
                                 ingredient=cos_dict['ingredient'],
                                 brand=cos_dict['brand'],
                                 image=cos_dict['image']
                                 ))
    except Exception as e:
        print(i, e)

pool = mp.pool.ThreadPool(2)
for i in range(1, redis3.dbsize()):
    p = mp.Process(target=preprocessing, args=(i,))
    p.start()
    p.join()

Cos.objects.bulk_create(bulk_data)
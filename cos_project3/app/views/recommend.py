# Cos 모델 설치
from app.models import Cos
# cache server
from django.core.cache import cache
# 성분추출함수에 쓰일 패키지 설치
from PIL import Image, ImageFont, ImageDraw
from pytesseract import *
import pandas as pd
# 코사인 유사도에 쓰일 패키지
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class recommend:

    def __init__(self, link):
        # 업로드 된 화장품 성분 이미지 주소
        self.link = link
        self.fflist = self.text()

    def jaccard_similarity(self, doc1, doc2):
        doc1 = set(doc1)
        doc2 = set(doc2)
        return len(doc1 & doc2) / len(doc1 | doc2)


    # 이미지에서 글자 추출 후 가공
    def text(self):
        arg = self.link
        os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'
        image = Image.open('./.' + arg)
        x = int(1920 / image.size[0])
        y = int(1080 / image.size[1])
        if x != 0:
            if y != 0:
                if x > y:
                    image = image.resize((image.size[0] * y, image.size[1] * y))
                else:
                    image = image.resize((image.size[0] * x, image.size[1] * x))

        text = image_to_string(image, lang="kor")
        fflist = text.replace('\n', '')
        fflist = list(map(lambda x: x.strip(), fflist.split(',')))
        return fflist

    # 코사인 유사도를 통한 추천
    def cosine(self):
        fflist = self.fflist
        data = pd.read_csv("././static/cos5.txt", header=None)
        listtt = fflist
        listtt = [v for v in listtt if v]
        lst2 = []
        for i in range(len(listtt)):
            lst = []
            for j in range(len(data[0])):
                test = self.jaccard_similarity(data[0][j], listtt[i])
                # 기존에 있던 화장품 성분과 이미지에서 추출한 성분의 자카드 유사도를 분석
                # 이미지에서 추출한 성분은 잘못읽혔을 가능성이 있으므로 논리비교 보다는 자카도 유사도의 유사도를 통해서 단어의 유사성을 판단
                if test > 0.5:
                    lst.append((test, data[0][j]))
            lst.sort(reverse=True)
            if len(lst) != 0:
                lst2.append(lst[0][1])
        lst2 = ', '.join(lst2)
        data2 = cache.get_or_set('cosin_cos', Cos.objects.all())
        ffflist = []
        # ffflist에는 각각의 코사인유사도와 상품의 인덱스 번호가 들어간다
        # ffflist = [(0.1231545, 0), (0.321516, 1) ...]와 같은 형식으로 데이터가 담긴다.
        for i in range(len(data2)):
            sent = (data2[i].ingredient, ''.join(lst2))
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(sent)  # 문장 벡터화 진행
            idf = tfidf_vectorizer.idf_

            cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            ffflist.append((float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])))

        for j, k in enumerate(ffflist):
            ffflist[j] = (k, j)
        ffflist = sorted(ffflist, reverse=True)
        result = []
        for i in range(10):
            idx = ffflist[i][1]
            result.append({'prdname': data2[idx].prdname,
                           'ingredient': data2[i].ingredient,
                           'image': data2[i].image,
                           'brand': data2[i].brand,
                           'price': data2[i].price,
                           'cosine': str(ffflist[i][0])})
        return result





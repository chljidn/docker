from app.models import Cos
from django.core.cache import cache
from PIL import Image
from pytesseract import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings
from common.models import User
from app.models import recommend_excel

class recommend:

    def __init__(self, link, user, title):
        # 업로드 된 화장품 성분 이미지 주소
        self.link = link
        self.fflist = self.text()
        self.user = user
        self.user_object = User.objects.get(username=self.user)
        self.title = title

    def jaccard_similarity(self, doc1, doc2):
        doc1 = set(doc1)
        doc2 = set(doc2)
        return len(doc1 & doc2) / len(doc1 | doc2)

    # 이미지에서 글자 추출 후 가공
    def text(self):
        arg = self.link
        os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'
        image = Image.open(f'././media/{str(arg)}')
        x = int(1920 / image.size[0])
        y = int(1080 / image.size[1])
        if x != 0 and y != 0:
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
        data2 = cache.get_or_set('cosine_cos', Cos.objects.all().distinct())
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
        for i in ffflist[:10]:
            result.append({'prdname': data2[i[1]].prdname,
                           'ingredient': data2[i[1]].ingredient,
                           'image': data2[i[1]].image,
                           'brand': data2[i[1]].brand,
                           'price': data2[i[1]].price,
                           'cosine': i[0]})
        return result

class excel_recommend(recommend):

    def cosine(self):
        data = super().cosine()
        excel_data = pd.DataFrame()
        for i in data:
            each_data = pd.DataFrame()
            each_data = each_data.append({"상품이름":i["prdname"], "성분":i["ingredient"], "브랜드" : i["brand"],
                                          "가격":i["price"], "유사도":i["cosine"]}, ignore_index=True)
            excel_data = excel_data.append(each_data, ignore_index=True)
        file_name = f"{self.user_object.username}_{self.title}"
        excel_data.to_excel(f"././media/recommend_excel/{file_name}.xlsx", index=False)

        recommend_excel.objects.create(
            user=self.user_object,
            file_title=self.title,
            recommend_file_dir=f"recommend_excel/{file_name}.xlsx"
        )




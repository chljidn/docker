from rest_framework.test import APITestCase, APIClient
from app.models import Cos
from common.models import User
from django.urls import reverse

# 화장품 데이터는 기존 db의 데이터를 사용해야 하므로
# settings_test.py와 test_runner.py 파일을 통해서 셋팅을 조정해주었다.
# 이 셋팅을 통해서 테스트 db를 생성하지 않고, 기존의 db에서 테스트를 진행한다.
# 실행은 python manage.py test app.tests.test_app_requests.cos_request_tests --settings='app.tests.settings_test 를 통해서 app의 테스트는 따로 진행하도록 했다.
class cos_request_tests(APITestCase):
    url = reverse('app:cos_list-list')
    # 전체 화장품 데이터 가져오기
    def test_cos_list_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # 하나의 화장품 데이터 가져오기(상세 페이지)
    def test_cos_list_detail_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class cos_like_request_tests(APITestCase):
    auth_url = reverse('common:auth')
    like_url = reverse('app:coslike')

    def setUp(self):
        user = User.objects.create_user(username='review_test', password='reviewtestpasswd', email='test@test.com',
                                             birth='2021-09-09', sex='M')
        response = self.client.post(self.auth_url, {'username': 'review_test', 'password': 'reviewtestpasswd'}, format='json')
        self.apiclient = APIClient()
        token = response.data['access']
        self.apiclient.credentials(HTTP_AUTHORIZATION='Bearer '+ token)
        cos = Cos.objects.get(id=2)
        cos.like.add(user)

    # post로 화장품의 기본키를 담아 보낸다.
    def test_cos_like_create(self):
        response = self.apiclient.post(self.like_url, {"pk": 1})
        self.assertEqual(response.status_code, 201)

    def test_cos_like_delete(self):
        response = self.apiclient.post(self.like_url, {"pk": 2})
        self.assertEqual(response.status_code, 200)

# class cos_review_requests(APITestCase):
#     pass
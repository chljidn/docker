from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

# 유저 인증(회원가입, 로그인) 및 유저 정보(읽기, 수정, 삭제) 테스트
class auth_user_request_tests(APITestCase):
    auth_url = reverse('common:auth')
    useredit_url = reverse('common:useredit')

    # 유저 생성하여 setUp
    def setUp(self):
        response = self.client.post(self.auth_url,
                                    {
                                        'username': 'test',
                                        'password': 'testpasswd123',
                                        'sex': 'M',
                                        'birth': '1995-05-05',
                                        'email': 'test@test.com'
                                    }, format='json')
        self.assertEqual(response.status_code, 201)

    # 유저 로그인
    def test_user_login(self):
        response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
        token = response.data['access']
        self.assertEqual(response.status_code, 200)

    # 유저 정보 읽기(마이 페이지)
    def test_user_get(self):
        # HTTP_AUTHORIZATION 을 사용하기 위함
        client = APIClient()
        response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(self.useredit_url)
        self.assertEqual(response.status_code, 200)

    # 유저 정보 수정
    def test_user_update(self):
        client = APIClient()
        response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.put(self.useredit_url,
                              {
                                  'username' : 'test',
                                  'sex' : 'F',
                                  'birth' : '1996-05-05',
                                  'email': 'testupdate@test.com'
                              }, format='json')
        self.assertEqual(response.status_code, 200)

    # 유저 삭제(회원탈퇴)
    def test_user_delete(self):
        client = APIClient()
        response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response.client.delete(self.useredit_url)
        self.assertEqual(response.status_code, 200)

# class qa_request_tests(APITestCase):
#
#     def setUp(self):
#         pass
#
#     def test_qa_create(self):
#         pass
#
#     def test_qa_list_get(self):
#         pass
#
#     def test_qa_detail_get(self):
#         pass
#
#     def test_qa_detail_update(self):
#         pass
#
#     def test_qa_detail_delete(self):
#         pass
#
#     def test_not_auth_create(self):
#         pass

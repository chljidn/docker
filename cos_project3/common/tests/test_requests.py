from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from common.models import Qa, User

# 회원가입 테스트
class auth_user_request_tests(APITestCase):
    signup_url = reverse('common:signup')

    # 유저 생성 setup
    def setUp(self):
        setup_data = {'username': 'test1', 'password': 'testpasswd', 'sex': 'M', 'birth': '1995-05-05', 'email': 'test1@test.com'}
        User.objects.create_user(**setup_data)

    def test_user_signup(self):
        response = self.client.post(self.signup_url, {'username': 'test2',
                                                      'password': 'testpasswd',
                                                      'sex': 'M',
                                                      'birth': '1995-05-05',
                                                      'email': 'test2@test.com'}, format='json')
        self.assertEqual(response.status_code, 201)

    # 중복되는 회원이 있어 예외 발생(아이디 중복 or 이메일 중복)
    def test_user_signup_duplicate_error(self):
        user_data = {'username': 'test1', 'password': 'testpasswd', 'sex': 'M', 'birth': '1995-05-05',
                      'email': 'test1@test.com'}
        response = self.client.post(self.signup_url, user_data)
        self.assertEqual(response.status_code, 409)

    # 모든 데이터가 충족되지 않을 경우 예외 발생(아이디 공백 or 패스워드 공백 등)
    # api에서 status_code = 400 할 수 있도록 수정 요망.
    def test_user_signup_not_enough_error(self):
        user_data = {'username': 'test2','password': 'testpasswd', 'sex': 'M', 'birth': '1995-05-05'}
        response = self.client.post(self.signup_url, user_data)
        self.assertEqual(response.status_code, 409)


# 로그인 테스트
class login_request_tests(APITestCase):
    login_url = reverse('common:login')

    # 유저 생성 setup
    def setUp(self):
        setup_data = {'username': 'test1', 'password': 'testpasswd', 'sex': 'M', 'birth': '1995-05-05', 'email': 'test1@test.com'}
        User.objects.create_user(**setup_data)

    # 유저 로그인
    def test_user_login(self):
        response = self.client.post(self.login_url, {'username': 'test1', 'password': 'testpasswd'}, format='json')
        self.assertEqual(response.status_code, 200)

    # 존재하지 않는 회원이 로그인 요청할 경우 예외 발생
    def test_user_login_error(self):
        response = self.client.post(self.login_url, {'username': 'test', 'password': 'testpasswd'}, format='json')
        self.assertEqual(response.status_code, 400)

    # 패스워드나 아이디가 틀린 상태로 로그인을 요청할 경우 예외 발생
    def test_user_login_wrong_data_error(self):
        response = self.client.post(self.login_url, {'username': 'test1', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, 400)


class myinfo_request_tests(APITestCase):

    def setUp(self):
        pass

#
#     # 유저 정보 읽기(마이 페이지)
#     def test_user_get(self):
#         # HTTP_AUTHORIZATION 을 사용하기 위함
#         client = APIClient()
#         response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
#         token = response.data['access']
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
#         response = client.get(self.useredit_url)
#         self.assertEqual(response.status_code, 200)
#
#     # 유저 정보 수정
#     def test_user_update(self):
#         client = APIClient()
#         response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
#         token = response.data['access']
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
#         response = client.patch(self.useredit_url,
#                               {
#                                   'sex' : 'F',
#                                   'birth' : '1996-05-05',
#                                   'email': 'testupdate@test.com'
#                               }, format='json')
#         self.assertEqual(response.status_code, 200)
#
#     # 유저 삭제(회원탈퇴)
#     def test_user_delete(self):
#         client = APIClient()
#         response = self.client.post(self.auth_url, {'username': 'test', 'password': 'testpasswd123'}, format='json')
#         token = response.data['access']
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
#         response.client.delete(self.useredit_url)
#         self.assertEqual(response.status_code, 200)
#
# class qa_request_tests(APITestCase):
#     auth_url = reverse('common:auth')
#     qa_url = reverse('common:qa-list')
#     url1 = None # qna 상세페이지에 사용할 url(패스워드가 없는 qna url) 초기화
#     url2 = None # qna 상세페이지에 사용할 url(패스워드가 있는 qna url) 초기
#
#     def setUp(self):
#         self.user = User.objects.create_user(username='qa_test', password='qatestpasswd', email='test@test.com', birth='2021-09-09', sex='M')
#         # 패스워드 없는 글 셋업
#         self.qa1 = Qa.objects.create(id=1, postname='setup1', content='setup1', qa_user=self.user)
#         self.url1 = reverse('common:qa-detail', kwargs={'pk': self.qa1.id})
#         # 패스워드 있는 글 셋업
#         self.qa2 = Qa.objects.create(id=2, postname='setup2', content='setup2', password='setup2', qa_user=self.user)
#         self.url2 = reverse('common:qa-detail', kwargs={'pk': self.qa2.id})
#
#         # qna 생성 요청에 사용할 APIClient 유저 객체에 토큰 담기
#         response = self.client.post(self.auth_url, {'username': 'qa_test', 'password': 'qatestpasswd'}, format='json')
#         self.apiclient = APIClient()
#         token = response.data['access']
#         self.apiclient.credentials(HTTP_AUTHORIZATION='Bearer '+ token)
#
#     # 패스워드가 있는 게시글과 패스워드가 없는 게시글 http request로 생성
#     def test_qa_create(self):
#         # 패스워드 없는 게시글 생성
#         response = self.apiclient.post(self.qa_url, {'postname' : 'request1', 'content' : 'request1'})
#         self.assertEqual(response.status_code, 201)
#         # 패스워드 있는 게시글 생성
#         response = self.apiclient.post(self.qa_url, {'postname' : 'request2', 'content' : 'request2', 'password':'request2'})
#         self.assertEqual(response.status_code, 201)
#
#     # 게시글 생성 에러 테스트
#     def test_qa_create_error(self):
#         # 로그인되어 있지 않은 경우
#         pass
#
#     # 전체 qna 데이터 읽기
#     def test_qa_list_get(self):
#         response = self.client.get(self.qa_url)
#         self.assertEqual(response.status_code, 200)
#
#     # qna 상세 페이지 읽기(패스워드가 있는 경우와 없는 경우)
#     def test_qa_detail_get(self):
#         # 패스워드가 없는 글은 get으로 가져오기
#         response = self.client.get(self.url1)
#         self.assertEqual(response.status_code, 200)
#
#         response = self.client.get(self.url2, {'password':'setup2'}, format='json')
#         print(response)
#         self.assertEqual(response.status_code, 200)
#
#     # qna 상세 페이지 읽기 에러(패스워드가 있는 게시물에 get 요청으로 패스워드를 보내지 않은 경우, 패스워드가 있는 게시물에 post 요청으로 보낸 패스워드가 틀린 경우)
#     def test_qa_detail_get_error(self):
#         # 패스워드가 있는 경우, get으로 요청했을 때 401 에러 발생
#         response = self.client.get(self.url2)
#         self.assertEqual(response.status_code, 401)
#         # 패스워드가 있는 게시글의 경우, 패스워드가 틀렸을 경우 에러 발생
#         response = self.client.get(self.url2, {'password':'setup1'}, format='json')
#         self.assertEqual(response.status_code, 401)
#
#     # qna 상세 페이지 수정.
#     def test_qa_detail_update(self):
#         # 현재까지는 qna 수정의 경우, 기존 ModelViewSet의 partial_update를 수정하지 않고 그대로 사용하므로 url은 기존 url에 pk가 붙은 common/qa/{pk}/가 왼다.
#         # 패스워드가 있는 경우
#         response = self.apiclient.patch(f'{self.qa_url}{self.qa1.id}/', {'content' : 'setup1 수정'}, format='json')
#         self.assertEqual(response.status_code, 200)
#         # 패스워드가 없는 경
#         response = self.apiclient.patch(f'{self.qa_url}{self.qa2.id}/', {'content' : 'setup2 수정', 'password': 'setup2'}, format='json')
#         self.assertEqual(response.status_code, 200)
#
#     def test_qa_detail_update_error(self):
#         # 패스워드가 틀렸을 경우
#         response = self.apiclient.patch(f'{self.qa_url}{self.qa2.id}/', {'content' : 'setup2 수정', 'password': 'setup1'}, format='json')
#         self.assertEqual(response.status_code, 401)
#
#         # 유저가 일치하지 않을 경우
#
#     def test_qa_detail_delete(self):
#         # 패스워드 없는 질문글을 지울 경우
#         response = self.apiclient.delete(f'{self.qa_url}{self.qa1.id}/')
#         self.assertEqual(response.status_code, 204)
#         # 패스워드가 있는 질문글을 지울 경우
#         response = self.apiclient.delete(f'{self.qa_url}{self.qa2.id}/', {'password': 'setup2'}, format='json')
#         self.assertEqual(response.status_code, 204)
#
#     def test_qa_detail_delete_error(self):
#         # 유저가 일치하지 않는데 삭제하려는 경우
#         pass
#
# class qa_reple_requests_tests(APITestCase):
#     def setUp(self):
#         pass

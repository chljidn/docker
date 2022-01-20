from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import QueryDict
from django.contrib.auth.hashers import check_password

from common.serializers import MyTokenObtainPairSerializer, UserSerializers
from common.models import User

# 회원가입 완료 이메일 보내기
# 추후 회원가입 이메일 인증으로 변환 예정
from django.core.mail import send_mail
from django.conf import settings # settigns에 정의한 이메일 변수를 사용하기 위해 setting 설치

# simplejwt을 이용한 Token 발급
# 회원가입 및 로그인
# set_cookie를 통해서 토큰을 response set-cookie header에 담아보낸다
# 참고 : https://stackoverflow.com/questions/66197928/django-rest-how-do-i-return-simplejwt-access-and-refresh-tokens-as-httponly-coo
class auth(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        if request.data.get('email', False):
            user = User.objects.create_user(username=request.data['username'],
                                            email=request.data['email'],
                                            birth=request.data['birth'],
                                            sex=request.data['sex'],
                                            password=request.data['password'],
                                       )
            user_data = QueryDict(f'''username={request.data['username']}&password={request.data['password']}''')
            auth_status = status.HTTP_201_CREATED

            # 가입 인증 메일 보내기(테스트 떄 계속 이메일 보내서 일단 기능 닫아놓)
            # send_mail(
            #     '회원가입이 완료되었습니다',
            #     'RECOS에 회원가입이 완료되었습니다. \n 회원이 되어주신 것에 감사드립니다. 성원에 보답하겠습니다.',
            #     settings.EMAIL_HOST_USER,
            #     [request.data['email']],
            #     # fail_silently = False일 경우, 에러가 발생하면 smtplib.STMPException이 발생한다.
            #     fail_silently=Falsㄸ음e,
            # )
        else:
            user_data = request.data
            auth_status = status.HTTP_200_OK

        serializer = MyTokenObtainPairSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data.get("access", None)
        refresh = serializer.validated_data.get("refresh", None)
        username = serializer.validated_data.get("username", None)
        return Response(serializer.validated_data, status=auth_status)
        # set_cookie에 담아보내기. 현재에는 vue를 시험하기 위해 사용하지 않는다.
        # if access is not None:
        #     response = Response({}, status=200)
        #     response.set_cookie('token', access, httponly=True)
        #     response.set_cookie('refresh', refresh, httponly=True)
        #     response.set_cookie('email', username, httponly=True)
        #     return response

# 유저 정보 읽기, 생성, 삭제(탈퇴)
class userEdit(APIView):
    #def get_queryset(self):
    #    pass

    # 유저가 인증되어 있으면 request.user에 유저 객체가 이미 들어있으므로 직렬화만 해서 리턴한다.
    def get(self, request):
        if request.user.is_authenticated:
            user_serializer = UserSerializers([request.user], many=True)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message' : '로그인이 필요한 기능입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.filter(id=request.user.id)
            if not request.data.get('password', False):
                password = user[0].password
            else:
                if request.data['password'] == '':
                    password = user[0].password
                else:
                    password = make_password(request.data['password'])

            user.update(
                username=request.user.username,
                password=password,
                sex=request.data['sex'],
                birth=request.data['birth'],
                email=request.data['email']
            )
            # 업데이트 된 경우 마이 페이지의 정보를 업로드하기 위해서 업데이트 된 정보를 다시 전송.
            user_serializer = UserSerializers(user, many=True)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message' : '로그인이 필요한 기능입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        if request.user.is_authenticated:
            # 회원탈퇴 하기 전에 프론트에서 패스워드를 한 번 더 입력받아 요청하고, 기존 유저의 패스워드와 입력받은 패스워드를 비교한다.
            if check_password(request.data['password'], request.user.password):
                User.delete(request.user)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'message' : '패스워드가 일치하지 않습니다. 다시 입력해 주세요'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': '로그인이 필요한 기능입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

# 패스워드가 탈취된 경우 refresh 토큰을 블랙리스트에 추가시켜 사용하지 못하도록 한다.
# 형식은 refresh token을 받아서 blacklist에 추가시키는 것. refresh token은 content 부분에 담겨 보내진다.
# 코드 출처 : https://medium.com/django-rest/logout-django-rest-framework-eb1b53ac6d35
class blacklist(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, reuqest):
        try:
            refresh_token = reuqest.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)



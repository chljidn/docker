from rest_framework import status, generics, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from common.serializers import MyTokenObtainPairSerializer, UserSerializers
from common.models import User
from django.utils.datastructures import MultiValueDictKeyError
from common.functions import jwt_set_cookie
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# 회원가입
class SignupView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.create_user(username=request.data['username'],
                                            email=request.data['email'],
                                            birth=request.data['birth'],
                                            sex=request.data['sex'],
                                            password=request.data['password'],
                                            )
            message = {"message" : "회원가입이 완료되었습니다."}
            signup_status = status.HTTP_201_CREATED
        except MultiValueDictKeyError:
            message = {"message": "회원가입에 실패했습니다. 회원정보를 정확히 입력하세요."}
            signup_status = status.HTTP_400_BAD_REQUEST
        finally:
            return Response(message, status=signup_status)


# 로그인
class LoginView(TokenObtainPairView):
    def post(self, request):
        try:
            user_data = request.data
            serializer = MyTokenObtainPairSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            response = jwt_set_cookie(serializer)
            response.status = status.HTTP_200_OK
            return response

        # 아이디나 비밀번호가 잘못될 경우 is_valid 부분에서 에러 발생 가능.
        # non_field_errors 에러 발생
        except serializers.ValidationError:
            return Response({"message" : "인증정보가 정확하지 않습니다. 아이디와 비밀번호를 다시 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST)


# Refresh view
# 기존에 data에 refres token을 담아서 보내던 것을 headers에 담아서 보내도록 수정.
class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.headers)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# 마이 페이지(유저 정보 조회/수정, 회원 탈퇴)
from common.decorators import login_decorator
class userEdit(APIView):
    # 유저가 인증되어 있으면 request.user에 유저 객체가 이미 들어있으므로 직렬화만 해서 리턴한다.
    @login_decorator
    def get(self, request):
        user_serializer = UserSerializers([request.user], many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @login_decorator
    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id)
        if not request.data.get('password', False):
            password = user[0].password
        else:
            if request.data['password'] == '':
                password = user[0].password
            else:
                password = make_password(request.data['password'])

        user.update(
            password=password,
            sex=request.data['sex'],
            birth=request.data['birth'],
            email=request.data['email']
        )
        # 업데이트 된 경우 마이 페이지의 정보를 업로드하기 위해서 업데이트 된 정보를 다시 전송.
        user_serializer = UserSerializers(user, many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @login_decorator
    def delete(self, request):
        # 회원탈퇴 하기 전에 프론트에서 패스워드를 한 번 더 입력받아 요청하고, 기존 유저의 패스워드와 입력받은 패스워드를 비교한다.
        if check_password(request.data['password'], request.user.password):
            User.delete(request.user)
            return Response(status=status.HTTP_200_OK)
        return Response({'message' : '패스워드가 일치하지 않습니다. 다시 입력해 주세요'}, status=status.HTTP_401_UNAUTHORIZED)


# 패스워드가 탈취된 경우 refresh 토큰을 블랙리스트에 추가시켜 사용하지 못하도록 한다.
# 형식은 refresh token을 받아서 blacklist에 추가시키는 것. refresh token은 content 부분에 담겨 보내진다.
# class blacklist(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, reuqest):
#         try:
#             refresh_token = reuqest.data['refresh']
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response(status=status.HTTP_205_RESET_CONTENT)
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)



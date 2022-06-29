from rest_framework import status, generics, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.hashers import check_password, make_password
from common.serializers import MyTokenObtainPairSerializer, UserSerializers
from common.models import User
from django.utils.datastructures import MultiValueDictKeyError
from common.functions import jwt_set_cookie
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from common.decorators import login_decorator

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
            return response

        # 아이디나 비밀번호가 잘못될 경우 is_valid 부분에서 에러 발생 가능.
        # non_field_errors 에러 발생
        except serializers.ValidationError:
            return Response({"message" : "인증정보가 정확하지 않습니다. 아이디와 비밀번호를 다시 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST)

# Refresh view
# 재발급 받은 access token을 set-cookie 헤더에 담아 보내기.
class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.headers)
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            response = jwt_set_cookie(serializer)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return response

class MyInfoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    @login_decorator
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return response

    # 패스워드가 ''로 들어오는 경우는 따로 고려하지 않는다.
    # 이 부분은 프론트 쪽에서 처리하도록 한다.
    @login_decorator
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return response

    @login_decorator
    def destroy(self, request, *args, **kwargs):
        try:
            if check_password(request.data['password'], request.user.password):
                User.delete(request.user)
                return Response(status=status.HTTP_200_OK)
            return Response({'message': '패스워드가 일치하지 않습니다. 회원 탈퇴를 위해서는 정확한 패스워드가 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        except KeyError:
            return Response({"message" : "패스워드를 입력하여 주세요."}, status=status.HTTP_400_BAD_REQUEST)

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



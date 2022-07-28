import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from common.models import User
from rest_framework import exceptions as rest_exceptions

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization", None)
            if token:
                token = token.replace("Bearer ", "")
            else:
                raise rest_exceptions.NotAuthenticated
            info = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            request.user = User.objects.get(id=info['user_id'])
        except rest_exceptions.NotAuthenticated:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.DecodeError:
            return Response({"message": "토큰이 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.ExpiredSignatureError:
            return Response({"message": "토큰의 유효기간이 만료되었습니다. 재인증 해주세요"}, status=status.HTTP_401_UNAUTHORIZED)
        except request.user.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return func(self, request, *args, **kwargs)
    return wrapper

def update_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        if not kwargs.get("partial", None):
            return Response({"message": "사용할 수 없는 기능입니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return func(self, request, *args, **kwargs)
    return wrapper

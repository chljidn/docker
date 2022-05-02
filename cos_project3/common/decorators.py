import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from common.models import User

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization", None).replace("Bearer ", "")
            info = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')

            # expire = datetime.utcfromtimestamp(info['exp'])
            # if settings.USE_TZ and expire <= datetime.utcnow():
            #     return Response({"토큰의 유효기간이 만료되었습니다. 다시 인증해주세요."}, status=status.HTTP_401_UNAUTHORIZED)

            # request.user = settings.AUTH_USER_MODEL.objects.get(id=info['user_id'])

            request.user = User.objects.get(id=info['user_id'])
        except jwt.exceptions.DecodeError:
            return Response({"message": "토큰이 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.ExpiredSignatureError:
            return Response({"message": "토큰의 유효기간이 만료되었습니다. 재인증 해주세요"}, status=status.HTTP_401_UNAUTHORIZED)
        except request.user.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return func(self, request, *args, **kwargs)
    return wrapper
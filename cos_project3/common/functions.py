from rest_framework.response import Response
from rest_framework import status

# 토큰을 헤더에 담기 위한 method
def jwt_set_cookie(serializer):
    headers_variable = ["access", "refresh", "id"]
    for i in headers_variable:
        globals()[f'i'] = serializer.validated_data.get(i, None)
    access = serializer.validated_data.get("access", None)
    refresh = serializer.validated_data.get("refresh", None)
    userid = serializer.validated_data.get("id", None)

    if access is not None:
        response = Response({}, status=status.HTTP_200_OK)
        response.set_cookie('access', access, httponly=True)
        response.set_cookie('id', userid, httponly=True)
        if refresh is not None:
            response.set_cookie('refresh', refresh, httponly=True)

    return response
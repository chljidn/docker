from rest_framework.response import Response

# 토큰을 헤더에 담기 위한 method
def jwt_set_cookie(serializer):
    headers_variable = ["access", "refresh"]
    for i in headers_variable:
        globals()[f'i'] = serializer.validated_data.get(i, None)
    access = serializer.validated_data.get("access", None)
    refresh = serializer.validated_data.get("refresh", None)

    if access is not None:
        response = Response({}, status=200)
        response.set_cookie('access', access, httponly=True)
        response.set_cookie('refresh', refresh, httponly=True)
    return response
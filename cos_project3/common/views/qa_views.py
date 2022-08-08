from rest_framework import viewsets, generics, mixins, status, decorators, exceptions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.paginations import QaPagination
from common import serializers
from common.models import Qa, QaReple
from common.filters import QaFilter
from common.decorators import login_decorator, update_decorator
from django.contrib.auth.hashers import check_password, make_password
from django_filters.rest_framework import DjangoFilterBackend
from django.http.response import Http404
from django.utils.datastructures import MultiValueDictKeyError

# QNA
class qa(viewsets.ModelViewSet):
    serializer_class = serializers.QaSerializers
    queryset = Qa.objects.all().order_by('-qaDate')
    filter_backends = [DjangoFilterBackend]
    filterset_class = QaFilter
    pagination_class = QaPagination

    def retrieve(self, request, *args, **kwargs):
        print(self.get_object().id)
        print(self.get_object().postname)
        print(self.get_object().password)
        if self.get_object().password is not None:
            return self.password_retrieve(request, *args, **kwargs)
        return super().retrieve(request, *args, **kwargs)

    @decorators.action(detail=True, methods=['post'])
    def password_retrieve(self, request, *args, **kwargs):
        try:
            qa_detail = self.get_object()
            password = request.data.get("password", None)
            # 패스워드 파라미터가 없을 경우, null로 설정.
            if not qa_detail.password or check_password(password, qa_detail.password):
                response = super().retrieve(request, *args, **kwargs)
                return response
            return Response({"message": "패스워드가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except Http404:
            return Response({"message": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

    @login_decorator
    def create(self, request, *args, **kwargs):
        try:
            password = request.data.get('password', None)
            if password: password = make_password(password)
            qa = Qa.objects.create(
                postname=request.data['postname'],
                content=request.data['content'],
                password=password,
                qa_user=request.user
            )
            return Response({'message':'질문이 저장되었습니다.'}, status=status.HTTP_201_CREATED)
        except exceptions.ValidationError as e:
            return Response({"message" : e.detail}, status=status.HTTP_400_BAD_REQUEST)

    @update_decorator
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return response
        except exceptions.ValidationError:
            return Response({"message": "요청 항목의 값이 올바르지 않습니다. 요청 항목의 값을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    @login_decorator
    def partial_update(self, request, *args, **kwargs):
        print(request.data)
        try:
            instance = self.get_object()
            if request.user != instance.qa_user:
                return Response({'message': '질문을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            response = super().partial_update(request, *args, **kwargs)
            return response
        except Http404:
            return Response({"message": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

    @login_decorator
    def destroy(self, request, *args, **kwargs):
        if request.user != self.get_object().qa_user:
            return Response({'message' : '질문을 삭제할 수 있는 권한이 없습니다. 작성자만이 질문을 삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(self.get_object())
        return Response({"message":"질문이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class qa_reple_list(generics.ListCreateAPIView):
    queryset = QaReple.objects.all()
    serializer_class = serializers.QaRepleSerializer

    def get_queryset(self):
        return self.queryset.filter(repleUser=self.request.user).order_by("-repleDate")

    @login_decorator
    def create(self, request, *args, **kwargs):
        reple = QaReple.objects.create(
            content=request.data['content'],
            qa=Qa.objects.get(id=request.data['pk']),
            repleUser=request.user
        )
        return Response({"message": "답글 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED)

class qa_reple_detail(mixins.DestroyModelMixin, generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        reple = QaReple.objects.get(id=kwargs['pk'])
        if request.user == reple.repleUser:
            reple.delete()
        return Response(status=status.HTTP_200_OK)
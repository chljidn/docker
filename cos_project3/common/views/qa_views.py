from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from common.paginations import QaPagination
from common import serializers
from common.models import Qa, QaReple
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from common.filters import QaFilter
from django.utils import timezone
from django.core import exceptions
from common.serializers import QaRepleSerializer

class qa(viewsets.ModelViewSet):
    serializer_class = serializers.QaSerializers
    queryset = Qa.objects.all().order_by('-qaDate')
    filter_backends = [DjangoFilterBackend]
    filterset_class = QaFilter
    pagination_class = QaPagination

    def retrieve(self, request, *args, **kwargs):
        try:
            qaDetail = Qa.objects.get(id=kwargs['pk'])
        except exceptions.ObjectDoesNotExist:
            return Response({"message": "Q&A가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            if getattr(qaDetail, "password"):
                if request.data.get("password", None) and request.data["password"] == qaDetail.password:
                    serialize = self.serializer_class(qaDetail)
                    return Response(serialize.data, status=status.HTTP_200_OK)
                return Response({"message":"패스워드가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                serialize = self.serializer_class(qaDetail)
                return Response(serialize.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        password = request.data.get('password', None)
        if password == '': password = None
        if request.user.is_authenticated:
            qa = Qa.objects.create(
                postname=request.data['postname'],
                content=request.data['content'],
                password=password,
                qa_user=request.user,
            )
            return Response({'message':'질문글이 저장되었습니다.'}, status=status.HTTP_201_CREATED)
        return Response({'message' : '인증이 필요합니다. 먼저 로그인을 해주세요.'}, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        # 유저가 일치하는지 확인. 추후 메서드로 만들어 놓을 것.
        if request.user != instance.qa_user:
            return Response({'message': '질문을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        # qna 객체가 기존에 패스워드 값을 가지고 있는데 패스워드가 일치하지 않을 경우에만 error 리턴
        if getattr(instance, 'password'):
            if instance.password != request.data['password']:
                return Response({'message':'패스워드가 일치하지 않습니다. 패스워드를 다시 확인해 주세요.'}, status=status.HTTP_401_UNAUTHORIZED)

        # qna 객체가 애초에 없거나, 있어도 패스워드가 일치하는 경우.
        # 여기서부터는 ModelViewSet의 기존 코드와 모드 일치한다.
        # partial = kwargs.pop('partial', False)
        # instance = self.get_object()
        # serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        #
        # if getattr(instance, '_prefetched_objects_cache', None):
        #     instance._prefetched_objects_cache = {}
        super().partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.qa_user:
            return Response({'message' : '질문글을 삭제할 수 있는 권한이 없습니다. 작성자만이 질문글을 삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class qa_reple_list(generics.ListCreateAPIView):
    queryset = QaReple.objects.all()
    serializer_class = QaRepleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(repleUser=self.request.user).order_by("-repleDate")

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            reple = QaReple.objects.create(
                content=request.data['content'],
                qa=Qa.objects.get(id=request.data['pk']),
                repleUser=request.user
            )
            return Response({"message": "답글 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response({"message": "로그인이 필요한 기능입니다."}, status=status.HTTP_401_UNAUTHORIZED)

class qa_reple_detail(mixins.DestroyModelMixin, generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        reple = QaReple.objects.get(id=kwargs['pk'])
        if request.user == reple.repleUser:
            reple.delete()
        return Response(status=status.HTTP_200_OK)
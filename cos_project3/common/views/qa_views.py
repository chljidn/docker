from rest_framework import viewsets, generics, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.paginations import QaPagination
from common import serializers
from common.models import Qa, QaReple
from django_filters.rest_framework import DjangoFilterBackend
from common.filters import QaFilter
from django.core import exceptions
from common.decorators import login_decorator

# QNA
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
            serialize = self.serializer_class(qaDetail)
            return Response(serialize.data, status=status.HTTP_200_OK)

    @login_decorator
    def create(self, request, *args, **kwargs):
        password = request.data.get('password', None)
        if password == '': password = None
        qa = Qa.objects.create(
            postname=request.data['postname'],
            content=request.data['content'],
            password=password,
            qa_user=request.user
        )
        return Response({'message':'질문글이 저장되었습니다.'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    @login_decorator
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        if request.user != instance.qa_user:
            return Response({'message': '질문을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        # qna 객체가 기존에 패스워드 값을 가지고 있는데 패스워드가 일치하지 않을 경우에만 error 리턴
        if getattr(instance, 'password'):
            if instance.password != request.data['password']:
                return Response({'message':'패스워드가 일치하지 않습니다. 패스워드를 다시 확인해 주세요.'}, status=status.HTTP_401_UNAUTHORIZED)
        super().partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.qa_user:
            return Response({'message' : '질문글을 삭제할 수 있는 권한이 없습니다. 작성자만이 질문글을 삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class qa_reple_list(generics.ListCreateAPIView):
    queryset = QaReple.objects.all()
    serializer_class = serializers.QaRepleSerializer
    permission_classes = [IsAuthenticated]

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
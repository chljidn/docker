# rest_framework 관련 설치
from rest_framework import viewsets
from rest_framework.views import APIView # 모든 함수를 클래스뷰로 하기 위해서 import
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer # html 렌더링 하기 위함
# 페이징
from rest_framework.pagination import PageNumberPagination
from common.paginations import QaPagination
# 데코레이터
from rest_framework.decorators import action
# 해쉬 암호화 모듈
from django.contrib.auth.hashers import make_password, check_password
# serializers.py 설치
from common import serializers
# 모델 설치
from common.models import Qa, QaReple
# cache
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from common.filters import QaFilter
from django.utils import timezone
from django.core import exceptions

class qa(viewsets.ModelViewSet):
    # 인증없이 qa를 읽을 수 있도록 함.
    permission_classes = []
    serializer_class = serializers.QaSerializers
    queryset = Qa.objects.all().order_by('-qaDate')
    filter_backends = [DjangoFilterBackend]
    # 파라미터 필드 지정
    filterset_class = QaFilter
    # pagination_class는 [PageNumberPagination] 처럼 리스트 형식으로 선언하면 에러 발생.
    pagination_class = QaPagination

    # def get_queryset(self):
    #     pass

    # post로 데이터가 넘어올 경우에는 저장과 인증 필요
    def create(self, request, *args, **kwargs):
        # 패스워드가 아예 없거나 ''인 경우는 None로 처리.
        # 모델 설정에서 default=None로 설정했기 때문에 가능.
        password = request.data.get('password', None)
        if password == '': password = None
        if request.user.is_authenticated:
            qa = Qa.objects.create(
                postname=request.data['postname'],
                content=request.data['content'],
                password=password,
                qa_user=request.user,
            )
            qa.save()
            return Response({'message':'게시글이 저장되었습니다.'},
                            status=status.HTTP_201_CREATED
                            )
        else:
            return Response({'message' : '인증이 필요합니다. 먼저 로그인을 해주세요.'},
                            status=status.HTTP_401_UNAUTHORIZED
                            )

    # 요청에 따라 유동적으로 리턴값을 변경하기 위해서 사용한다.
    # 가장 기본적인 get은 qa 리스트를 모두 가져오는 것이다.
    # 하지만 하나의 게시글만 클릭해서 보고 싶을 경우, 기존에 게시글을 작성하는 기능인 create와 다르게 작동시킬 수 있어야 한다. 이 경우 Post의 인자는 password 뿐이다
    # 이럴 때 actions을 사용하여 다르게 작동할 수 있는 post를 만든다
    # detail=True를 사용하면 pk를 받겠다는 의미이며, url은 common/qa/{pk}/qa_detail/ 이 된다.
    # qa_detail은 함수 이름이다.
    @action(detail=True, methods=['get', 'post'])
    def qa_detail(self, request, pk=None):
        try:
            qaDetail = Qa.objects.get(id=pk)
        except exceptions.ObjectDoesNotExist:
            return Response({"message": "Q&A가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            if request.method == "GET":
                if qaDetail.password != None:
                    return Response({'message' : '패스워드가 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    qaDetailSerializer = serializers.QaSerializers(data=[qaDetail], many=True)
                    qaDetailSerializer.is_valid()
                    return Response(qaDetailSerializer.data, status=status.HTTP_200_OK)

            if request.method == 'POST':
                # 유저가 스태프일 경우 그냥 확인할 수 있고, 아닐 경우는 패스워드 비교
                if qaDetail.password == request.data['password'] or request.user.is_staff:
                    qaDetailSerializer = serializers.QaSerializers(data=[qaDetail], many=True)
                    qaDetailSerializer.is_valid()
                    return Response(qaDetailSerializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "패스워드가 일치하지 않습니다. 다시 시도해 주십시오."}, status=status.HTTP_401_UNAUTHORIZED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        # qna 객체가 기존에 패스워드 값을 가지고 있는데 패스워드가 일치하지 않을 경우에만 error 리턴
        if getattr(instance, 'password'):
            if instance.password != request.data['password']:
                return Response({'message':'패스워드가 일치하지 않습니다. 패스워드를 다시 확인해 주세요.'}, status=status.HTTP_401_UNAUTHORIZED)

        # qna 객체가 애초에 없거나, 있어도 패스워드가 일치하는 경우.
        # 여기서부터는 ModelViewSet의 기존 코드와 모드 일치한다.
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


        # 패스워드가 있는 경우만 재정의하고, 나머지는 부모클래스의 partial_update를 그대로 사용한다.

        # print(request.data)
        # if password_qna.password != None:
        #     if request.user == password_qna.qa_user:
        #         if request.password == password_qna.password:
        #             password_qna.update(**kwargs)
        #         else: return Response({'message' : '패스워드가 일치하지 않습니다. 패스워드를 다시 확인해주세요.'})
        #     else: return Response({'message' : '게시글의 작성자만 수정할 수 있습니다.'})
        # else:


# QNA 리플 기능
# qna에 패스워드를 쳐야만 들어올 수 있으므로 리플 기느에 제한을 둘 필요는 없을 듯 함
# 패스워드가 없는 qna라면 이미 작성자가 공개적으로 개방하겠다는 뜻으로 받아들여 리플 기능을 제한하지 않는다
# get은 qa에서 가져올 수 있으므로 작성하지 앟는다
class qaReple(viewsets.ViewSet):
    permission_classes = []

    def create(self, request):
        # pk는 qna의 Pk.
        # 리플을 달기 위해서는 로그인이 필요하다.
        if request.user.is_authenticated:
            reple = QaReple.objects.create(
                content=request.data['content'],
                # qa_id는 ForeignKey이기 때문에 해당 Qa 객체가 들어가야 한다.
                # 이 부분은 차후 수정할 예정
                qa=Qa.objects.get(id=request.data['pk']),
                repleUser=request.user
            )
            return Response({"message" : "답글 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message" : "로그인이 필요한 기능입니다."}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        reple = qaReple.objects.get(id=pk)
        if request.user == reple.repleUser:
            reple.delete()
        return Response(status=status.HTTP_200_OK)
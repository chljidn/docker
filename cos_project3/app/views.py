from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from app.filters import CosFilter
from app.serializers import CosSerializer, RecommendSerializer, CosReviewSerializer
from app.models import ImageUpload, Cos, CosReviewModel
from common.models import User
from app.recommend import recommend
from django.core.cache import cache
from rest_framework import generics

# 이미지 파일은 'media/imageupload' 디렉터리 경로로 저장
class image_upload(generics.CreateAPIView):
    # queryset =
    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            image = ImageUpload.objects.create(
                title=request.data['title'],
                pic = request.data['pic']
            )
            recommend_object = recommend(image.pic)
            result = recommend_object.cosine()
            serialize = RecommendSerializer(result, many=True)
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        return Response({"message": "회원만 가능한 기능입니다."}, status=status.HTTP_401_UNAUTHORIZED)


class cos_list(generics.ListAPIView):
    permission_classes = []
    queryset = cache.get_or_set('coslist', Cos.objects.filter().distinct().order_by('id'))
    serializer_class = CosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CosFilter


class cosLike(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        cos = Cos.objects.get(id=request.data['pk'])
        if cos.like.filter(id=request.user.id):
            cos.like.remove(user)
            return Response(status=status.HTTP_200_OK)
        else:
            cos.like.add(user)
            return Response(status=status.HTTP_201_CREATED)


class cos_review(viewsets.ModelViewSet):
    queryset = CosReviewModel.objects.all()
    serializer_class = CosReviewSerializer

    def get_permissions(self):
        if self.action in ['create', 'partial_update', "destroy"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes ]

    def create(self, request):
        if request.user.is_authenticated:
            review = CosReviewModel.objects.create(
                reviewName=request.data['reviewName'],
                reviewContent=request.data['reviewContent'],
                reviewImage=request.data['reviewImage'],
                reviewUser=request.user,
                reviewCos=Cos.objects.get(id=request.data['cos_id'])
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({'message' : '로그인이 필요한 기능입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().reviewUser:
            super().partial_update(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        return Response({'message' : '해당 글을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().reviewUser:
            super().destroy(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        return Response({'message' : '해당 글을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
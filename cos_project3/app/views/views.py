# rest_framework 관련 모듈 설치
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
# filter
from django_filters.rest_framework import DjangoFilterBackend
from app.filters import CosFilter
# serializers
from app.serializers import CosSerializer, RecommendSerializer, CosReviewSerializer
# models
from app.models import ImageUpload, Cos, CosReviewModel
from common.models import User
# 추천
from app.views.recommend import recommend
# 캐시 사용 위해 설치
from django.core.cache import cache


# 이미지 업로드 페이지
# 이미지 파일은 'media/imageupload' 디렉터리 경로로 저장
class image_upload(viewsets.ViewSet):
    permission_classes = []
    def create(self, request):
        image = ImageUpload()
        image.title = request.POST['title']
        image.pic = request.FILES['pic']
        image.save()
        # recommend class의 객체 생성
        # image.pic.url로 하면 한글파일의 경우 파일 이름의 인코딩 에러 발생.
        recommend_function = recommend(image.pic)
        result = recommend_function.cosine()
        result_serializer = RecommendSerializer(result, many=True)
        return Response(result_serializer.data)

# 화장품 리스트 페이지
class cos_list(viewsets.ModelViewSet):
    permission_classes = []
    queryset = cache.get_or_set('coslist', Cos.objects.filter().distinct().order_by('id'))
    serializer_class = CosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CosFilter

# 좋아요 기능
# ManyToManyField 사용
class cosLike(APIView):
    def post(self, request):
        user = User.objects.get(id=request.user.id)
        cos = Cos.objects.get(id=request.data['pk'])
        if cos.like.filter(id=request.user.id):
            cos.like.remove(user)
            return Response(status=status.HTTP_200_OK)
        else:
            cos.like.add(user)
            return Response(status=status.HTTP_201_CREATED)

class cosReview(viewsets.ModelViewSet):
    queryset = CosReviewModel.objects.all()
    permission_classes = []
    serializer_class = CosReviewSerializer

    def list(self, request):
        reviewSerializer = self.get_serializer(data=self.queryset, many=True)
        reviewSerializer.is_valid()
        return Response(reviewSerializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        if request.user.is_authenticated:
            review = CosReviewModel.objects.create(
                reviewName=request.data['reviewName'],
                reviewContent=request.data['reviewContent'],
                reviewImage=request.data['reviewImage'],
                reviewUser=request.user,
                reviewCos=Cos.objects.get(id=request.data['cos_id'])
            )
            review.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({'message' : '로그인이 필요한 기능입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        review = self.get_object()
        if request.user == review.reviewUser:
            return self.update(request, *args, **kwargs)
        else:
            return Response({'message' : '해당 글을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

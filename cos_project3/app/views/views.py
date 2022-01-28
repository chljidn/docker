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
        print(request)
        image = ImageUpload()
        image.title = request.POST['title']
        image.pic = request.FILES['pic']
        image.save()
        # recommend class의 객체 생성
        # image.pic.url로 하면 한글파일의 경우 파일 이름의 인코딩 에러 발생.
        recommend_function = recommend(image.pic)
        # 추출된 성분 문자열로 코사인 유사도 수행.
        result = recommend_function.cosine()
        result_serializer = RecommendSerializer(result, many=True)
        return Response(result_serializer.data)

# 화장품 리스트 페이지
class cos_list(viewsets.ModelViewSet):
    permission_classes = []
    # pagination 사용 위해서 id를 기준으로 정렬시켜야 함.
    # 작동하지 않는 것은 아니나 에러문구가 자꾸 나타나기 때문에 처리함.
    queryset = cache.get_or_set('coslist', Cos.objects.filter().distinct().order_by('id'))
    serializer_class = CosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CosFilter

# 좋아요 기능
# ManyToManyField 사용
class cosLike(APIView):
    def post(self, request):
        # 요청한 유저 객체 생성
        user = User.objects.get(id=request.user.id)
        # 현재 '좋아요' 버튼을 누른 화장품 객체를 가져온다.
        cos = Cos.objects.get(id=request.data['pk'])
        # 만약 이미 '좋아요'를 해 놓은 화장품들 중에 지금 '좋아요'를 누른 화장품이 들어있다면
        if cos.like.filter(id=request.user.id):
            # 화장품 객체의 like 컬럼에서 user 객체를 삭제한다. 따라서 app_cos_like 테이블에서 해당 row가 삭제된다.
            cos.like.remove(user)
            return Response(status=status.HTTP_200_OK)
        else:
            # 화장품 객체의 like 컬럼에 user 객체를 집어넣는다.
            # app_cos_like에 cos_id는 cos의 pk 값이고, user_id는 user의 id인 row가 생성된다.
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

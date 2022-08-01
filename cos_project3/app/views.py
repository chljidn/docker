from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from django_filters.rest_framework import DjangoFilterBackend
from app.filters import CosFilter
from app.serializers import CosSerializer, RecommendSerializer, CosReviewSerializer, recommend_excel_serializer
from app.models import ImageUpload, Cos, CosReviewModel, recommend_excel
from app.recommend import recommend
from django.core.cache import cache
from app.tasks import excel_recommend_task
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from common.decorators import login_decorator
# from app.filters import cos_list_filters

class cos_list(generics.ListAPIView):
    queryset = cache.get_or_set('coslist', Cos.objects.filter().distinct().order_by('-id'))
    serializer_class = CosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CosFilter
    # filter_backends = [cos_list_filters]





# 이미지 파일은 'media/imageupload' 디렉터리 경로로 저장
class image_upload(generics.CreateAPIView):
    @login_decorator
    def create(self, request, *args, **kwargs):
        image = ImageUpload.objects.create(
            title=request.data['title'],
            pic=request.data['pic']
        )
        if request.data["recommend_save"] == 'true':
            if request.user.is_authenticated:
                # celery에 매개변수를 넣어 보낼 때, 그냥 image.pic를 보내면 <class 'django.db.models.fields.files.ImageFieldFile'> 객체 타입이기 때문에
                # celery task가 작동하지 않는다. 때문에 문자열로 변경해서 보내주어야 한다.
                excel_recommend_task.delay(str(image.pic), str(request.user.username), str(image.title))
                return Response({"message": "이미지가 업로드 되었습니다. 추천이 진행 중입니다."}, status=status.HTTP_201_CREATED)
            return Response({"message": "해당 기능은 회원만 가능합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        recommend_object = recommend(image.pic)
        result = recommend_object.cosine()
        serializer = RecommendSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class recommend_excel_detail_view(generics.ListAPIView):
    queryset = recommend_excel.objects.all()
    serializer_class = recommend_excel_serializer

    def get_queryset(self, **kwargs):
        queryset = recommend_excel.objects.all()
        if kwargs.get("pk", None):
            queryset = queryset.filter(user__id=kwargs["pk"])
        return queryset

    @login_decorator
    def list(self, request, *args, **kwargs):
        instances = self.get_queryset(**kwargs)
        serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)


class recommend_file(generics.RetrieveDestroyAPIView):
    @login_decorator
    def retrieve(self, request, *args, **kwargs):
        file = FileSystemStorage("media/")
        response = Response(file,
                            content_type="application//vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            status=status.HTTP_200_OK
                            )
        response = FileResponse(file.open(f"recommend_excel/{request.user.username}_{kwargs['pk']}.xlsx", "rb"),
                                content_type="application//vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
        response['Content-Disposition'] = f'attachment; filename="recommend_file_.xlsx"'
        return response

    @login_decorator
    def destroy(self, request, *args, **kwargs):
        try:
            file = FileSystemStorage("media/recommend_excel/")
            if file.exists(f"{request.user.username}_{kwargs['pk']}.xlsx"):
                file.delete(f"{request.user.username}_{kwargs['pk']}.xlsx")
                my_recommend = recommend_excel.objects.filter(user_id=request.user.id, file_title=kwargs["pk"])
                my_recommend.delete()
                return Response({"message": "해당 추천 파일이 삭제되었습니다."}, status=status.HTTP_200_OK)
            return Response({"message": "해당 파일이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : e}, status=status.HTTP_400_BAD_REQUEST)


class cosLike(generics.CreateAPIView):
    @login_decorator
    def post(self, request, *args, **kwargs):
        cos = Cos.objects.get(id=request.data['pk'])
        if cos.like.filter(id=request.user.id):
            cos.like.remove(request.user)
            return Response(status=status.HTTP_200_OK)
        cos.like.add(request.user)
        return Response(status=status.HTTP_201_CREATED)


class cos_review(viewsets.ModelViewSet):
    queryset = CosReviewModel.objects.all()
    serializer_class = CosReviewSerializer

    @login_decorator
    def create(self, request):
        review = CosReviewModel.objects.create(
            reviewName=request.data['reviewName'],
            reviewContent=request.data['reviewContent'],
            reviewImage=request.data['reviewImage'],
            reviewUser=request.user,
            reviewCos=Cos.objects.get(id=request.data['cos_id'])
        )
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    @login_decorator
    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().reviewUser:
            super().partial_update(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        return Response({'message' : '해당 글을 수정할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    @login_decorator
    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().reviewUser:
            super().destroy(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        return Response({'message' : '해당 글을 삭제할 수 있는 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

from django.urls import path, include
from app import views as app_views
from rest_framework.routers import DefaultRouter
app_name = 'app'

router = DefaultRouter()
router.register(r'cos_review', app_views.cos_review, basename='cos_review')

urlpatterns = [
    path('coslike/', app_views.cosLike.as_view(), name='coslike'),
    path("upload/", app_views.image_upload.as_view(), name="image_upload"),
    path("cos_list/", app_views.cos_list.as_view(),name="cos_list"),
    path("recommend_excel/<str:pk>/", app_views.recommend_file().as_view(), name="recommend_excel"),
    path("recommend_excel_list/<int:pk>/", app_views.recommend_excel_detail_view.as_view(), name="recommend_excel_list"),
    path('', include(router.urls))
]
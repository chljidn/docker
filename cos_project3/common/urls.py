from django.urls import include, path
from common.views import qa_views, auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'common'

router = DefaultRouter()
router.register(r'qa', qa_views.qa, basename='qa')
router.register(r'qa_reple', qa_views.qaReple, basename='qa_reple')

urlpatterns = [
    path('auth/', auth_views.auth.as_view(), name='auth'),
    path('useredit/', auth_views.userEdit.as_view(), name='useredit'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('', include(router.urls))
]


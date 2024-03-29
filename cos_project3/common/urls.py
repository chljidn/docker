from django.urls import include, path
from common.views import qa_views, auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'common'

router = DefaultRouter()
router.register(r'qa', qa_views.qa, basename='qa')

urlpatterns = [
    path('signup/', auth_views.SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('myinfo/<int:pk>/', auth_views.MyInfoView.as_view(), name='myinfo'),
    path('refresh/', TokenRefreshView.as_view(), name="refresh"),
    path('qa_reple/', qa_views.qa_reple_list.as_view(), name="qa_reple_list"),
    path('qa_reple/<int:pk>/', qa_views.qa_reple_detail.as_view(), name="qa_reple_detail"),
    path('', include(router.urls))
]


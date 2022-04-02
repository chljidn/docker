from django.contrib import admin
from django.urls import path, include

from django.conf import settings # settings 설치
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('common/', include('common.urls')),
    path('app/', include('app.urls'))
]
# media 파일을 저장한 경로를 setting하기 위한 코드
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

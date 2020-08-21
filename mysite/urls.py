from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from mysite.core import views

urlpatterns = [
    path('',views.upload, name='upload' ),
    path('video/', views.video_process, name='video_process'),
    path('eliminate/', views.raw_remove, name='get_pdf'),
    path('admin/', admin.site.urls),
    path('pdf/', views.download)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.video import views

app_name = 'video'

router = DefaultRouter()
router.register('tasks', views.VideoCompressionTaskViewSet, basename='task')

urlpatterns = [
    # 视频压缩页面
    path('', views.video_compression_page, name='compression_page'),

    # API 路由
    path('api/', include(router.urls)),
]

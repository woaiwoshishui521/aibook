from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.image.views import ImageCompressionTaskViewSet, image_compression_page

router = DefaultRouter()
router.register(r'tasks', ImageCompressionTaskViewSet, basename='image-compression-task')

urlpatterns = [
    path('', image_compression_page, name='image-compression-page'),
    path('api/', include(router.urls)),
]

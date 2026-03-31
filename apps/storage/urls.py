from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.storage.views import OSSFileViewSet, oss_upload_page

router = DefaultRouter()
router.register(r'api/files', OSSFileViewSet, basename='oss-file')

urlpatterns = [
    path('', oss_upload_page, name='oss-upload-page'),
    path('', include(router.urls)),
]

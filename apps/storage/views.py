import os
import logging
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.http import HttpResponse

from apps.storage.models import OSSFile
from apps.storage.serializers import OSSFileSerializer, OSSFileUploadSerializer
from apps.storage.services import (
    generate_oss_key,
    upload_file_to_oss,
    upload_file_to_oss_multipart,
    delete_file_from_oss,
    generate_presigned_url,
    check_oss_connection,
)

logger = logging.getLogger(__name__)

# 大文件阈值：100MB 以上使用分片上传
MULTIPART_THRESHOLD = 100 * 1024 * 1024


class OSSFileViewSet(viewsets.ModelViewSet):
    """OSS文件管理视图集"""

    queryset = OSSFile.objects.all()
    serializer_class = OSSFileSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return OSSFileUploadSerializer
        return OSSFileSerializer

    def create(self, request, *args, **kwargs):
        """上传文件到OSS"""
        serializer = OSSFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data['file']
        description = serializer.validated_data.get('description', '')

        original_name = file_obj.name
        mime_type = file_obj.content_type or ''
        file_ext = os.path.splitext(original_name)[1].lower().lstrip('.')
        file_type = OSSFile.detect_file_type(mime_type, file_ext)

        # 生成OSS Key
        oss_key = generate_oss_key(original_name, file_type)

        # 创建数据库记录（状态为上传中）
        oss_file = OSSFile.objects.create(
            name=os.path.splitext(original_name)[0],
            original_name=original_name,
            file_type=file_type,
            mime_type=mime_type,
            file_ext=file_ext,
            oss_key=oss_key,
            oss_bucket=settings.OSS_BUCKET_NAME,
            description=description,
            status='uploading',
        )

        try:
            # 根据文件大小选择上传方式
            if file_obj.size and file_obj.size > MULTIPART_THRESHOLD:
                result = upload_file_to_oss_multipart(file_obj, oss_key, mime_type)
            else:
                result = upload_file_to_oss(file_obj, oss_key, mime_type)

            # 更新记录
            oss_file.oss_url = result['url']
            oss_file.file_size = result['size']
            oss_file.status = 'completed'
            oss_file.save()

        except Exception as e:
            logger.error(f"OSS上传失败: {str(e)}")
            oss_file.status = 'failed'
            oss_file.error_message = str(e)
            oss_file.save()
            return Response(
                {'error': f'文件上传失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_serializer = OSSFileSerializer(oss_file)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """删除文件（同时删除OSS上的文件）"""
        oss_file = self.get_object()

        # 从OSS删除
        if oss_file.oss_key and oss_file.status == 'completed':
            deleted = delete_file_from_oss(oss_file.oss_key)
            if not deleted:
                logger.warning(f"OSS文件删除失败，但继续删除数据库记录: {oss_file.oss_key}")

        # 删除数据库记录
        oss_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def presigned_url(self, request, pk=None):
        """获取预签名URL（用于私有Bucket临时访问）"""
        oss_file = self.get_object()

        if oss_file.status != 'completed':
            return Response(
                {'error': '文件未上传完成'},
                status=status.HTTP_400_BAD_REQUEST
            )

        expires = int(request.query_params.get('expires', 3600))
        expires = min(expires, 86400)  # 最长24小时

        try:
            url = generate_presigned_url(oss_file.oss_key, expires)
            return Response({'url': url, 'expires': expires})
        except Exception as e:
            return Response(
                {'error': f'生成预签名URL失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取文件统计信息"""
        from django.db.models import Sum, Count

        total = OSSFile.objects.exclude(status='deleted').count()
        total_size = OSSFile.objects.filter(status='completed').aggregate(
            total=Sum('file_size')
        )['total'] or 0

        by_type = OSSFile.objects.filter(status='completed').values('file_type').annotate(
            count=Count('id'),
            size=Sum('file_size')
        )

        type_stats = {item['file_type']: {
            'count': item['count'],
            'size': item['size'] or 0
        } for item in by_type}

        return Response({
            'total': total,
            'completed': OSSFile.objects.filter(status='completed').count(),
            'uploading': OSSFile.objects.filter(status='uploading').count(),
            'failed': OSSFile.objects.filter(status='failed').count(),
            'total_size': total_size,
            'total_size_display': _format_size(total_size),
            'by_type': type_stats,
        })

    @action(detail=False, methods=['get'])
    def health(self, request):
        """检查OSS连接状态"""
        result = check_oss_connection()
        status_code = status.HTTP_200_OK if result['status'] == 'ok' else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(result, status=status_code)


def _format_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def oss_upload_page(request):
    """OSS文件上传页面 —— 直接返回纯静态 HTML，不经过 Django 模板引擎"""
    html_path = Path(__file__).parent / 'static' / 'storage' / 'upload.html'
    html = html_path.read_text(encoding='utf-8')
    return HttpResponse(html, content_type='text/html; charset=utf-8')



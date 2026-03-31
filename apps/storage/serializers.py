import os
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.storage.models import OSSFile


class OSSFileSerializer(serializers.ModelSerializer):
    """OSS文件序列化器（列表/详情）"""
    file_size_display = serializers.SerializerMethodField()
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OSSFile
        fields = [
            'id', 'name', 'original_name', 'file_type', 'file_type_display',
            'mime_type', 'file_size', 'file_size_display', 'file_ext',
            'oss_key', 'oss_bucket', 'oss_url',
            'status', 'status_display', 'error_message',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'name', 'file_type', 'mime_type', 'file_size', 'file_ext',
            'oss_key', 'oss_bucket', 'oss_url', 'status', 'error_message',
            'created_at', 'updated_at',
        ]

    @extend_schema_field(serializers.CharField())
    def get_file_size_display(self, obj) -> str:
        return obj.get_file_size_display()


class OSSFileUploadSerializer(serializers.Serializer):
    """文件上传序列化器"""
    file = serializers.FileField(label='文件')
    description = serializers.CharField(
        label='描述',
        required=False,
        allow_blank=True,
        max_length=500
    )

    def validate_file(self, value):
        # 限制文件大小：最大 2GB
        max_size = 2 * 1024 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"文件大小不能超过 2GB，当前文件大小: {value.size / (1024*1024*1024):.2f} GB")

        # 获取文件扩展名
        ext = os.path.splitext(value.name)[1].lower().lstrip('.')

        # 允许的扩展名
        allowed_extensions = {
            # 图片
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff',
            # 视频
            'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v', 'rmvb',
            # 音频
            'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'opus',
            # 文档
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'csv', 'md', 'html', 'xml', 'json', 'zip', 'rar', '7z',
        }

        if ext not in allowed_extensions:
            raise serializers.ValidationError(f"不支持的文件格式: .{ext}")

        return value


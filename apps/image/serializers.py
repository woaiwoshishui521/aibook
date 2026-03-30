from rest_framework import serializers
from apps.image.models import ImageCompressionTask


class ImageCompressionTaskSerializer(serializers.ModelSerializer):
    """图片压缩任务序列化器"""

    original_size_mb = serializers.SerializerMethodField()
    compressed_size_mb = serializers.SerializerMethodField()
    compression_percentage = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    format_display = serializers.CharField(source='get_target_format_display', read_only=True)
    original_resolution = serializers.SerializerMethodField()
    compressed_resolution = serializers.SerializerMethodField()

    class Meta:
        model = ImageCompressionTask
        fields = [
            'id', 'title', 'original_image', 'compressed_image',
            'quality', 'quality_display', 'target_quality', 'target_format', 'format_display',
            'max_width', 'max_height',
            'status', 'status_display', 'progress', 'error_message',
            'original_size', 'compressed_size', 'compression_ratio',
            'original_size_mb', 'compressed_size_mb', 'compression_percentage',
            'original_width', 'original_height', 'original_format', 'original_resolution',
            'compressed_width', 'compressed_height', 'compressed_format', 'compressed_resolution',
            'created_at', 'updated_at', 'completed_at',
        ]
        read_only_fields = [
            'compressed_image', 'status', 'progress', 'error_message',
            'original_size', 'compressed_size', 'compression_ratio',
            'original_width', 'original_height', 'original_format',
            'compressed_width', 'compressed_height', 'compressed_format',
            'completed_at',
        ]

    def get_original_size_mb(self, obj):
        return obj.get_original_size_mb()

    def get_compressed_size_mb(self, obj):
        return obj.get_compressed_size_mb()

    def get_compression_percentage(self, obj):
        return obj.get_compression_percentage()
    
    def get_original_resolution(self, obj):
        return obj.get_original_resolution()
    
    def get_compressed_resolution(self, obj):
        return obj.get_compressed_resolution()


class ImageCompressionTaskCreateSerializer(serializers.ModelSerializer):
    """创建图片压缩任务序列化器"""

    class Meta:
        model = ImageCompressionTask
        fields = [
            'title', 'original_image', 'quality', 'target_quality',
            'target_format', 'max_width', 'max_height',
        ]

    def validate_original_image(self, value):
        """验证图片文件"""
        # 检查文件大小 (限制为50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(f"图片文件大小不能超过 {max_size / (1024 * 1024)}MB")

        return value

    def validate_target_quality(self, value):
        """验证目标质量"""
        if value is not None and (value < 1 or value > 100):
            raise serializers.ValidationError("目标质量必须在 1-100 之间")
        return value

    def validate_max_width(self, value):
        """验证最大宽度"""
        if value is not None and value < 1:
            raise serializers.ValidationError("最大宽度必须大于 0")
        return value

    def validate_max_height(self, value):
        """验证最大高度"""
        if value is not None and value < 1:
            raise serializers.ValidationError("最大高度必须大于 0")
        return value

    def validate(self, attrs):
        """验证自定义参数"""
        quality = attrs.get('quality')

        if quality == 'custom':
            # 自定义质量必须提供至少一个参数
            if not any([
                attrs.get('target_quality'),
                attrs.get('max_width'),
                attrs.get('max_height')
            ]):
                raise serializers.ValidationError(
                    "自定义质量模式下，必须至少提供一个压缩参数（目标质量、最大宽度或最大高度）"
                )

        return attrs

from rest_framework import serializers
from apps.video.models import VideoCompressionTask


class VideoCompressionTaskSerializer(serializers.ModelSerializer):
    """视频压缩任务序列化器"""

    original_size_mb = serializers.SerializerMethodField()
    compressed_size_mb = serializers.SerializerMethodField()
    compression_percentage = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)

    class Meta:
        model = VideoCompressionTask
        fields = [
            'id', 'title', 'original_video', 'compressed_video',
            'quality', 'quality_display', 'target_resolution', 'target_bitrate', 'target_fps',
            'status', 'status_display', 'progress', 'error_message',
            'original_size', 'compressed_size', 'compression_ratio',
            'original_size_mb', 'compressed_size_mb', 'compression_percentage',
            'original_duration', 'original_resolution', 'original_bitrate',
            'created_at', 'updated_at', 'completed_at',
        ]
        read_only_fields = [
            'compressed_video', 'status', 'progress', 'error_message',
            'original_size', 'compressed_size', 'compression_ratio',
            'original_duration', 'original_resolution', 'original_bitrate',
            'completed_at',
        ]

    def get_original_size_mb(self, obj):
        return obj.get_original_size_mb()

    def get_compressed_size_mb(self, obj):
        return obj.get_compressed_size_mb()

    def get_compression_percentage(self, obj):
        return obj.get_compression_percentage()


class VideoCompressionTaskCreateSerializer(serializers.ModelSerializer):
    """创建视频压缩任务序列化器"""

    class Meta:
        model = VideoCompressionTask
        fields = [
            'title', 'original_video', 'quality',
            'target_resolution', 'target_bitrate', 'target_fps',
        ]

    def validate_original_video(self, value):
        """验证视频文件"""
        # 检查文件大小 (限制为500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if value.size > max_size:
            raise serializers.ValidationError(f"视频文件大小不能超过 {max_size / (1024 * 1024)}MB")

        return value

    def validate(self, attrs):
        """验证自定义参数"""
        quality = attrs.get('quality')

        if quality == 'custom':
            # 自定义质量必须提供至少一个参数
            if not any([
                attrs.get('target_resolution'),
                attrs.get('target_bitrate'),
                attrs.get('target_fps')
            ]):
                raise serializers.ValidationError(
                    "自定义质量模式下，必须至少提供一个压缩参数（分辨率、比特率或帧率）"
                )

        return attrs

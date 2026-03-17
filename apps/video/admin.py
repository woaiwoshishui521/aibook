from django.contrib import admin
from apps.video.models import VideoCompressionTask


@admin.register(VideoCompressionTask)
class VideoCompressionTaskAdmin(admin.ModelAdmin):
    """视频压缩任务管理"""

    list_display = [
        'id', 'title', 'quality', 'status', 'progress',
        'get_original_size_mb', 'get_compressed_size_mb',
        'get_compression_percentage', 'created_at'
    ]
    list_filter = ['status', 'quality', 'created_at']
    search_fields = ['title']
    readonly_fields = [
        'compressed_video', 'status', 'progress', 'error_message',
        'original_size', 'compressed_size', 'compression_ratio',
        'original_duration', 'original_resolution', 'original_bitrate',
        'completed_at', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'original_video', 'compressed_video')
        }),
        ('压缩参数', {
            'fields': ('quality', 'target_resolution', 'target_bitrate', 'target_fps')
        }),
        ('任务状态', {
            'fields': ('status', 'progress', 'error_message')
        }),
        ('文件信息', {
            'fields': (
                'original_size', 'compressed_size', 'compression_ratio',
                'original_duration', 'original_resolution', 'original_bitrate'
            )
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )

    def get_original_size_mb(self, obj):
        return f"{obj.get_original_size_mb()} MB"
    get_original_size_mb.short_description = '原始大小'

    def get_compressed_size_mb(self, obj):
        return f"{obj.get_compressed_size_mb()} MB"
    get_compressed_size_mb.short_description = '压缩后大小'

    def get_compression_percentage(self, obj):
        return f"{obj.get_compression_percentage()}%"
    get_compression_percentage.short_description = '压缩率'

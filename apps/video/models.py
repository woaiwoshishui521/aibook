import os
from django.db import models
from django.core.validators import FileExtensionValidator


class VideoCompressionTask(models.Model):
    """视频压缩任务模型"""

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    QUALITY_CHOICES = [
        ('low', '低质量 (480p)'),
        ('medium', '中等质量 (720p)'),
        ('high', '高质量 (1080p)'),
        ('custom', '自定义'),
    ]

    # 基本信息
    title = models.CharField('任务名称', max_length=255)
    original_video = models.FileField(
        '原始视频',
        upload_to='videos/original/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'])]
    )
    compressed_video = models.FileField(
        '压缩后视频',
        upload_to='videos/compressed/%Y/%m/%d/',
        blank=True,
        null=True
    )

    # 压缩参数
    quality = models.CharField('压缩质量', max_length=20, choices=QUALITY_CHOICES, default='medium')
    target_resolution = models.CharField('目标分辨率', max_length=20, blank=True, null=True, help_text='例如: 1280x720')
    target_bitrate = models.CharField('目标比特率', max_length=20, blank=True, null=True, help_text='例如: 1000k')
    target_fps = models.IntegerField('目标帧率', blank=True, null=True, help_text='例如: 30')

    # 任务状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField('进度', default=0, help_text='0-100')
    error_message = models.TextField('错误信息', blank=True, null=True)

    # 文件信息
    original_size = models.BigIntegerField('原始文件大小(字节)', blank=True, null=True)
    compressed_size = models.BigIntegerField('压缩后文件大小(字节)', blank=True, null=True)
    compression_ratio = models.FloatField('压缩比', blank=True, null=True, help_text='压缩后大小/原始大小')

    # 视频元信息
    original_duration = models.FloatField('原始时长(秒)', blank=True, null=True)
    original_resolution = models.CharField('原始分辨率', max_length=20, blank=True, null=True)
    original_bitrate = models.CharField('原始比特率', max_length=20, blank=True, null=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)

    class Meta:
        db_table = 'video_compression_task'
        verbose_name = '视频压缩任务'
        verbose_name_plural = '视频压缩任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def get_compression_percentage(self):
        """获取压缩百分比"""
        if self.compression_ratio:
            return round((1 - self.compression_ratio) * 100, 2)
        return 0

    def get_original_size_mb(self):
        """获取原始文件大小(MB)"""
        if self.original_size:
            return round(self.original_size / (1024 * 1024), 2)
        return 0

    def get_compressed_size_mb(self):
        """获取压缩后文件大小(MB)"""
        if self.compressed_size:
            return round(self.compressed_size / (1024 * 1024), 2)
        return 0

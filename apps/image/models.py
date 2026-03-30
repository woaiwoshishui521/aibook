import os
from django.db import models
from django.core.validators import FileExtensionValidator


class ImageCompressionTask(models.Model):
    """图片压缩任务模型"""

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    QUALITY_CHOICES = [
        ('low', '低质量 (60%)'),
        ('medium', '中等质量 (80%)'),
        ('high', '高质量 (90%)'),
        ('custom', '自定义'),
    ]

    FORMAT_CHOICES = [
        ('same', '保持原格式'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
        ('webp', 'WebP'),
    ]

    # 基本信息
    title = models.CharField('任务名称', max_length=255)
    original_image = models.FileField(
        '原始图片',
        upload_to='images/original/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'tiff'])]
    )
    compressed_image = models.FileField(
        '压缩后图片',
        upload_to='images/compressed/%Y/%m/%d/',
        blank=True,
        null=True
    )

    # 压缩参数
    quality = models.CharField('压缩质量', max_length=20, choices=QUALITY_CHOICES, default='medium')
    target_quality = models.IntegerField('目标质量', blank=True, null=True, help_text='1-100，数值越大质量越好')
    target_format = models.CharField('目标格式', max_length=10, choices=FORMAT_CHOICES, default='same')
    max_width = models.IntegerField('最大宽度', blank=True, null=True, help_text='像素，超过此宽度将等比缩放')
    max_height = models.IntegerField('最大高度', blank=True, null=True, help_text='像素，超过此高度将等比缩放')

    # 任务状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField('进度', default=0, help_text='0-100')
    error_message = models.TextField('错误信息', blank=True, null=True)

    # 文件信息
    original_size = models.BigIntegerField('原始文件大小(字节)', blank=True, null=True)
    compressed_size = models.BigIntegerField('压缩后文件大小(字节)', blank=True, null=True)
    compression_ratio = models.FloatField('压缩比', blank=True, null=True, help_text='压缩后大小/原始大小')

    # 图片元信息
    original_width = models.IntegerField('原始宽度', blank=True, null=True)
    original_height = models.IntegerField('原始高度', blank=True, null=True)
    original_format = models.CharField('原始格式', max_length=10, blank=True, null=True)
    compressed_width = models.IntegerField('压缩后宽度', blank=True, null=True)
    compressed_height = models.IntegerField('压缩后高度', blank=True, null=True)
    compressed_format = models.CharField('压缩后格式', max_length=10, blank=True, null=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)

    class Meta:
        db_table = 'image_compression_task'
        verbose_name = '图片压缩任务'
        verbose_name_plural = '图片压缩任务'
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
    
    def get_original_resolution(self):
        """获取原始分辨率"""
        if self.original_width and self.original_height:
            return f"{self.original_width}x{self.original_height}"
        return None
    
    def get_compressed_resolution(self):
        """获取压缩后分辨率"""
        if self.compressed_width and self.compressed_height:
            return f"{self.compressed_width}x{self.compressed_height}"
        return None

import uuid
from django.db import models


class OSSFile(models.Model):
    """阿里云OSS文件记录"""

    FILE_TYPE_CHOICES = [
        ('document', '文档'),
        ('video', '视频'),
        ('image', '图片'),
        ('audio', '音频'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('uploading', '上传中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('deleted', '已删除'),
    ]

    # 文件标识
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 文件基本信息
    name = models.CharField('文件名', max_length=255)
    original_name = models.CharField('原始文件名', max_length=255)
    file_type = models.CharField('文件类型', max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    mime_type = models.CharField('MIME类型', max_length=100, blank=True)
    file_size = models.BigIntegerField('文件大小(字节)', default=0)
    file_ext = models.CharField('文件扩展名', max_length=20, blank=True)

    # OSS 信息
    oss_key = models.CharField('OSS对象Key', max_length=500, unique=True)
    oss_bucket = models.CharField('OSS Bucket', max_length=100)
    oss_url = models.URLField('OSS访问URL', max_length=1000, blank=True)

    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='uploading')
    error_message = models.TextField('错误信息', blank=True)

    # 描述
    description = models.TextField('描述', blank=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'oss_files'
        verbose_name = 'OSS文件'
        verbose_name_plural = 'OSS文件'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_name} ({self.get_file_type_display()})"

    def get_file_size_display(self):
        """获取人性化的文件大小"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    @classmethod
    def detect_file_type(cls, mime_type: str, ext: str) -> str:
        """根据MIME类型和扩展名判断文件类型"""
        ext = ext.lower().lstrip('.')
        mime = mime_type.lower() if mime_type else ''

        if mime.startswith('image/') or ext in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff'):
            return 'image'
        elif mime.startswith('video/') or ext in ('mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v', 'rmvb'):
            return 'video'
        elif mime.startswith('audio/') or ext in ('mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'opus'):
            return 'audio'
        elif (mime in ('application/pdf', 'application/msword',
                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                       'application/vnd.ms-excel',
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                       'application/vnd.ms-powerpoint',
                       'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                       'text/plain', 'text/csv', 'text/html', 'text/markdown')
              or ext in ('pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'md', 'html', 'xml', 'json')):
            return 'document'
        return 'other'

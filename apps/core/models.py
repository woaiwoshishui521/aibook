from django.db import models
import uuid


class BaseModel(models.Model):
    """基础模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

from django.db import models


class ServiceLog(models.Model):
    """服务运行日志"""
    service_name = models.CharField(max_length=100, verbose_name='服务名称')
    action = models.CharField(max_length=50, verbose_name='操作')
    status = models.CharField(max_length=20, verbose_name='状态')
    message = models.TextField(blank=True, verbose_name='消息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'service_log'
        verbose_name = '服务日志'
        verbose_name_plural = '服务日志'
        ordering = ['-created_at']

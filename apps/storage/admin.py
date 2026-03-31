from django.contrib import admin
from apps.storage.models import OSSFile


@admin.register(OSSFile)
class OSSFileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'file_type', 'get_file_size_display', 'status', 'oss_bucket', 'created_at']
    list_filter = ['file_type', 'status', 'oss_bucket']
    search_fields = ['original_name', 'name', 'oss_key']
    readonly_fields = ['id', 'oss_key', 'oss_url', 'file_size', 'created_at', 'updated_at']
    ordering = ['-created_at']

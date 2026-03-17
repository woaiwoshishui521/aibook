from django.contrib import admin
from .models import ServiceLog


@admin.register(ServiceLog)
class ServiceLogAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'action', 'status', 'created_at']
    list_filter = ['service_name', 'action', 'status']
    search_fields = ['service_name', 'message']
    readonly_fields = ['created_at']

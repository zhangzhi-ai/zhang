from django.contrib import admin
from .models import SystemConfig, AccessLog


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['config_key', 'config_value', 'config_type', 'is_active', 'updated_at']
    list_filter = ['config_type', 'is_active', 'created_at']
    search_fields = ['config_key', 'description']
    ordering = ['config_key']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'user', 'request_method', 'request_url', 'response_status', 'created_at']
    list_filter = ['request_method', 'response_status', 'created_at']
    search_fields = ['ip_address', 'request_url', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
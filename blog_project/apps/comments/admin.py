from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'user', 'article', 'parent', 'status', 'like_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['content', 'user__username', 'article__title']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('content', 'article', 'user', 'parent')
        }),
        ('状态和统计', {
            'fields': ('status', 'like_count')
        }),
        ('技术信息', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['like_count']
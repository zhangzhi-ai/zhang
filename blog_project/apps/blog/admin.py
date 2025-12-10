from django.contrib import admin
from .models import Category, Tag, Article, ArticleTag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'id']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'use_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['-use_count', 'id']


class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_top', 'is_recommend', 'view_count', 'published_at']
    list_filter = ['status', 'is_top', 'is_recommend', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created_at']
    inlines = [ArticleTagInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'summary', 'cover_image')
        }),
        ('分类和标签', {
            'fields': ('category',)
        }),
        ('设置', {
            'fields': ('status', 'is_top', 'is_recommend')
        }),
        ('统计信息', {
            'fields': ('view_count', 'like_count', 'comment_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['view_count', 'like_count', 'comment_count']
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时设置作者
            obj.author = request.user
        super().save_model(request, obj, form, change)
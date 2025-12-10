from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
import os
from .models import Category, Tag, Article
from .serializers import (
    CategorySerializer, CategoryManageSerializer, TagSerializer, ArticleListSerializer,
    ArticleDetailSerializer, ArticleCreateUpdateSerializer, ArticleSearchSerializer
)


class CategoryListView(generics.ListAPIView):
    """分类列表"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class TagListView(generics.ListAPIView):
    """标签列表"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class ArticleListView(generics.ListAPIView):
    """文章列表"""
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = Article.objects.filter(status=1).select_related('author', 'category').prefetch_related('tags')
        
        # 搜索参数
        search_serializer = ArticleSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data
            
            # 关键词搜索
            keyword = data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(content__icontains=keyword) |
                    Q(summary__icontains=keyword)
                )
            
            # 分类筛选
            category_id = data.get('category_id')
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            # 标签筛选
            tag_id = data.get('tag_id')
            if tag_id:
                queryset = queryset.filter(tags__id=tag_id)
            
            # 作者筛选
            author_id = data.get('author_id')
            if author_id:
                queryset = queryset.filter(author_id=author_id)
            
            # 推荐筛选
            is_recommend = data.get('is_recommend')
            if is_recommend is not None:
                queryset = queryset.filter(is_recommend=is_recommend)
            
            # 排序
            ordering = data.get('ordering', '-published_at')
            queryset = queryset.order_by(ordering)
        
        return queryset.distinct()


class ArticleDetailView(generics.RetrieveAPIView):
    """文章详情"""
    queryset = Article.objects.filter(status=1)
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加浏览量
        instance.increase_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ArticleCreateView(generics.CreateAPIView):
    """创建文章"""
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleUpdateView(generics.UpdateAPIView):
    """更新文章"""
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)


class ArticleDeleteView(generics.DestroyAPIView):
    """删除文章"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)
    
    def perform_destroy(self, instance):
        # 软删除：将状态设为已删除
        instance.status = 2
        instance.save()


class MyArticleListView(generics.ListAPIView):
    """我的文章列表"""
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        return Article.objects.filter(
            author=self.request.user
        ).exclude(status=2).select_related('category').prefetch_related('tags')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def article_recommend_view(request):
    """推荐文章"""
    try:
        articles = list(Article.objects.filter(
            status__in=[0, 1], is_recommend=True
        ).select_related('author', 'category').prefetch_related('tags')[:6])
        
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def article_hot_view(request):
    """热门文章（按浏览量排序）"""
    try:
        articles = list(Article.objects.filter(
            status__in=[0, 1]
        ).select_related('author', 'category').prefetch_related('tags').order_by('-view_count')[:10])
        
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def article_like_view(request, article_id):
    """文章点赞/取消点赞"""
    from apps.users.models import UserLike
    
    article = get_object_or_404(Article, id=article_id, status=1)
    user = request.user
    
    like_obj, created = UserLike.objects.get_or_create(
        user=user,
        target_type=1,  # 文章
        target_id=article_id
    )
    
    if created:
        # 点赞
        article.like_count += 1
        article.save(update_fields=['like_count'])
        message = '点赞成功'
        is_liked = True
    else:
        # 取消点赞
        like_obj.delete()
        article.like_count = max(0, article.like_count - 1)
        article.save(update_fields=['like_count'])
        message = '取消点赞'
        is_liked = False
    
    return Response({
        'message': message,
        'is_liked': is_liked,
        'like_count': article.like_count
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def article_cover_upload_view(request):
    """上传文章封面"""
    file_obj = request.FILES.get('cover')
    if not file_obj:
        return Response({'message': '请上传封面文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    ext = os.path.splitext(file_obj.name)[1].lower() or '.jpg'
    allowed_ext = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if ext not in allowed_ext:
        return Response({'message': '仅支持 JPG/PNG/GIF/WebP 图片'}, status=status.HTTP_400_BAD_REQUEST)
    
    filename = timezone.now().strftime('articles/%Y/%m/%d/%H%M%S')
    filename = f"{filename}_{get_random_string(6)}{ext}"
    saved_path = default_storage.save(filename, file_obj)
    relative_url = default_storage.url(saved_path)
    absolute_url = request.build_absolute_uri(relative_url)
    
    return Response({
        'message': '上传成功',
        'url': absolute_url,
        'path': relative_url
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def statistics_view(request):
    """网站统计信息"""
    from apps.users.models import User
    from apps.comments.models import Comment
    
    stats = {
        'article_count': Article.objects.filter(status=1).count(),
        'user_count': User.objects.filter(is_active=True).count(),
        'comment_count': Comment.objects.filter(status=1).count(),
        'category_count': Category.objects.filter(is_active=True).count(),
        'tag_count': Tag.objects.count(),
    }
    
    return Response(stats)


# ==================== 分类管理（仅管理员） ====================

class CategoryManageListView(generics.ListCreateAPIView):
    """分类管理列表（创建、查看）"""
    serializer_class = CategoryManageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 禁用分页，返回所有分类
    
    def get_queryset(self):
        # 只有管理员可以访问
        if not self.request.user.is_staff:
            return Category.objects.none()
        return Category.objects.all().order_by('sort_order', 'id')
    
    def perform_create(self, serializer):
        # 只有管理员可以创建
        if not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只有管理员可以创建分类")
        serializer.save()


class CategoryManageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """分类管理详情（查看、更新、删除）"""
    serializer_class = CategoryManageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        # 只有管理员可以访问
        if not self.request.user.is_staff:
            return Category.objects.none()
        return Category.objects.all()
    
    def perform_update(self, serializer):
        # 只有管理员可以更新
        if not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只有管理员可以更新分类")
        serializer.save()
    
    def perform_destroy(self, instance):
        # 只有管理员可以删除
        if not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只有管理员可以删除分类")
        # 检查是否有文章使用该分类
        article_count = instance.articles.exclude(status=2).count()
        if article_count > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"该分类下还有 {article_count} 篇文章，请先删除或移动这些文章后再删除分类")
        instance.delete()
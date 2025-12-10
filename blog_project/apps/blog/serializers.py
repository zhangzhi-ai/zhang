from rest_framework import serializers
from django.conf import settings
from .models import Category, Tag, Article, ArticleTag
from apps.users.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'sort_order', 'article_count']
    
    def get_article_count(self, obj):
        try:
            return obj.get_article_count()
        except Exception:
            return 0


class CategoryManageSerializer(serializers.ModelSerializer):
    """分类管理序列化器（包含is_active字段）"""
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'sort_order', 'is_active', 'article_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_article_count(self, obj):
        try:
            return obj.get_article_count()
        except Exception:
            return 0


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'use_count']


class ArticleListSerializer(serializers.ModelSerializer):
    """文章列表序列化器"""
    author = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'summary', 'cover_image', 'author', 'category', 
            'tags', 'is_top', 'is_recommend', 'view_count', 'like_count', 
            'comment_count', 'published_at', 'created_at'
        ]
    
    def get_cover_image(self, obj):
        """返回封面图片的绝对URL"""
        # 优先使用 cover_image_url
        if obj.cover_image_url:
            return obj.cover_image_url
        
        # 如果没有URL，尝试使用ImageField
        if not obj.cover_image:
            return None
        
        # 尝试获取cover_image的值（可能是ImageField或字符串）
        try:
            # 如果是ImageField，尝试获取URL
            if hasattr(obj.cover_image, 'url'):
                image_url = obj.cover_image.url
            else:
                # 否则转换为字符串
                image_url = str(obj.cover_image)
        except (ValueError, AttributeError):
            # 如果获取失败，使用字符串值
            image_url = str(obj.cover_image) if obj.cover_image else None
        
        if not image_url:
            return None
        
        # 如果已经是完整URL，直接返回
        if image_url.startswith('http://') or image_url.startswith('https://'):
            return image_url
        
        # 构建绝对URL
        request = self.context.get('request')
        if request:
            # 如果image_url已经是绝对路径（以/开头），直接构建
            if image_url.startswith('/'):
                return request.build_absolute_uri(image_url)
            else:
                # 否则使用MEDIA_URL
                return request.build_absolute_uri(settings.MEDIA_URL + image_url)
        
        # 如果没有request上下文，使用settings中的信息
        if image_url.startswith('/'):
            return image_url
        return f"{settings.MEDIA_URL}{image_url}" if image_url else None


class ArticleDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器"""
    author = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'summary', 'cover_image', 'author', 
            'category', 'tags', 'is_top', 'is_recommend', 'view_count', 
            'like_count', 'comment_count', 'published_at', 'created_at', 'updated_at'
        ]
    
    def get_cover_image(self, obj):
        """返回封面图片的绝对URL"""
        # 优先使用 cover_image_url
        if obj.cover_image_url:
            return obj.cover_image_url
        
        # 如果没有URL，尝试使用ImageField
        if not obj.cover_image:
            return None
        
        # 尝试获取cover_image的值（可能是ImageField或字符串）
        try:
            # 如果是ImageField，尝试获取URL
            if hasattr(obj.cover_image, 'url'):
                image_url = obj.cover_image.url
            else:
                # 否则转换为字符串
                image_url = str(obj.cover_image)
        except (ValueError, AttributeError):
            # 如果获取失败，使用字符串值
            image_url = str(obj.cover_image) if obj.cover_image else None
        
        if not image_url:
            return None
        
        # 如果已经是完整URL，直接返回
        if image_url.startswith('http://') or image_url.startswith('https://'):
            return image_url
        
        # 构建绝对URL
        request = self.context.get('request')
        if request:
            # 如果image_url已经是绝对路径（以/开头），直接构建
            if image_url.startswith('/'):
                return request.build_absolute_uri(image_url)
            else:
                # 否则使用MEDIA_URL
                return request.build_absolute_uri(settings.MEDIA_URL + image_url)
        
        # 如果没有request上下文，使用settings中的信息
        if image_url.startswith('/'):
            return image_url
        return f"{settings.MEDIA_URL}{image_url}" if image_url else None


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """文章创建/更新序列化器"""
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=30),
        write_only=True,
        required=False,
        help_text='标签名称列表'
    )
    cover_image = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'summary', 'cover_image', 'category', 
            'status', 'is_top', 'is_recommend', 'tag_names'
        ]
    
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        cover_image = validated_data.pop('cover_image', None)
        
        # 处理封面图片：如果是URL字符串，保存到cover_image_url字段
        if cover_image:
            if cover_image.startswith('http://') or cover_image.startswith('https://'):
                # 如果是URL，保存到cover_image_url字段
                validated_data['cover_image_url'] = cover_image
                validated_data['cover_image'] = None
            else:
                # 否则保存到cover_image字段（文件路径）
                validated_data['cover_image'] = cover_image
                validated_data['cover_image_url'] = ''
        else:
            validated_data['cover_image'] = None
            validated_data['cover_image_url'] = ''
        
        article = Article.objects.create(**validated_data)
        
        # 处理标签
        self._handle_tags(article, tag_names)
        return article
    
    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        cover_image = validated_data.pop('cover_image', None)
        
        # 处理封面图片
        if cover_image is not None:
            if cover_image and (cover_image.startswith('http://') or cover_image.startswith('https://')):
                # 如果是URL，保存到cover_image_url字段
                validated_data['cover_image_url'] = cover_image
                validated_data['cover_image'] = None  # 清空ImageField
            elif cover_image:
                # 如果是文件路径，保存到cover_image字段
                validated_data['cover_image'] = cover_image
                validated_data['cover_image_url'] = ''  # 清空URL字段
            else:
                # 如果为空，清空两个字段
                validated_data['cover_image'] = None
                validated_data['cover_image_url'] = ''
        
        # 更新文章基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理标签
        if tag_names is not None:
            self._handle_tags(instance, tag_names)
        
        return instance
    
    def _handle_tags(self, article, tag_names):
        """处理文章标签"""
        # 清除现有标签关联
        ArticleTag.objects.filter(article=article).delete()
        
        # 添加新标签
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            ArticleTag.objects.create(article=article, tag=tag)
            
            # 更新标签使用次数
            if created:
                tag.use_count = 1
            else:
                tag.use_count += 1
            tag.save()


class ArticleSearchSerializer(serializers.Serializer):
    """文章搜索序列化器"""
    keyword = serializers.CharField(required=False, help_text='搜索关键词')
    category_id = serializers.IntegerField(required=False, help_text='分类ID')
    tag_id = serializers.IntegerField(required=False, help_text='标签ID')
    author_id = serializers.IntegerField(required=False, help_text='作者ID')
    is_recommend = serializers.BooleanField(required=False, help_text='是否推荐')
    ordering = serializers.ChoiceField(
        choices=[
            ('-published_at', '发布时间倒序'),
            ('published_at', '发布时间正序'),
            ('-view_count', '浏览量倒序'),
            ('-like_count', '点赞数倒序'),
            ('-comment_count', '评论数倒序'),
        ],
        default='-published_at',
        help_text='排序方式'
    )
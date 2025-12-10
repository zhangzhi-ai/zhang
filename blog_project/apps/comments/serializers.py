from rest_framework import serializers
from .models import Comment
from apps.users.serializers import UserProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    user = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user', 'parent', 'like_count', 
            'created_at', 'updated_at', 'replies', 'is_liked', 'article'
        ]
        read_only_fields = ['id', 'user', 'like_count', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """获取回复列表"""
        if obj.parent is None:  # 只有顶级评论才显示回复
            replies = obj.get_replies()
            return CommentReplySerializer(replies, many=True, context=self.context).data
        return []
    
    def get_is_liked(self, obj):
        """当前用户是否点赞了该评论"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.users.models import UserLike
            return UserLike.objects.filter(
                user=request.user,
                target_type=2,  # 评论
                target_id=obj.id
            ).exists()
        return False
    
    def get_article(self, obj):
        return {
            'id': obj.article_id,
            'title': obj.article.title
        }


class CommentReplySerializer(serializers.ModelSerializer):
    """评论回复序列化器（简化版，不包含嵌套回复）"""
    user = UserProfileSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user', 'parent', 'like_count', 
            'created_at', 'is_liked'
        ]
    
    def get_is_liked(self, obj):
        """当前用户是否点赞了该评论"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.users.models import UserLike
            return UserLike.objects.filter(
                user=request.user,
                target_type=2,  # 评论
                target_id=obj.id
            ).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    
    class Meta:
        model = Comment
        fields = ['content', 'article', 'parent']
    
    def validate_parent(self, value):
        """验证父评论"""
        if value:
            # 确保父评论存在且属于同一篇文章
            article_id = self.initial_data.get('article')
            if value.article_id != int(article_id):
                raise serializers.ValidationError("回复的评论不属于当前文章")
            if value.status != 1:
                raise serializers.ValidationError("无法回复已删除的评论")
        return value
    
    def create(self, validated_data):
        # 获取请求信息
        request = self.context['request']
        validated_data['user'] = request.user
        
        # 获取IP地址和用户代理
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            validated_data['ip_address'] = x_forwarded_for.split(',')[0]
        else:
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)
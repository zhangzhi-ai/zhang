from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from apps.blog.models import Article


class CommentListView(generics.ListAPIView):
    """评论列表"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        # 只返回顶级评论（非回复），回复通过序列化器中的replies字段获取
        return Comment.objects.filter(
            article_id=article_id,
            status=1,
            parent__isnull=True
        ).select_related('user', 'article').order_by('-created_at')


class CommentCreateView(generics.CreateAPIView):
    """创建评论"""
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # 检查用户是否登录
        if not request.user.is_authenticated:
            return Response({
                'message': '请先登录后再发表评论',
                'code': 'login_required'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    def create(self, request, *args, **kwargs):
        # 验证文章是否存在
        article_id = kwargs.get('article_id')
        article = get_object_or_404(Article, id=article_id, status=1)
        
        # 添加文章ID到请求数据
        data = request.data.copy()
        data['article'] = article_id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        # 返回创建的评论详情
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(generics.DestroyAPIView):
    """删除评论"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # 软删除：将状态设为已删除
        instance.status = 0
        instance.save()
        
        # 更新文章评论数
        instance.article.comment_count = max(0, instance.article.comment_count - 1)
        instance.article.save(update_fields=['comment_count'])


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def comment_like_view(request, comment_id):
    """评论点赞/取消点赞"""
    from apps.users.models import UserLike
    
    comment = get_object_or_404(Comment, id=comment_id, status=1)
    user = request.user
    
    like_obj, created = UserLike.objects.get_or_create(
        user=user,
        target_type=2,  # 评论
        target_id=comment_id
    )
    
    if created:
        # 点赞
        comment.like_count += 1
        comment.save(update_fields=['like_count'])
        message = '点赞成功'
        is_liked = True
    else:
        # 取消点赞
        like_obj.delete()
        comment.like_count = max(0, comment.like_count - 1)
        comment.save(update_fields=['like_count'])
        message = '取消点赞'
        is_liked = False
    
    return Response({
        'message': message,
        'is_liked': is_liked,
        'like_count': comment.like_count
    })


class MyCommentListView(generics.ListAPIView):
    """我的评论列表"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(
            user=self.request.user,
            status=1
        ).select_related('user', 'article').order_by('-created_at')
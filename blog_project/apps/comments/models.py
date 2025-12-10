from django.db import models
from django.conf import settings


class Comment(models.Model):
    """评论模型"""
    STATUS_CHOICES = [
        (0, '已删除'),
        (1, '正常'),
        (2, '待审核'),
    ]
    
    content = models.TextField('评论内容')
    article = models.ForeignKey(
        'blog.Article', 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='文章'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='评论用户'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    like_count = models.PositiveIntegerField('点赞数', default=0)
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=1)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('用户代理', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'comments'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'
    
    def get_replies(self):
        """获取回复列表"""
        return self.replies.filter(status=1).order_by('created_at')
    
    def is_reply(self):
        """是否为回复"""
        return self.parent is not None
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 新评论时更新文章评论数
        if is_new and self.status == 1:
            self.article.comment_count += 1
            self.article.save(update_fields=['comment_count'])
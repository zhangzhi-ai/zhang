from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """用户模型"""
    GENDER_CHOICES = [
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    ]
    
    phone = models.CharField('手机号', max_length=11, unique=True)
    avatar = models.ImageField('头像', upload_to='avatars/', default='avatars/default.jpg')
    nickname = models.CharField('昵称', max_length=50, blank=True, default='')
    bio = models.TextField('个人简介', blank=True, default='')
    gender = models.SmallIntegerField('性别', choices=GENDER_CHOICES, default=0)
    birthday = models.DateField('生日', null=True, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        
    def __str__(self):
        return self.username
    
    @property
    def display_name(self):
        """显示名称：优先显示昵称，否则显示用户名"""
        return self.nickname or self.username
    
    def get_article_count(self):
        """获取用户发布的文章数量"""
        return self.articles.filter(status=1).count()
    
    def get_comment_count(self):
        """获取用户的评论数量"""
        return self.comments.filter(status=1).count()


class UserLike(models.Model):
    """用户点赞记录"""
    TARGET_TYPE_CHOICES = [
        (1, '文章'),
        (2, '评论'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    target_type = models.SmallIntegerField('目标类型', choices=TARGET_TYPE_CHOICES)
    target_id = models.PositiveIntegerField('目标ID')
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)
    
    class Meta:
        db_table = 'user_likes'
        verbose_name = '用户点赞记录'
        verbose_name_plural = '用户点赞记录'
        unique_together = ['user', 'target_type', 'target_id']
        
    def __str__(self):
        return f'{self.user.username} 点赞了 {self.get_target_type_display()}'
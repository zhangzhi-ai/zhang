from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """文章分类"""
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('分类描述', blank=True)
    sort_order = models.IntegerField('排序号', default=0, help_text='数字越小越靠前')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'
        ordering = ['sort_order', 'id']
        
    def __str__(self):
        return self.name
    
    def get_article_count(self):
        """获取分类下的文章数量"""
        return self.articles.filter(status=1).count()


class Tag(models.Model):
    """标签"""
    name = models.CharField('标签名称', max_length=30, unique=True)
    color = models.CharField('标签颜色', max_length=7, default='#007bff', help_text='十六进制颜色值')
    use_count = models.IntegerField('使用次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['-use_count', 'id']
        
    def __str__(self):
        return self.name


class Article(models.Model):
    """文章"""
    STATUS_CHOICES = [
        (0, '草稿'),
        (1, '已发布'),
        (2, '已删除'),
    ]
    
    title = models.CharField('文章标题', max_length=200)
    content = models.TextField('文章内容')
    summary = models.TextField('文章摘要', blank=True)
    cover_image = models.ImageField('封面图片', upload_to='articles/', blank=True)
    cover_image_url = models.CharField('封面图片URL', max_length=500, blank=True, help_text='外部图片URL或上传后的完整URL')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='articles',
        verbose_name='作者'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='articles',
        verbose_name='分类'
    )
    tags = models.ManyToManyField(Tag, through='ArticleTag', verbose_name='标签')
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=0)
    is_top = models.BooleanField('是否置顶', default=False)
    is_recommend = models.BooleanField('是否推荐', default=False)
    view_count = models.PositiveIntegerField('浏览量', default=0)
    like_count = models.PositiveIntegerField('点赞数', default=0)
    comment_count = models.PositiveIntegerField('评论数', default=0)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'articles'
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-is_top', '-published_at', '-created_at']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 如果状态从非发布改为发布，设置发布时间
        if self.status == 1 and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'id': self.id})
    
    def increase_view_count(self):
        """增加浏览量"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_tag_list(self):
        """获取标签列表"""
        return list(self.tags.values_list('name', flat=True))


class ArticleTag(models.Model):
    """文章标签关联"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'article_tags'
        verbose_name = '文章标签关联'
        verbose_name_plural = '文章标签关联'
        unique_together = ['article', 'tag']
        
    def __str__(self):
        return f'{self.article.title} - {self.tag.name}'
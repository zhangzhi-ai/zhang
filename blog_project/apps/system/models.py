from django.db import models
from django.conf import settings
import json


class SystemConfig(models.Model):
    """系统配置"""
    CONFIG_TYPE_CHOICES = [
        ('string', '字符串'),
        ('int', '整数'),
        ('bool', '布尔值'),
        ('json', 'JSON'),
    ]
    
    config_key = models.CharField('配置键', max_length=100, unique=True)
    config_value = models.TextField('配置值', blank=True)
    config_type = models.CharField('配置类型', max_length=20, choices=CONFIG_TYPE_CHOICES, default='string')
    description = models.CharField('配置描述', max_length=255, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        
    def __str__(self):
        return f'{self.config_key}: {self.config_value}'
    
    def get_value(self):
        """获取配置值（根据类型转换）"""
        if not self.is_active:
            return None
            
        if self.config_type == 'int':
            try:
                return int(self.config_value)
            except (ValueError, TypeError):
                return 0
        elif self.config_type == 'bool':
            return self.config_value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'json':
            try:
                return json.loads(self.config_value)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:
            return self.config_value
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(config_key=key, is_active=True)
            return config.get_value()
        except cls.DoesNotExist:
            return default


class AccessLog(models.Model):
    """访问日志"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='用户'
    )
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    request_url = models.CharField('请求URL', max_length=500)
    request_method = models.CharField('请求方法', max_length=10, default='GET')
    response_status = models.IntegerField('响应状态码', default=200)
    response_time = models.IntegerField('响应时间（毫秒）', default=0)
    referer = models.CharField('来源页面', max_length=500, blank=True)
    created_at = models.DateTimeField('访问时间', auto_now_add=True)
    
    class Meta:
        db_table = 'access_logs'
        verbose_name = '访问日志'
        verbose_name_plural = '访问日志'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.ip_address} - {self.request_url}'
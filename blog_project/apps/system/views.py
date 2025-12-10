from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SystemConfig


@api_view(['GET'])
@permission_classes([AllowAny])
def site_config_view(request):
    """获取网站配置信息"""
    configs = {
        'site_name': SystemConfig.get_config('site_name', '个人博客系统'),
        'site_description': SystemConfig.get_config('site_description', '专注于个人内容分享的博客系统'),
        'site_keywords': SystemConfig.get_config('site_keywords', 'Python,Django,Vue.js,Web开发'),
        'allow_register': SystemConfig.get_config('allow_register', True),
        'comment_need_audit': SystemConfig.get_config('comment_need_audit', False),
    }
    
    return Response(configs)
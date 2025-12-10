import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

import django
django.setup()

from apps.system.models import SystemConfig

def update_site_config():
    """更新网站配置信息"""
    print("开始更新网站配置...")
    
    # 更新网站名称
    try:
        # 尝试获取现有配置
        site_name_config, created = SystemConfig.objects.get_or_create(
            config_key='site_name',
            defaults={
                'config_value': '个人博客系统',
                'config_type': 'string',
                'description': '网站名称',
                'is_active': True
            }
        )
        
        if not created:
            # 如果配置已存在，更新值
            site_name_config.config_value = '个人博客系统'
            site_name_config.save()
            print(f"已更新网站名称配置: {site_name_config.config_value}")
        else:
            print(f"已创建网站名称配置: {site_name_config.config_value}")
    except Exception as e:
        print(f"更新网站名称失败: {e}")
    
    # 更新网站描述
    try:
        site_desc_config, created = SystemConfig.objects.get_or_create(
            config_key='site_description',
            defaults={
                'config_value': '专注于个人内容分享的博客系统',
                'config_type': 'string',
                'description': '网站描述',
                'is_active': True
            }
        )
        
        if not created:
            site_desc_config.config_value = '专注于个人内容分享的博客系统'
            site_desc_config.save()
            print(f"已更新网站描述配置: {site_desc_config.config_value}")
        else:
            print(f"已创建网站描述配置: {site_desc_config.config_value}")
    except Exception as e:
        print(f"更新网站描述失败: {e}")
    
    print("网站配置更新完成！")

if __name__ == '__main__':
    update_site_config()
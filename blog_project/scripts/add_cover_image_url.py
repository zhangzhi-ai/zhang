#!/usr/bin/env python
"""
手动添加 cover_image_url 字段到 articles 表
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from django.db import connection

def add_cover_image_url_column():
    """添加 cover_image_url 字段"""
    with connection.cursor() as cursor:
        try:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'articles' 
                AND COLUMN_NAME = 'cover_image_url'
            """)
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                print("字段 cover_image_url 已存在，跳过添加")
                return
            
            # 添加字段
            cursor.execute("""
                ALTER TABLE articles 
                ADD COLUMN cover_image_url VARCHAR(500) DEFAULT '' 
                COMMENT '封面图片URL或上传后的完整URL'
            """)
            print("成功添加 cover_image_url 字段到 articles 表")
        except Exception as e:
            print(f"添加字段时出错: {e}")
            # 如果是字段已存在的错误，忽略
            if 'Duplicate column name' not in str(e):
                raise

if __name__ == '__main__':
    add_cover_image_url_column()


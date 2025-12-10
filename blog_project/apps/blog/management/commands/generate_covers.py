from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.blog.models import Article
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os


class Command(BaseCommand):
    help = '为没有封面的文章生成封面图片'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制为所有文章重新生成封面',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write('开始生成文章封面...')
        
        # 获取需要生成封面的文章
        if force:
            articles = Article.objects.all()
            self.stdout.write(f'强制模式：为所有 {articles.count()} 篇文章生成封面')
        else:
            articles = Article.objects.filter(cover_image='')
            self.stdout.write(f'为 {articles.count()} 篇没有封面的文章生成封面')
        
        if articles.count() == 0:
            self.stdout.write(self.style.SUCCESS('没有需要生成封面的文章'))
            return
        
        # 定义颜色方案
        color_schemes = [
            {'bg': '#667eea', 'text': '#ffffff'},  # 紫色
            {'bg': '#f093fb', 'text': '#ffffff'},  # 粉色
            {'bg': '#4facfe', 'text': '#ffffff'},  # 蓝色
            {'bg': '#43e97b', 'text': '#ffffff'},  # 绿色
            {'bg': '#fa709a', 'text': '#ffffff'},  # 红粉色
            {'bg': '#30cfd0', 'text': '#ffffff'},  # 青色
            {'bg': '#a8edea', 'text': '#333333'},  # 浅青色
            {'bg': '#ffd89b', 'text': '#333333'},  # 橙色
        ]
        
        success_count = 0
        error_count = 0
        
        for index, article in enumerate(articles):
            try:
                # 选择颜色方案
                color_scheme = color_schemes[index % len(color_schemes)]
                
                # 生成封面图片
                cover_image = self.generate_cover_image(
                    article.title,
                    article.category.name if article.category else '未分类',
                    color_scheme
                )
                
                # 保存图片
                filename = f'cover_{article.id}.png'
                article.cover_image.save(
                    filename,
                    ContentFile(cover_image),
                    save=True
                )
                
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ [{success_count}/{articles.count()}] {article.title}')
                )
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ 生成封面失败: {article.title} - {str(e)}')
                )
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'完成！成功: {success_count}, 失败: {error_count}'))

    def generate_cover_image(self, title, category, color_scheme):
        """生成封面图片"""
        # 图片尺寸
        width = 1200
        height = 630
        
        # 创建图片
        image = Image.new('RGB', (width, height), color_scheme['bg'])
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            # Windows系统字体路径
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
            ]
            
            title_font = None
            category_font = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    title_font = ImageFont.truetype(font_path, 60)
                    category_font = ImageFont.truetype(font_path, 30)
                    break
            
            if not title_font:
                # 如果找不到字体，使用默认字体
                title_font = ImageFont.load_default()
                category_font = ImageFont.load_default()
                
        except Exception as e:
            # 使用默认字体
            title_font = ImageFont.load_default()
            category_font = ImageFont.load_default()
        
        # 绘制分类标签
        category_text = f'# {category}'
        category_bbox = draw.textbbox((0, 0), category_text, font=category_font)
        category_width = category_bbox[2] - category_bbox[0]
        category_x = (width - category_width) // 2
        draw.text((category_x, 100), category_text, fill=color_scheme['text'], font=category_font)
        
        # 处理标题文本（自动换行）
        max_chars_per_line = 20
        if len(title) > max_chars_per_line:
            # 简单的换行处理
            lines = []
            current_line = ''
            for char in title:
                if len(current_line) >= max_chars_per_line:
                    lines.append(current_line)
                    current_line = char
                else:
                    current_line += char
            if current_line:
                lines.append(current_line)
            title_text = '\n'.join(lines[:3])  # 最多3行
        else:
            title_text = title
        
        # 绘制标题
        title_lines = title_text.split('\n')
        y_offset = 250
        line_height = 80
        
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, y_offset), line, fill=color_scheme['text'], font=title_font)
            y_offset += line_height
        
        # 添加装饰线
        line_y = height - 100
        line_margin = 200
        draw.line(
            [(line_margin, line_y), (width - line_margin, line_y)],
            fill=color_scheme['text'],
            width=3
        )
        
        # 保存到字节流
        img_io = io.BytesIO()
        image.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        return img_io.read()

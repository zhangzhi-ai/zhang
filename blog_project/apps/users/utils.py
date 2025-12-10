"""
验证码工具类
"""
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.cache import cache
from django.conf import settings
import hashlib
import time


def generate_captcha_code(length=4):
    """生成验证码字符串"""
    # 使用数字和大小写字母，排除容易混淆的字符
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(length))


def generate_captcha_image(code):
    """生成验证码图片"""
    # 图片尺寸
    width, height = 120, 40
    
    # 创建图片
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255)), width=1)
    
    # 绘制干扰点
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
    
    # 绘制验证码文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
    
    # 计算文字位置
    char_width = width // len(code)
    for i, char in enumerate(code):
        x = char_width * i + random.randint(5, 10)
        y = random.randint(5, 10)
        # 随机颜色
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, font=font, fill=color)
    
    # 保存到BytesIO
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def generate_sms_code(length=6):
    """生成短信验证码"""
    return ''.join(random.choice(string.digits) for _ in range(length))


def save_captcha_code(key, code, timeout=300):
    """保存验证码到缓存（5分钟过期）"""
    cache.set(f'captcha_{key}', code.lower(), timeout)


def verify_captcha_code(key, code):
    """验证图片验证码"""
    if not key or not code:
        return False
    cached_code = cache.get(f'captcha_{key}')
    if not cached_code:
        return False
    return cached_code.lower() == code.lower()


def save_sms_code(phone, code, timeout=300):
    """保存短信验证码到缓存（5分钟过期）"""
    cache.set(f'sms_{phone}', code, timeout)
    # 同时记录发送时间，防止频繁发送
    cache.set(f'sms_time_{phone}', time.time(), timeout)


def verify_sms_code(phone, code):
    """验证短信验证码"""
    if not phone or not code:
        return False
    cached_code = cache.get(f'sms_{phone}')
    if not cached_code:
        return False
    return cached_code == code


def can_send_sms(phone, interval=60):
    """检查是否可以发送短信（防止频繁发送，默认60秒间隔）"""
    last_send_time = cache.get(f'sms_time_{phone}')
    if last_send_time:
        elapsed = time.time() - last_send_time
        if elapsed < interval:
            return False, int(interval - elapsed)
    return True, 0


def send_sms_code(phone, code):
    """
    发送短信验证码
    这里使用模拟发送，实际项目中需要接入短信服务商API（如阿里云、腾讯云等）
    """
    # TODO: 接入真实的短信服务
    # 示例：使用阿里云短信服务
    # from aliyunsdkcore.client import AcsClient
    # from aliyunsdkcore.request import CommonRequest
    # ...
    
    # 开发环境：打印到控制台
    print(f'[短信验证码] 手机号: {phone}, 验证码: {code} (有效期5分钟)')
    return True


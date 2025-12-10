"""
验证码相关视图
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from .utils import (
    generate_captcha_code, generate_captcha_image,
    save_captcha_code, verify_captcha_code,
    generate_sms_code, save_sms_code, verify_sms_code,
    can_send_sms, send_sms_code
)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def captcha_image_view(request):
    """生成图片验证码"""
    # 生成验证码
    code = generate_captcha_code(4)
    
    # 生成唯一key
    key = get_random_string(32)
    
    # 保存验证码到缓存
    save_captcha_code(key, code)
    
    # 生成图片
    image_buffer = generate_captcha_image(code)
    
    # 返回图片和key
    response = HttpResponse(image_buffer.getvalue(), content_type='image/png')
    response['X-Captcha-Key'] = key
    return response


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_sms_code_view(request):
    """发送短信验证码"""
    phone = request.data.get('phone')
    captcha_key = request.data.get('captcha_key')
    captcha_code = request.data.get('captcha_code')
    
    if not phone:
        return Response({'message': '请输入手机号'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证手机号格式
    import re
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return Response({'message': '手机号格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证图片验证码
    if not captcha_key or not captcha_code:
        return Response({'message': '请先完成图片验证码验证'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not verify_captcha_code(captcha_key, captcha_code):
        return Response({'message': '图片验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查发送频率
    can_send, wait_time = can_send_sms(phone, interval=60)
    if not can_send:
        return Response({
            'message': f'发送过于频繁，请{wait_time}秒后再试'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 生成短信验证码
    sms_code = generate_sms_code(6)
    
    # 保存验证码
    save_sms_code(phone, sms_code)
    
    # 发送短信
    try:
        send_sms_code(phone, sms_code)
        return Response({
            'message': '验证码已发送',
            'code': sms_code  # 开发环境返回验证码，生产环境应移除
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': f'发送失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_sms_code_view(request):
    """验证短信验证码"""
    phone = request.data.get('phone')
    code = request.data.get('code')
    
    if not phone or not code:
        return Response({'message': '请输入手机号和验证码'}, status=status.HTTP_400_BAD_REQUEST)
    
    if verify_sms_code(phone, code):
        return Response({'message': '验证成功'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)


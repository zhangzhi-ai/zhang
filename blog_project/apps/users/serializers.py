from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
# 保留图片验证码，注释掉短信验证码
from .utils import verify_captcha_code  # , verify_sms_code


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器（保留图片验证码，移除短信验证码）"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    captcha_key = serializers.CharField(write_only=True, required=True)
    captcha_code = serializers.CharField(write_only=True, required=True)
    # sms_code = serializers.CharField(write_only=True, required=False)  # 已注释
    
    class Meta:
        model = User
        fields = ['username', 'phone', 'password', 'password_confirm', 'email', 'nickname', 
                  'captcha_key', 'captcha_code']  # 移除 'sms_code'
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次密码输入不一致")
        
        # 验证图片验证码（保留）
        captcha_key = attrs.get('captcha_key')
        captcha_code = attrs.get('captcha_code')
        if not captcha_key or not captcha_code:
            raise serializers.ValidationError("请完成图片验证码验证")
        if not verify_captcha_code(captcha_key, captcha_code):
            raise serializers.ValidationError("图片验证码错误或已过期")
        
        # 注释掉短信验证码验证
        # phone = attrs.get('phone')
        # sms_code = attrs.get('sms_code')
        # if not sms_code:
        #     raise serializers.ValidationError("请输入短信验证码")
        # if not verify_sms_code(phone, sms_code):
        #     raise serializers.ValidationError("短信验证码错误或已过期")
        
        return attrs
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被注册")
        return value
    
    def create(self, validated_data):
        # 移除验证码相关字段
        validated_data.pop('password_confirm')
        validated_data.pop('captcha_key', None)
        validated_data.pop('captcha_code', None)
        # validated_data.pop('sms_code', None)  # 已移除
        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("请输入用户名和密码")
        
        user_obj = None
        
        # 支持用户名或手机号登录
        if username.isdigit():
            # 手机号登录
            try:
                user_obj = User.objects.get(phone=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("手机号或密码错误")
        else:
            # 用户名登录
            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("用户名或密码错误")
            
            # 兼容明文密码数据（例如通过SQL脚本初始化的默认账号）
            if user_obj and '$' not in user_obj.password:
                if user_obj.password == password:
                    user_obj.set_password(password)
                    user_obj.save(update_fields=['password'])
                    user = authenticate(username=user_obj.username, password=password)
                    if user:
                        attrs['user'] = user
                        return attrs

        # 先检查用户是否被禁用
        if not user_obj.is_active:
            raise serializers.ValidationError("账户已被禁用，请联系管理员")
        
        # 验证密码
        if not user_obj.check_password(password):
            raise serializers.ValidationError("用户名或密码错误")
        
        # 使用authenticate进行最终验证
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError("登录失败，请重试")
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    article_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email', 'nickname', 'bio', 
            'avatar', 'gender', 'birthday', 'is_staff', 'is_active', 'date_joined',
            'article_count', 'comment_count'
        ]
        read_only_fields = ['id', 'username', 'is_staff', 'date_joined']
    
    def get_avatar(self, obj):
        """返回头像的绝对URL"""
        if not obj.avatar:
            return None
        
        # 尝试获取avatar的URL
        try:
            if hasattr(obj.avatar, 'url'):
                avatar_url = obj.avatar.url
            else:
                avatar_url = str(obj.avatar)
        except (ValueError, AttributeError):
            avatar_url = str(obj.avatar) if obj.avatar else None
        
        if not avatar_url:
            return None
        
        # 如果已经是完整URL，直接返回
        if avatar_url.startswith('http://') or avatar_url.startswith('https://'):
            return avatar_url
        
        # 构建绝对URL
        request = self.context.get('request')
        if request:
            if avatar_url.startswith('/'):
                return request.build_absolute_uri(avatar_url)
            else:
                from django.conf import settings
                return request.build_absolute_uri(settings.MEDIA_URL + avatar_url)
        
        # 如果没有request上下文，使用settings中的信息
        from django.conf import settings
        if avatar_url.startswith('/'):
            return avatar_url
        return f"{settings.MEDIA_URL}{avatar_url}" if avatar_url else None
    
    def get_article_count(self, obj):
        try:
            return obj.get_article_count()
        except Exception:
            return 0
    
    def get_comment_count(self, obj):
        try:
            return obj.get_comment_count()
        except Exception:
            return 0


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    
    class Meta:
        model = User
        fields = ['nickname', 'bio', 'email', 'gender', 'birthday', 'avatar', 'phone']
        
    def validate_email(self, value):
        user = self.instance
        if value and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被使用")
        return value
    
    def validate_phone(self, value):
        user = self.instance
        if value and User.objects.exclude(pk=user.pk).filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被使用")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码错误")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("两次新密码输入不一致")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
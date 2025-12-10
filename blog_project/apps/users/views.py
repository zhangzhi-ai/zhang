from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from urllib.parse import urljoin
import os
from .models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserProfileSerializer, UserUpdateSerializer, PasswordChangeSerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': '注册成功',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        profile_serializer = UserProfileSerializer(user, context={'request': request})
        return Response({
            'message': '登录成功',
            'user': profile_serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def logout_view(request):
    """用户退出登录"""
    logout(request)
    return Response({'message': '退出登录成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user_view(request):
    """获取当前用户信息"""
    if request.user.is_authenticated:
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    return Response({'message': '用户未登录'}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料查看和更新"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """修改密码"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '密码修改成功'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    """用户详情（公开信息）"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['public_view'] = True
        return context


# ========== 用户管理功能（仅管理员） ==========

class IsAdminUser(permissions.BasePermission):
    """管理员权限"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class UserManagementListView(generics.ListAPIView):
    """用户管理列表（仅管理员）"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # 禁用分页，返回所有数据
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 支持搜索
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(phone__icontains=search) | 
                Q(email__icontains=search) |
                Q(nickname__icontains=search)
            )
        
        # 支持状态筛选（只有明确传递参数时才筛选）
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None and is_active != '':
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 支持用户类型筛选（只有明确传递参数时才筛选）
        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None and is_staff != '':
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        return queryset


class UserManagementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户管理详情（仅管理员）"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    
    def perform_destroy(self, instance):
        # 软删除：禁用用户而不是真正删除
        instance.is_active = False
        instance.save()


@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_user_status_view(request, user_id):
    """切换用户状态（启用/禁用）"""
    try:
        user = User.objects.get(id=user_id)
        
        # 不能禁用自己
        if user.id == request.user.id:
            return Response({
                'message': '不能禁用自己的账号'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'用户已{"启用" if user.is_active else "禁用"}',
            'is_active': user.is_active
        })
    except User.DoesNotExist:
        return Response({
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reset_user_password_view(request, user_id):
    """重置用户密码"""
    try:
        user = User.objects.get(id=user_id)
        
        # 不能重置自己的密码
        if user.id == request.user.id:
            return Response({
                'message': '不能重置自己的密码，请使用修改密码功能'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 重置密码为123456
        user.set_password('123456')
        user.save()
        
        return Response({
            'message': f'用户 {user.username} 的密码已重置为：123456'
        })
    except User.DoesNotExist:
        return Response({
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_statistics_view(request):
    """用户统计信息（仅管理员）"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # 最近30天新增用户
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # 最近7天活跃用户（有登录记录）
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_users_7d = User.objects.filter(last_login__gte=seven_days_ago).count()
    
    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'staff_users': staff_users,
        'new_users_30d': new_users_30d,
        'active_users_7d': active_users_7d
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def avatar_upload_view(request):
    """上传并更新头像"""
    file_obj = request.FILES.get('avatar')
    if not file_obj:
        return Response({'message': '请上传头像文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    ext = os.path.splitext(file_obj.name)[1] or '.jpg'
    filename = timezone.now().strftime('avatars/%Y/%m/%d/%H%M%S')
    filename = f"{filename}_{get_random_string(6)}{ext}"
    
    saved_path = default_storage.save(filename, file_obj)
    request.user.avatar = saved_path
    request.user.save(update_fields=['avatar'])
    
    serializer = UserProfileSerializer(request.user, context={'request': request})
    avatar_url = serializer.data.get('avatar')
    
    return Response({
        'message': '上传成功',
        'url': avatar_url
    }, status=status.HTTP_200_OK)
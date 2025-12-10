from django.urls import path
from . import views
from . import captcha_views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('current/', views.current_user_view, name='current_user'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('avatar/upload/', views.avatar_upload_view, name='avatar_upload'),
    path('<int:id>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # 用户管理（仅管理员）
    path('management/', views.UserManagementListView.as_view(), name='user_management_list'),
    path('management/<int:id>/', views.UserManagementDetailView.as_view(), name='user_management_detail'),
    path('management/<int:user_id>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
    path('management/<int:user_id>/reset-password/', views.reset_user_password_view, name='reset_user_password'),
    path('management/statistics/', views.user_statistics_view, name='user_statistics'),
    
    # 验证码相关（保留图片验证码，注释掉短信验证码）
    path('captcha/image/', captcha_views.captcha_image_view, name='captcha_image'),
    # path('sms/send/', captcha_views.send_sms_code_view, name='send_sms_code'),
    # path('sms/verify/', captcha_views.verify_sms_code_view, name='verify_sms_code'),
]
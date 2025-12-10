"""
URL configuration for blog_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/users/', include('apps.users.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/comments/', include('apps.comments.urls')),
    path('api/system/', include('apps.system.urls')),
    
    # Frontend URLs (Vue.js SPA)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('article/<int:id>/', TemplateView.as_view(template_name='index.html'), name='article_detail'),
    path('category/<str:name>/', TemplateView.as_view(template_name='index.html'), name='category'),
    path('user/', TemplateView.as_view(template_name='index.html'), name='user_center'),
    path('write/', TemplateView.as_view(template_name='index.html'), name='write_article'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
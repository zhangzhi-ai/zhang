from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('config/', views.site_config_view, name='site_config'),
]
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # 分类和标签
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    
    # 分类管理（仅管理员）
    path('categories/manage/', views.CategoryManageListView.as_view(), name='category_manage_list'),
    path('categories/manage/<int:id>/', views.CategoryManageDetailView.as_view(), name='category_manage_detail'),
    
    # 文章
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/my/', views.MyArticleListView.as_view(), name='my_articles'),
    path('articles/recommend/', views.article_recommend_view, name='article_recommend'),
    path('articles/hot/', views.article_hot_view, name='article_hot'),
    path('articles/cover/upload/', views.article_cover_upload_view, name='article_cover_upload'),
    path('articles/<int:id>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:id>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:id>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<int:article_id>/like/', views.article_like_view, name='article_like'),
    
    # 统计
    path('statistics/', views.statistics_view, name='statistics'),
]
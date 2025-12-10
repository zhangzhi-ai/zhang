from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('articles/<int:article_id>/', views.CommentListView.as_view(), name='comment_list'),
    path('articles/<int:article_id>/create/', views.CommentCreateView.as_view(), name='comment_create'),
    path('<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('<int:comment_id>/like/', views.comment_like_view, name='comment_like'),
    path('my/', views.MyCommentListView.as_view(), name='my_comments'),
]
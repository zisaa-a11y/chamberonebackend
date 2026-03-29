from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    TagListCreateView,
    TagDetailView,
    BlogPostListView,
    BlogPostCreateView,
    BlogPostDetailView,
    BlogPostAdminDetailView,
    BlogPostAdminListView,
    CommentListCreateView,
    CommentDetailView,
    CommentApproveView,
    FeaturedPostsView,
)

app_name = 'blog'

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Tags
    path('tags/', TagListCreateView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
    
    # Posts (public GET, admin POST for create)
    path('posts/', BlogPostListView.as_view(), name='post_list'),
    path('posts/create/', BlogPostCreateView.as_view(), name='post_create'),
    path('posts/featured/', FeaturedPostsView.as_view(), name='featured_posts'),
    path('posts/<slug:slug>/', BlogPostDetailView.as_view(), name='post_detail'),
    
    # Posts (admin)
    path('admin/posts/', BlogPostAdminListView.as_view(), name='admin_post_list'),
    path('admin/posts/create/', BlogPostCreateView.as_view(), name='admin_post_create'),
    path('admin/posts/<slug:slug>/', BlogPostAdminDetailView.as_view(), name='admin_post_detail'),
    
    # Comments
    path('posts/<slug:post_slug>/comments/', CommentListCreateView.as_view(), name='post_comments'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('comments/<int:pk>/approve/', CommentApproveView.as_view(), name='comment_approve'),
]

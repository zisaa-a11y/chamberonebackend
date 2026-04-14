from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import F

from .models import Category, Tag, BlogPost, Comment
from .serializers import (
    CategorySerializer,
    TagSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostCreateSerializer,
    CommentSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for everyone, write only for admins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for category detail."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Tag Views
class TagListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for tag detail."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Blog Post Views
class BlogPostListView(generics.ListCreateAPIView):
    """API endpoint to list published blog posts (GET) and create new posts (POST, admin only)."""
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt', 'category__name', 'tags__name']
    ordering_fields = ['published_date', 'views_count', 'created_at']
    ordering = ['-published_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BlogPostCreateSerializer
        return BlogPostListSerializer

    def get_queryset(self):
        queryset = BlogPost.objects.select_related('author', 'category').prefetch_related('tags')

        include_unpublished = (
            self.request.query_params.get('include_unpublished', '').lower() == 'true'
        )
        if include_unpublished and self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(status=BlogPost.Status.PUBLISHED)
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Featured posts only
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset


class BlogPostWriteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for backend writes by post id."""
    permission_classes = [permissions.IsAdminUser]
    queryset = BlogPost.objects.all().select_related('author', 'category').prefetch_related('tags', 'comments')
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BlogPostCreateSerializer
        return BlogPostSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {'success': True, 'detail': 'Blog post deleted successfully.'},
            status=status.HTTP_200_OK,
        )


class BlogPostCreateView(generics.CreateAPIView):
    """API endpoint to create blog posts (admin only)."""
    serializer_class = BlogPostCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for blog post detail (public GET, admin PATCH/DELETE)."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return BlogPostCreateSerializer
        return BlogPostSerializer

    def get_queryset(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return BlogPost.objects.all().select_related('author', 'category').prefetch_related('tags', 'comments')
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED
        ).select_related('author', 'category').prefetch_related('tags', 'comments')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        BlogPost.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogPostAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for blog post admin management."""
    queryset = BlogPost.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BlogPostCreateSerializer
        return BlogPostSerializer


class BlogPostAdminListView(generics.ListAPIView):
    """API endpoint to list all blog posts for admin."""
    queryset = BlogPost.objects.all().select_related('author', 'category')
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'status']
    ordering = ['-created_at']


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create comments."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs.get('post_slug')
        queryset = Comment.objects.filter(
            post__slug=post_slug
        ).select_related('author')
        
        # Non-admins only see approved comments
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_approved=True)
        
        return queryset

    def perform_create(self, serializer):
        post_slug = self.kwargs.get('post_slug')
        post = BlogPost.objects.get(slug=post_slug)
        serializer.save(
            post=post,
            author=self.request.user
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for comment detail."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CommentApproveView(APIView):
    """API endpoint to approve comments (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comment.is_approved = True
        comment.save()
        
        return Response(CommentSerializer(comment).data)


class FeaturedPostsView(generics.ListAPIView):
    """API endpoint for featured blog posts."""
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED,
            is_featured=True
        ).select_related('author', 'category')[:5]

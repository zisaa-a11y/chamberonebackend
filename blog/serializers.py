from rest_framework import serializers
from .models import Category, Tag, BlogPost, Comment
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'post_count']
        read_only_fields = ['id', 'slug']

    def get_post_count(self, obj):
        return obj.posts.filter(status=BlogPost.Status.PUBLISHED).count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_name',
            'content', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'created_at', 'updated_at']


class BlogPostSerializer(serializers.ModelSerializer):
    """Full serializer for BlogPost model."""
    author = UserSerializer(read_only=True)
    author_name = serializers.ReadOnlyField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='tags',
        required=False
    )
    image_url = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'author', 'author_name',
            'category', 'category_id',
            'tags', 'tag_ids',
            'featured_image', 'image_url',
            'status', 'status_display',
            'is_featured', 'views_count',
            'published_date', 'created_at', 'updated_at',
            'comments_count'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing blog posts."""
    author_name = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt',
            'author_name', 'category_name', 'image_url',
            'is_featured', 'views_count',
            'published_date'
        ]


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog posts."""
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        required=False
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category',
            'tag_ids', 'featured_image', 'status',
            'is_featured', 'published_date'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        post = BlogPost.objects.create(**validated_data)
        post.tags.set(tags)
        return post

from rest_framework import serializers
from django.utils import timezone
from django.utils.text import slugify
from .models import Category, Tag, BlogPost, Comment, LEGAL_BLOG_CATEGORIES
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
    image_url = serializers.SerializerMethodField()
    external_image_url = serializers.URLField(required=False, allow_blank=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'author', 'author_name',
            'category', 'category_id',
            'tags', 'tag_ids',
            'featured_image', 'external_image_url', 'image_url',
            'status', 'status_display',
            'is_featured', 'views_count',
            'published_date', 'created_at', 'updated_at',
            'comments_count'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request is None:
                return obj.featured_image.url
            return request.build_absolute_uri(obj.featured_image.url)

        if obj.external_image_url:
            return obj.external_image_url

        return None


class BlogPostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing blog posts."""
    author_name = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    external_image_url = serializers.URLField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt',
            'author_name', 'category_name', 'image_url', 'external_image_url',
            'status',
            'is_featured', 'views_count',
            'published_date'
        ]

    def get_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request is None:
                return obj.featured_image.url
            return request.build_absolute_uri(obj.featured_image.url)

        if obj.external_image_url:
            return obj.external_image_url

        return None


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog posts."""
    category = serializers.ChoiceField(
        choices=LEGAL_BLOG_CATEGORIES,
        required=False,
        write_only=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True,
        required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        required=False
    )
    image_url = serializers.URLField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category', 'category_id',
            'tag_ids', 'featured_image', 'external_image_url', 'image_url', 'status',
            'is_featured', 'published_date'
        ]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Title is required.')
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Content is required.')
        return value

    def validate_excerpt(self, value):
        value = (value or '').strip()
        if self.instance is None and not value:
            raise serializers.ValidationError('Excerpt is required.')
        return value

    def validate_featured_image(self, value):
        if not value:
            return value

        max_size_bytes = 10 * 1024 * 1024
        if value.size > max_size_bytes:
            raise serializers.ValidationError('Featured image must be 10MB or smaller.')

        content_type = (getattr(value, 'content_type', '') or '').lower()
        allowed_types = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        if content_type and content_type not in allowed_types:
            raise serializers.ValidationError('Unsupported image format. Use JPG, PNG, WEBP, or GIF.')

        return value

    def validate(self, attrs):
        category_name = attrs.pop('category', None)
        category_obj = attrs.get('category')

        if self.instance is None and category_name is None and category_obj is None:
            raise serializers.ValidationError({'category': 'Category is required.'})

        if category_name:
            category_slug = slugify(category_name)
            category_obj, _ = Category.objects.get_or_create(
                slug=category_slug,
                defaults={
                    'name': category_name,
                    'is_active': True,
                },
            )
            if category_obj.name != category_name or not category_obj.is_active:
                category_obj.name = category_name
                category_obj.is_active = True
                category_obj.save(update_fields=['name', 'is_active'])
            attrs['category'] = category_obj

        # Admin-created posts should be visible by default unless draft/archived is explicit.
        if self.instance is None and not attrs.get('status'):
            attrs['status'] = BlogPost.Status.PUBLISHED
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        image_url = validated_data.pop('image_url', '').strip()
        validated_data['author'] = self.context['request'].user
        if image_url:
            validated_data['external_image_url'] = image_url
        if validated_data.get('status') == BlogPost.Status.PUBLISHED and not validated_data.get('published_date'):
            validated_data['published_date'] = timezone.now()
        post = BlogPost.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        image_url = validated_data.pop('image_url', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_url is not None:
            instance.external_image_url = image_url.strip()

        if instance.status == BlogPost.Status.PUBLISHED and not instance.published_date:
            instance.published_date = timezone.now()

        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        return instance

    def to_representation(self, instance):
        return BlogPostSerializer(instance, context=self.context).data

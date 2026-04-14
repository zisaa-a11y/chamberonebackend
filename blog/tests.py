from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import BlogPost, Category
from .views import BlogPostCreateView, BlogPostListView


User = get_user_model()


class BlogPostApiTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.category = Category.objects.create(name='Announcements')
        self.published_post = BlogPost.objects.create(
            title='Published Post',
            content='Published content',
            author=self.admin,
            category=self.category,
            status=BlogPost.Status.PUBLISHED,
        )
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            content='Draft content',
            author=self.admin,
            category=self.category,
            status=BlogPost.Status.DRAFT,
        )

    def test_blog_list_excludes_drafts_for_public_access(self):
        request = self.factory.get(reverse('blog:post_list'))
        response = BlogPostListView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        titles = {item['title'] for item in results}

        self.assertIn('Published Post', titles)
        self.assertNotIn('Draft Post', titles)

    def test_admin_can_request_unpublished_blog_posts(self):
        request = self.factory.get(
            reverse('blog:post_list'),
            {'include_unpublished': 'true'},
        )
        force_authenticate(request, user=self.admin)
        response = BlogPostListView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        titles = {item['title'] for item in results}

        self.assertIn('Published Post', titles)
        self.assertIn('Draft Post', titles)

    def test_admin_blog_create_persists_published_status(self):
        request = self.factory.post(
            reverse('blog:post_create'),
            {
                'title': 'New Published Post',
                'content': 'New content',
                'status': BlogPost.Status.PUBLISHED,
            },
            format='json',
        )
        force_authenticate(request, user=self.admin)
        response = BlogPostCreateView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = BlogPost.objects.get(title='New Published Post')
        self.assertEqual(post.status, BlogPost.Status.PUBLISHED)
        self.assertEqual(post.author, self.admin)
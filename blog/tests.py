import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import BlogPost, Category


class BlogImageUrlTests(APITestCase):
    def setUp(self):
        self._tmp_media = tempfile.mkdtemp(prefix='blog-test-media-')
        self.override = override_settings(MEDIA_ROOT=self._tmp_media)
        self.override.enable()

        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            email='admin@example.com',
            password='StrongPass123!',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
        )

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self._tmp_media, ignore_errors=True)

    def test_list_endpoint_returns_absolute_image_url(self):
        image_file = SimpleUploadedFile(
            'post.jpg',
            b'\x47\x49\x46\x38\x39\x61',
            content_type='image/jpeg',
        )
        post = BlogPost.objects.create(
            title='Test post',
            content='Lorem ipsum',
            author=self.admin,
            status=BlogPost.Status.PUBLISHED,
            featured_image=image_file,
        )

        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.data
        item = payload['results'][0] if isinstance(payload, dict) else payload[0]
        self.assertEqual(item['slug'], post.slug)
        self.assertTrue(item['image_url'].startswith('http://testserver/media/'))

    def test_external_image_url_is_returned_when_featured_image_missing(self):
        post = BlogPost.objects.create(
            title='External image post',
            content='Lorem ipsum',
            author=self.admin,
            status=BlogPost.Status.PUBLISHED,
            external_image_url='https://images.example.com/blog/external.jpg',
        )

        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.data
        item = payload['results'][0] if isinstance(payload, dict) else payload[0]
        self.assertEqual(item['slug'], post.slug)
        self.assertEqual(
            item['image_url'],
            'https://images.example.com/blog/external.jpg',
        )

    def test_create_post_accepts_image_url_field(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            '/api/blog/posts/',
            {
                'title': 'Create with image url',
                'content': 'Body',
                'excerpt': 'Short',
                'image_url': 'https://images.example.com/blog/created.jpg',
                'status': BlogPost.Status.PUBLISHED,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = BlogPost.objects.get(pk=response.data['id'])
        self.assertEqual(
            created.external_image_url,
            'https://images.example.com/blog/created.jpg',
        )
        self.assertEqual(
            response.data['image_url'],
            'https://images.example.com/blog/created.jpg',
        )


class BlogCategoryFilterTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(
            email='author@example.com',
            password='StrongPass123!',
            first_name='Author',
            last_name='User',
        )
        self.corporate = Category.objects.create(name='Corporate Law')
        self.family = Category.objects.create(name='Family Law')

        BlogPost.objects.create(
            title='Corporate compliance checklist',
            content='Corporate legal content',
            excerpt='Corporate excerpt',
            author=self.author,
            category=self.corporate,
            status=BlogPost.Status.PUBLISHED,
        )
        BlogPost.objects.create(
            title='Family settlement basics',
            content='Family legal content',
            excerpt='Family excerpt',
            author=self.author,
            category=self.family,
            status=BlogPost.Status.PUBLISHED,
        )

    def _extract_results(self, response_data):
        if isinstance(response_data, dict):
            return response_data.get('results', [])
        return response_data

    def test_filters_by_category_slug(self):
        response = self.client.get(f'/api/blog/posts/?category={self.corporate.slug}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._extract_results(response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category_name'], 'Corporate Law')

    def test_filters_by_category_name(self):
        response = self.client.get('/api/blog/posts/?category=Family Law')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._extract_results(response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category_name'], 'Family Law')

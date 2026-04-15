import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import BlogPost


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

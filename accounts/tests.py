from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationPersistenceTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email='auth-client@example.com',
            password='StrongPass123!',
            first_name='Auth',
            last_name='Client',
            role='client',
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_profile_access_persists_with_valid_access_token(self):
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
            },
            format='json',
        )
        access = login_response.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        profile_response = self.client.get('/api/auth/profile/')

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], self.user.email)
        self.assertEqual(profile_response.data['role'], 'client')

    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
            },
            format='json',
        )
        refresh = login_response.data['tokens']['refresh']

        refresh_response = self.client.post(
            '/api/auth/token/refresh/',
            {'refresh': refresh},
            format='json',
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': 'StrongPass123!',
            },
            format='json',
        )
        access = login_response.data['tokens']['access']
        refresh = login_response.data['tokens']['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        logout_response = self.client.post(
            '/api/auth/logout/',
            {'refresh_token': refresh},
            format='json',
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            '/api/auth/token/refresh/',
            {'refresh': refresh},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_access_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

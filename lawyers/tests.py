from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import LawyerProfile
from .views import LawyerCreateView


User = get_user_model()


class LawyerCreateApiTests(APITestCase):
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

    def _base_payload(self, email):
        return {
            'full_name': 'Rahim Uddin',
            'email': email,
            'phone': '01700000000',
            'bio': 'Experienced lawyer',
            'profession': 'Lawyer',
            'specialization': 'Civil Law',
            'location': 'Dhaka',
            'city': 'Dhaka',
            'district': 'Dhaka',
            'chamber_info': 'Dhaka Chamber',
            'gender': 'male',
            'years_experience': 5,
            'cases_solved': 20,
            'consultancy_fees': '2500.00',
            'practice_areas': ['civil law'],
            'is_available': True,
        }

    def test_create_lawyer_profile_persists_new_user_and_profile(self):
        email = 'newlawyer@example.com'
        request = self.factory.post(
            reverse('lawyers:lawyer_create'),
            self._base_payload(email),
            format='json',
        )
        force_authenticate(request, user=self.admin)
        response = LawyerCreateView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertTrue(LawyerProfile.objects.filter(user__email=email).exists())

    def test_duplicate_lawyer_email_is_rejected(self):
        email = 'duplicate@example.com'
        User.objects.create_user(
            email=email,
            password='existingpass123',
            first_name='Existing',
            last_name='Lawyer',
            role=User.Role.LAWYER,
        )

        request = self.factory.post(
            reverse('lawyers:lawyer_create'),
            self._base_payload(email),
            format='json',
        )
        force_authenticate(request, user=self.admin)
        response = LawyerCreateView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(User.objects.filter(email=email).count(), 1)
        self.assertEqual(LawyerProfile.objects.filter(user__email=email).count(), 0)

    def test_missing_profile_photo_file_returns_none(self):
        user = User.objects.create_user(
            email='photo-missing@example.com',
            password='testpass123',
            first_name='Missing',
            last_name='Photo',
            role=User.Role.LAWYER,
        )
        profile = LawyerProfile.objects.create(user=user)
        user.profile_photo.name = 'profiles/profile_1.jpeg'
        user.save(update_fields=['profile_photo'])

        self.assertFalse(default_storage.exists('profiles/profile_1.jpeg'))
        self.assertIsNone(profile.profile_photo_url)


class LawyerAdminPermissionAndCredentialTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin2@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='Two',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='ClientPass123!',
            first_name='Client',
            last_name='One',
            role=User.Role.CLIENT,
            is_staff=False,
        )

    def test_admin_can_create_lawyer_via_api(self):
        self.client.force_authenticate(user=self.admin)

        payload = {
            'full_name': 'Create Lawyer',
            'email': 'created-by-admin@example.com',
            'phone': '01712345678',
            'location': 'Dhaka',
            'password': 'NewLawyer123!',
        }

        response = self.client.post(reverse('lawyers:lawyer_create'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='created-by-admin@example.com', role=User.Role.LAWYER).exists())
        self.assertTrue(LawyerProfile.objects.filter(user__email='created-by-admin@example.com').exists())

    def test_non_admin_cannot_create_lawyer_via_api(self):
        self.client.force_authenticate(user=self.client_user)

        payload = {
            'full_name': 'Blocked Create',
            'email': 'blocked-create@example.com',
            'location': 'Dhaka',
            'password': 'Blocked123!',
        }

        response = self.client.post(reverse('lawyers:lawyer_create'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(email='blocked-create@example.com').exists())

    def test_admin_can_update_lawyer_email_and_password(self):
        lawyer_user = User.objects.create_user(
            email='lawyer-old@example.com',
            password='OldPass123!',
            first_name='Lawyer',
            last_name='Old',
            role=User.Role.LAWYER,
        )
        lawyer_profile = LawyerProfile.objects.create(user=lawyer_user, location='Dhaka')

        self.client.force_authenticate(user=self.admin)
        payload = {
            'email': 'lawyer-new@example.com',
            'password': 'UpdatedPass123!',
        }

        response = self.client.patch(
            reverse('lawyers:lawyer_update', kwargs={'pk': lawyer_profile.pk}),
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        lawyer_user.refresh_from_db()
        self.assertEqual(lawyer_user.email, 'lawyer-new@example.com')
        self.assertTrue(lawyer_user.check_password('UpdatedPass123!'))
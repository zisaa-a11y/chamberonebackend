from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from cases.models import Case


class CaseApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.client_user = user_model.objects.create_user(
            email='case-client@example.com',
            password='StrongPass123!',
            first_name='Rahim',
            last_name='Ahmed',
            role='client',
        )
        self.other_client = user_model.objects.create_user(
            email='other-client@example.com',
            password='StrongPass123!',
            first_name='Karim',
            last_name='Hasan',
            role='client',
        )
        self.role_admin_user = user_model.objects.create_user(
            email='role-admin@example.com',
            password='StrongPass123!',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=False,
        )

    def _extract_results(self, payload):
        if isinstance(payload, dict):
            return payload.get('results', [])
        return payload

    def test_create_case_with_client_name_success(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            '/api/cases/',
            {
                'title': 'Land dispute hearing',
                'client_name': 'Rahim Ahmed',
                'court_name': 'High Court',
                'description': 'Client-side property dispute case',
                'status': 'open',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        case = Case.objects.get(pk=response.data['id'])
        self.assertEqual(case.client_name, 'Rahim Ahmed')
        self.assertEqual(case.court_name, 'High Court')

    def test_create_case_missing_client_name_rejected(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            '/api/cases/',
            {
                'title': 'Missing client name case',
                'court_name': 'High Court',
                'description': 'Validation test',
                'status': 'open',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client_name', response.data)

    def test_get_cases_returns_expected_listing_contract(self):
        self.client.force_authenticate(user=self.client_user)

        case = Case.objects.create(
            title='Criminal appeal',
            client_name='Rahim Ahmed',
            description='Appeal case',
            court_name='High Court',
            client=self.client_user,
            lawyer=None,
            status=Case.Status.OPEN,
        )

        response = self.client.get('/api/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._extract_results(response.data)
        self.assertGreaterEqual(len(results), 1)

        listed = next((item for item in results if item['id'] == case.id), None)
        self.assertIsNotNone(listed)
        self.assertEqual(listed['title'], 'Criminal appeal')
        self.assertEqual(listed['court_name'], 'High Court')
        self.assertEqual(listed['client_name'], 'Rahim Ahmed')
        self.assertIn('case_number', listed)

    def test_case_detail_allows_role_admin_without_staff_flag(self):
        case = Case.objects.create(
            title='Civil dispute',
            client_name='Rahim Ahmed',
            description='Detail access test',
            court_name='District Court',
            client=self.client_user,
            status=Case.Status.OPEN,
        )

        self.client.force_authenticate(user=self.role_admin_user)
        response = self.client.get(f'/api/cases/{case.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], case.id)
        self.assertEqual(response.data['title'], 'Civil dispute')
        self.assertEqual(response.data['client_name'], 'Rahim Ahmed')
        self.assertEqual(response.data['court_name'], 'District Court')
        self.assertEqual(response.data['description'], 'Detail access test')

    def test_case_detail_blocks_unrelated_client(self):
        case = Case.objects.create(
            title='Tax appeal',
            client_name='Rahim Ahmed',
            description='Unauthorized access test',
            court_name='Tax Court',
            client=self.client_user,
            status=Case.Status.OPEN,
        )

        self.client.force_authenticate(user=self.other_client)
        response = self.client.get(f'/api/cases/{case.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

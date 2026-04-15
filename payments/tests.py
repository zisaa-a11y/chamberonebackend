from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from payments.models import Invoice, Payment


class PaymentApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.client_user = user_model.objects.create_user(
            email='client@example.com',
            password='StrongPass123!',
            first_name='Client',
            last_name='One',
            role='client',
        )
        self.other_user = user_model.objects.create_user(
            email='other@example.com',
            password='StrongPass123!',
            first_name='Other',
            last_name='User',
            role='client',
        )

        self.invoice = Invoice.objects.create(
            client=self.client_user,
            description='Legal consultation',
            subtotal=1000,
            tax_amount=100,
            status=Invoice.Status.PENDING,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )

    def test_create_payment_persists_to_database(self):
        self.client.force_authenticate(user=self.client_user)

        payload = {
            'invoice': self.invoice.id,
            'amount': '1100.00',
            'payment_method': 'ssl',
            'notes': 'Paid from API test',
        }
        response = self.client.post('/api/payments/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.invoice_id, self.invoice.id)
        self.assertEqual(payment.client_id, self.client_user.id)
        self.assertEqual(payment.payment_method, Payment.PaymentMethod.SSLCOMMERZ)

    def test_payment_creation_rejects_other_users_invoice(self):
        foreign_invoice = Invoice.objects.create(
            client=self.other_user,
            description='Foreign invoice',
            subtotal=500,
            tax_amount=0,
            status=Invoice.Status.PENDING,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )

        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            '/api/payments/',
            {
                'invoice': foreign_invoice.id,
                'amount': '100.00',
                'payment_method': 'card',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invoice', response.data)
        self.assertEqual(Payment.objects.count(), 0)

    def test_invalid_invoice_id_returns_clear_message(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            '/api/payments/',
            {
                'invoice': 999999,
                'amount': '100.00',
                'payment_method': 'card',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invoice', response.data)
        self.assertIn('Invoice not found', str(response.data['invoice']))
        self.assertEqual(Payment.objects.count(), 0)

    def test_unauthenticated_payment_request_is_rejected(self):
        response = self.client.post(
            '/api/payments/',
            {
                'invoice': self.invoice.id,
                'amount': '100.00',
                'payment_method': 'card',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_flow_create_invoice_then_create_payment(self):
        self.client.force_authenticate(user=self.client_user)

        invoice_response = self.client.post(
            '/api/payments/invoices/',
            {
                'description': 'API flow invoice',
                'subtotal': '2000.00',
                'tax_amount': '200.00',
                'status': 'pending',
                'issue_date': date.today().isoformat(),
                'due_date': (date.today() + timedelta(days=10)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(invoice_response.status_code, status.HTTP_201_CREATED)
        created_invoice_id = invoice_response.data['id']

        payment_response = self.client.post(
            '/api/payments/',
            {
                'invoice': created_invoice_id,
                'amount': '2200.00',
                'payment_method': 'ssl',
                'notes': 'Flow test payment',
            },
            format='json',
        )
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.filter(invoice_id=created_invoice_id).count(), 1)

    def test_invoice_creation_accepts_legacy_frontend_fields(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            '/api/payments/invoices/',
            {
                'client_name': 'Legacy Frontend Client',
                'case_title': 'Legacy Case Title',
                'description': 'Legacy payload compatibility',
                'subtotal': '1450.00',
                'tax_amount': '50.00',
                'status': 'pending',
                'issue_date': date.today().isoformat(),
                'due_date': (date.today() + timedelta(days=7)).isoformat(),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['client']['id'], self.client_user.id)
        self.assertEqual(Invoice.objects.count(), 2)

    def test_invoice_creation_accepts_datetime_like_date_strings(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            '/api/payments/invoices/',
            {
                'description': 'Date compatibility test',
                'subtotal': '1800.00',
                'tax_amount': '200.00',
                'status': 'pending',
                'issue_date': '2026-04-15T00:00:00.000Z',
                'due_date': '2026-04-22T00:00:00.000Z',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['issue_date'], '2026-04-15')
        self.assertEqual(response.data['due_date'], '2026-04-22')

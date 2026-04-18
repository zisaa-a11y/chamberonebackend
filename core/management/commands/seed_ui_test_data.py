from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from cases.models import Case


class Command(BaseCommand):
    help = 'Seed deterministic users and cases for UI testing.'

    def handle(self, *args, **options):
        user_model = get_user_model()

        with transaction.atomic():
            admin_user, _ = user_model.objects.update_or_create(
                email='playwright.admin@chamberone.test',
                defaults={
                    'first_name': 'Playwright',
                    'last_name': 'Admin',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                },
            )
            admin_user.set_password('Playwright123!')
            admin_user.save(update_fields=['password'])

            client_user, _ = user_model.objects.update_or_create(
                email='playwright.client@chamberone.test',
                defaults={
                    'first_name': 'Playwright',
                    'last_name': 'Client',
                    'role': 'client',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                },
            )
            client_user.set_password('Playwright123!')
            client_user.save(update_fields=['password'])

            other_client, _ = user_model.objects.update_or_create(
                email='playwright.other@chamberone.test',
                defaults={
                    'first_name': 'Other',
                    'last_name': 'Client',
                    'role': 'client',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                },
            )
            other_client.set_password('Playwright123!')
            other_client.save(update_fields=['password'])

            client_case, _ = Case.objects.update_or_create(
                title='Playwright Client Case',
                client=client_user,
                defaults={
                    'client_name': client_user.full_name,
                    'description': 'Seeded case for Playwright client flow.',
                    'court_name': 'Dhaka District Court',
                    'status': Case.Status.OPEN,
                },
            )

            other_case, _ = Case.objects.update_or_create(
                title='Playwright Restricted Case',
                client=other_client,
                defaults={
                    'client_name': other_client.full_name,
                    'description': 'Seeded case for unauthorized access flow.',
                    'court_name': 'Chattogram District Court',
                    'status': Case.Status.PENDING,
                },
            )

        self.stdout.write(self.style.SUCCESS('Seeded Playwright UI test data successfully.'))
        self.stdout.write(f'Admin: {admin_user.email} / Playwright123!')
        self.stdout.write(f'Client: {client_user.email} / Playwright123!')
        self.stdout.write(f'Other Client: {other_client.email} / Playwright123!')
        self.stdout.write(f'Client Case ID: {client_case.id}')
        self.stdout.write(f'Restricted Case ID: {other_case.id}')

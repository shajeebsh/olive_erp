from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an ERP-only user (no admin access)'

    def handle(self, *args, **options):
        username = 'erpadmin'
        email = 'erpadmin@oliveerp.com'
        password = 'erpadmin123'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        else:
            self.stdout.write(f'User {username} already exists, password reset')

        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  is_staff: {user.is_staff}')
        self.stdout.write(f'  is_superuser: {user.is_superuser}')
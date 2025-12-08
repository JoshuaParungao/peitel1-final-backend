from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Run migrations, collectstatic, and optionally create an admin user.'

    def add_arguments(self, parser):
        parser.add_argument('--admin-username', default=None, help='Admin username')
        parser.add_argument('--admin-email', default=None, help='Admin email')
        parser.add_argument('--admin-password', default=None, help='Admin password')

    def handle(self, *args, **options):
        # Run migrations
        self.stdout.write('[postdeploy] Running migrations...')
        call_command('migrate', '--noinput')

        # Collect static files
        self.stdout.write('[postdeploy] Collecting static files...')
        call_command('collectstatic', '--noinput')

        # Determine admin credentials from options or environment
        admin_username = options.get('admin_username') or os.environ.get('ADMIN_USERNAME')
        admin_email = options.get('admin_email') or os.environ.get('ADMIN_EMAIL')
        admin_password = options.get('admin_password') or os.environ.get('ADMIN_PASSWORD')

        if admin_username and admin_email and admin_password:
            # Create or update a superuser with given credentials
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(is_superuser=True).exists():
                if not User.objects.filter(username=admin_username).exists():
                    User.objects.create_superuser(admin_username, admin_email, admin_password)
                    self.stdout.write(self.style.SUCCESS(f'Superuser created: {admin_username}'))
                else:
                    u = User.objects.get(username=admin_username)
                    u.is_superuser = True
                    u.is_staff = True
                    u.email = admin_email
                    u.set_password(admin_password)
                    u.save()
                    self.stdout.write(self.style.SUCCESS(f'Existing user promoted to superuser: {admin_username}'))
            else:
                self.stdout.write(self.style.WARNING('Superuser already exists, skipping creation.'))
        else:
            # Try to call the repo's `create_superuser` management command, if present.
            try:
                call_command('create_superuser')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No admin info provided and create_superuser command failed or not present: {e}'))

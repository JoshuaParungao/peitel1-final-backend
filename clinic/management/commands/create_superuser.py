from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create superuser if it does not exist'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            # Create StaffProfile for the superuser
            from clinic.models import StaffProfile
            StaffProfile.objects.get_or_create(user=user, defaults={'position': 'admin'})
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created with StaffProfile'))
        else:
            user = User.objects.get(username='admin')
            # Ensure superuser has a StaffProfile
            from clinic.models import StaffProfile
            profile, created = StaffProfile.objects.get_or_create(user=user, defaults={'position': 'admin'})
            if created:
                self.stdout.write(self.style.SUCCESS('StaffProfile created for existing "admin" superuser'))
            else:
                self.stdout.write(self.style.WARNING('Superuser "admin" already exists with StaffProfile'))


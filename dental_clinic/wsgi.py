"""
WSGI config for dental_clinic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dental_clinic.settings")

# Initialize Django first
django.setup()
from django.core.wsgi import get_wsgi_application

# Run startup maintenance tasks automatically on process start.
# This helps free-tier Render deployments where a shell may not be available.
try:
	run_startup = os.getenv('RUN_STARTUP_TASKS', 'True')
	if run_startup.lower() in ('1', 'true', 'yes'):
		# Import here so settings are loaded
		from django.core.management import call_command
		# Apply migrations (idempotent)
		try:
			print('[startup] Running database migrations...')
			call_command('migrate', '--noinput')
			print('[startup] Migrations complete.')
		except Exception as e:
			# Log but continue; a failing migrate shouldn't prevent app from starting
			print(f'[startup] Migrate failed: {e}')

		# Collect static files
		try:
			print('[startup] Collecting static files...')
			call_command('collectstatic', '--noinput')
			print('[startup] Collectstatic complete.')
		except Exception as e:
			print(f'[startup] Collectstatic failed: {e}')

		# Create or update admin user if env vars present, otherwise try existing create_superuser command
		try:
			admin_user = os.getenv('ADMIN_USERNAME')
			admin_email = os.getenv('ADMIN_EMAIL')
			admin_pass = os.getenv('ADMIN_PASSWORD')
			if admin_user and admin_email and admin_pass:
				from django.contrib.auth import get_user_model
				User = get_user_model()
				u, created = User.objects.get_or_create(username=admin_user, defaults={'email': admin_email})
				u.is_staff = True
				u.is_superuser = True
				u.email = admin_email
				u.set_password(admin_pass)
				u.save()
				print('[startup] Admin user created/updated:', admin_user)
			else:
				# Fallback: call repository's create_superuser management command if present
				try:
					call_command('create_superuser')
					print('[startup] Ran create_superuser command')
				except Exception as e:
					print(f'[startup] create_superuser command not available or failed: {e}')
		except Exception as e:
			print(f'[startup] Admin creation failed: {e}')
except Exception as e:
	print(f'[startup] Unexpected error during startup tasks: {e}')

application = get_wsgi_application()

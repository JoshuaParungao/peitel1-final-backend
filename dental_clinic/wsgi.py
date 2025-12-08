"""
WSGI config for dental_clinic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import django
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dental_clinic.settings")

# Initialize Django first
django.setup()
from django.core.wsgi import get_wsgi_application

# Configure a simple logger for startup tasks
logger = logging.getLogger('startup')
if not logger.handlers:
	logging.basicConfig(level=logging.INFO)

# Run startup maintenance tasks automatically on process start.
# Use logging instead of print to avoid stdout lock issues at interpreter shutdown.
try:
	run_startup = os.getenv('RUN_STARTUP_TASKS', 'True')
	if run_startup.lower() in ('1', 'true', 'yes'):
		# Import here so settings are loaded
		from django.core.management import call_command

		# Apply migrations (idempotent)
		try:
			logger.info('[startup] Running database migrations...')
			# Quiet output in production
			call_command('migrate', '--noinput', verbosity=0)
			logger.info('[startup] Migrations complete.')
		except Exception as e:
			# Log but continue; a failing migrate shouldn't prevent app from starting
			logger.exception('[startup] Migrate failed')

		# Collect static files
		try:
			logger.info('[startup] Collecting static files...')
			call_command('collectstatic', '--noinput', verbosity=0)
			logger.info('[startup] Collectstatic complete.')
		except Exception as e:
			logger.exception('[startup] Collectstatic failed')

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
				logger.info('[startup] Admin user created/updated: %s', admin_user)
			else:
				# Fallback: call repository's create_superuser management command if present
				try:
					call_command('create_superuser', verbosity=0)
					logger.info('[startup] Ran create_superuser command')
				except Exception:
					logger.debug('[startup] create_superuser command not available or failed')
		except Exception:
			logger.exception('[startup] Admin creation failed')
except Exception:
	logger.exception('[startup] Unexpected error during startup tasks')

application = get_wsgi_application()

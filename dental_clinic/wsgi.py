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

application = get_wsgi_application()

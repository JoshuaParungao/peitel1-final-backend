#!/usr/bin/env bash
set -e

echo "[postdeploy] Running migrations..."
python manage.py migrate --noinput

echo "[postdeploy] Collecting static files..."
python manage.py collectstatic --noinput

if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo "[postdeploy] Ensuring superuser exists..."
  python - <<'PY'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('ADMIN_USERNAME')
email = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASSWORD')
if not User.objects.filter(is_superuser=True).exists():
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print('Superuser created:', username)
    else:
        u = User.objects.get(username=username)
        u.is_superuser = True
        u.is_staff = True
        u.email = email
        u.set_password(password)
        u.save()
        print('Existing user promoted to superuser:', username)
else:
    print('Superuser already exists, skipping creation.')
PY
else
  echo "[postdeploy] ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD not provided; skipping superuser creation."
fi

echo "[postdeploy] Done."

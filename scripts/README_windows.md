# Windows / PowerShell development notes

If you're developing on Windows with PowerShell, follow these steps after activating the virtualenv.

1. Install dependencies

```powershell
pip install -r requirements.txt
```

2. (Optional) If you don't have a `DATABASE_URL` env var set, the settings file will fall back to SQLite for local development.

To set `DATABASE_URL` for local SQLite (recommended default):

```powershell
$env:DATABASE_URL = "sqlite:///E:/DentalClinic/dental_clinic/db.sqlite3"
$env:DJANGO_DEBUG = "True"
```

3. Run migrations and collectstatic (or run the postdeploy script):

```powershell
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# or
./scripts/postdeploy.ps1
```

4. Create default admin (the repo already includes `clinic/management/commands/create_superuser.py`):

```powershell
python manage.py create_superuser
```

That command will create `admin`/`admin` if the superuser does not exist.

If you want to create/update the admin user manually (non-interactive):

```powershell
python -c "from django.contrib.auth import get_user_model; User=get_user_model(); u,created = User.objects.get_or_create(username='admin', defaults={'email':'admin@example.com'}); u.set_password('admin'); u.is_staff=True; u.is_superuser=True; u.save(); print('created' if created else 'updated')"
```

Security note: using `admin/admin` is insecure; change the password before exposing the app publicly.

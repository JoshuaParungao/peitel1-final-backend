# PowerShell post-deploy script for Windows-friendly environments
# Usage: ./scripts/postdeploy.ps1 (run from project root with venv activated)
$ErrorActionPreference = 'Stop'
Write-Host "Running Django migrations..."
python manage.py migrate --noinput
Write-Host "Collecting static files..."
python manage.py collectstatic --noinput
# Create default admin using existing management command if present
Write-Host "Ensuring default superuser exists (create_superuser command)..."
python manage.py create_superuser || Write-Host "create_superuser command failed or not present; skipping"
Write-Host "Postdeploy script finished."
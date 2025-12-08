#!/usr/bin/env bash
set -e

echo "[postdeploy] Running postdeploy management command (migrate + collectstatic + create admin)..."
python manage.py postdeploy || (
  echo "[postdeploy] postdeploy command failed; falling back to manual steps"
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
)

echo "[postdeploy] Done."

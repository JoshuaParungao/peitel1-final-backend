# peitel1-final-backend

[![CI](https://github.com/JoshuaParungao/peitel1-final-backend/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/JoshuaParungao/peitel1-final-backend/actions/workflows/ci.yml)

This repository contains the Django backend for a Dental POS/web app.

CI workflow: the `CI - Django` GitHub Actions workflow runs on push and pull request to `main` and performs the following steps:

- Installs dependencies from `requirements.txt`.
- Runs migrations and `collectstatic` using SQLite in CI.
- Runs the Django test suite.

If you want to see the CI status, click the badge above or visit the Actions tab in the GitHub repository.

Local development notes are available in `scripts/README_windows.md`.

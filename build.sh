#!/usr/bin/env bash
# Render runs this on every deploy (Build Command: bash build.sh).
set -o errexit  # stop at the first command that fails

pip install -r requirements.txt
python manage.py tailwind build          # Tailwind + daisyUI -> static/css/tailwind.css
python manage.py collectstatic --no-input
#!/bin/sh
set -eu

# Management commands bypass startup work, e.g. createsuperuser and loaddata.
if [ "${1:-}" != "serve" ]; then
    exec "$@"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-600}" \
    --access-logfile - --error-logfile -

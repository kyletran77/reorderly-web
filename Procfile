web: gunicorn reorderly.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --log-file -
worker: python manage.py run_monitor
release: python manage.py migrate --noinput

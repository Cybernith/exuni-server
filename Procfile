migrate: python manage.py migrate --no-input
web: python -m gunicorn server.wsgi:application --host 0.0.0.0 --port 5000 --workers 8 --timeout-keep-alive 60
collectstatic : python manage.py collectstatic --no-input
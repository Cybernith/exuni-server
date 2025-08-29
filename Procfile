migrate: python manage.py migrate --no-input
web: gunicorn server.wsgi:application --bind 0.0.0.0:5000 --workers ${WEB_CONCURRENCY:-3} --timeout 60 --keep-alive 60

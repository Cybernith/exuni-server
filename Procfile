migrate: python manage.py migrate --no-input
web: gunicorn server.wsgi:application --bind 0.0.0.0:5000 --workers 8 --timeout 180 --keep-alive 5

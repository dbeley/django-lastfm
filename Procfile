release: python manage.py migrate --noinput
web: gunicorn lastfm_django.wsgi --bind 0.0.0.0:$PORT --timeout 600

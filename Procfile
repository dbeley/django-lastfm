release: python manage.py migrate
worker: celery -A lastfm_django worker
web: gunicorn lastfm_django.wsgi

release: python manage.py migrate
worker: celery -A lastfm_django worker -l info
web: gunicorn lastfm_django.wsgi

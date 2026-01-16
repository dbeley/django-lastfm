from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lastfm_django.settings")

app = Celery("lastfm_django")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure task defaults
app.conf.update(
    task_soft_time_limit=600,  # 10 minutes soft limit (raises exception)
    task_time_limit=660,       # 11 minutes hard limit (kills worker)
    task_acks_late=True,       # Acknowledge tasks after completion
    worker_prefetch_multiplier=1,  # Don't prefetch tasks (better for long tasks)
    task_reject_on_worker_lost=True,  # Reject tasks if worker is lost
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))

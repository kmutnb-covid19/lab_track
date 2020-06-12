from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_name.settings")
app = Celery("project_name")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
     # Everyday at 22:00
    "backup": {
        "task": "core.tasks.backup",
        "schedule": crontab(hour=22, minute=00)
    },
}
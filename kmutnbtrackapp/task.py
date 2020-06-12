import datetime
from celery import shared_task
from django.conf import settings
from django.core.management import call_command


@shared_task
def backup():
    if settings.DEBUG is True:
        return f"Could not be backed up: Debug is True"
    else:
        try:
            call_command("dbbackup")
            return f"Backed up successfully: {datetime.datetime.now()}"
        except:
            return f"Could not be backed up: {datetime.datetime.now()}"
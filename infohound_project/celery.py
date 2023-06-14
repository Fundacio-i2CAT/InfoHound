import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infohound_project.settings")
app = Celery("infohound_project_site")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


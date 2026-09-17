# lynxreactor/celery.py

import os
from celery import Celery

# Не хардкодим dev/prod — берём из переменной окружения
# (systemd задаёт DJANGO_SETTINGS_MODULE=lynxreactor.settings.prod)
# Fallback — dev, если переменная не задана
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynxreactor.settings.dev')

app = Celery('lynxreactor')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
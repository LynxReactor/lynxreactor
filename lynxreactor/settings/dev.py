# lynxreactor/settings/dev.py

"""
Настройки для разработки.
- SQLite
- LocMemCache
- Console email
- Celery EAGER
- DEBUG=True
"""

from .base import *  # noqa
import os
from django.conf import settings as django_settings

# ============================================================
# ОСНОВНОЕ
# ============================================================

DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ============================================================
# БАЗА ДАННЫХ — SQLite
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# КЕШ — LocMemCache (не требует Redis)
# ============================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lynxreactor_cache',
    }
}

# ============================================================
# EMAIL — Console
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================================
# CELERY — EAGER (синхронно)
# ============================================================

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://localhost/'
CELERY_RESULT_BACKEND = None
CELERY_TASK_IGNORE_RESULT = True

# ============================================================
# STORAGES
# ============================================================

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# ============================================================
# DEBUG TOOLBAR (опционально)
# ============================================================

# ============================================================
# DEBUG TOOLBAR
# ============================================================

INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ['127.0.0.1', 'localhost']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: (
        request.META.get('REMOTE_ADDR') in ['127.0.0.1', '::1']
        and django_settings.DEBUG
    ),
}

# lynxreactor/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

# По умолчанию dev. В проде задаётся через DJANGO_SETTINGS_MODULE в systemd/gunicorn
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynxreactor.settings.dev')

application = get_wsgi_application()
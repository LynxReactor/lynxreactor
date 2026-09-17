# manage.py

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# ============================================================
# GETTEXT для Windows — принудительно добавляем в PATH
# ============================================================
if os.name == 'nt':  # Windows
    GETTEXT_PATHS = [
        r'C:\Program Files\Poedit\GettextTools\bin',
        r'C:\Program Files\gettext-iconv\bin',
        r'C:\Program Files (x86)\gettext-iconv\bin',
    ]
    for path in GETTEXT_PATHS:
        if os.path.exists(os.path.join(path, 'msguniq.exe')):
            os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
            print(f"✅ Gettext найден: {path}")
            break
    else:
        print("⚠️ Gettext не найден. Установите Poedit или gettext-iconv.")

def main():
    """Run administrative tasks."""
    # По умолчанию — dev. Для прода: DJANGO_SETTINGS_MODULE=lynxreactor.settings.prod
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynxreactor.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
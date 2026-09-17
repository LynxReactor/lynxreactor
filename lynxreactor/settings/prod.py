# lynxreactor/settings/prod.py

"""
Настройки для продакшена.
- PostgreSQL
- Redis (cache + broker + result backend)
- SMTP email
- Celery worker + beat
- SECURE_* настройки
- StaticFilesStorage (без Manifest — обходит проблемы с jazzmin/bootstrap sourcemap)
- RotatingFileHandler для логов
- Fail-fast проверки: не запустимся с dev-настройками
"""

from .base import *  # noqa
import os


# ============================================================
# FAIL-FAST ПРОВЕРКИ (до всего остального)
# ============================================================

# 1. .env.prod (или .env.production) должен существовать
_env_file_prod = BASE_DIR / '.env.prod'
_env_file_production = BASE_DIR / '.env.production'

if not _env_file_prod.exists() and not _env_file_production.exists():
    raise RuntimeError(
        f'❌ Файл .env.prod или .env.production НЕ найден в {BASE_DIR}. '
        f'Production не может стартовать без env-файла с секретами.\n'
        f'   Создайте .env.prod с production-настройками.'
    )

# 2. Обязательные переменные окружения
_REQUIRED_ENV_VARS = [
    'SECRET_KEY',
    'ALLOWED_HOSTS',
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'DB_HOST',
]
_missing_vars = [v for v in _REQUIRED_ENV_VARS if not os.getenv(v)]
if _missing_vars:
    raise RuntimeError(
        f'❌ В production env отсутствуют переменные: {_missing_vars}.\n'
        f'   Проверьте .env.prod или .env.production.'
    )

# 3. SECRET_KEY не должен быть дефолтным
_INSECURE_KEYS = {
    '',
    'django-insecure-...',
    'dev-secret-key-change-me',
    'your-secret-key-here',
}
if SECRET_KEY in _INSECURE_KEYS or len(SECRET_KEY) < 30:
    raise RuntimeError(
        '❌ SECRET_KEY в production — дефолтный или слишком короткий.\n'
        '   Сгенерируйте новый: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
    )

# 4. ALLOWED_HOSTS не должен быть ["*"] и должен быть задан
_allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '').strip()
if not _allowed_hosts_env or _allowed_hosts_env == '*':
    raise RuntimeError(
        '❌ ALLOWED_HOSTS в production должен содержать конкретные домены.\n'
        '   Пример: ALLOWED_HOSTS=lynxreactor.by,www.lynxreactor.by'
    )

# 5. Turnstile НЕ должен быть отключён в production
if TURNSTILE_DISABLED:
    raise RuntimeError(
        '❌ TURNSTILE_DISABLED=True в production — недопустимо.\n'
        '   Формы без капчи → спам-боты → захламление БД.\n'
        '   Установите TURNSTILE_DISABLED=False в .env.prod или удалите переменную.'
    )

# 6. Проверка, что БД — НЕ SQLite
_db_engine = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
if 'sqlite' in _db_engine.lower():
    raise RuntimeError(
        '❌ Production использует SQLite. Укажите PostgreSQL в .env.prod:\n'
        '   DB_ENGINE=django.db.backends.postgresql'
    )


# ============================================================
# ОСНОВНОЕ
# ============================================================

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]


# ============================================================
# БАЗА ДАННЫХ — PostgreSQL
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'lynxreactor_prod'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': False,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        },
    }
}


# ============================================================
# REDIS — CACHE + CELERY
# ============================================================
# Разделение DB с проектом luxestretch на том же сервере:
#   DB 0 — luxestretch Celery broker (занято)
#   DB 1, 2, 3 — свободно (запас на будущее)
#   DB 4 — lynxreactor cache
#   DB 5 — lynxreactor Celery broker
#   DB 6 — lynxreactor Celery result backend

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Извлекаем хост:порт из URL (для разделения БД)
_redis_base = REDIS_URL.rsplit('/', 1)[0]

# Кеш — DB 4
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'{_redis_base}/4',
        'OPTIONS': {
            'db': '4',
        },
    }
}

# Celery — broker DB 5, result DB 6
CELERY_BROKER_URL = f'{_redis_base}/5'
CELERY_RESULT_BACKEND = f'{_redis_base}/6'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False


# ============================================================
# EMAIL — SMTP
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# ============================================================
# БЕЗОПАСНОСТЬ
# ============================================================

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# HSTS (год)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Дополнительно
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Referrer-Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# ============================================================
# STORAGES
# ============================================================
# ManifestStaticFilesStorage отключён из-за проблемы с jazzmin:
# bootstrap.min.css из jazzmin ссылается на .map файл, которого нет,
# и collectstatic падает. StaticFilesStorage работает без hashed-имён.

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


# ============================================================
# ЛОГИРОВАНИЕ — RotatingFileHandler
# ============================================================

LOGGING['handlers']['file'] = {
    'level': 'WARNING',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': BASE_DIR / 'logs' / 'django.log',
    'maxBytes': 10 * 1024 * 1024,
    'backupCount': 5,
    'formatter': 'verbose',
}

LOGGING['loggers']['django']['handlers'] = ['console', 'file']
LOGGING['loggers']['django.request']['handlers'] = ['console', 'file']
LOGGING['loggers']['agency']['handlers'] = ['console', 'file']
LOGGING['loggers']['agency']['level'] = 'INFO'


# ============================================================
# INDEXNOW — файл ключа
# ============================================================

if INDEXNOW_ENABLED and INDEXNOW_KEY:
    try:
        key_file = BASE_DIR / 'static' / f"{INDEXNOW_KEY}.txt"
        if not key_file.exists():
            with open(key_file, 'w') as f:
                f.write(INDEXNOW_KEY)
            logger.info(f"✅ Создан файл ключа IndexNow: {INDEXNOW_KEY}.txt")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось создать файл ключа IndexNow: {e}")


# ============================================================
# RATELIMIT
# ============================================================

RATELIMIT_IP_META_KEY = 'HTTP_X_FORWARDED_FOR'
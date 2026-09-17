# lynxreactor/settings/base.py

"""
Общие настройки для всех окружений.
Специфичные настройки — в dev.py / prod.py.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
from celery.schedules import crontab
import logging


# ============================================================
# БАЗОВЫЕ ПУТИ
# ============================================================

# BASE_DIR = корень проекта (там где manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ============================================================
# ЗАГРУЗКА .env
#
# Приоритет:
#   1. DJANGO_ENV (если явно задан) — например, 'production'
#   2. Из DJANGO_SETTINGS_MODULE — 'lynxreactor.settings.prod' → 'prod'
#   3. По умолчанию — 'dev'
#
# Это гарантирует, что .env.prod загрузится при запуске
# с DJANGO_SETTINGS_MODULE=lynxreactor.settings.prod, даже если
# DJANGO_ENV не задан.
# ============================================================

def _detect_env_name() -> str:
    """
    Определяет имя env из DJANGO_ENV или DJANGO_SETTINGS_MODULE.

    Примеры:
        DJANGO_ENV=production                       → 'production'
        DJANGO_SETTINGS_MODULE=...settings.prod     → 'prod'
        DJANGO_SETTINGS_MODULE=...settings.production → 'prod'
        Ничего не задано                            → 'dev'
    """
    # 1. Приоритет — явный DJANGO_ENV
    env_name = os.getenv('DJANGO_ENV', '').strip()
    if env_name:
        return env_name

    # 2. Из DJANGO_SETTINGS_MODULE
    settings_module = os.getenv('DJANGO_SETTINGS_MODULE', '')
    if settings_module:
        parts = settings_module.split('.')
        for candidate in ('production', 'prod', 'staging', 'dev', 'development', 'test'):
            if candidate in parts:
                if candidate == 'production':
                    return 'prod'
                if candidate == 'development':
                    return 'dev'
                return candidate

    # 3. Fallback
    return 'dev'


env_name = _detect_env_name()

env_specific = BASE_DIR / f'.env.{env_name}'
env_default = BASE_DIR / '.env'

if env_specific.exists():
    load_dotenv(env_specific)
    _loaded_env_file = env_specific
elif env_default.exists():
    load_dotenv(env_default)
    _loaded_env_file = env_default
else:
    _loaded_env_file = None

# Настройка логирования для загрузки настроек
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if _loaded_env_file:
    logger.info(f"🔧 Environment: {env_name} (loaded from {_loaded_env_file.name})")
else:
    logger.warning("⚠️ No .env file found, using system environment variables only")


# ============================================================
# БАЗОВЫЕ НАСТРОЙКИ
# ============================================================

SECRET_KEY = os.getenv('SECRET_KEY', '')

# DEBUG переопределяется в dev.py / prod.py
DEBUG = False

ALLOWED_HOSTS = []


# ============================================================
# ПРИЛОЖЕНИЯ
# ============================================================

INSTALLED_APPS = [
    'modeltranslation',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # Third party
    'corsheaders',
    'imagekit',
    'ckeditor',
    'django_cf_turnstile',

    # Local
    'agency',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'agency.middleware.MaintenanceModeMiddleware',
    'agency.middleware.ThemeMiddleware',
    'agency.middleware.BlogViewCountMiddleware',
]

ROOT_URLCONF = 'lynxreactor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'agency.context_processors.theme_context',
                'agency.context_processors.site_config',
                'agency.context_processors.contact_info',
                'agency.context_processors.canonical_context',
                'agency.context_processors.tariffs_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'lynxreactor.wsgi.application'
ASGI_APPLICATION = 'lynxreactor.asgi.application'


# ============================================================
# БАЗА ДАННЫХ — ЗАГЛУШКА (переопределяется в dev.py / prod.py)
# ============================================================

DATABASES = {}


# ============================================================
# ПАРОЛИ
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# ЛОКАЛИЗАЦИЯ
# ============================================================

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Model Translation
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru',)
MODELTRANSLATION_AUTO_ADD_FIELD = True
MODELTRANSLATION_AUTO_ADD_VIEW_FIELD = True

# Тема
THEME_COOKIE_NAME = 'theme_preference'
THEME_SESSION_KEY = 'theme'
DEFAULT_THEME = 'light'
AVAILABLE_THEMES = ['light', 'dark']


# ============================================================
# STATIC & MEDIA
# ============================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Создаём директории
for dir_path in [BASE_DIR / 'static', BASE_DIR / 'media', BASE_DIR / 'logs', BASE_DIR / 'locale', BASE_DIR / 'cache']:
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Создана директория: {dir_path}")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# CLOUDFLARE TURNSTILE
# ============================================================

CF_TURNSTILE_SITE_KEY = os.getenv('CF_TURNSTILE_SITE_KEY', '1x00000000000000000000AA')
CF_TURNSTILE_SECRET_KEY = os.getenv('CF_TURNSTILE_SECRET_KEY', '1x0000000000000000000000000000000AA')
CF_TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

# Отключение Turnstile (для локальной отладки, тестов, CI).
# В production должно быть False. Fail-fast проверка — в prod.py.
TURNSTILE_DISABLED = os.getenv('TURNSTILE_DISABLED', 'False') == 'True'


# ============================================================
# CORS / CSRF
# ============================================================

CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')


# ============================================================
# EMAIL (базовые адреса; backend переопределяется)
# ============================================================

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'LYNXREACTOR <lynxreacto@gmail.com>')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'lynxreacto@gmail.com')
CONTACT_FORM_EMAIL = os.getenv('CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'lynxreacto@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_NOTIFICATIONS_ENABLED = os.getenv('TELEGRAM_NOTIFICATIONS_ENABLED', 'False') == 'True'
TELEGRAM_DEBUG_CHAT_ID = os.getenv('TELEGRAM_DEBUG_CHAT_ID', '')
TELEGRAM_DEBUG_NOTIFICATIONS = os.getenv('TELEGRAM_DEBUG_NOTIFICATIONS', 'True') == 'True'


# ============================================================
# INDEXNOW
# ============================================================

INDEXNOW_ENABLED = os.getenv('INDEXNOW_ENABLED', 'False') == 'True'
INDEXNOW_KEY = os.getenv('INDEXNOW_KEY', '')
INDEXNOW_API_URL = os.getenv('INDEXNOW_API_URL', 'https://api.indexnow.org/IndexNow')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')


# ============================================================
# CELERY (базовые; broker/backend переопределяются)
# ============================================================

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False


# ============================================================
# CELERY BEAT SCHEDULE
# ============================================================
# Периодические задачи.
# Запускается через lynxreactor-celerybeat.service.

CELERY_BEAT_SCHEDULE = {
    # Очистка старых заявок (GDPR + разгрузка БД)
    # Запуск: 1-е число каждого месяца, 03:00 Europe/Moscow
    # Удаляет заявки со статусом completed/rejected старше 90 дней
    'cleanup-old-contact-requests': {
        'task': 'agency.tasks.cleanup_old_contact_requests',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),
        'kwargs': {'days': 90},
    },
}

# ============================================================
# IMAGEKIT
# ============================================================

IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.JustInTime'
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'default'


# ============================================================
# ДОВЕРЕННЫЕ ПРОКСИ (для корректного определения IP клиента)
# ============================================================
# Формат: IP или CIDR через запятую.
# В dev — только localhost.
# В prod — IP/сети вашего nginx/Cloudflare.

TRUSTED_PROXIES = [
    p.strip() for p in os.getenv(
        'TRUSTED_PROXIES',
        '127.0.0.1,::1'
    ).split(',') if p.strip()
]

# ============================================================
# JAZZMIN
# ============================================================

JAZZMIN_SETTINGS = {
    "site_title": "LYNXREACTOR Admin",
    "site_header": "LYNXREACTOR",
    "site_brand": "LYNXREACTOR",
    "welcome_sign": "Welcome to LYNXREACTOR Admin Panel",
    "copyright": "LYNXREACTOR",
    "search_model": ["auth.User", "auth.Group"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Site", "url": "/", "new_window": True},
        {"name": "Contact Requests", "url": "admin:agency_contactrequest_changelist"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "agency",
        "agency.HeroSection",
        "agency.ServicesSection",
        "agency.LandingSection",
        "agency.BusinessSection",
        "agency.RefactorSection",
        "agency.PortfolioSection",
        "agency.Tariff",
        "agency.FAQSection",
        "agency.CTASection",
        "agency.ReviewsSection",
        "agency.ContactPage",
        "agency.BlogCategory",
        "agency.BlogPost",
        "agency.ContactRequest",
        "agency.SiteConfiguration",
        "agency.PageSEO",
    ],
    "icons": {
        "agency.HeroSection": "fas fa-image",
        "agency.ServicesSection": "fas fa-cogs",
        "agency.ServiceItem": "fas fa-cog",
        "agency.TechSection": "fas fa-microchip",
        "agency.TechItem": "fas fa-code",
        "agency.LandingSection": "fas fa-landmark",
        "agency.BusinessSection": "fas fa-store",
        "agency.RefactorSection": "fas fa-sync-alt",
        "agency.PortfolioSection": "fas fa-images",
        "agency.PortfolioItem": "fas fa-folder-open",
        "agency.Tariff": "fas fa-tag",
        "agency.FAQSection": "fas fa-question-circle",
        "agency.FAQItem": "fas fa-question",
        "agency.CTASection": "fas fa-bullhorn",
        "agency.ReviewsSection": "fas fa-star",
        "agency.Review": "fas fa-star",
        "agency.ContactPage": "fas fa-address-card",
        "agency.ContactRequest": "fas fa-envelope",
        "agency.BlogCategory": "fas fa-folder",
        "agency.BlogPost": "fas fa-blog",
        "agency.SiteConfiguration": "fas fa-cog",
        "agency.PageSEO": "fas fa-search",
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-teal",
    "navbar": "navbar-dark navbar-success",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# ============================================================
# CKEDITOR
# ============================================================

CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'toolbar_full': [
            ['Format', 'Font', 'FontSize'],
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak'],
            ['TextColor', 'BGColor'],
            ['Source', 'ShowBlocks'],
            ['Maximize'],
            ['CodeSnippet'],
        ],
        'toolbar': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll', '-', 'Scayt']},
            {'name': 'forms', 'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField']},
            '/',
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'code', 'items': ['Source']},
        ],
        'extraPlugins': ','.join(['codesnippet', 'widget', 'dialog', 'image2']),
        'codeSnippet_theme': 'monokai_sublime',
        'codeSnippet_languages': {
            'python': 'Python',
            'javascript': 'JavaScript',
            'html': 'HTML',
            'css': 'CSS',
            'bash': 'Bash',
            'sql': 'SQL',
            'json': 'JSON',
            'xml': 'XML',
        },
        'image2_alignClasses': ['image-left', 'image-center', 'image-right'],
        'image2_disableResizer': False,
    },
    'basic': {
        'toolbar': [
            ['Bold', 'Italic', 'Underline', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink', '-', 'Image', 'Table'],
        ],
        'height': 150,
        'width': '100%',
        'extraPlugins': ['image2'],
    },
}

CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_IMAGE_BACKEND = 'pillow'
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001', 'security.W019']

SITE_ID = 2


# ============================================================
# ЛОГИРОВАНИЕ (без файлового handler — переопределяется)
# ============================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'agency': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}
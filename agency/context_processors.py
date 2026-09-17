# agency/context_processors.py

from django.conf import settings
from django.core.cache import cache

from .models import SiteConfiguration


# ============================================================
# SITE CONFIG
# ============================================================

def site_config(request):
    """SiteConfiguration с кешем на 1 час."""
    config = cache.get('site_config_obj')
    if config is None:
        try:
            config = SiteConfiguration.objects.first()
            cache.set('site_config_obj', config, 60 * 60)
        except Exception:
            config = None
    return {'site_config': config}


# ============================================================
# CONTACT INFO
# ============================================================

def contact_info(request):
    """ContactPage (email, phone, telegram, ...) с кешем на 1 час."""
    page = cache.get('contact_info_obj')
    if page is None:
        try:
            from .models import ContactPage
            page = ContactPage.objects.first()
            cache.set('contact_info_obj', page, 60 * 60)
        except Exception:
            page = None
    return {'contact_info': page}


# ============================================================
# THEME
# ============================================================

def theme_context(request):
    theme = getattr(request, 'theme', settings.DEFAULT_THEME)
    return {
        'current_theme': theme,
        'available_themes': settings.AVAILABLE_THEMES,
        'theme_cookie_name': settings.THEME_COOKIE_NAME,
    }


# ============================================================
# DEBUG
# ============================================================

def debug_context(request):
    return {'debug': settings.DEBUG}


# ============================================================
# LANGUAGES
# ============================================================

def languages_context(request):
    from django.utils.translation import get_language
    current_language = get_language()
    languages = []
    for lang_code, lang_name in settings.LANGUAGES:
        languages.append({
            'code': lang_code,
            'name': lang_name,
            'current': lang_code == current_language,
        })
    return {
        'languages': languages,
        'current_language': current_language,
    }


# ============================================================
# CANONICAL
# ============================================================

def canonical_context(request):
    """Canonical URL для текущей страницы. Вью может переопределить canonical_url."""
    return {
        'canonical_url': request.build_absolute_uri(request.path),
    }


# ============================================================
# TARIFFS (для модальных форм)
# ============================================================

# ============================================================
# TARIFFS (для модальных форм)
# ============================================================

def tariffs_context(request):
    """
    Активные тарифы для модальных форм обратной связи.

    Модалка #contactModal подключается через base.html на всех страницах,
    поэтому данные должны быть доступны везде — не только на home/contact.

    Кеш отдельно для каждого языка (modeltranslation: name_ru/name_en).
    Инвалидация — в signals.py (Tariff post_save/post_delete).
    """
    from django.utils.translation import get_language

    lang = (get_language() or 'ru').split('-')[0]
    if lang not in ('ru', 'en'):
        lang = 'ru'

    cache_key = f'active_tariffs_list_{lang}'
    tariffs = cache.get(cache_key)

    if tariffs is None:
        try:
            from .models import Tariff
            tariffs = list(Tariff.objects.filter(is_active=True).order_by('order'))
            cache.set(cache_key, tariffs, 60 * 60)
        except Exception:
            tariffs = []

    return {'tariffs': tariffs}
# agency/seo_helpers.py
"""
PageSEOAdapter — обёртка над PageSEO с поддержкой override-объекта.

Приоритет:
    1. override_obj.get_seo_title(lang) / get_seo_description(lang)
    2. PageSEO.get_title(lang) / get_description(lang) / get_keywords(lang)
    3. fallback (agency/seo_defaults.py)
"""

import logging

logger = logging.getLogger(__name__)


class PageSEOAdapter:
    def __init__(self, page_seo, override_obj=None):
        self.page_seo = page_seo
        self.override_obj = override_obj

    def get_title(self, lang=None):
        if self.override_obj and hasattr(self.override_obj, 'get_seo_title'):
            try:
                value = self.override_obj.get_seo_title(lang)
                if value:
                    return value
            except Exception as e:
                logger.warning(f'PageSEOAdapter.get_seo_title: {e}')
        return self.page_seo.get_title(lang)

    def get_description(self, lang=None):
        if self.override_obj and hasattr(self.override_obj, 'get_seo_description'):
            try:
                value = self.override_obj.get_seo_description(lang)
                if value:
                    return value
            except Exception as e:
                logger.warning(f'PageSEOAdapter.get_seo_description: {e}')
        return self.page_seo.get_description(lang)

    def get_keywords(self, lang=None):
        return self.page_seo.get_keywords(lang)

    def get_og_title(self, lang=None):
        if self.override_obj and hasattr(self.override_obj, 'get_seo_title'):
            value = self.override_obj.get_seo_title(lang)
            if value:
                return value
        return self.page_seo.get_og_title(lang)

    def get_og_description(self, lang=None):
        if self.override_obj and hasattr(self.override_obj, 'get_seo_description'):
            value = self.override_obj.get_seo_description(lang)
            if value:
                return value
        return self.page_seo.get_og_description(lang)

    @property
    def page_key(self):
        return getattr(self.page_seo, 'page_key', '')

    @property
    def has_custom_title(self):
        if self.override_obj and hasattr(self.override_obj, 'get_seo_title'):
            if self.override_obj.get_seo_title():
                return True
        if hasattr(self.page_seo, 'has_custom_title'):
            return self.page_seo.has_custom_title()
        return False

    def __repr__(self):
        return (
            f'<PageSEOAdapter page_key={self.page_key!r} '
            f'override={type(self.override_obj).__name__ if self.override_obj else None}>'
        )


def make_seo_context(page_key, override_obj=None):
    from .models import PageSEO

    try:
        page_seo = PageSEO.get_for_page(page_key)
    except Exception as e:
        logger.exception(f'make_seo_context: ошибка PageSEO для {page_key}: {e}')
        page_seo = None

    if page_seo is None:
        from .seo_defaults import get_default_seo

        class _Fallback:
            page_key = page_key

            def get_title(self, lang=None):
                return get_default_seo(page_key, lang or 'ru').get('title', '')

            def get_description(self, lang=None):
                return get_default_seo(page_key, lang or 'ru').get('description', '')

            def get_keywords(self, lang=None):
                return get_default_seo(page_key, lang or 'ru').get('keywords', '')

            def get_og_title(self, lang=None):
                return self.get_title(lang)

            def get_og_description(self, lang=None):
                return self.get_description(lang)

            def has_custom_title(self, lang=None):
                return False

        page_seo = _Fallback()

    return {
        'seo': PageSEOAdapter(page_seo, override_obj),
        'seo_page_key': page_key,
    }
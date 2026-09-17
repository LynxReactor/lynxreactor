# agency/mixins.py

import logging

from django.conf import settings

from .seo_helpers import make_seo_context

logger = logging.getLogger(__name__)


class ThemeMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_theme'] = getattr(self.request, 'theme', settings.DEFAULT_THEME)
        return context


class LanguageMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils.translation import get_language
        lang = get_language() or 'ru'
        context['current_language'] = lang.split('-')[0]
        return context


class SEOContextMixin:
    seo_page_key = None

    URL_TO_PAGE = {
        # Активные страницы:
        'home': 'home',
        'contact': 'contact',
        'blog': 'blog',
        'blog_detail': 'blog',
        'blog_category': 'blog',

        # Зарезервировано на будущее:
        # когда появятся отдельные URL и вью — эти маппинги заработают
        'portfolio': 'portfolio',
        'portfolio_detail': 'portfolio',
        'about': 'about',
        'services': 'services',
        'pricing': 'pricing',
    }

    def get_seo_page_key(self):
        if self.seo_page_key:
            return self.seo_page_key
        resolver_match = getattr(self.request, 'resolver_match', None)
        url_name = resolver_match.url_name if resolver_match else None
        return self.URL_TO_PAGE.get(url_name, 'home')

    def get_seo_override(self):
        """Переопределите в наследниках — возвращайте объект с get_seo_title/get_seo_description."""
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(make_seo_context(
            self.get_seo_page_key(),
            override_obj=self.get_seo_override(),
        ))
        return context
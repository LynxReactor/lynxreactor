# agency/middleware.py

import logging
import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ThemeMiddleware(MiddlewareMixin):
    """Middleware для определения и переключения темы"""

    def process_request(self, request):
        theme = request.COOKIES.get(settings.THEME_COOKIE_NAME)
        if not theme:
            theme = request.session.get(settings.THEME_SESSION_KEY)
        if not theme or theme not in settings.AVAILABLE_THEMES:
            theme = settings.DEFAULT_THEME
        request.theme = theme

    def process_response(self, request, response):
        if hasattr(request, 'theme'):
            response.set_cookie(
                settings.THEME_COOKIE_NAME,
                request.theme,
                max_age=365 * 24 * 60 * 60,
                httponly=True,
                samesite='Lax',
            )
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware для проверки режима обслуживания.

    SiteConfiguration берётся из кэша (тот же ключ `site_config_obj`,
    что и в context_processors.site_config). Инвалидация — в signals.handle_site_config_save.
    """

    EXCLUDE_PATHS = (
        '/admin/',
        '/static/',
        '/media/',
        '/sitemap.xml',
        '/robots.txt',
        '/favicon.ico',
    )

    def process_request(self, request):
        # Пропускаем служебные пути
        for prefix in self.EXCLUDE_PATHS:
            if request.path.startswith(prefix):
                return None

        try:
            config = cache.get('site_config_obj')

            if config is None:
                # Cache miss — грузим из БД и кладём в кэш
                from .models import SiteConfiguration
                config = SiteConfiguration.objects.first()
                cache.set('site_config_obj', config, 60 * 60)

            if config and config.is_maintenance_mode:
                from django.shortcuts import render
                theme = request.COOKIES.get('theme_preference', 'light')
                return render(
                    request,
                    'agency/maintenance.html',
                    {'config': config, 'current_theme': theme},
                    status=503,
                )
        except Exception as e:
            logger.warning(f'MaintenanceModeMiddleware error: {e}')

        return None


class BlogViewCountMiddleware(MiddlewareMixin):
    """
    Middleware для подсчёта просмотров постов блога.

    счётчик инкрементится в process_response только при 200 OK.
    IP берётся через get_client_ip() — корректно за прокси.
    """

    EXCLUDE_PATHS = [
        r'^/admin/',
        r'^/static/',
        r'^/media/',
        r'^/api/',
        r'^/toggle-theme/',
    ]

    def process_request(self, request):
        """Только вычисляем slug и сохраняем в request — БЕЗ записи в БД."""
        if request.method != 'GET':
            return None

        path = request.path

        for pattern in self.EXCLUDE_PATHS:
            if re.match(pattern, path):
                return None

        if not path.startswith('/blog/'):
            return None

        # Список и категории не считаем
        if path in ('/blog/', '/blog'):
            return None
        if '/category/' in path:
            return None

        slug = path.replace('/blog/', '').strip('/')
        if not slug:
            return None

        request.blog_post_slug = slug
        return None

    def process_response(self, request, response):
        """Считаем просмотр только при успешном 200-ответе."""
        slug = getattr(request, 'blog_post_slug', None)
        if not slug:
            return response

        if response.status_code != 200:
            return response

        try:
            from .utils import get_client_ip
            client_ip = get_client_ip(request)
        except Exception:
            client_ip = request.META.get('REMOTE_ADDR', '')

        cache_key = f'blog_view_{slug}_{client_ip}'
        if cache.get(cache_key):
            return response  # Уже считали в течение часа

        from .models import BlogPost
        try:
            post = BlogPost.objects.get(slug=slug, is_published=True, is_active=True)
            post.increment_views()
            cache.set(cache_key, True, 60 * 60)
        except BlogPost.DoesNotExist:
            pass
        except Exception as e:
            logger.warning(f'BlogViewCount error: {e}')

        return response
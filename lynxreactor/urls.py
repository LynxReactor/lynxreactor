# lynxreactor/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.sitemaps.views import sitemap
from django.views.i18n import set_language

from agency.admin_views import (
    admin_send_indexnow,
    admin_test_telegram,
    admin_clear_cache,
)

from agency.sitemaps import (
    StaticViewSitemap,
    BlogSitemap,
)

from agency.views_indexnow import IndexNowKeyView

from agency.error_handlers import (
    error_400,
    error_403,
    error_404,
    error_500,
)

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    # ============================================================
    # CUSTOM ADMIN API
    # ============================================================
    path('admin/indexnow/submit/', admin_send_indexnow, name='admin_send_indexnow'),
    path('admin/telegram/test/', admin_test_telegram, name='admin_test_telegram'),
    path('admin/clear-cache/', admin_clear_cache, name='admin_clear_cache'),

    # ============================================================
    # DJANGO ADMIN
    # ============================================================
    path('admin/', admin.site.urls),
    path('admin/logout/', LogoutView.as_view(), name='admin_logout'),

    # ============================================================
    # LANGUAGE
    # ============================================================
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),

    # ============================================================
    # APP URLS
    # ============================================================
    path('', include('agency.urls')),

    # ============================================================
    # SITEMAP
    # ============================================================
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # ============================================================
    # INDEXNOW KEY
    # ============================================================
    re_path(r'^(?P<key>[a-f0-9]+)\.txt$', IndexNowKeyView.as_view(), name='indexnow_key'),
]

# ============================================================
# STATIC & MEDIA (DEVELOPMENT)
# ============================================================

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# ============================================================
# ERROR HANDLERS
# ============================================================

handler400 = 'agency.error_handlers.error_400'
handler403 = 'agency.error_handlers.error_403'
handler404 = 'agency.error_handlers.error_404'
handler500 = 'agency.error_handlers.error_500'
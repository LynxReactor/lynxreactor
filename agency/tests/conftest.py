# agency/tests/conftest.py

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from agency.models import (
    BlogCategory, BlogPost, Subscriber, Tariff,
    PortfolioSection, PortfolioItem,
    HeroSection, SiteConfiguration,
)

User = get_user_model()


# ============================================================
# AUTO-USE ФИКСТУРЫ
# ============================================================

@pytest.fixture(autouse=True)
def clear_cache():
    """Очищаем кэш до и после каждого теста."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def disable_debug_toolbar(settings):
    """
    Debug Toolbar ломает тесты: 'djdt' is not a registered namespace.
    Убираем его из INSTALLED_APPS и MIDDLEWARE для всех тестов.
    """
    if hasattr(settings, 'MIDDLEWARE'):
        settings.MIDDLEWARE = [
            mw for mw in settings.MIDDLEWARE
            if 'debug_toolbar' not in mw
        ]
    if hasattr(settings, 'INSTALLED_APPS'):
        settings.INSTALLED_APPS = [
            app for app in settings.INSTALLED_APPS
            if app != 'debug_toolbar'
        ]
    yield


@pytest.fixture(autouse=True)
def disable_turnstile(settings):
    """Отключаем Cloudflare Turnstile в тестах."""
    settings.TURNSTILE_DISABLED = True
    yield


@pytest.fixture(autouse=True)
def email_backend_locmem(settings):
    """В тестах всегда используем locmem backend для email."""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    yield


# ============================================================
# ФИКСТУРЫ
# ============================================================

@pytest.fixture
def settings_with_locmem(settings):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test_lynxreactor',
        }
    }
    return settings


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
    )


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture
def blog_category(db):
    return BlogCategory.objects.create(name='Django', slug='django', is_active=True)


@pytest.fixture
def blog_post(db, blog_category):
    return BlogPost.objects.create(
        category=blog_category,
        title='Test Post',
        slug='test-post',
        excerpt='Short excerpt for test post',
        content='<p>Full content of the post.</p>',
        author='LYNXREACTOR',
        is_published=True,
        is_active=True,
        published_at=timezone.now(),
    )


@pytest.fixture
def draft_post(db, blog_category):
    return BlogPost.objects.create(
        category=blog_category,
        title='Draft Post',
        slug='draft-post',
        excerpt='Draft excerpt',
        content='<p>Draft content.</p>',
        author='LYNXREACTOR',
        is_published=False,
        is_active=True,
    )


@pytest.fixture
def subscriber(db):
    return Subscriber.objects.create(
        email='subscriber@example.com',
        source='test',
        is_active=True,
    )


@pytest.fixture
def tariff(db):
    return Tariff.objects.create(
        name='START',
        slug='start',
        site_format='Landing Page',
        description='Landing page tariff',
        price_byn=500,
        is_active=True,
        order=1,
    )


@pytest.fixture
def portfolio_section(db):
    return PortfolioSection.objects.create(
        title_ru='Наши работы',
        title_en='Our works',
        is_active=True,
    )


@pytest.fixture
def portfolio_item(db, portfolio_section):
    return PortfolioItem.objects.create(
        section=portfolio_section,
        title_ru='Test Project',
        title_en='Test Project',
        slug='test-project',
        category_ru='Landing',
        category_en='Landing',
        description_ru='Test description',
        description_en='Test description',
        is_active=True,
    )


@pytest.fixture
def hero_contacts(db):
    return HeroSection.objects.create(
        page='contacts',
        title='Contacts',
        subtitle='Get in touch',
        description='Contact us',
        cta_text='На главную',
        cta_url='/',
        secondary_cta_text='Читать блог',
        secondary_cta_url='/blog/',
        is_active=True,
    )


@pytest.fixture
def site_config(db):
    return SiteConfiguration.objects.create(
        site_name='LYNXREACTOR',
        site_description='Test description',
    )
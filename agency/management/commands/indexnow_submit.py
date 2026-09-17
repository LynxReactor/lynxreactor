# agency/management/commands/indexnow_submit.py

"""
Management command for submitting URLs to IndexNow.

Usage:
    python manage.py indexnow_submit --urls /about/ /contact/
    python manage.py indexnow_submit --all
    python manage.py indexnow_submit --blog
    python manage.py indexnow_submit --portfolio
    python manage.py indexnow_submit --generate-key
"""

import hashlib
import secrets
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from agency.services.indexnow import indexnow_service
from agency.models import (
    BlogPost,
    PortfolioItem,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка URL в IndexNow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--urls',
            nargs='+',
            help='Список URL для отправки'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Отправить все URL из sitemap'
        )
        parser.add_argument(
            '--blog',
            action='store_true',
            help='Отправить все посты блога'
        )
        parser.add_argument(
            '--portfolio',
            action='store_true',
            help='Отправить все проекты портфолио'
        )
        parser.add_argument(
            '--generate-key',
            action='store_true',
            help='Сгенерировать новый ключ IndexNow'
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('IndexNow Submission Tool')
        self.stdout.write('=' * 50)

        # Генерация ключа
        if options.get('generate_key'):
            self.generate_key()
            return

        # Проверка настройки
        if not indexnow_service.enabled:
            self.stderr.write('[ERROR] IndexNow is disabled in settings')
            self.stderr.write('   Set INDEXNOW_ENABLED=True in .env')
            return

        if not settings.INDEXNOW_KEY:
            self.stderr.write('[ERROR] INDEXNOW_KEY is not configured')
            self.stderr.write('   Set INDEXNOW_KEY in .env')
            return

        if not settings.SITE_URL:
            self.stderr.write('[ERROR] SITE_URL is not configured')
            self.stderr.write('   Set SITE_URL in .env')
            return

        # Отправка URL
        if options.get('urls'):
            self.submit_urls(options.get('urls'))

        elif options.get('all'):
            self.submit_all()

        elif options.get('blog'):
            self.submit_blog_posts()

        elif options.get('portfolio'):
            self.submit_portfolio_items()

        else:
            self.show_help()

    # ============================================================
    # МЕТОДЫ ОТПРАВКИ
    # ============================================================

    def submit_urls(self, urls):
        """Отправка списка URL"""
        self.stdout.write(f'Sending {len(urls)} URLs...')
        success = indexnow_service.submit_urls(urls)
        if success:
            self.stdout.write('[OK] URLs sent successfully')
        else:
            self.stderr.write('[ERROR] Failed to send URLs')

    def submit_all(self):
        """Отправка всех URL из sitemap"""
        self.stdout.write('Sending all URLs from sitemap...')
        success = indexnow_service.submit_all_sitemap()
        if success:
            self.stdout.write('[OK] All URLs sent successfully')
        else:
            self.stderr.write('[ERROR] Failed to send all URLs')

    def submit_blog_posts(self):
        """Отправка всех постов блога (только опубликованные в прошлом)."""
        posts = BlogPost.objects.filter(
            is_published=True,
            is_active=True,
            published_at__lte=timezone.now(),
        )
        urls = []

        for post in posts:
            url = post.get_absolute_url()
            if url:
                urls.append(url)

        if not urls:
            self.stdout.write('[WARNING] No blog posts with URLs found')
            return

        self.stdout.write(f'Sending {len(urls)} blog posts...')
        success = indexnow_service.submit_urls(urls)
        if success:
            self.stdout.write('[OK] Blog posts sent successfully')
        else:
            self.stderr.write('[ERROR] Failed to send blog posts')

    def submit_portfolio_items(self):
        """Отправка всех проектов портфолио"""
        items = PortfolioItem.objects.filter(is_active=True)
        urls = []

        for item in items:
            url = item.get_absolute_url()
            if url:
                urls.append(url)

        if not urls:
            self.stdout.write('[WARNING] No portfolio items with URLs found')
            return

        self.stdout.write(f'Sending {len(urls)} portfolio items...')
        success = indexnow_service.submit_urls(urls)
        if success:
            self.stdout.write('[OK] Portfolio items sent successfully')
        else:
            self.stderr.write('[ERROR] Failed to send portfolio items')

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================

    def show_help(self):
        """Показать справку по использованию"""
        self.stdout.write('')
        self.stdout.write('[INFO] No parameters specified')
        self.stdout.write('')
        self.stdout.write('Usage:')
        self.stdout.write('  python manage.py indexnow_submit --urls /about/ /contact/')
        self.stdout.write('  python manage.py indexnow_submit --all')
        self.stdout.write('  python manage.py indexnow_submit --blog')
        self.stdout.write('  python manage.py indexnow_submit --portfolio')
        self.stdout.write('  python manage.py indexnow_submit --generate-key')
        self.stdout.write('')
        self.stdout.write('Note:')
        self.stdout.write('  - Services and Tariffs do NOT have individual pages')
        self.stdout.write('  - Use --urls for custom URLs')

    def generate_key(self):
        """Генерация нового ключа IndexNow"""
        random_string = secrets.token_hex(32)
        key = hashlib.sha256(random_string.encode()).hexdigest()[:32]

        self.stdout.write('')
        self.stdout.write('[NEW KEY] IndexNow key generated:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'INDEXNOW_KEY={key}')
        self.stdout.write('=' * 50)
        self.stdout.write('')
        self.stdout.write('Add this line to your .env file:')
        self.stdout.write(f'INDEXNOW_KEY={key}')
        self.stdout.write('')
        self.stdout.write('Make sure the URL is accessible:')
        site_url = settings.SITE_URL.replace('https://', '').replace('http://', '')
        self.stdout.write(f'https://{site_url}/{key}.txt')
        self.stdout.write('')
        self.stdout.write('[INFO] The key file is generated automatically via view.')
        self.stdout.write('  URL pattern: /{key}.txt -> IndexNowKeyView')
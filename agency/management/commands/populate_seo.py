# agency/management/commands/populate_seo.py

from django.core.management.base import BaseCommand
from django.db import transaction

from agency.models import PageSEO
from agency.seo_defaults import DEFAULT_SEO, SEO_PAGES


class Command(BaseCommand):
    help = 'Заполняет SEO-записи для страниц значениями по умолчанию'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Перезаписать существующие')
        parser.add_argument('--page', type=str, help='Только указанная страница')
        parser.add_argument('--lang', type=str, choices=['ru', 'en', 'all'], default='all')

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('📝 Populate PageSEO')
        self.stdout.write('=' * 60)

        force = options['force']
        page_filter = options.get('page')
        lang_filter = options.get('lang', 'all')

        pages_to_process = []
        if page_filter:
            if page_filter not in dict(SEO_PAGES):
                self.stderr.write(f'❌ Неизвестная страница: {page_filter}')
                return
            pages_to_process = [page_filter]
        else:
            pages_to_process = list(dict(SEO_PAGES).keys())

        created_count = updated_count = skipped_count = 0

        for page_key in pages_to_process:
            defaults = DEFAULT_SEO.get(page_key)
            if not defaults:
                self.stdout.write(f'⚠️  {page_key}: нет fallback')
                continue

            obj, created = PageSEO.objects.get_or_create(
                page_key=page_key, defaults={'is_active': True}
            )

            if created:
                created_count += 1
                self.stdout.write(f'✅ Создано: {obj.get_page_key_display()}')
            elif force:
                updated_count += 1
                self.stdout.write(f'🔄 Обновлено: {obj.get_page_key_display()}')
            else:
                skipped_count += 1
                self.stdout.write(f'⏭️  Пропущено: {obj.get_page_key_display()}')

            langs = ['ru', 'en'] if lang_filter == 'all' else [lang_filter]
            changed = False

            for lang in langs:
                lang_data = defaults.get(lang, {})
                if not lang_data:
                    continue
                for field in ('title', 'description', 'keywords'):
                    field_name = f'{field}_{lang}'
                    new_value = lang_data.get(field, '')
                    if not created and not force:
                        existing = getattr(obj, field_name, '') or ''
                        if existing.strip():
                            continue
                    if new_value and getattr(obj, field_name, '') != new_value:
                        setattr(obj, field_name, new_value)
                        changed = True

            if changed and (created or force):
                with transaction.atomic():
                    obj.save()

        self.stdout.write('=' * 60)
        self.stdout.write(f'📊 Создано: {created_count}, Обновлено: {updated_count}, Пропущено: {skipped_count}')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write('ℹ️  Активные страницы (SEO выводится): home, contact, blog')
        self.stdout.write('ℹ️  Зарезервированные (секции главной): portfolio, about, services, pricing')
        self.stdout.write('')
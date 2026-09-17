# agency/management/commands/test_email.py

from django.core.management.base import BaseCommand
from django.conf import settings
from agency.services.email import send_test_email


class Command(BaseCommand):
    help = 'Отправка тестового email для проверки настроек почты'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email адрес для отправки тестового письма'
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('📧 Тестирование почты')
        self.stdout.write('=' * 50)

        to_email = options.get('email') or getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')

        self.stdout.write(f'📤 Отправка тестового письма на {to_email}...')

        result = send_test_email(to_email)

        if result:
            self.stdout.write('✅ Тестовое письмо отправлено успешно!')
            self.stdout.write(f'📧 Проверьте почту: {to_email}')
        else:
            self.stderr.write('❌ Ошибка отправки тестового письма')
            self.stderr.write('   Проверьте настройки EMAIL в .env')
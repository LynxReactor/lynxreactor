# agency/management/commands/test_telegram.py

from django.core.management.base import BaseCommand
from django.conf import settings
from agency.services.telegram import telegram_service


class Command(BaseCommand):
    help = 'Тестирование Telegram-бота (отправка тестового сообщения)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('🤖 Тестирование Telegram')
        self.stdout.write('=' * 50)

        # 1. Проверка, что уведомления включены
        if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            self.stderr.write(self.style.ERROR(
                '❌ Telegram уведомления отключены '
                '(TELEGRAM_NOTIFICATIONS_ENABLED=False)'
            ))
            self.stderr.write(
                '   Установите TELEGRAM_NOTIFICATIONS_ENABLED=True в .env'
            )
            return

        # 2. Проверка, что токен настроен
        if not telegram_service.token:
            self.stderr.write(self.style.ERROR(
                '❌ TELEGRAM_BOT_TOKEN не настроен'
            ))
            self.stderr.write('   Добавьте TELEGRAM_BOT_TOKEN=<token> в .env')
            return

        # 3. Проверка, что chat_id настроен
        if not telegram_service.default_chat_id:
            self.stderr.write(self.style.ERROR(
                '❌ TELEGRAM_CHAT_ID не настроен'
            ))
            self.stderr.write('   Добавьте TELEGRAM_CHAT_ID=<chat_id> в .env')
            return

        # 4. Отправка тестового сообщения
        self.stdout.write(
            f'📤 Отправка тестового сообщения в chat_id='
            f'{telegram_service.default_chat_id}...'
        )

        result = telegram_service.send_test_message()

        if result:
            self.stdout.write(self.style.SUCCESS(
                '✅ Тестовое сообщение отправлено! Проверьте Telegram.'
            ))
        else:
            self.stderr.write(self.style.ERROR(
                '❌ Ошибка отправки — смотрите логи и TelegramLog в админке'
            ))
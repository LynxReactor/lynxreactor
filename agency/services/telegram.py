# agency/services/telegram.py

import requests
import logging
from django.conf import settings
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramService:
    """Сервис для работы с Telegram API"""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.notifications_enabled = settings.TELEGRAM_NOTIFICATIONS_ENABLED
        self.site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')

    def send_message(self, message: str, chat_id: Optional[str] = None, parse_mode: str = 'HTML') -> bool:
        """
        Отправка сообщения в Telegram

        Args:
            message: Текст сообщения
            chat_id: ID чата (если None, используется default)
            parse_mode: HTML или Markdown

        Returns:
            bool: успешно ли отправлено
        """
        if not self.token or self.token == 'your_bot_token_here':
            logger.warning("Telegram token not configured")
            return False

        if not self.notifications_enabled:
            logger.info("Telegram notifications disabled")
            return False

        chat_id = chat_id or self.default_chat_id

        if not chat_id or chat_id == 'your_chat_id_here':
            logger.warning("Telegram chat_id not configured")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True,
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            # Логируем успешную отправку
            self._log_send(chat_id, message, True)

            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            self._log_send(chat_id, message, False, str(e))
            return False

    def _get_admin_url(self, contact_request) -> str:
        """
        Формирует URL для админки заявки
        """
        return f"{self.site_url}/admin/agency/contactrequest/{contact_request.id}/change/"

    def send_contact_notification(self, contact_request) -> bool:
        """
        Отправка уведомления о новой заявке
        """
        if not self.notifications_enabled:
            logger.info("Telegram notifications disabled, skipping")
            return False

        if not contact_request:
            logger.warning("ContactRequest is None, skipping")
            return False

        admin_url = self._get_admin_url(contact_request)

        # Формируем сообщение
        message = f"""
📋 <b>Новая заявка с сайта</b>

👤 <b>Имя:</b> {contact_request.name}
📧 <b>Email:</b> {contact_request.email}
📱 <b>Телефон:</b> {contact_request.phone or 'Не указан'}
📱 <b>Способ связи:</b> {contact_request.get_contact_method_display() or contact_request.contact_method}
📞 <b>Контакт:</b> {contact_request.contact_value or 'Не указан'}

📝 <b>Сообщение:</b>
{contact_request.message[:500]}

📅 <b>Дата:</b> {contact_request.created_at.strftime('%d.%m.%Y %H:%M')}
🌐 <b>IP:</b> {contact_request.ip_address or 'Не определен'}

🔗 <b>Ссылка в админке:</b> {admin_url}
        """

        return self.send_message(message)

    def send_error_notification(self, request, error: Exception, traceback: str) -> bool:
        """
        Отправка уведомления об ошибке
        """
        if not getattr(settings, 'TELEGRAM_DEBUG_NOTIFICATIONS', False):
            return False

        message = f"""
❌ <b>Ошибка на сайте</b>

📍 <b>URL:</b> {request.build_absolute_uri() if request else 'Unknown'}
🔧 <b>Ошибка:</b> {str(error)}
👤 <b>Пользователь:</b> {request.user.username if request and hasattr(request, 'user') else 'Anonymous'}
📅 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

<b>Трассировка:</b>
<code>{traceback[:1000]}</code>
        """

        # Отправляем в debug чат
        chat_id = getattr(settings, 'TELEGRAM_DEBUG_CHAT_ID', None) or self.default_chat_id
        return self.send_message(message, chat_id)

    def send_status_notification(self, status: str = 'running', uptime: str = 'N/A',
                                  memory: str = 'N/A', load: str = 'N/A') -> bool:
        """
        Отправка уведомления о статусе сервера
        """
        if not getattr(settings, 'TELEGRAM_DEBUG_NOTIFICATIONS', False):
            return False

        message = f"""
🖥️ <b>Статус сервера</b>

📊 <b>Статус:</b> {status}
⏱️ <b>Аптайм:</b> {uptime}
🧠 <b>Память:</b> {memory}
📈 <b>Нагрузка:</b> {load}
📅 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """

        return self.send_message(message)

    def send_test_message(self) -> bool:
        """
        Отправка тестового сообщения для проверки бота
        """
        test_message = f"""
🔬 <b>TELEGRAM TEST MESSAGE</b> 🔬

✅ Бот настроен правильно!
📅 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🚀 <b>Статус:</b> Работает
🌐 <b>Сайт:</b> {self.site_url}

<i>Если вы видите это сообщение, значит все работает!</i>
        """

        return self.send_message(test_message)

    def _log_send(self, chat_id: str, message: str, is_sent: bool, error: Optional[str] = None) -> None:
        """
        Логирование отправки сообщения
        """
        try:
            from agency.models import TelegramLog

            # Укорачиваем сообщение для лога
            message_preview = message[:200]
            if len(message) > 200:
                message_preview += '...'

            TelegramLog.objects.create(
                chat_id=chat_id,
                message=message_preview,
                is_sent=is_sent,
                error=error or ''
            )
        except Exception as e:
            logger.error(f"Failed to log Telegram message: {str(e)}")


# Синглтон для использования в приложении
telegram_service = TelegramService()


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ УДОБСТВА
# ============================================================

def send_contact_notification(contact_request) -> bool:
    """
    Упрощённая функция для отправки уведомления о заявке
    """
    return telegram_service.send_contact_notification(contact_request)


def send_test_message() -> bool:
    """
    Упрощённая функция для отправки тестового сообщения
    """
    return telegram_service.send_test_message()
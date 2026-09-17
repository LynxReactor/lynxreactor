# agency/services/email.py

"""
Утилиты для отправки email
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from ..models import SiteConfiguration, ContactPage
from django.utils.translation import gettext as _, override
import logging
from smtplib import SMTPException

# Логгер
logger = logging.getLogger(__name__)


class ContactNotificationError(SMTPException):
    """
    Критичный канал доставки не сработал (client/admin email).

    Наследуемся от SMTPException, чтобы попасть в autoretry_for
    в send_contact_notification_task.

    Используется как fallback, когда send_client_confirmation /
    send_admin_notification вернули False, но не бросили исключение
    (например, сработал внутренний except в send_*).
    """
    pass


def send_client_confirmation(contact, site_url=None):
    logger.info(f"🔵 send_client_confirmation called for {contact.email}")

    if not site_url:
        site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')

    config = SiteConfiguration.objects.first()
    contact_page = ContactPage.objects.first()

    # ✅ Язык из заявки (или 'ru' по умолчанию)
    lang = getattr(contact, 'language', 'ru') or 'ru'

    with override(lang):
        context = {
            'contact': contact,
            'site_config': config,
            'contact_info': contact_page,
            'site_url': site_url,
            'now': timezone.now(),
        }

        try:
            html_content = render_to_string('agency/emails/client_confirmation.html', context)
            plain_content = strip_tags(html_content)
        except Exception as e:
            logger.exception(f"⚠️ Template error in client_confirmation: {e}")
            plain_content = f"""
Здравствуйте, {contact.name}!

Спасибо, что обратились в LYNXREACTOR.

📋 Номер заявки: #{contact.id}
📅 Дата: {contact.created_at.strftime('%d.%m.%Y %H:%M')}

С уважением,
Команда LYNXREACTOR
{site_url}
"""
            html_content = plain_content.replace('\n', '<br>')

        subject = _("Ваша заявка на сайте LYNXREACTOR")

    try:
        logger.info(f'📧 Sending client confirmation email to {contact.email}...')
        result = send_mail(
            subject, plain_content, settings.DEFAULT_FROM_EMAIL,
            [contact.email], html_message=html_content, fail_silently=False,
        )
        logger.info(f'✅ Client confirmation email sent to {contact.email}, result: {result}')
        return True

    except SMTPException:
        # Пробрасываем SMTP-ошибки наверх — Celery через autoretry_for
        # / dont_autoretry_for решит, ретраить или нет.
        # SMTPConnectError  → retry
        # SMTPRecipientsRefused → НЕ retry (в dont_autoretry_for)
        logger.exception(f'❌ SMTP error sending client email to {contact.email}')
        raise

    except Exception as e:
        # Неожиданные ошибки (шаблон, кодировка) — превращаем в False,
        # send_contact_notifications обернёт в ContactNotificationError → retry
        logger.exception(f'❌ Non-SMTP error sending client confirmation email: {e}')
        return False


def send_admin_notification(contact, admin_email=None, site_url=None):
    """
    Отправка уведомления администратору о новой заявке
    """
    if not admin_email:
        admin_email = getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')

    logger.info(f"🔵 send_admin_notification called for {admin_email}")

    if not site_url:
        site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')

    config = SiteConfiguration.objects.first()
    admin_url = f"{site_url}/admin/agency/contactrequest/{contact.id}/change/"

    context = {
        'contact': contact,
        'site_config': config,
        'site_url': site_url,
        'admin_url': admin_url,
        'now': timezone.now(),
    }

    try:
        html_content = render_to_string('agency/emails/admin_notification.html', context)
        plain_content = strip_tags(html_content)
    except Exception as e:
        logger.exception(f"⚠️ Template error in admin_notification: {e}")
        # Fallback plain text
        plain_content = f"""
Новая заявка с сайта LYNXREACTOR

👤 Имя: {contact.name}
📧 Email: {contact.email}
📱 Телефон: {contact.phone or 'Не указан'}

📝 Сообщение:
{contact.message}

📅 Дата: {contact.created_at.strftime('%d.%m.%Y %H:%M')}
🌐 IP: {contact.ip_address or 'Не определен'}

🔗 Ссылка в админке: {admin_url}
"""
        html_content = plain_content.replace('\n', '<br>')

    subject = f"🔔 Новая заявка от {contact.name} — LYNXREACTOR"

    try:
        logger.info(f'📧 Sending admin notification to {admin_email}...')
        result = send_mail(
            subject, plain_content, settings.DEFAULT_FROM_EMAIL,
            [admin_email], html_message=html_content, fail_silently=False,
        )
        logger.info(f'✅ Admin notification email sent to {admin_email}, result: {result}')
        return True

    except SMTPException:
        logger.exception(f'❌ SMTP error sending admin email to {admin_email}')
        raise

    except Exception as e:
        logger.exception(f'❌ Non-SMTP error sending admin notification email: {e}')
        return False


def send_contact_notifications(contact):
    """
    Отправка всех уведомлений о новой заявке.

    Критичные каналы (client/admin email) — при провале raise'ят
    исключение, чтобы Celery сделал retry (см. tasks.py).

    Telegram — вторичный канал: ошибки логируются, но не поднимают
    исключение. Заявка уже в БД, email доставлены — терять задачу
    из-за недоступного Telegram нельзя.
    """
    logger.info("send_contact_notifications for request #%s", contact.id)
    logger.info("  contact.email: %s", contact.email)
    logger.info("  settings.CONTACT_FORM_EMAIL: %s", settings.CONTACT_FORM_EMAIL)

    results = {
        'client_email': False,
        'admin_email': False,
        'telegram': False,
    }

    client_error = None
    admin_error = None

    # --- 1. Письмо клиенту (критично, если contact.email задан) ---
    if contact.email:
        logger.info('Sending client email: %s', contact.email)
        try:
            results['client_email'] = send_client_confirmation(contact)
            if not results['client_email']:
                client_error = ContactNotificationError(
                    f'Client email failed for contact #{contact.id}'
                )
        except SMTPException as e:
            client_error = e
            logger.exception('Client email SMTP error for contact #%s', contact.id)
        except Exception as e:
            client_error = e
            logger.exception('Client email unexpected error for contact #%s', contact.id)
    else:
        logger.warning('Client email not provided — skipping client notification')

    # --- 2. Письмо администратору (критично) ---
    admin_email = getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')
    logger.info('Sending admin email: %s', admin_email)
    try:
        results['admin_email'] = send_admin_notification(contact)
        if not results['admin_email']:
            admin_error = ContactNotificationError(
                f'Admin email failed for contact #{contact.id}'
            )
    except SMTPException as e:
        admin_error = e
        logger.exception('Admin email SMTP error for contact #%s', contact.id)
    except Exception as e:
        admin_error = e
        logger.exception('Admin email unexpected error for contact #%s', contact.id)

    # --- 3. Telegram (вторично, НЕ raise) ---
    try:
        from .telegram import telegram_service
        if settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            logger.info('Sending Telegram notification')
            results['telegram'] = telegram_service.send_contact_notification(contact)
        else:
            logger.info('Telegram notifications disabled')
    except Exception as e:
        logger.exception('Telegram error (non-critical, task continues): %s', e)

    # --- Итог ---
    logger.info('Contact #%s notification results: %s', contact.id, results)

    # Raise исходного исключения — Celery через autoretry_for
    # поймёт, что нужно сделать retry (для временных ошибок).
    # Постоянные ошибки (SMTPRecipientsRefused и т.п.) в dont_autoretry_for,
    # поэтому задача упадёт без retry.
    if client_error is not None:
        raise client_error

    if admin_error is not None:
        raise admin_error

    return results


def send_test_email(to_email=None):
    """
    Отправка тестового email для проверки настроек почты
    """
    if not to_email:
        to_email = getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')

    site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')

    subject = 'Тестовое письмо от LYNXREACTOR'
    message = f"""
Это тестовое письмо для проверки работы почты.

Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}
Сайт: {site_url}

Если вы получили это письмо, значит почта работает правильно!

С уважением,
LYNXREACTOR Studio
{site_url}
"""

    try:
        logger.info(f'📧 Sending test email to {to_email}...')
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info(f"✅ Test email sent to {to_email}, result: {result}")
        return True
    except Exception as e:
        logger.exception(f"❌ Failed to send test email to {to_email}: {e}")
        return False


def get_admin_url(contact):
    """
    Вспомогательная функция для получения URL заявки в админке
    """
    site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')
    return f"{site_url}/admin/agency/contactrequest/{contact.id}/change/"


def send_subscribe_notification(subscriber):
    """
    Уведомление админу о новом подписчике.
    """
    admin_email = getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')
    site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')

    logger.info(f"🔵 send_subscribe_notification for {subscriber.email}")

    subject = f"📬 Новый подписчик — LYNXREACTOR"

    plain_content = f"""
Новая подписка на обновления блога

📧 Email: {subscriber.email}
📌 Источник: {subscriber.source}
🌐 IP: {subscriber.ip_address or 'Не определен'}
📅 Дата: {subscriber.created_at.strftime('%d.%m.%Y %H:%M')}

🔗 Список подписчиков: {site_url}/admin/agency/subscriber/
"""

    try:
        result = send_mail(
            subject,
            plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
        logger.info(f'✅ Subscribe notification sent to {admin_email}')
        return True
    except Exception as e:
        logger.exception(f'❌ Failed to send subscribe notification: {e}')
        return False
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

# Логгер
logger = logging.getLogger(__name__)


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
        logger.info(f'📧 Sending client confirmation email to {contact.email} (lang={lang})...')
        result = send_mail(
            subject,
            plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [contact.email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f'✅ Client confirmation email sent to {contact.email}, result: {result}')
        return True

    except Exception as e:
        logger.exception(f'❌ Failed to send client confirmation email to {contact.email}: {e}')
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
            subject,
            plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f'✅ Admin notification email sent to {admin_email}, result: {result}')
        return True

    except Exception as e:
        logger.exception(f'❌ Failed to send admin notification email to {admin_email}: {e}')
        return False


def send_contact_notifications(contact):
    """
    Отправка всех уведомлений о новой заявке:
    1. Письмо клиенту
    2. Письмо администратору
    3. Telegram уведомление (если настроен)
    """
    logger.info(f"🔵🔵🔵 send_contact_notifications called for request #{contact.id}")
    logger.info(f"   contact.email: {contact.email}")
    logger.info(f"   settings.CONTACT_FORM_EMAIL: {settings.CONTACT_FORM_EMAIL}")

    results = {
        'client_email': False,
        'admin_email': False,
        'telegram': False,
    }

    # 1. Письмо клиенту
    if contact.email:
        logger.info(f'📧 Sending client email: {contact.email}')
        try:
            results['client_email'] = send_client_confirmation(contact)
            logger.info(f'  Result: {results["client_email"]}')
        except Exception as e:
            logger.exception(f'  ❌ Error sending client email: {e}')
    else:
        logger.warning('⚠️ Client email not provided')

    # 2. Письмо администратору
    admin_email = getattr(settings, 'CONTACT_FORM_EMAIL', 'lynxreacto@gmail.com')
    logger.info(f'📧 Sending admin email: {admin_email}')
    try:
        results['admin_email'] = send_admin_notification(contact)
        logger.info(f'  Result: {results["admin_email"]}')
    except Exception as e:
        logger.exception(f'  ❌ Error sending admin email: {e}')

    # 3. Telegram уведомление
    try:
        from .telegram import telegram_service
        if settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            logger.info('📱 Sending Telegram notification')
            results['telegram'] = telegram_service.send_contact_notification(contact)
            logger.info(f'  Result: {results["telegram"]}')
        else:
            logger.info('📱 Telegram notifications disabled')
    except Exception as e:
        logger.exception(f'❌ Telegram error: {e}')

    logger.info(f'✅ FINAL RESULTS: {results}')
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
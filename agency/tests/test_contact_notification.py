# agency/tests/test_contact_notification.py
"""
Тесты Celery-задачи send_contact_notification_task.

Проверяем:
  - постановка задачи в очередь (signals)
  - постановка только после transaction.on_commit
  - retry при временных SMTP-ошибках (через .apply())
  - Telegram failure НЕ роняет задачу
  - постоянные SMTP-ошибки пробрасываются без глотания

Важно: dev.py ставит CELERY_TASK_ALWAYS_EAGER=True + EAGER_PROPAGATES=True,
поэтому .delay() выполняется синхронно. Для тестов retry используем .apply().

В EAGER-режиме Celery оборачивает исходное исключение в celery.exceptions.Retry
при срабатывании autoretry_for. Проверяем именно это — Retry.exc содержит
исходное исключение (SMTPConnectError / ContactNotificationError).

on_commit тестируется через фикстуру django_capture_on_commit_callbacks —
pytest-django оборачивает каждый тест в транзакцию, поэтому реального
commit не происходит, и on_commit-callback без фикстуры не вызовется.
"""
from smtplib import (
    SMTPRecipientsRefused,
    SMTPConnectError,
    SMTPAuthenticationError,
    SMTPNotSupportedError,
)
from unittest.mock import patch

import pytest
from celery.exceptions import Retry
from django.db import transaction

from agency.models import ContactRequest
from agency.tasks import send_contact_notification_task


# ============================================================
# ФИКСТУРЫ
# ============================================================

@pytest.fixture
def contact_payload():
    return {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'message': 'Test message with enough characters for validation.',
        'contact_method': 'email',
        'contact_value': 'jane@example.com',
        'turnstile_verified': True,
    }


# ============================================================
# 1. ContactRequest → task queued
# ============================================================

@pytest.mark.django_db
def test_contact_request_creates_celery_task(
    contact_payload, django_capture_on_commit_callbacks,
):
    """
    ContactRequest.objects.create() → сигнал → .delay() вызван.

    Используем django_capture_on_commit_callbacks(execute=True) —
    эмулирует реальный commit, заставляя on_commit-callback выполниться.
    """
    with patch(
        'agency.signals.send_contact_notification_task.delay'
    ) as mock_delay:
        with django_capture_on_commit_callbacks(execute=True):
            contact = ContactRequest.objects.create(**contact_payload)

    mock_delay.assert_called_once_with(contact.id)


# ============================================================
# 2. on_commit: task НЕ вызывается до commit транзакции
# ============================================================

@pytest.mark.django_db
def test_task_queued_only_after_transaction_commit(
    contact_payload, django_capture_on_commit_callbacks,
):
    """
    Ключевой тест on_commit.

    Внутри transaction.atomic() задача не должна ставиться
    (колбэк зарегистрирован, но ещё не выполнен).

    После выхода из atomic() и ручного вызова колбэков —
    .delay() должен быть вызван.
    """
    with patch(
        'agency.signals.send_contact_notification_task.delay'
    ) as mock_delay:
        # capture без execute=True — колбэки копятся, но не выполняются
        with django_capture_on_commit_callbacks() as callbacks:
            with transaction.atomic():
                contact = ContactRequest.objects.create(**contact_payload)
                # Внутри транзакции — ещё НЕ вызвано
                mock_delay.assert_not_called()

            # Вышли из atomic(), но колбэк всё ещё не выполнен —
            # эмуляция «commit произошёл, но callback ещё в очереди»
            mock_delay.assert_not_called()

        # Вручную «прожигаем» колбэки — эмуляция commit
        for callback in callbacks:
            callback()

    mock_delay.assert_called_once_with(contact.id)


# ============================================================
# 3. Временная SMTP-ошибка → retry (через .apply)
# ============================================================

@pytest.mark.django_db
def test_smtp_temporary_error_triggers_retry(contact_payload):
    """
    SMTPConnectError (временная) → задача raise'ит Retry
    с исходным SMTPConnectError внутри → Celery сделает retry.

    В EAGER-режиме Celery оборачивает исключение в celery.exceptions.Retry.
    Проверяем именно это: Retry.exc — исходный SMTPConnectError.
    """
    contact = ContactRequest.objects.create(**contact_payload)

    with patch(
        'agency.services.email.send_client_confirmation',
        side_effect=SMTPConnectError(421, 'Service not available'),
    ), patch(
        'agency.services.email.send_admin_notification',
        return_value=True,
    ):
        with pytest.raises(Retry) as exc_info:
            send_contact_notification_task.apply(args=[contact.id]).get()

    # Celery завернул наше SMTP-исключение в Retry
    assert isinstance(exc_info.value.exc, SMTPConnectError)


# ============================================================
# 4. Telegram failure НЕ роняет задачу
# ============================================================

@pytest.mark.django_db
def test_telegram_failure_doesnt_fail_task(contact_payload, settings):
    """
    Telegram недоступен → задача завершается успешно.
    Client + admin email доставлены.
    """
    settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
    contact = ContactRequest.objects.create(**contact_payload)

    with patch(
        'agency.services.email.send_client_confirmation',
        return_value=True,
    ), patch(
        'agency.services.email.send_admin_notification',
        return_value=True,
    ), patch(
        'agency.services.telegram.telegram_service.send_contact_notification',
        side_effect=ConnectionError('Telegram down'),
    ):
        # Не должно бросить
        result = send_contact_notification_task.apply(args=[contact.id]).get()

    assert 'client_email' in result or 'admin_email' in result


# ============================================================
# 5. Admin email failure → retry (raise)
# ============================================================

@pytest.mark.django_db
def test_admin_email_failure_triggers_retry(contact_payload):
    """
    send_admin_notification → False → ContactNotificationError → Retry.
    """
    from agency.services.email import ContactNotificationError

    contact = ContactRequest.objects.create(**contact_payload)

    with patch(
        'agency.services.email.send_client_confirmation',
        return_value=True,
    ), patch(
        'agency.services.email.send_admin_notification',
        return_value=False,
    ):
        with pytest.raises(Retry) as exc_info:
            send_contact_notification_task.apply(args=[contact.id]).get()

    assert isinstance(exc_info.value.exc, ContactNotificationError)


# ============================================================
# 6. Client email failure → retry (raise)
# ============================================================

@pytest.mark.django_db
def test_client_email_failure_triggers_retry(contact_payload):
    """
    send_client_confirmation → False → ContactNotificationError → Retry.
    """
    from agency.services.email import ContactNotificationError

    contact = ContactRequest.objects.create(**contact_payload)

    with patch(
        'agency.services.email.send_client_confirmation',
        return_value=False,
    ), patch(
        'agency.services.email.send_admin_notification',
        return_value=True,
    ):
        with pytest.raises(Retry) as exc_info:
            send_contact_notification_task.apply(args=[contact.id]).get()

    assert isinstance(exc_info.value.exc, ContactNotificationError)


# ============================================================
# 7. Постоянная SMTP-ошибка НЕ должна retry
# ============================================================

@pytest.mark.django_db
def test_permanent_smtp_error_not_in_autoretry(contact_payload):
    """
    SMTPRecipientsRefused (битый адрес) — постоянная.
    Должна быть в dont_autoretry_for, чтобы Celery не ретраил.

    SMTPException в autoretry_for — fallback, но dont_autoretry_for
    имеет приоритет: если исключение есть в обоих списках — retry НЕ будет.
    """
    task = send_contact_notification_task
    dont = getattr(task, 'dont_autoretry_for', ()) or ()

    assert SMTPRecipientsRefused in dont
    assert SMTPAuthenticationError in dont
    assert SMTPNotSupportedError in dont


@pytest.mark.django_db
def test_permanent_smtp_error_not_retried_end_to_end(contact_payload):
    """
    End-to-end: постоянная SMTP-ошибка не должна retry.

    SMTPRecipientsRefused идёт из send_mail → пробрасывается
    через send_client_confirmation → ловится в send_contact_notifications
    → raise → Celery видит тип в dont_autoretry_for → задача падает
    без Retry.

    Проверяем именно это: pytest.raises(SMTPRecipientsRefused),
    а НЕ Retry.
    """
    contact = ContactRequest.objects.create(**contact_payload)

    with patch(
        'agency.services.email.send_client_confirmation',
        side_effect=SMTPRecipientsRefused(
            {'bad@example.com': (550, b'No such user')}
        ),
    ), patch(
        'agency.services.email.send_admin_notification',
        return_value=True,
    ):
        # Должно поднять SMTPRecipientsRefused НАПРЯМУЮ,
        # без обёртки в Retry — значит Celery не будет ретраить.
        with pytest.raises(SMTPRecipientsRefused):
            send_contact_notification_task.apply(args=[contact.id]).get()
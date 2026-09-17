# agency/admin_actions.py

from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
import csv
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================
# ЭКСПОРТ
# ============================================================

def export_selected_as_csv(modeladmin, request, queryset):
    """Экспорт выбранных записей в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"export_{queryset.model.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    fields = [f for f in queryset.model._meta.fields]
    writer.writerow([f.verbose_name for f in fields])

    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name)
            if hasattr(value, 'strftime'):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, bool):
                value = 'Да' if value else 'Нет'
            elif value is None:
                value = ''
            row.append(str(value))
        writer.writerow(row)

    modeladmin.message_user(request, f'✅ Экспортировано {queryset.count()} записей')
    return response

export_selected_as_csv.short_description = "📤 Экспортировать выбранные в CSV"


def export_selected_as_json(modeladmin, request, queryset):
    """Экспорт выбранных записей в JSON"""
    data = []
    for obj in queryset:
        obj_data = {}
        for field in queryset.model._meta.fields:
            value = getattr(obj, field.name)
            if hasattr(value, 'strftime'):
                value = value.isoformat()
            elif value is None:
                value = None
            obj_data[field.name] = value
        data.append(obj_data)

    response = HttpResponse(content_type='application/json; charset=utf-8')
    filename = f"export_{queryset.model.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    json.dump(data, response, ensure_ascii=False, indent=2)

    modeladmin.message_user(request, f'✅ Экспортировано {queryset.count()} записей')
    return response

export_selected_as_json.short_description = "📤 Экспортировать выбранные в JSON"


# ============================================================
# ДУБЛИРОВАНИЕ
# ============================================================

def duplicate_selected(modeladmin, request, queryset):
    """
    Дублирование выбранных записей.

    Дополнительно:
      - BlogPost: сбрасывает views/likes/dislikes/published_at/is_published
      - BlogPostVote не копируется (OneToOne-подобная связь)
    """
    from django.db import IntegrityError

    count = 0
    errors = 0

    for obj in queryset:
        try:
            obj.pk = None

            # Сбрасываем счётчики и статус публикации у BlogPost
            if obj.__class__.__name__ == 'BlogPost':
                obj.views = 0
                obj.likes = 0
                obj.dislikes = 0
                obj.published_at = None
                obj.is_published = False

            # Уникальный slug
            if hasattr(obj, 'slug') and obj.slug:
                obj.slug = f"{obj.slug}-copy-{count + 1}"

            obj.save()
            count += 1
        except IntegrityError as e:
            errors += 1
            logger.warning(f'Не удалось дублировать {obj.__class__.__name__}: {e}')
        except Exception as e:
            errors += 1
            logger.exception(f'Ошибка дублирования: {e}')

    if count:
        modeladmin.message_user(request, f'✅ Создано {count} копий')
    if errors:
        modeladmin.message_user(
            request,
            f'⚠️ Не удалось дублировать {errors} записей (см. логи)',
            level=messages.WARNING,
        )

duplicate_selected.short_description = "📋 Дублировать выбранные"


# ============================================================
# АКТИВНОСТЬ
# ============================================================

def set_active_true(modeladmin, request, queryset):
    count = queryset.update(is_active=True)
    modeladmin.message_user(request, f'✅ Активировано {count} записей')

set_active_true.short_description = "✅ Активировать выбранные"


def set_active_false(modeladmin, request, queryset):
    count = queryset.update(is_active=False)
    modeladmin.message_user(request, f'✅ Деактивировано {count} записей')

set_active_false.short_description = "❌ Деактивировать выбранные"


# ============================================================
# EMAIL
# ============================================================

def send_test_email(modeladmin, request, queryset):
    emails = [obj.email for obj in queryset if hasattr(obj, 'email') and obj.email]

    if not emails:
        modeladmin.message_user(request, '⚠️ Не найдены email адреса', level=messages.ERROR)
        return

    try:
        send_mail(
            'Тестовое письмо от LYNXREACTOR',
            f'Это тестовое письмо.\n\n'
            f'Количество получателей: {len(emails)}\n'
            f'Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}\n\n'
            f'С уважением,\nLYNXREACTOR Studio',
            settings.DEFAULT_FROM_EMAIL,
            emails,
            fail_silently=False,
        )
        modeladmin.message_user(request, f'✅ Письмо отправлено на {len(emails)} адресов')
    except Exception as e:
        logger.error(f'Ошибка отправки email: {e}')
        modeladmin.message_user(request, f'❌ Ошибка отправки: {str(e)}', level=messages.ERROR)

send_test_email.short_description = "📧 Отправить тестовое письмо"


# ============================================================
# TELEGRAM
# ============================================================

def send_to_telegram(modeladmin, request, queryset):
    from agency.services.telegram import telegram_service

    if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
        modeladmin.message_user(request, '⚠️ Telegram уведомления отключены', level=messages.ERROR)
        return

    if not telegram_service.token:
        modeladmin.message_user(request, '⚠️ Telegram Bot Token не настроен', level=messages.ERROR)
        return

    count = 0
    for obj in queryset:
        try:
            message = f"📋 <b>Запись из админки</b>\n\n"
            for field in obj._meta.fields:
                value = getattr(obj, field.name)
                if value and not callable(value):
                    if hasattr(value, 'strftime'):
                        value = value.strftime('%d.%m.%Y %H:%M')
                    message += f"<b>{field.verbose_name}:</b> {value}\n"
            if telegram_service.send_message(message):
                count += 1
        except Exception as e:
            logger.error(f'Ошибка отправки в Telegram: {e}')

    modeladmin.message_user(request, f'✅ Отправлено {count} записей в Telegram')

send_to_telegram.short_description = "📱 Отправить в Telegram"


# ============================================================
# СТАТУСЫ ЗАЯВОК
# ============================================================

def mark_as_new(modeladmin, request, queryset):
    count = queryset.update(status='new')
    modeladmin.message_user(request, f'✅ Отмечено {count} заявок как "Новые"')

mark_as_new.short_description = "🆕 Отметить как новые"


def mark_as_in_progress(modeladmin, request, queryset):
    count = queryset.update(status='in_progress')
    modeladmin.message_user(request, f'✅ Отмечено {count} заявок как "В работе"')

mark_as_in_progress.short_description = "🔄 Отметить как в работе"


def mark_as_completed(modeladmin, request, queryset):
    count = queryset.update(status='completed')
    modeladmin.message_user(request, f'✅ Отмечено {count} заявок как "Завершенные"')

mark_as_completed.short_description = "✅ Отметить как завершенные"


def mark_as_rejected(modeladmin, request, queryset):
    count = queryset.update(status='rejected')
    modeladmin.message_user(request, f'✅ Отмечено {count} заявок как "Отклоненные"')

mark_as_rejected.short_description = "❌ Отметить как отклоненные"


# ============================================================
# БЛОГ
# ============================================================

def publish_selected(modeladmin, request, queryset):
    from django.utils import timezone
    count = 0
    for obj in queryset:
        if hasattr(obj, 'is_published'):
            obj.is_published = True
            if hasattr(obj, 'published_at') and not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()
            count += 1
    modeladmin.message_user(request, f'✅ Опубликовано {count} записей')

publish_selected.short_description = "📰 Опубликовать выбранные"


def unpublish_selected(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        if hasattr(obj, 'is_published'):
            obj.is_published = False
            obj.save()
            count += 1
    modeladmin.message_user(request, f'✅ Снято с публикации {count} записей')

unpublish_selected.short_description = "📕 Снять с публикации"

def send_newsletter(modeladmin, request, queryset):
    """
    Отправка рассылки о выбранных постах блога.
    Запускает Celery-задачу send_blog_post_newsletter для каждого поста.
    Будущие посты (published_at > now) исключаются.
    """
    from django.utils import timezone
    from .tasks import send_blog_post_newsletter

    now = timezone.now()
    selected_posts = [
        obj for obj in queryset
        if obj.is_published
        and obj.published_at
        and obj.published_at <= now
    ]

    if not selected_posts:
        modeladmin.message_user(
            request,
            '⚠️ Среди выбранных нет опубликованных постов (включая запланированные)',
            level=messages.WARNING,
        )
        return

    queued = 0
    for post in selected_posts:
        try:
            send_blog_post_newsletter.delay(post.id)
            queued += 1
        except Exception as e:
            logger.exception(f'Newsletter error for post #{post.pk}: {e}')

    if queued:
        modeladmin.message_user(
            request,
            f'📤 Рассылка запущена для {queued} из {len(selected_posts)} постов',
        )
    else:
        modeladmin.message_user(
            request,
            '⚠️ Не удалось запустить рассылку (см. логи)',
            level=messages.WARNING,
        )

send_newsletter.short_description = "📨 Отправить рассылку о выбранных постах"
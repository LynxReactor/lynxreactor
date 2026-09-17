# agency/admin_views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================
# INDEXNOW
# ============================================================

@staff_member_required
@require_POST
def admin_send_indexnow(request):
    """Admin API для отправки страницы в IndexNow"""
    try:
        # ✅ Lazy import — не падаем, если requests не установлен
        from .services.indexnow import IndexNowService

        data = json.loads(request.body)
        url = data.get('url')
        urls = data.get('urls', [])

        if not url and not urls:
            return JsonResponse({'success': False, 'message': 'URL не указан'}, status=400)

        if url:
            urls = [url]

        logger.info(f'📤 IndexNow submission: {len(urls)} URLs')

        if not settings.INDEXNOW_ENABLED:
            return JsonResponse(
                {'success': False, 'message': 'IndexNow отключен в настройках'},
                status=400,
            )

        indexnow = IndexNowService()
        result = indexnow.submit_urls(urls)

        if result:
            return JsonResponse({
                'success': True,
                'message': f'✅ Отправлено {len(urls)} URL в IndexNow',
            })
        return JsonResponse(
            {'success': False, 'message': '❌ Ошибка отправки в IndexNow'},
            status=400,
        )

    except json.JSONDecodeError:
        logger.warning('❌ Invalid JSON in IndexNow request')
        return JsonResponse(
            {'success': False, 'message': 'Неверный формат JSON'},
            status=400,
        )
    except Exception as e:
        logger.exception(f'❌ IndexNow error: {e}')
        return JsonResponse(
            {'success': False, 'message': 'Внутренняя ошибка сервера'},
            status=500,
        )


# ============================================================
# TELEGRAM TEST
# ============================================================

@staff_member_required
@require_POST
def admin_test_telegram(request):
    try:
        from agency.services.telegram import telegram_service

        if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            return JsonResponse(
                {'success': False, 'message': 'Telegram уведомления отключены в настройках'},
                status=400,
            )

        if not telegram_service.token:
            return JsonResponse(
                {'success': False, 'message': 'Telegram Bot Token не настроен'},
                status=400,
            )

        success = telegram_service.send_test_message()

        if success:
            return JsonResponse({
                'success': True,
                'message': '✅ Тестовое сообщение отправлено в Telegram',
            })
        return JsonResponse(
            {'success': False, 'message': '❌ Ошибка отправки тестового сообщения'},
            status=400,
        )

    except Exception as e:
        logger.exception(f'❌ Ошибка в admin_test_telegram: {e}')
        return JsonResponse(
            {'success': False, 'message': 'Внутренняя ошибка сервера'},
            status=500,
        )


# ============================================================
# CLEAR CACHE
# ============================================================

@staff_member_required
@require_POST
def admin_clear_cache(request):
    try:
        from django.core.cache import cache
        cache.clear()
        logger.info('✅ Кеш очищен через админку')
        return JsonResponse({'success': True, 'message': '✅ Кеш успешно очищен'})
    except Exception as e:
        logger.exception(f'❌ Ошибка очистки кеша: {e}')
        return JsonResponse(
            {'success': False, 'message': 'Внутренняя ошибка сервера'},
            status=500,
        )
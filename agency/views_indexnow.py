# agency/views_indexnow.py

from django.views.generic import View
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)


@method_decorator(cache_control(max_age=86400, public=True), name='dispatch')
class IndexNowKeyView(View):
    """
    Представление для ключа IndexNow
    Доступно по URL: /{INDEXNOW_KEY}.txt

    В production генерирует ключ "на лету" без создания физического файла.
    """

    def get(self, request, *args, **kwargs):
        key = getattr(settings, 'INDEXNOW_KEY', '')

        if not key:
            logger.warning("⚠️ INDEXNOW_KEY не настроен в settings.py")
            raise Http404("IndexNow key not configured")

        # Проверяем, что запрошенный ключ соответствует настройке
        request_key = kwargs.get('key', '')
        if request_key and request_key != key:
            logger.warning(f"⚠️ Запрошен неверный ключ: {request_key}")
            raise Http404("Invalid key")

        logger.info(f"✅ Отдан ключ IndexNow: {key}")

        # Возвращаем ключ как текстовый файл
        response = HttpResponse(key, content_type='text/plain')
        response['Cache-Control'] = 'public, max-age=86400'
        response['Pragma'] = 'cache'
        response['Expires'] = None
        return response
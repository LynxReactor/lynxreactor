# agency/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class AgencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agency'
    verbose_name = _('Agency')

    def ready(self):
        try:
            from . import signals  # noqa
            logger.info("✅ Сигналы agency загружены")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки сигналов: {e}")
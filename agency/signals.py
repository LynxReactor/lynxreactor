# agency/signals.py

from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging

from .models import (
    ContactRequest,
    BlogPost,
    PortfolioItem,
    HeroSection,
    SiteConfiguration,
    ServicesSection, ServiceItem,
    TechSection, TechItem,
    LandingSection, LandingFeature, LandingDetail,
    BusinessSection, BusinessFeature, BusinessDetail,
    RefactorSection, RefactorFeature, RefactorDetail,
    PortfolioSection,
    FAQSection, FAQItem,
    CTASection,
    ReviewsSection, Review,
    BlogCategory,
    Tariff,
    PageSEO,
    Mission,
    ContactPage,
)

from .tasks import send_contact_notification_task, clear_cache_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ContactRequest)
def notify_on_contact_request(sender, instance, created, **kwargs):
    if not created:
        return

    logger.info("New contact request #%s created", instance.id)

    # Захватываем pk в локальную переменную — instance может стать
    # невалидным, если транзакция откатится или объект удалят.
    contact_id = instance.pk

    # Задача ставится ТОЛЬКО после commit транзакции.
    # В autocommit-режиме (обычный POST) — срабатывает сразу.
    # Внутри transaction.atomic() — после выхода из блока.
    transaction.on_commit(
        lambda: send_contact_notification_task.delay(contact_id)
    )


# ============================================================
# ИНВАЛИДАЦИЯ КЕША ГЛАВНОЙ — НЕ ТРЕБУЕТСЯ
# ============================================================
# Кеш homepage_context_* никогда не заполнялся (нет cache.set),
# поэтому инвалидация была мёртвой. Убрана — не дёргаем кеш
# зря на каждый post_save/post_delete контента.
#
# Если в будущем понадобится кеш главной — верните инвалидацию
# вместе с реальным кешированием в IndexView.


# ============================================================
# BLOG POST SIGNALS
# ============================================================

@receiver(post_save, sender=BlogPost)
def handle_blog_post_save(sender, instance, created, **kwargs):
    """Логирование сохранения поста блога."""
    if instance.is_published and created:
        logger.info(f"📰 Опубликован пост: {instance.title}")


@receiver(post_delete, sender=BlogPost)
def handle_blog_post_delete(sender, instance, **kwargs):
    """Логирование удаления поста блога."""
    logger.info(f"🗑️ Удален пост: {instance.title}")


# ============================================================
# PORTFOLIO SIGNALS
# ============================================================

@receiver(post_save, sender=PortfolioItem)
def handle_portfolio_save(sender, instance, created, **kwargs):
    if instance.is_active and created:
        logger.info(f"🖼️ Создан проект: {instance.get_title()}")


@receiver(post_delete, sender=PortfolioItem)
def handle_portfolio_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Удален проект: {instance.get_title()}")


# ============================================================
# SERVICE ITEM SIGNALS
# ============================================================

@receiver(post_save, sender=ServiceItem)
def handle_service_item_save(sender, instance, created, **kwargs):
    if instance.is_active and created:
        logger.info(f"💼 Создана услуга: {instance.title}")


@receiver(post_delete, sender=ServiceItem)
def handle_service_item_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Удалена услуга: {instance.title}")


# ============================================================
# TARIFF SIGNALS
# ============================================================

@receiver(post_save, sender=Tariff)
def handle_tariff_save(sender, instance, created, **kwargs):
    for lang in ('ru', 'en'):
        cache.delete(f'active_tariffs_list_{lang}')
    logger.info(f"💰 Обновлен тариф: {instance.name}")


@receiver(post_delete, sender=Tariff)
def handle_tariff_delete(sender, instance, **kwargs):
    for lang in ('ru', 'en'):
        cache.delete(f'active_tariffs_list_{lang}')
    logger.info(f"🗑️ Удален тариф: {instance.name}")


# ============================================================
# REVIEW SIGNALS
# ============================================================

@receiver(post_save, sender=Review)
def handle_review_save(sender, instance, created, **kwargs):
    logger.info(f"⭐ Обновлен отзыв: {instance.client_name}")


@receiver(post_delete, sender=Review)
def handle_review_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Удален отзыв: {instance.client_name}")


# ============================================================
# FAQ ITEM SIGNALS
# ============================================================

@receiver(post_save, sender=FAQItem)
def handle_faq_save(sender, instance, created, **kwargs):
    logger.info(f"❓ Обновлен FAQ: {instance.question[:50]}...")


@receiver(post_delete, sender=FAQItem)
def handle_faq_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Удален FAQ: {instance.question[:50]}...")


# ============================================================
# HERO SECTION SIGNALS
# ============================================================

@receiver(post_save, sender=HeroSection)
def handle_hero_save(sender, instance, created, **kwargs):
    logger.info(f"🎯 Обновлена Hero секция: {instance.get_page_display()}")


# ============================================================
# SITE CONFIGURATION SIGNALS
# ============================================================

@receiver(post_save, sender=SiteConfiguration)
def handle_site_config_save(sender, instance, created, **kwargs):
    """
    Единый обработчик SiteConfiguration:
      1. Инвалидирует кэш контекст-процессора (site_config_obj)
      2. Если включён maintenance — очищает весь кеш через Celery
    """
    # 1. Кэш контекст-процессора
    cache.delete('site_config_obj')

    # 2. Maintenance — очистка через on_commit (безопасно при транзакциях)
    if instance.is_maintenance_mode:
        logger.warning("🔧 Включен режим обслуживания — очистка кеша")
        transaction.on_commit(lambda: clear_cache_task.delay())


# ============================================================
# ВАЛИДАЦИЯ ДАТЫ ПУБЛИКАЦИИ
# ============================================================

@receiver(pre_save, sender=BlogPost)
def set_published_date(sender, instance, **kwargs):
    """Устанавливает дату публикации при первой публикации."""
    if instance.is_published and not instance.published_at:
        instance.published_at = timezone.now()
        logger.info(f"📅 Установлена дата публикации: {instance.title}")


# ============================================================
# CONTACT PAGE CACHE
# ============================================================

@receiver(post_save, sender=ContactPage)
def invalidate_contact_info_cache(sender, instance, **kwargs):
    """Инвалидирует кеш ContactPage при сохранении."""
    cache.delete('contact_info_obj')


@receiver(post_delete, sender=ContactPage)
def invalidate_contact_info_cache_on_delete(sender, instance, **kwargs):
    cache.delete('contact_info_obj')
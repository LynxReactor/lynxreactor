# agency/tasks.py

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_contact_notification_task(contact_id):
    """Отправка всех уведомлений о новой заявке."""
    from .models import ContactRequest
    from .services.email import send_contact_notifications

    try:
        contact = ContactRequest.objects.get(id=contact_id)
        results = send_contact_notifications(contact)

        logger.info(f"✅ Уведомления для заявки #{contact_id}: {results}")
        return f"Уведомления отправлены для заявки #{contact_id}: {results}"

    except ContactRequest.DoesNotExist:
        logger.error(f"❌ Заявка #{contact_id} не найдена")
        return f"Заявка #{contact_id} не найдена"
    except Exception as e:
        logger.exception(f"❌ Ошибка в send_contact_notification_task: {e}")
        raise


@shared_task
def clear_cache_task():
    """Очистка кеша"""
    try:
        cache.clear()
        logger.info("✅ Кеш очищен")
        return "Кеш очищен"
    except Exception as e:
        logger.error(f"❌ Ошибка очистки кеша: {e}")
        raise


@shared_task
def cleanup_old_contact_requests(days=30):
    """Очистка старых заявок"""
    from datetime import timedelta
    from django.utils import timezone
    from .models import ContactRequest

    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        old_requests = ContactRequest.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'rejected'],
        )
        count = old_requests.count()
        old_requests.delete()
        logger.info(f"🗑️ Удалено {count} старых заявок")
        return f"Удалено {count} старых заявок"
    except Exception as e:
        logger.error(f"❌ Ошибка очистки заявок: {e}")
        raise


@shared_task(ignore_result=True)
def send_subscribe_notification_task(subscriber_id):
    """Отправка уведомления админу о новом подписчике."""
    from .models import Subscriber
    from .services.email import send_subscribe_notification

    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        result = send_subscribe_notification(subscriber)
        return f"Subscribe notification sent: {result}"
    except Subscriber.DoesNotExist:
        logger.error(f"❌ Subscriber #{subscriber_id} not found")
        return f"Subscriber #{subscriber_id} not found"
    except Exception as e:
        logger.exception(f"❌ Error in send_subscribe_notification_task: {e}")
        raise


@shared_task(ignore_result=True)
def send_blog_post_newsletter(post_id):
    """
    Отправка рассылки о новом посте всем активным подписчикам.

    - Идёт по Subscriber.objects.filter(is_active=True)
    - Письмо через шаблон agency/emails/blog_newsletter.html
    - Персонализирует ссылку отписки для каждого подписчика
    """
    from .models import BlogPost, Subscriber
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings
    from django.utils import timezone

    try:
        post = BlogPost.objects.get(
            id=post_id,
            is_published=True,
            is_active=True,
            published_at__lte=timezone.now(),
        )
    except BlogPost.DoesNotExist:
        logger.error(f"❌ BlogPost #{post_id} not found, not published, or scheduled for future")
        return f"BlogPost #{post_id} not found"

    subscribers = Subscriber.objects.filter(is_active=True)
    total = subscribers.count()

    if not total:
        logger.info("📭 No active subscribers for newsletter")
        return "No active subscribers"

    logger.info(f"📤 Sending newsletter for post '{post.title}' to {total} subscribers")

    site_url = getattr(settings, 'SITE_URL', 'https://lynxreactor.by')
    post_url = f"{site_url}{post.get_absolute_url()}"
    subject = f"📰 Новая статья: {post.title}"

    sent = 0
    errors = 0

    for subscriber in subscribers.iterator(chunk_size=100):
        try:
            context = {
                'post': post,
                'post_url': post_url,
                'subscriber': subscriber,
                'unsubscribe_url': subscriber.get_unsubscribe_url(),
                'site_url': site_url,
            }

            html_content = render_to_string('agency/emails/blog_newsletter.html', context)
            plain_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send(fail_silently=False)

            # Обновляем last_emailed_at
            Subscriber.objects.filter(pk=subscriber.pk).update(last_emailed_at=timezone.now())
            sent += 1

        except Exception as e:
            errors += 1
            logger.warning(f'⚠️ Failed to email {subscriber.email}: {e}')

    logger.info(f"✅ Newsletter sent: {sent}/{total}, errors: {errors}")
    return f"Newsletter for post #{post_id}: sent {sent}/{total}, errors: {errors}"


@shared_task
def send_blog_newsletter_manual(post_id):
    """
    Ручной запуск рассылки (для админки).
    Обёртка над send_blog_post_newsletter с логированием.
    """
    return send_blog_post_newsletter(post_id)
# agency/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
import json
import logging
import re
import requests
from .utils import check_rate_limit, get_rate_limit_key, get_client_ip

from .models import (
    HeroSection, ServicesSection, ServiceItem,
    TechSection, TechItem,
    LandingSection, LandingFeature, LandingDetail,
    BusinessSection, BusinessFeature, BusinessDetail,
    RefactorSection, RefactorFeature, RefactorDetail,
    PortfolioSection, PortfolioItem,
    Tariff, FAQSection, FAQItem,
    CTASection, ReviewsSection, Review,
    ContactPage, BlogCategory, BlogPost, ContactRequest,
    SiteConfiguration, BlogPostVote, Mission, Subscriber,
)
from .forms import ContactForm, AjaxContactForm, SubscribeForm
from .mixins import (
    ThemeMixin,
    LanguageMixin,
    SEOContextMixin,
)

logger = logging.getLogger(__name__)


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_current_language():
    """Текущий язык без региона"""
    from django.utils.translation import get_language
    lang = get_language() or 'ru'
    return lang.split('-')[0]


# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# ============================================================

class IndexView(
    SEOContextMixin,
    ThemeMixin,
    LanguageMixin,
    TemplateView,
):
    template_name = 'agency/home.html'
    seo_page_key = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # HERO
        context['hero'] = HeroSection.objects.filter(page='home', is_active=True).first()

        # SERVICES
        services_section = ServicesSection.objects.filter(is_active=True).first()
        context['services_section'] = services_section
        context['services'] = (
            ServiceItem.objects.filter(section=services_section, is_active=True)
            .order_by('order', 'number')
            if services_section else []
        )

        # TECH
        tech_section = TechSection.objects.filter(is_active=True).first()
        context['tech_section'] = tech_section
        context['technologies'] = (
            TechItem.objects.filter(section=tech_section, is_active=True).order_by('order')
            if tech_section else []
        )

        # LANDING
        landing = LandingSection.objects.filter(is_active=True).first()
        context['landing'] = landing
        context['landing_features'] = (
            LandingFeature.objects.filter(section=landing, is_active=True).order_by('order')
            if landing else []
        )
        context['landing_details'] = (
            LandingDetail.objects.filter(section=landing, is_active=True).order_by('order')
            if landing else []
        )

        # BUSINESS
        business = BusinessSection.objects.filter(is_active=True).first()
        context['business'] = business
        context['business_features'] = (
            BusinessFeature.objects.filter(section=business, is_active=True).order_by('order')
            if business else []
        )
        context['business_details'] = (
            BusinessDetail.objects.filter(section=business, is_active=True).order_by('order')
            if business else []
        )

        # REFACTOR
        refactor = RefactorSection.objects.filter(is_active=True).first()
        context['refactor'] = refactor
        context['refactor_features'] = (
            RefactorFeature.objects.filter(section=refactor, is_active=True).order_by('order')
            if refactor else []
        )
        context['refactor_details'] = (
            RefactorDetail.objects.filter(section=refactor, is_active=True).order_by('order')
            if refactor else []
        )

        # PORTFOLIO
        portfolio_section = PortfolioSection.objects.filter(is_active=True).first()
        context['portfolio_section'] = portfolio_section
        context['portfolio_items'] = (
            PortfolioItem.objects.filter(section=portfolio_section, is_active=True)
            .order_by('-created_at')[:6]
            if portfolio_section else []
        )

        # TARIFFS — из context processor (agency.context_processors.tariffs_context)

        # FAQ
        faq_section = FAQSection.objects.filter(is_active=True).first()
        context['faq_section'] = faq_section
        context['faqs'] = (
            FAQItem.objects.filter(section=faq_section, is_active=True).order_by('order')
            if faq_section else []
        )

        # CTA
        context['cta'] = CTASection.objects.filter(is_active=True).first()

        # MISSION
        context['mission'] = Mission.objects.filter(page='home', is_active=True).first()

        # REVIEWS
        reviews_section = ReviewsSection.objects.filter(is_active=True).first()
        context['reviews_section'] = reviews_section
        context['reviews'] = (
            Review.objects.filter(section=reviews_section, is_active=True)
            .order_by('-created_at')[:6]
            if reviews_section else []
        )

        # СВЕЖИЕ ЗНАЧЕНИЯ (НЕ кешируются)
        context['form'] = ContactForm()
        context['cf_turnstile_site_key'] = settings.CF_TURNSTILE_SITE_KEY

        return context


# ============================================================
# СТРАНИЦА КОНТАКТОВ
# ============================================================

class ContactView(
    SEOContextMixin,
    ThemeMixin,
    LanguageMixin,
    TemplateView,
):
    template_name = 'agency/contact.html'
    seo_page_key = 'contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['hero'] = HeroSection.objects.filter(page='contacts', is_active=True).first()
        context['contact_page'] = ContactPage.objects.first()
        context['form'] = ContactForm()
        context['mission'] = Mission.objects.filter(page='contacts', is_active=True).first()
        context['cf_turnstile_site_key'] = settings.CF_TURNSTILE_SITE_KEY

        return context


# ============================================================
# БЛОГ
# ============================================================

class BlogListView(
    SEOContextMixin,
    ThemeMixin,
    LanguageMixin,
    ListView,
):
    """Список постов блога"""
    model = BlogPost
    template_name = 'agency/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    seo_page_key = 'blog'

    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            is_active=True,
            is_published=True,
            published_at__lte=timezone.now(),
        ).select_related('category').defer('content').order_by('-published_at', '-created_at')

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['hero'] = HeroSection.objects.filter(page='blog', is_active=True).first()

        context['categories'] = BlogCategory.objects.filter(is_active=True).annotate(
            post_count=Count(
                'posts',
                filter=Q(
                    posts__is_published=True,
                    posts__is_active=True,
                    posts__published_at__lte=timezone.now(),
                )
            )
        ).order_by('order', 'name')

        context['popular_posts'] = BlogPost.objects.filter(
            is_active=True,
            is_published=True,
            published_at__lte=timezone.now(),
        ).only(
            'id', 'title', 'slug', 'views', 'published_at', 'image_light', 'image_dark',
        ).order_by('-views', '-created_at')[:5]

        context['mission'] = Mission.objects.filter(page='blog', is_active=True).first()

        return context


class BlogDetailView(
    SEOContextMixin,
    ThemeMixin,
    LanguageMixin,
    DetailView,
):
    """Детальная страница поста"""
    model = BlogPost
    template_name = 'agency/blog_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    seo_page_key = 'blog'

    def get_queryset(self):
        return BlogPost.objects.filter(
            is_active=True,
            is_published=True,
            published_at__lte=timezone.now(),
        ).select_related('category')

    def get_seo_override(self):
        """SEO конкретного поста имеет приоритет"""
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Canonical
        context['canonical_url'] = self.request.build_absolute_uri(
            reverse('agency:blog_detail', kwargs={'slug': post.slug})
        )

        # ПОХОЖИЕ (только опубликованные в прошлом — не будущие)
        if post.category:
            context['related_posts'] = BlogPost.objects.filter(
                is_active=True,
                is_published=True,
                published_at__lte=timezone.now(),
                category=post.category,
            ).exclude(id=post.id).select_related('category').only(
                'id', 'title', 'slug', 'published_at', 'updated_at',
                'image_light', 'image_dark', 'category',
            ).order_by('-published_at')[:3]
        else:
            context['related_posts'] = []

        # НАВИГАЦИЯ
        context['previous_post'] = BlogPost.objects.filter(
            is_active=True, is_published=True,
            published_at__lt=post.published_at,
        ).only('id', 'title', 'slug').order_by('-published_at').first()

        context['next_post'] = BlogPost.objects.filter(
            is_active=True, is_published=True,
            published_at__gt=post.published_at,
            published_at__lte=timezone.now(),
        ).only('id', 'title', 'slug').order_by('published_at').first()

        ip = get_client_ip(self.request)
        user_vote = BlogPostVote.objects.filter(post=post, ip_address=ip).first()
        context['user_vote'] = user_vote.vote_type if user_vote else None

        # MISSION (для страницы статьи)
        context['mission'] = Mission.objects.filter(page='blog_detail', is_active=True).first()

        return context


class BlogCategoryView(
    SEOContextMixin,
    ThemeMixin,
    LanguageMixin,
    ListView,
):
    """Посты категории"""
    model = BlogPost
    template_name = 'agency/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    seo_page_key = 'blog'

    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'], is_active=True)
        return BlogPost.objects.filter(
            is_active=True,
            is_published=True,
            category=self.category,
            published_at__lte=timezone.now(),
        ).order_by('-published_at', '-created_at')

    def get_seo_override(self):
        """SEO категории имеет приоритет"""
        return self.category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.category
        context['hero'] = None

        context['canonical_url'] = self.request.build_absolute_uri(
            reverse('agency:blog_category', kwargs={'slug': self.category.slug})
        )

        context['categories'] = BlogCategory.objects.filter(is_active=True).annotate(
            post_count=Count(
                'posts',
                filter=Q(
                    posts__is_published=True,
                    posts__is_active=True,
                    posts__published_at__lte=timezone.now(),
                )
            )
        ).order_by('order', 'name')

        context['popular_posts'] = BlogPost.objects.filter(
            is_active=True, is_published=True,
            published_at__lte=timezone.now(),
        ).only(
            'id', 'title', 'slug', 'views', 'published_at', 'image_light', 'image_dark',
        ).order_by('-views', '-created_at')[:5]

        return context


# ============================================================
# ГОЛОСОВАНИЕ ЗА ПОСТ (ОБЪЕДИНЁННЫЙ ОБРАБОТЧИК)
# ============================================================

def _handle_blog_vote(request, post):
    """
    Общая логика голосования.
    Возвращает JsonResponse.

    Защита:
      - rate limit — 20 голосов в час на IP
      - get_client_ip() с учётом X-Forwarded-For
      - select_for_update + get_or_create от race condition
    """
    from django.db import transaction, IntegrityError

    key = get_rate_limit_key('vote', request)
    allowed, remaining = check_rate_limit(key, limit=20, period_seconds=3600)
    if not allowed:
        logger.warning(f'⚠️ Vote rate limit exceeded for {get_client_ip(request)}')
        return JsonResponse(
            {'success': False, 'error': 'Слишком много голосов. Попробуйте позже.'},
            status=429,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    vote_type = data.get('vote_type')
    if vote_type not in ('like', 'dislike'):
        return JsonResponse({'success': False, 'error': 'Invalid vote type'}, status=400)

    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    try:
        with transaction.atomic():
            post_locked = type(post).objects.select_for_update().get(pk=post.pk)

            existing = BlogPostVote.objects.filter(
                post=post_locked, ip_address=ip
            ).first()

            if existing:
                if existing.vote_type == vote_type:
                    # Отмена
                    if vote_type == 'like':
                        post_locked.likes = max(0, post_locked.likes - 1)
                    else:
                        post_locked.dislikes = max(0, post_locked.dislikes - 1)
                    post_locked.save(update_fields=['likes', 'dislikes'])
                    existing.delete()
                    return JsonResponse({
                        'success': True,
                        'action': 'removed',
                        'likes': post_locked.likes,
                        'dislikes': post_locked.dislikes,
                        'user_vote': None,
                    })
                else:
                    # Смена
                    if existing.vote_type == 'like':
                        post_locked.likes = max(0, post_locked.likes - 1)
                        post_locked.dislikes += 1
                    else:
                        post_locked.dislikes = max(0, post_locked.dislikes - 1)
                        post_locked.likes += 1
                    existing.vote_type = vote_type
                    existing.save(update_fields=['vote_type'])
                    post_locked.save(update_fields=['likes', 'dislikes'])
                    return JsonResponse({
                        'success': True,
                        'action': 'changed',
                        'likes': post_locked.likes,
                        'dislikes': post_locked.dislikes,
                        'user_vote': vote_type,
                    })

            # Новый голос — get_or_create защищает от race
            vote_obj, created = BlogPostVote.objects.get_or_create(
                post=post_locked,
                ip_address=ip,
                defaults={
                    'vote_type': vote_type,
                    'user_agent': user_agent,
                }
            )

            if not created:
                # Гонка — кто-то успел создать. Обновляем.
                if vote_obj.vote_type != vote_type:
                    vote_obj.vote_type = vote_type
                    vote_obj.save(update_fields=['vote_type'])
                    if vote_type == 'like':
                        post_locked.likes += 1
                        post_locked.dislikes = max(0, post_locked.dislikes - 1)
                    else:
                        post_locked.dislikes += 1
                        post_locked.likes = max(0, post_locked.likes - 1)
                    post_locked.save(update_fields=['likes', 'dislikes'])

                return JsonResponse({
                    'success': True,
                    'action': 'changed',
                    'likes': post_locked.likes,
                    'dislikes': post_locked.dislikes,
                    'user_vote': vote_type,
                })

            # Успешно создали — увеличиваем
            if vote_type == 'like':
                post_locked.likes += 1
            else:
                post_locked.dislikes += 1
            post_locked.save(update_fields=['likes', 'dislikes'])

            return JsonResponse({
                'success': True,
                'action': 'added',
                'likes': post_locked.likes,
                'dislikes': post_locked.dislikes,
                'user_vote': vote_type,
            })

    except IntegrityError as e:
        logger.warning(f'Vote IntegrityError (race condition) for post #{post.pk}: {e}')
        post.refresh_from_db()
        return JsonResponse({
            'success': True,
            'action': 'noop',
            'likes': post.likes,
            'dislikes': post.dislikes,
            'user_vote': vote_type,
        })
    except Exception as e:
        logger.exception(f'Vote error for post #{post.pk}: {e}')
        return JsonResponse({
            'success': False,
            'error': 'Ошибка голосования',
        }, status=500)


@csrf_protect
@require_POST
def blog_post_vote(request, slug):
    """AJAX-голосование за пост блога по slug"""
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_published=True,
        is_active=True,
        published_at__lte=timezone.now(),
    )
    return _handle_blog_vote(request, post)


@csrf_protect
@require_POST
def blog_post_vote_by_id(request, post_id):
    """AJAX-голосование за пост блога по ID"""
    post = get_object_or_404(
        BlogPost,
        id=post_id,
        is_published=True,
        is_active=True,
        published_at__lte=timezone.now(),
    )
    return _handle_blog_vote(request, post)


# ============================================================
# AJAX CONTACT
# ============================================================

@require_http_methods(["POST"])
def ajax_contact(request):
    """
    Обработка AJAX-формы обратной связи.

    Валидация выполняется через ContactForm (единый источник правил
    с обычной POST-формой на /contact/). Отличия от обычного POST:
      - Turnstile проверяется вручную (до формы)
      - Rate limit по IP
      - Из request берутся user_agent, ip, referer, language
    """
    client_ip = get_client_ip(request)

    # --- Rate limit ---
    key = get_rate_limit_key('contact', request)
    allowed, remaining = check_rate_limit(key, limit=5, period_seconds=3600)

    if not allowed:
        logger.warning(f'⚠️ Rate limit exceeded for {client_ip}')
        return JsonResponse({
            'success': False,
            'error': _('Слишком много заявок. Попробуйте через час или свяжитесь напрямую.'),
        }, status=429)

    user_agent = request.META.get('HTTP_USER_AGENT', '')[:100]
    logger.info(f'📨 Contact request from {client_ip}')

    try:
        # --- Парсинг входящих данных (JSON или form-data) ---
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        turnstile_token = data.get('cf-turnstile-response', '')

        # --- Turnstile (проверяем ДО формы) ---
        if not settings.DEBUG and not getattr(settings, 'TURNSTILE_DISABLED', False):
            if not turnstile_token:
                return JsonResponse({
                    'success': False,
                    'error': _('Please complete the captcha verification'),
                }, status=400)

            try:
                r = requests.post(
                    settings.CF_TURNSTILE_VERIFY_URL,
                    data={
                        'secret': settings.CF_TURNSTILE_SECRET_KEY,
                        'response': turnstile_token,
                        'remoteip': client_ip,
                    },
                    timeout=10,
                )
                result = r.json()

                if not result.get('success'):
                    codes = result.get('error-codes', [])
                    msg = _('Captcha verification failed. Please try again.')

                    if 'timeout' in codes:
                        msg = _('Captcha verification timed out. Please try again.')
                    elif 'invalid-input-response' in codes:
                        msg = _('Invalid captcha response. Please refresh the page and try again.')
                    elif 'invalid-input-secret' in codes:
                        logger.error('❌ Invalid Turnstile secret key!')
                        msg = _('Service configuration error. Please contact support.')

                    return JsonResponse({'success': False, 'error': msg}, status=400)

                logger.info(f'✅ Turnstile validated for {client_ip}')

            except requests.exceptions.Timeout:
                return JsonResponse({
                    'success': False,
                    'error': _('Verification service is temporarily unavailable. Please try again later.'),
                }, status=503)
            except requests.exceptions.RequestException as e:
                logger.exception(f'Turnstile error: {e}')
                return JsonResponse({
                    'success': False,
                    'error': _('Verification service is temporarily unavailable. Please try again later.'),
                }, status=503)

        # --- Валидация через AjaxContactForm (единый источник правил) ---
        # AjaxContactForm — тот же ContactForm, но без captcha
        # (Turnstile уже проверен выше вручную).
        form = AjaxContactForm(data=data)

        if not form.is_valid():
            # Приводим django ErrorDict → плоский dict {field: message}
            flat_errors = {}
            for field, errs in form.errors.items():
                if isinstance(errs, list):
                    flat_errors[field] = errs[0] if errs else ''
                else:
                    flat_errors[field] = str(errs)

            logger.warning(f'Validation errors: {list(flat_errors.keys())}')
            return JsonResponse(
                {'success': False, 'errors': flat_errors},
                status=400,
            )

        # --- Сохранение с метаданными запроса ---
        contact = form.save(commit=False)

        # Данные из request (не из формы)
        contact.turnstile_verified = bool(turnstile_token)
        contact.user_agent = user_agent
        contact.ip_address = client_ip
        contact.referer = request.META.get('HTTP_REFERER', '')

        # Язык, на котором отправлена заявка
        from django.utils.translation import get_language
        lang = (get_language() or 'ru').split('-')[0]
        if lang not in ('ru', 'en'):
            lang = 'ru'
        contact.language = lang

        contact.save()

        logger.info(f'✅ Contact #{contact.id} created from {client_ip}')

        return JsonResponse({
            'success': True,
            'message': _('Your message has been sent successfully! We will contact you shortly.'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': _('Invalid request format')}, status=400)
    except Exception as e:
        logger.exception(f'Unexpected error in ajax_contact: {e}')
        return JsonResponse({
            'success': False,
            'error': _('An internal error occurred. Please try again later.'),
        }, status=500)


# ============================================================
# AJAX SUBSCRIBE
# ============================================================

@require_http_methods(["POST"])
def ajax_subscribe(request):
    """
    Подписка на обновления блога.

    POST email, опционально source.
    Возвращает JSON {success, message}.
    """
    client_ip = get_client_ip(request)

    # Rate limit: 3 подписки в час на IP
    key = get_rate_limit_key('subscribe', request)
    allowed, remaining = check_rate_limit(key, limit=3, period_seconds=3600)
    if not allowed:
        logger.warning(f'⚠️ Subscribe rate limit exceeded for {client_ip}')
        return JsonResponse(
            {'success': False, 'error': 'Слишком много попыток. Попробуйте позже.'},
            status=429,
        )

    try:
        # Принимаем и JSON, и form-data
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        email = (data.get('email') or '').strip().lower()
        source = (data.get('source') or 'blog_detail').strip()[:50]

        # Валидация email
        if not email:
            return JsonResponse(
                {'success': False, 'error': _('Please enter your email')},
                status=400,
            )

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return JsonResponse(
                {'success': False, 'error': _('Please enter a valid email address')},
                status=400,
            )

        # Создаём или обновляем
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                'source': source,
                'ip_address': client_ip,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
                'is_active': True,
            },
        )

        # Уведомление админу (только для новых подписок)
        if created:
            try:
                from .tasks import send_subscribe_notification_task
                send_subscribe_notification_task.delay(subscriber.id)
            except Exception as e:
                logger.warning(f'Failed to queue subscribe notification: {e}')


        if not created:
            # Уже подписан — но если был отписан, включаем обратно
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=['is_active', 'updated_at'])
                return JsonResponse({
                    'success': True,
                    'message': _('You have been re-subscribed. Thank you!'),
                })
            return JsonResponse({
                'success': True,
                'message': _('You are already subscribed.'),
            })

        logger.info(f'✅ Subscriber #{subscriber.id} ({email}) from {client_ip}')

        return JsonResponse({
            'success': True,
            'message': _('Thank you for subscribing!'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': _('Invalid request format')}, status=400)
    except Exception as e:
        logger.exception(f'Unexpected error in ajax_subscribe: {e}')
        return JsonResponse(
            {'success': False, 'error': _('An internal error occurred. Please try again later.')},
            status=500,
        )


def unsubscribe_view(request):
    """
    Страница отписки от рассылки.

    GET /unsubscribe/?token=<token>
    Отписывает подписчика и показывает страницу подтверждения.
    """
    token = request.GET.get('token', '').strip()

    subscriber = None
    if token:
        try:
            subscriber = Subscriber.objects.get(unsubscribe_token=token)
        except Subscriber.DoesNotExist:
            subscriber = None

    if subscriber and subscriber.is_active:
        subscriber.unsubscribe()
        logger.info(f'📭 Unsubscribed: {subscriber.email}')
        status = 'unsubscribed'
    elif subscriber:
        status = 'already_unsubscribed'
    else:
        status = 'invalid'

    return render(
        request,
        'agency/unsubscribe.html',
        {
            'subscriber': subscriber,
            'status': status,
            'current_theme': request.COOKIES.get('theme_preference', 'light'),
        },
    )


# ============================================================
# TOGGLE THEME
# ============================================================

@require_http_methods(["POST"])
def toggle_theme(request):
    """Переключение темы"""
    theme = request.POST.get('theme', settings.DEFAULT_THEME)

    if theme not in settings.AVAILABLE_THEMES:
        return JsonResponse({'success': False, 'error': 'Invalid theme'}, status=400)

    request.session[settings.THEME_SESSION_KEY] = theme
    request.theme = theme

    logger.info(f'🔄 Theme changed to {theme}')

    response = JsonResponse({'success': True, 'theme': theme})
    response.set_cookie(
        settings.THEME_COOKIE_NAME, theme,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        samesite='Lax',
    )
    return response


# ============================================================
# ROBOTS.TXT
# ============================================================

def robots_txt(request):
    """Генерация robots.txt"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Service sections",
        "Disallow: /admin/",
        "Disallow: /api/",
        "",
        "# Service pages",
        "Disallow: /unsubscribe/",
        "Disallow: /thanks/",
        "Disallow: /maintenance/",
        "",
        "# Technical endpoints",
        "Disallow: /set-language/",
        "Disallow: /i18n/",
        "Disallow: /toggle-theme/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


# ============================================================
# MAINTENANCE
# ============================================================

def maintenance_view(request):
    """Страница обслуживания"""
    config = SiteConfiguration.objects.first()
    theme = request.COOKIES.get('theme_preference', 'light')
    return render(
        request,
        'agency/maintenance.html',
        {'config': config, 'current_theme': theme},
        status=503,
    )